"""
Stock Analysis Dashboard with Historical Put Options Backtest.

Extended version of robust_app.py that includes an Options Backtest page.
Run with: streamlit run itm_app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Stock Analysis + Options Backtest",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Page registry
# ---------------------------------------------------------------------------
def page_home():
    """Render home/welcome page (imported from robust_app logic)."""
    st.title("📊 Stock Analysis Dashboard")
    st.markdown("""
    Welcome! This dashboard helps you analyze stocks, understand drawdowns,
    and learn about put options using real market data.

    **Use the sidebar to navigate:**
    - **Home** — Overview and user guide
    - **Stock Analysis** — Charts, drawdowns, technical indicators
    - **Put Options** — Educational options explorer
    - **Options Backtest** — Historical put P&L backtest
    """)

    st.info(
        "Select **Options Backtest** in the sidebar to run historical put option "
        "backtests across 16 tickers with data from 2010–2026."
    )


def page_options_backtest():
    """Historical Put Options P&L Backtest page."""
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px
    from datetime import date
    from options_utils import (
        available_tickers,
        ticker_date_range,
        load_puts_for_backtest,
        compute_put_backtest,
        compute_backtest_summary,
    )

    st.title("Historical Put Options P&L Backtest")
    st.markdown(
        "If you bought a put on day X, what would your P&L be at various horizons? "
        "Select parameters and click **Run Backtest** to find out."
    )

    # ── Sidebar controls ──────────────────────────────────────────────────
    st.sidebar.header("Backtest Parameters")

    tickers = available_tickers()
    default_idx = tickers.index("PLTR") if "PLTR" in tickers else 0
    ticker = st.sidebar.selectbox("Ticker", tickers, index=default_idx)

    # Get ticker date bounds (cached to avoid re-reading on every rerun)
    @st.cache_data(ttl=3600)
    def _date_range(t):
        return ticker_date_range(t)

    data_min, data_max = _date_range(ticker)
    today = date.today()
    # entry_end can't go past today; clamp data_max as well
    max_date = min(data_max.date(), today)
    min_date = data_min.date()

    st.sidebar.caption(f"Data available: **{min_date}** to **{max_date}**")

    # Default start: 1 year before max_date (or min_date if range is short)
    default_start = max(min_date, (pd.Timestamp(max_date) - pd.DateOffset(years=2)).date())
    default_end = max_date

    col_start, col_end = st.sidebar.columns(2)
    with col_start:
        entry_start = st.sidebar.date_input(
            "Entry start",
            value=default_start,
            min_value=min_date,
            max_value=max_date,
        )
    with col_end:
        entry_end = st.sidebar.date_input(
            "Entry end",
            value=default_end,
            min_value=min_date,
            max_value=max_date,
        )

    moneyness = st.sidebar.selectbox(
        "Moneyness",
        ["ATM", "5% OTM", "10% OTM", "15% OTM", "20% OTM"],
        index=0,
    )

    min_dte_weeks = st.sidebar.slider(
        "Min DTE at entry (weeks)", min_value=4, max_value=52, value=24
    )
    min_dte_days = min_dte_weeks * 7

    all_horizons = [1, 2, 3, 4, 8, 12, 16, 20, 24]
    horizons = st.sidebar.multiselect(
        "Horizons (weeks)",
        all_horizons,
        default=all_horizons,
    )

    if not horizons:
        st.warning("Select at least one horizon.")
        return

    max_horizon_days = max(horizons) * 7 + 7  # extra week buffer

    run_clicked = st.sidebar.button("Run Backtest", type="primary")

    # ── Caching wrappers ──────────────────────────────────────────────────
    @st.cache_data(ttl=600, show_spinner="Loading options data...")
    def _load(ticker, entry_start, entry_end, max_horizon_days):
        return load_puts_for_backtest(
            ticker,
            str(entry_start),
            str(entry_end),
            max_horizon_days=max_horizon_days,
        )

    @st.cache_data(ttl=600, show_spinner="Computing backtest...")
    def _backtest(ticker, entry_start, entry_end, moneyness, min_dte_days, horizons, max_horizon_days):
        df = _load(ticker, entry_start, entry_end, max_horizon_days)
        return compute_put_backtest(
            df,
            str(entry_start),
            str(entry_end),
            moneyness=moneyness,
            min_dte_days=min_dte_days,
            horizons_weeks=horizons,
        )

    # ── Run backtest ──────────────────────────────────────────────────────
    if run_clicked:
        st.session_state["bt_params"] = {
            "ticker": ticker,
            "entry_start": str(entry_start),
            "entry_end": str(entry_end),
            "moneyness": moneyness,
            "min_dte_days": min_dte_days,
            "horizons": horizons,
            "max_horizon_days": max_horizon_days,
        }

    params = st.session_state.get("bt_params")
    if params is None:
        st.info("Configure parameters in the sidebar and click **Run Backtest**.")
        return

    backtest_df = _backtest(
        params["ticker"],
        params["entry_start"],
        params["entry_end"],
        params["moneyness"],
        params["min_dte_days"],
        params["horizons"],
        params["max_horizon_days"],
    )

    if backtest_df.empty:
        st.error(
            "No qualifying contracts found. Try a different ticker, date range, "
            "or lower the Min DTE."
        )
        return

    horizons = params["horizons"]
    summary_df = compute_backtest_summary(backtest_df, horizons)

    st.success(
        f"Backtest complete: **{len(backtest_df)}** entry dates, "
        f"**{params['ticker']}** {params['moneyness']} puts, "
        f"min DTE {params['min_dte_days']}d"
    )

    # ── 1. Summary table ─────────────────────────────────────────────────
    st.subheader("Summary Statistics")

    display_cols = [
        "horizon_label", "win_rate", "avg_return_pct", "median_return_pct",
        "std_return_pct", "max_return_pct", "min_return_pct", "n_entries", "n_expired",
    ]
    display_df = summary_df[display_cols].copy()
    display_df.columns = [
        "Horizon", "Win Rate %", "Avg Return %", "Median Return %",
        "Std Dev %", "Max Return %", "Min Return %", "Entries", "Expired",
    ]

    def _color_val(val, col_name):
        """Return CSS for green (positive) / red (negative) styling."""
        if col_name == "Win Rate %" and pd.notna(val):
            color = "green" if val > 50 else ("red" if val < 50 else "inherit")
            return f"color: {color}; font-weight: bold"
        if col_name in ("Avg Return %", "Median Return %") and pd.notna(val):
            color = "green" if val > 0 else ("red" if val < 0 else "inherit")
            return f"color: {color}; font-weight: bold"
        return ""

    styled = display_df.style.apply(
        lambda s: [
            _color_val(v, s.name) for v in s
        ],
        axis=0,
    ).format(
        {
            "Win Rate %": "{:.1f}",
            "Avg Return %": "{:.1f}",
            "Median Return %": "{:.1f}",
            "Std Dev %": "{:.1f}",
            "Max Return %": "{:.1f}",
            "Min Return %": "{:.1f}",
        },
        na_rep="—",
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── 2. P&L distribution (box / violin) ────────────────────────────────
    st.subheader("P&L Distribution by Horizon")
    chart_type = st.radio(
        "Chart type", ["Box plot", "Violin plot"], horizontal=True, label_visibility="collapsed"
    )

    # Melt the P&L % columns for plotting
    pct_cols = [f"pl_pct_{hw}w" for hw in horizons if f"pl_pct_{hw}w" in backtest_df.columns]
    labels = {f"pl_pct_{hw}w": f"{hw}w" for hw in horizons}

    melt_df = backtest_df[["entry_date"] + pct_cols].melt(
        id_vars="entry_date", var_name="horizon", value_name="return_pct"
    )
    melt_df["horizon"] = melt_df["horizon"].map(labels)
    melt_df = melt_df.dropna(subset=["return_pct"])

    if chart_type == "Box plot":
        fig_dist = px.box(
            melt_df, x="horizon", y="return_pct",
            labels={"return_pct": "Return %", "horizon": "Horizon"},
            color="horizon",
        )
    else:
        fig_dist = px.violin(
            melt_df, x="horizon", y="return_pct",
            labels={"return_pct": "Return %", "horizon": "Horizon"},
            color="horizon", box=True,
        )

    fig_dist.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.6)
    fig_dist.update_layout(
        showlegend=False,
        height=450,
        margin=dict(t=30, b=40),
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    # ── 3. Heatmap: entry date × horizon ──────────────────────────────────
    st.subheader("P&L Heatmap (Entry Date × Horizon)")

    heat_cols = [f"pl_pct_{hw}w" for hw in horizons if f"pl_pct_{hw}w" in backtest_df.columns]
    heat_labels = [f"{hw}w" for hw in horizons if f"pl_pct_{hw}w" in backtest_df.columns]

    heat_matrix = backtest_df[heat_cols].values
    entry_dates_str = backtest_df["entry_date"].dt.strftime("%Y-%m-%d").values

    # Subsample rows if too many for readable heatmap
    max_rows = 200
    if len(entry_dates_str) > max_rows:
        step = len(entry_dates_str) // max_rows
        heat_matrix = heat_matrix[::step]
        entry_dates_str = entry_dates_str[::step]

    fig_heat = go.Figure(
        data=go.Heatmap(
            z=heat_matrix,
            x=heat_labels,
            y=entry_dates_str,
            colorscale="RdYlGn",
            zmid=0,
            colorbar=dict(title="Return %"),
            hoverongaps=False,
            hovertemplate="Entry: %{y}<br>Horizon: %{x}<br>Return: %{z:.1f}%<extra></extra>",
        )
    )
    fig_heat.update_layout(
        xaxis_title="Horizon",
        yaxis_title="Entry Date",
        yaxis=dict(autorange="reversed"),
        height=max(400, min(len(entry_dates_str) * 4, 800)),
        margin=dict(t=30, b=40),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # ── 4. Rolling win rate ───────────────────────────────────────────────
    st.subheader("Rolling Win Rate (20-entry window)")

    fig_roll = go.Figure()
    for hw in horizons:
        col = f"pl_pct_{hw}w"
        if col not in backtest_df.columns:
            continue
        wins = (backtest_df[col] > 0).astype(float)
        rolling_wr = wins.rolling(20, min_periods=10).mean() * 100
        fig_roll.add_trace(
            go.Scatter(
                x=backtest_df["entry_date"],
                y=rolling_wr,
                mode="lines",
                name=f"{hw}w",
            )
        )

    fig_roll.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.6)
    fig_roll.update_layout(
        xaxis_title="Entry Date",
        yaxis_title="Win Rate %",
        yaxis=dict(range=[0, 100]),
        legend_title="Horizon",
        height=400,
        margin=dict(t=30, b=40),
    )
    st.plotly_chart(fig_roll, use_container_width=True)

    # ── Expander: raw data ────────────────────────────────────────────────
    with st.expander("View raw backtest data"):
        st.dataframe(backtest_df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
PAGES = {
    "Home": page_home,
    "Options Backtest": page_options_backtest,
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()), label_visibility="collapsed")

PAGES[selection]()
