"""
Compare BTC, ETH, SOL, SUI, and ZEC at minute resolution for lead-lag relationships.

Uses Binance US /klines API (free, no key needed) for ~1 year of 1-minute data.
Prices are min-max normalized per asset.  Lead-lag analysis tests +/- 60 minutes.

Usage:
    python crypto_lead_lag.py
"""

import requests
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timezone, timedelta

# ── config ──────────────────────────────────────────────────────────────────
SYMBOLS = {
    "BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT",
    "SUI": "SUIUSDT", "ZEC": "ZECUSDT",
}
BASE_URL = "https://api.binance.us/api/v3/klines"
LIMIT = 1000  # max per request
LOOKBACK_DAYS = 365


def fetch_minute(symbol, pair, days=LOOKBACK_DAYS):
    """Paginate forward from (now - days) to now, 1000 bars at a time."""
    start_ms = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    all_rows = []
    cursor = start_ms
    while cursor < end_ms:
        r = requests.get(BASE_URL, params={
            "symbol": pair,
            "interval": "1m",
            "startTime": cursor,
            "limit": LIMIT,
        }, timeout=30)
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        all_rows.extend(data)
        # each row: [open_time, o, h, l, c, vol, close_time, ...]
        cursor = data[-1][6] + 1  # close_time + 1ms
        if len(data) < LIMIT:
            break
    df = pd.DataFrame(all_rows, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_vol", "trades", "taker_buy_base",
        "taker_buy_quote", "ignore",
    ])
    df["time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["close"] = df["close"].astype(float)
    df = df.set_index("time").sort_index()
    df = df[~df.index.duplicated(keep="last")]
    return df["close"].rename(symbol)


# ── fetch data ──────────────────────────────────────────────────────────────
print(f"Fetching {LOOKBACK_DAYS} days of 1-minute data from Binance US...")
prices = {}
for sym, pair in SYMBOLS.items():
    t0 = time.time()
    s = fetch_minute(sym, pair)
    elapsed = time.time() - t0
    prices[sym] = s
    print(f"  {sym}: {len(s):,} bars, {s.index.min()} to {s.index.max()}  ({elapsed:.1f}s)")

df = pd.DataFrame(prices).sort_index()
df.index = df.index.tz_localize(None)
df = df.ffill(limit=5)

# ── normalise to [0, 1] per asset ──────────────────────────────────────────
norm = (df - df.min()) / (df.max() - df.min())

# ── minute log-returns ─────────────────────────────────────────────────────
log_ret = np.log(df / df.shift(1)).dropna(how="all")

# ── lead-lag: +/- 60 minutes ──────────────────────────────────────────────
LAGS = range(-60, 61)
ROLL_WINDOW = 60 * 24  # 1 day of minutes

from itertools import combinations
pairs = list(combinations(SYMBOLS.keys(), 2))

print(f"\nComputing lead-lag correlations (+/- 60 min) for {len(pairs)} pairs...")
lag_summary = {}
for a, b in pairs:
    common = log_ret[[a, b]].dropna()
    corrs = {}
    for lag in LAGS:
        shifted = common[b].shift(-lag)
        valid = pd.concat([common[a], shifted], axis=1).dropna()
        corrs[lag] = valid.iloc[:, 0].corr(valid.iloc[:, 1])
    best_lag = max(corrs, key=corrs.get)
    lag_summary[(a, b)] = (best_lag, corrs[best_lag], corrs)
    print(f"  {a}-{b}: done")

# ── build figure ────────────────────────────────────────────────────────────
COLORS = {
    "BTC": "#F7931A", "ETH": "#627EEA", "SOL": "#00FFA3",
    "SUI": "#4DA2FF", "ZEC": "#ECB244",
}

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.06,
    row_heights=[0.50, 0.25, 0.25],
    subplot_titles=[
        "Normalised prices (min-max scaled, 1-minute bars)",
        "24-hour rolling correlation of minute log-returns",
        "Lead-lag profile (avg correlation vs lag in minutes)",
    ],
)

# row 1: normalised prices (downsample to hourly for plotting performance)
norm_hourly = norm.resample("1h").last().dropna(how="all")
for name in SYMBOLS:
    fig.add_trace(
        go.Scatter(
            x=norm_hourly.index, y=norm_hourly[name], name=name,
            line=dict(color=COLORS[name], width=1.5),
        ),
        row=1, col=1,
    )

# row 2: rolling correlation (lag=0), downsampled to hourly for plotting
for a, b in pairs:
    common = log_ret[[a, b]].dropna()
    rc = common[a].rolling(ROLL_WINDOW).corr(common[b])
    rc_hourly = rc.resample("1h").last().dropna()
    fig.add_trace(
        go.Scatter(
            x=rc_hourly.index, y=rc_hourly, name=f"{a}-{b}",
            line=dict(width=1.3),
        ),
        row=2, col=1,
    )
fig.add_hline(y=0, line_dash="dot", line_color="gray", row=2, col=1)

# row 3: lag profile bars
for a, b in pairs:
    _, _, corrs = lag_summary[(a, b)]
    lags_list = sorted(corrs.keys())
    fig.add_trace(
        go.Bar(
            x=[l for l in lags_list],
            y=[corrs[l] for l in lags_list],
            name=f"{a} vs {b}",
            opacity=0.7,
        ),
        row=3, col=1,
    )

fig.update_layout(
    height=1050, width=1200,
    template="plotly_dark",
    title_text="Crypto lead-lag analysis: BTC / ETH / SOL / SUI / ZEC (1-minute, last year)",
    legend=dict(orientation="h", y=-0.05),
    barmode="group",
)
fig.update_yaxes(title_text="Scaled price", row=1, col=1)
fig.update_yaxes(title_text="Correlation", row=2, col=1)
fig.update_xaxes(title_text="Lag (minutes, negative = first asset leads)", row=3, col=1)

# ── print summary ───────────────────────────────────────────────────────────
print(f"\nData range: {df.index.min()} to {df.index.max()}  ({len(df):,} minute bars)")
print(f"\n=== Lead-lag summary (minute log-returns, +/-60 min) ===")
print(f"{'Pair':<12} {'Best lag':>10} {'Corr':>8}")
print("-" * 36)
for (a, b), (lag, corr, _) in lag_summary.items():
    direction = (
        f"{a} leads by {abs(lag)}m" if lag < 0
        else f"{b} leads by {lag}m" if lag > 0
        else "synchronous"
    )
    print(f"{a}-{b:<8} {lag:>+5}m      {corr:.5f}   ({direction})")

fig.show()
