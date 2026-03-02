"""
Utility functions for put options education dashboard.

Supports multi-ticker options data stored as parquet files in options_data/.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional

OPTIONS_DATA_DIR = Path("options_data")

# Educational resource links
EDUCATIONAL_LINKS = {
    # Beginner Resources
    "put_options_intro": "https://www.investopedia.com/terms/p/putoption.asp",
    "cboe_education": "https://www.cboe.com/education/",
    "long_put_strategy": "https://www.optionsplaybook.com/option-strategies/long-put/",

    # Greeks
    "delta": "https://www.investopedia.com/terms/d/delta.asp",
    "theta": "https://www.investopedia.com/terms/t/theta.asp",
    "gamma": "https://www.investopedia.com/terms/g/gamma.asp",
    "vega": "https://www.investopedia.com/terms/v/vega.asp",

    # AMD-specific
    "yahoo_amd_options": "https://finance.yahoo.com/quote/AMD/options/",
}


def available_tickers() -> list[str]:
    """Return sorted list of tickers that have options data parquet files."""
    tickers = sorted(
        p.stem.replace("_options", "")
        for p in OPTIONS_DATA_DIR.glob("*_options.parquet")
    )
    # Also check for legacy AMD location
    if not tickers or "AMD" not in tickers:
        legacy = OPTIONS_DATA_DIR / "amd_test" / "AMD_options.parquet"
        if legacy.exists() and "AMD" not in tickers:
            tickers = sorted(tickers + ["AMD"])
    return tickers


def _resolve_parquet_path(ticker: str) -> Path:
    """Resolve the parquet file path for a given ticker."""
    path = OPTIONS_DATA_DIR / f"{ticker}_options.parquet"
    if path.exists():
        return path
    # Legacy AMD path
    legacy = OPTIONS_DATA_DIR / "amd_test" / f"{ticker}_options.parquet"
    if legacy.exists():
        return legacy
    raise FileNotFoundError(f"No options data found for {ticker}")


def ticker_date_range(ticker: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    """
    Return (min_date, max_date) available in a ticker's parquet file.

    Reads only the 'date' column via pyarrow for speed (~0.1s even for large files).
    """
    import pyarrow.parquet as pq
    import pyarrow.compute as pc

    path = _resolve_parquet_path(ticker)
    table = pq.read_table(path, columns=["date"])
    col = table.column("date")
    mn = pd.Timestamp(pc.min(col).as_py())
    mx = pd.Timestamp(pc.max(col).as_py())
    return mn, mx


def load_puts(
    ticker: str = "AMD",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Load options data for a ticker and filter to puts only.

    Args:
        ticker: Stock ticker symbol (e.g. "AAPL", "TSLA")
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)

    Returns:
        DataFrame with put options data
    """
    path = _resolve_parquet_path(ticker)
    df = pd.read_parquet(path)

    # Filter to puts only (handle mixed case: 'put', 'PUT')
    df = df[df["type"].str.upper() == "PUT"].copy()

    # Ensure date columns are datetime
    df["date"] = pd.to_datetime(df["date"])
    df["expiration"] = pd.to_datetime(df["expiration"])

    # Apply date filters
    if start_date:
        df = df[df["date"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["date"] <= pd.to_datetime(end_date)]

    return df


def load_amd_puts(
    parquet_path: str = "options_data/amd_test/AMD_options.parquet",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Backward-compatible wrapper. Use load_puts() for new code."""
    return load_puts("AMD", start_date=start_date, end_date=end_date)


def classify_moneyness(strike: float, current_price: float, threshold: float = 0.02) -> str:
    """
    Classify option as ITM, ATM, or OTM.

    Args:
        strike: Option strike price
        current_price: Current stock price
        threshold: Percentage threshold for ATM classification (default 2%)

    Returns:
        "ITM" (in-the-money), "ATM" (at-the-money), or "OTM" (out-of-the-money)
    """
    pct_diff = (strike - current_price) / current_price

    if abs(pct_diff) <= threshold:
        return "ATM"
    elif strike > current_price:
        return "ITM"  # For puts, strike > price = ITM
    else:
        return "OTM"


def calculate_break_even(strike: float, premium: float) -> float:
    """
    Calculate break-even price for a long put position.

    Break-even = Strike Price - Premium Paid

    Args:
        strike: Strike price
        premium: Premium paid per share

    Returns:
        Break-even stock price
    """
    return strike - premium


def calculate_position_size(
    account_value: float,
    risk_percent: float,
    premium_per_contract: float,
) -> int:
    """
    Calculate maximum number of contracts based on risk tolerance.

    Args:
        account_value: Total account value in dollars
        risk_percent: Maximum percentage of account to risk (0-100)
        premium_per_contract: Premium per contract (premium * 100)

    Returns:
        Maximum number of contracts (floored to int)
    """
    if premium_per_contract <= 0:
        return 0

    max_risk = account_value * (risk_percent / 100)
    max_contracts = max_risk / premium_per_contract

    return int(max_contracts)


def estimate_put_value_change(
    price_change: float,
    delta: float,
    gamma: float,
    current_premium: float,
) -> float:
    """
    Estimate new put premium using delta-gamma approximation.

    New Premium ≈ Old Premium + (Delta * Price Change) + (0.5 * Gamma * Price Change²)

    Note: For puts, delta is negative, so price decreases increase put value.

    Args:
        price_change: Change in underlying stock price
        delta: Option delta (negative for puts)
        gamma: Option gamma
        current_premium: Current option premium

    Returns:
        Estimated new premium
    """
    delta_effect = delta * price_change
    gamma_effect = 0.5 * gamma * (price_change ** 2)

    new_premium = current_premium + delta_effect + gamma_effect
    return max(0, new_premium)  # Premium can't go negative


def calculate_time_decay(
    days_remaining: int,
    theta: float,
    current_premium: float,
) -> pd.DataFrame:
    """
    Calculate projected premium decay over time.

    Uses square root decay curve: premium decays faster as expiration approaches.

    Args:
        days_remaining: Days until expiration
        theta: Daily theta (usually negative)
        current_premium: Current option premium

    Returns:
        DataFrame with days and projected premium columns
    """
    if days_remaining <= 0:
        return pd.DataFrame({"days": [0], "premium": [current_premium]})

    days = list(range(days_remaining + 1))
    premiums = []

    for day in days:
        days_passed = days_remaining - day
        # Square root decay approximation
        if days_remaining > 0:
            decay_factor = np.sqrt(day / days_remaining)
            # Total theta decay adjusted by sqrt factor
            total_decay = abs(theta) * days_passed * (1 - decay_factor * 0.3)
            premium = max(0, current_premium - total_decay)
        else:
            premium = current_premium
        premiums.append(premium)

    return pd.DataFrame({
        "days_remaining": list(reversed(days)),
        "premium": list(reversed(premiums)),
    })


def calculate_pl_scenarios(
    strike: float,
    premium: float,
    price_range: Optional[list] = None,
    num_points: int = 11,
) -> pd.DataFrame:
    """
    Calculate profit/loss at various stock prices for a long put.

    Long Put P/L at expiration:
    - If Stock Price < Strike: P/L = Strike - Stock Price - Premium
    - If Stock Price >= Strike: P/L = -Premium (max loss)

    Args:
        strike: Strike price
        premium: Premium paid per share
        price_range: [min_price, max_price] or None for auto-range
        num_points: Number of price points to calculate

    Returns:
        DataFrame with stock_price, pl_per_share, pl_per_contract columns
    """
    if price_range is None:
        # Auto-generate range around strike
        price_range = [strike * 0.7, strike * 1.3]

    prices = np.linspace(price_range[0], price_range[1], num_points)

    results = []
    for price in prices:
        if price < strike:
            # Put is ITM at expiration
            pl_per_share = strike - price - premium
        else:
            # Put expires worthless
            pl_per_share = -premium

        results.append({
            "stock_price": round(price, 2),
            "pl_per_share": round(pl_per_share, 2),
            "pl_per_contract": round(pl_per_share * 100, 2),
        })

    return pd.DataFrame(results)


def load_puts_for_backtest(
    ticker: str,
    entry_start: str,
    entry_end: str,
    max_horizon_days: int = 168,
    columns: Optional[list[str]] = None,
) -> pd.DataFrame:
    """
    Load put options data with pyarrow predicate pushdown for backtest efficiency.

    Loads only the date range needed (entry_start through entry_end + max_horizon_days)
    and only the columns needed, keeping memory usage manageable even for large tickers.

    Args:
        ticker: Stock ticker symbol
        entry_start: First entry date (YYYY-MM-DD)
        entry_end: Last entry date (YYYY-MM-DD)
        max_horizon_days: Days beyond entry_end to load for exit lookups
        columns: Columns to load. Default: contractID, date, strike, expiration, mark, delta

    Returns:
        DataFrame with filtered put options data
    """
    import pyarrow.parquet as pq
    import pyarrow.compute as pc
    import pyarrow as pa

    if columns is None:
        columns = ["contractID", "date", "strike", "expiration", "mark", "delta"]

    path = _resolve_parquet_path(ticker)

    # Compute the full date range we need: entry_start through entry_end + horizon
    end_dt = pd.to_datetime(entry_end) + pd.Timedelta(days=max_horizon_days)

    # Detect whether the parquet stores date as string or timestamp
    schema = pq.read_schema(path)
    date_field = schema.field("date")
    date_is_timestamp = pa.types.is_timestamp(date_field.type)

    if date_is_timestamp:
        date_min = pd.Timestamp(entry_start)
        date_max = pd.Timestamp(end_dt)
    else:
        date_min = entry_start
        date_max = end_dt.strftime("%Y-%m-%d")

    # Read with pyarrow filters for predicate pushdown
    table = pq.read_table(
        path,
        columns=columns,
        filters=[
            ("date", ">=", date_min),
            ("date", "<=", date_max),
            ("type", "=", "put"),
        ],
    )

    # If no rows matched with lowercase, try uppercase
    if table.num_rows == 0:
        table = pq.read_table(
            path,
            columns=columns + ["type"] if "type" not in columns else columns,
            filters=[
                ("date", ">=", date_min),
                ("date", "<=", date_max),
                ("type", "=", "PUT"),
            ],
        )

    df = table.to_pandas()

    # Drop type column if we added it just for filtering
    if "type" in df.columns and "type" not in (columns or []):
        df = df.drop(columns=["type"])

    # Convert date strings to datetime
    df["date"] = pd.to_datetime(df["date"])
    df["expiration"] = pd.to_datetime(df["expiration"])

    return df


def compute_put_backtest(
    df: pd.DataFrame,
    entry_start: str,
    entry_end: str,
    moneyness: str = "ATM",
    min_dte_days: int = 168,
    horizons_weeks: Optional[list[int]] = None,
) -> pd.DataFrame:
    """
    Run a put options backtest: for each entry date, buy a put and track P&L at N-week horizons.

    Args:
        df: DataFrame from load_puts_for_backtest (must have contractID, date, strike, expiration, mark, delta)
        entry_start: First entry date (YYYY-MM-DD)
        entry_end: Last entry date (YYYY-MM-DD)
        moneyness: Target moneyness - "ATM", "5% OTM", "10% OTM", "15% OTM", "20% OTM"
        min_dte_days: Minimum days to expiration at entry
        horizons_weeks: List of horizon weeks to evaluate. Default: [1,2,3,4,8,12,16,20,24]

    Returns:
        DataFrame with one row per entry date and columns for each horizon's P&L
    """
    if horizons_weeks is None:
        horizons_weeks = [1, 2, 3, 4, 8, 12, 16, 20, 24]

    # Map moneyness to target |delta|
    delta_targets = {
        "ATM": 0.50,
        "5% OTM": 0.35,
        "10% OTM": 0.25,
        "15% OTM": 0.18,
        "20% OTM": 0.12,
    }
    target_delta = delta_targets.get(moneyness, 0.50)

    # Build O(1) lookup: {(contractID, date) -> mark}
    mark_lookup = {}
    for row in df.itertuples(index=False):
        mark_lookup[(row.contractID, row.date)] = row.mark

    # Get sorted unique trading dates as pandas DatetimeIndex for consistent types
    all_dates = pd.DatetimeIndex(np.sort(df["date"].unique()))
    entry_start_dt = pd.to_datetime(entry_start)
    entry_end_dt = pd.to_datetime(entry_end)

    # Filter to entry date range
    entry_dates = all_dates[(all_dates >= entry_start_dt) & (all_dates <= entry_end_dt)]

    results = []

    for entry_date in entry_dates:
        entry_date_ts = pd.Timestamp(entry_date)

        # Filter to puts available on this entry date
        day_df = df[df["date"] == entry_date].copy()

        # Filter: DTE >= min_dte_days, mark > 0.01
        day_df = day_df[
            ((day_df["expiration"] - entry_date_ts).dt.days >= min_dte_days)
            & (day_df["mark"] > 0.01)
        ]

        if day_df.empty:
            continue

        # Filter to valid delta values (puts have negative delta)
        day_df = day_df[day_df["delta"].notna() & (day_df["delta"] < 0)]
        if day_df.empty:
            continue

        # Select contract closest to target |delta|
        day_df = day_df.copy()
        day_df["delta_dist"] = (day_df["delta"].abs() - target_delta).abs()
        best = day_df.loc[day_df["delta_dist"].idxmin()]

        contract_id = best["contractID"]
        entry_mark = best["mark"]
        entry_delta = best["delta"]
        entry_strike = best["strike"]
        entry_expiration = best["expiration"]

        row = {
            "entry_date": entry_date_ts,
            "contract_id": contract_id,
            "entry_mark": entry_mark,
            "entry_delta": entry_delta,
            "strike": entry_strike,
            "expiration": entry_expiration,
            "dte_at_entry": (entry_expiration - entry_date_ts).days,
        }

        for hw in horizons_weeks:
            target_date = entry_date_ts + pd.Timedelta(weeks=hw)

            # Check if contract expired before horizon
            expired = target_date > entry_expiration

            # Snap to nearest trading date using searchsorted
            idx = np.searchsorted(all_dates, target_date)

            # Find nearest trading date within ±3 days
            exit_mark = np.nan
            best_date = None
            min_gap = pd.Timedelta(days=999)

            for candidate_idx in [idx - 1, idx, idx + 1, idx - 2, idx + 2]:
                if 0 <= candidate_idx < len(all_dates):
                    cand_date = pd.Timestamp(all_dates[candidate_idx])
                    gap = abs(cand_date - target_date)
                    if gap <= pd.Timedelta(days=3) and gap < min_gap:
                        lookup_mark = mark_lookup.get((contract_id, cand_date))
                        if lookup_mark is not None:
                            exit_mark = lookup_mark
                            best_date = cand_date
                            min_gap = gap

            # If expired and no mark found, use last available mark
            if expired and np.isnan(exit_mark):
                # Search backwards from expiration for last available mark
                exp_idx = np.searchsorted(all_dates, entry_expiration)
                for search_idx in range(min(exp_idx, len(all_dates) - 1), -1, -1):
                    cand_date = pd.Timestamp(all_dates[search_idx])
                    if cand_date < entry_date_ts:
                        break
                    lookup_mark = mark_lookup.get((contract_id, cand_date))
                    if lookup_mark is not None:
                        exit_mark = lookup_mark
                        break

            if not np.isnan(exit_mark):
                pl_dollar = exit_mark - entry_mark
                pl_pct = (pl_dollar / entry_mark) * 100 if entry_mark > 0 else np.nan
            else:
                pl_dollar = np.nan
                pl_pct = np.nan

            row[f"pl_{hw}w"] = pl_dollar
            row[f"pl_pct_{hw}w"] = pl_pct
            row[f"expired_{hw}w"] = expired

        results.append(row)

    if not results:
        return pd.DataFrame()

    return pd.DataFrame(results)


def compute_backtest_summary(
    backtest_df: pd.DataFrame,
    horizons_weeks: Optional[list[int]] = None,
) -> pd.DataFrame:
    """
    Compute summary statistics per horizon from backtest results.

    Args:
        backtest_df: DataFrame from compute_put_backtest
        horizons_weeks: List of horizon weeks. Default: [1,2,3,4,8,12,16,20,24]

    Returns:
        DataFrame with one row per horizon: win_rate, avg_return_pct, median_return_pct,
        std_return_pct, max_return_pct, min_return_pct, n_entries, n_expired
    """
    if horizons_weeks is None:
        horizons_weeks = [1, 2, 3, 4, 8, 12, 16, 20, 24]

    if backtest_df.empty:
        return pd.DataFrame()

    rows = []
    for hw in horizons_weeks:
        col = f"pl_pct_{hw}w"
        exp_col = f"expired_{hw}w"

        if col not in backtest_df.columns:
            continue

        returns = backtest_df[col].dropna()
        n_entries = len(returns)

        if n_entries == 0:
            rows.append({
                "horizon_weeks": hw,
                "horizon_label": f"{hw}w",
                "win_rate": np.nan,
                "avg_return_pct": np.nan,
                "median_return_pct": np.nan,
                "std_return_pct": np.nan,
                "max_return_pct": np.nan,
                "min_return_pct": np.nan,
                "n_entries": 0,
                "n_expired": 0,
            })
            continue

        n_expired = backtest_df[exp_col].sum() if exp_col in backtest_df.columns else 0
        win_rate = (returns > 0).sum() / n_entries * 100

        rows.append({
            "horizon_weeks": hw,
            "horizon_label": f"{hw}w",
            "win_rate": round(win_rate, 1),
            "avg_return_pct": round(returns.mean(), 2),
            "median_return_pct": round(returns.median(), 2),
            "std_return_pct": round(returns.std(), 2),
            "max_return_pct": round(returns.max(), 2),
            "min_return_pct": round(returns.min(), 2),
            "n_entries": n_entries,
            "n_expired": int(n_expired),
        })

    return pd.DataFrame(rows)


def get_iv_smile_data(
    df: pd.DataFrame,
    date: str,
    expiration: str,
) -> pd.DataFrame:
    """
    Extract implied volatility vs strike data for IV smile/skew visualization.

    Args:
        df: DataFrame with put options data
        date: Quote date (YYYY-MM-DD)
        expiration: Expiration date (YYYY-MM-DD)

    Returns:
        DataFrame with strike and implied_volatility columns, sorted by strike
    """
    mask = (
        (df["date"] == pd.to_datetime(date)) &
        (df["expiration"] == pd.to_datetime(expiration))
    )

    subset = df.loc[mask, ["strike", "implied_volatility"]].copy()
    subset = subset.dropna()
    subset = subset.sort_values("strike")

    return subset
