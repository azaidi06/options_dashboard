"""
Stock Analysis Dashboard with Gradient-Colored Price Charts

A Streamlit dashboard for visualizing stock price data with percentage change
from rolling highs displayed as gradient colors.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Optional

from utils import (
    get_stock_data,
    compute_prev_xday_high,
    get_stock_with_metrics,
    POPULAR_TICKERS,
    compute_rsi,
    compute_macd,
    compute_bollinger_bands,
    compute_sma,
    compute_ema,
    compute_underwater_periods,
    identify_drawdown_events,
    compute_drawdown_time_distribution,
    compute_recovery_stats,
    compute_opportunity_windows,
    compute_opportunity_stats,
    get_realtime_quote,
)
from options_utils import load_puts, available_tickers as available_options_tickers

# Page config
st.set_page_config(
    page_title="Stock Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_data(ticker: str, start: str, end: str, lookback: int) -> pd.DataFrame:
    """Cached wrapper for fetching stock data with metrics."""
    return get_stock_with_metrics(ticker, start, end, lookback)


@st.cache_data(ttl=300)
def fetch_realtime_quote(ticker: str) -> dict:
    """Cached wrapper for realtime quote (avoids re-fetching on every rerun)."""
    return get_realtime_quote(ticker)


@st.cache_data(ttl=300)
def fetch_indicator(df: pd.DataFrame, indicator_type: str, period: int = 14) -> Optional[pd.DataFrame]:
    """Cached wrapper for computing technical indicators from price data."""
    if indicator_type == "RSI":
        return compute_rsi(df, period)
    elif indicator_type == "MACD":
        return compute_macd(df)
    elif indicator_type == "BBANDS":
        return compute_bollinger_bands(df, period)
    elif indicator_type == "SMA":
        return compute_sma(df, period)
    elif indicator_type == "EMA":
        return compute_ema(df, period)
    return None


def create_gradient_line_chart(
    df: pd.DataFrame,
    ticker: str,
    show_volume: bool = True,
    color_intensity: float = 0.15,
) -> go.Figure:
    """
    Create an interactive Plotly chart with gradient-colored line segments.

    The color represents percentage change from the rolling high:
    - Red: Below the rolling high (negative)
    - Green: At or above the rolling high (positive/recovery)
    """
    # Prepare data
    dates = pd.to_datetime(df["Date"])
    close = df["Close"].values.flatten() if hasattr(df["Close"], "values") else df["Close"].to_numpy()
    pct_change = df["pct_change"].values if "pct_change" in df.columns else np.zeros(len(close))

    # Create figure with secondary y-axis for volume
    if show_volume and "Volume" in df.columns:
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.8, 0.2],
            subplot_titles=(f"{ticker} Price", "Volume"),
        )
    else:
        fig = go.Figure()

    # Create color scale based on pct_change
    # Clamp values for better color distribution
    pct_clamped = np.clip(pct_change, -color_intensity, color_intensity)

    # Normalize to 0-1 range for colorscale
    pct_normalized = (pct_clamped + color_intensity) / (2 * color_intensity)

    # Create segments as individual traces for gradient effect
    # Using a more efficient approach with markers
    colors = []
    for p in pct_normalized:
        if np.isnan(p):
            colors.append("rgba(128, 128, 128, 0.5)")
        else:
            # Red to Green gradient
            r = int(255 * (1 - p))
            g = int(255 * p)
            colors.append(f"rgba({r}, {g}, 50, 0.9)")

    # Main price line with color markers
    main_trace = go.Scatter(
        x=dates,
        y=close,
        mode="lines+markers",
        name=f"{ticker} Close",
        line=dict(color="rgba(100, 100, 100, 0.3)", width=1),
        marker=dict(
            size=6,
            color=pct_change,
            colorscale="RdYlGn",
            cmin=-color_intensity,
            cmax=color_intensity,
            colorbar=dict(
                title="% from<br>Rolling High",
                tickformat=".0%",
                x=1.02,
            ),
            showscale=True,
        ),
        hovertemplate=(
            "<b>%{x|%Y-%m-%d}</b><br>"
            "Close: $%{y:.2f}<br>"
            "% from High: %{marker.color:.2%}<br>"
            "<extra></extra>"
        ),
    )

    if show_volume and "Volume" in df.columns:
        fig.add_trace(main_trace, row=1, col=1)

        # Add rolling high line
        if f"prev_30_high" in df.columns:
            high_col = "prev_30_high"
        else:
            # Find the rolling high column
            high_cols = [c for c in df.columns if c.startswith("prev_") and c.endswith("_high")]
            high_col = high_cols[0] if high_cols else None

        if high_col:
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=df[high_col],
                    mode="lines",
                    name="Rolling High",
                    line=dict(color="rgba(255, 165, 0, 0.5)", width=1, dash="dot"),
                    hovertemplate="Rolling High: $%{y:.2f}<extra></extra>",
                ),
                row=1,
                col=1,
            )

        # Volume bars
        volume = df["Volume"].values.flatten() if hasattr(df["Volume"], "values") else df["Volume"].to_numpy()
        vol_colors = ["rgba(0, 150, 0, 0.6)" if c >= 0 else "rgba(150, 0, 0, 0.6)" for c in pct_change]

        fig.add_trace(
            go.Bar(
                x=dates,
                y=volume,
                name="Volume",
                marker_color=vol_colors,
                hovertemplate="Volume: %{y:,.0f}<extra></extra>",
            ),
            row=2,
            col=1,
        )

        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
    else:
        fig.add_trace(main_trace)
        fig.update_yaxes(title_text="Price ($)")

    if show_volume and "Volume" in df.columns:
        fig.update_xaxes(title_text="Date", row=2, col=1)
    else:
        fig.update_xaxes(title_text="Date")

    fig.update_layout(
        height=600 if show_volume else 500,
        hovermode="x unified",
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=60, r=100, t=40, b=40),
    )

    return fig


def create_chart_with_indicators(
    df: pd.DataFrame,
    ticker: str,
    indicators: dict,
    show_volume: bool = True,
    color_intensity: float = 0.15,
) -> go.Figure:
    """
    Create an interactive Plotly chart with technical indicator overlays and subplots.

    Args:
        df: DataFrame with price data
        ticker: Stock ticker symbol
        indicators: Dict of indicator name to DataFrame (e.g., {"RSI": df, "MACD": df})
        show_volume: Whether to show volume subplot
        color_intensity: Color scale intensity for gradient coloring
    """
    dates = pd.to_datetime(df["Date"])
    close = df["Close"].values.flatten() if hasattr(df["Close"], "values") else df["Close"].to_numpy()
    pct_change = df["pct_change"].values if "pct_change" in df.columns else np.zeros(len(close))

    # Determine subplot configuration
    has_rsi = "RSI" in indicators and indicators["RSI"] is not None
    has_macd = "MACD" in indicators and indicators["MACD"] is not None
    num_subplots = 1  # Price chart
    if show_volume and "Volume" in df.columns:
        num_subplots += 1
    if has_rsi:
        num_subplots += 1
    if has_macd:
        num_subplots += 1

    # Calculate row heights
    row_heights = []
    subplot_titles = [f"{ticker} Price"]
    if show_volume and "Volume" in df.columns:
        row_heights = [0.5, 0.1]
        subplot_titles.append("Volume")
    else:
        row_heights = [0.6]

    if has_rsi:
        row_heights.append(0.15)
        subplot_titles.append("RSI")
    if has_macd:
        row_heights.append(0.15)
        subplot_titles.append("MACD")

    # Normalize heights
    total = sum(row_heights)
    row_heights = [h / total for h in row_heights]

    fig = make_subplots(
        rows=num_subplots,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
        subplot_titles=subplot_titles,
    )

    # Normalize pct_change for coloring
    pct_clamped = np.clip(pct_change, -color_intensity, color_intensity)
    pct_normalized = (pct_clamped + color_intensity) / (2 * color_intensity)

    # Main price trace
    main_trace = go.Scatter(
        x=dates,
        y=close,
        mode="lines+markers",
        name=f"{ticker} Close",
        line=dict(color="rgba(100, 100, 100, 0.3)", width=1),
        marker=dict(
            size=6,
            color=pct_change,
            colorscale="RdYlGn",
            cmin=-color_intensity,
            cmax=color_intensity,
            colorbar=dict(
                title="% from<br>Rolling High",
                tickformat=".0%",
                x=1.02,
            ),
            showscale=True,
        ),
        hovertemplate=(
            "<b>%{x|%Y-%m-%d}</b><br>"
            "Close: $%{y:.2f}<br>"
            "% from High: %{marker.color:.2%}<br>"
            "<extra></extra>"
        ),
    )
    fig.add_trace(main_trace, row=1, col=1)

    # Add rolling high line
    high_cols = [c for c in df.columns if c.startswith("prev_") and c.endswith("_high")]
    if high_cols:
        high_col = high_cols[0]
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=df[high_col],
                mode="lines",
                name="Rolling High",
                line=dict(color="rgba(255, 165, 0, 0.5)", width=1, dash="dot"),
                hovertemplate="Rolling High: $%{y:.2f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

    # Add Bollinger Bands as shaded area on price chart
    if "BBANDS" in indicators and indicators["BBANDS"] is not None:
        bb_df = indicators["BBANDS"]
        # Merge on date, using nearest date match
        bb_df["Date"] = pd.to_datetime(bb_df["Date"])
        merged_bb = pd.merge_asof(
            df[["Date"]].sort_values("Date"),
            bb_df.sort_values("Date"),
            on="Date",
            direction="nearest",
        )

        if "BB_Upper" in merged_bb.columns and "BB_Lower" in merged_bb.columns:
            # Upper band
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=merged_bb["BB_Upper"],
                    mode="lines",
                    name="BB Upper",
                    line=dict(color="rgba(173, 216, 230, 0.5)", width=1),
                    hovertemplate="BB Upper: $%{y:.2f}<extra></extra>",
                ),
                row=1,
                col=1,
            )
            # Lower band with fill
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=merged_bb["BB_Lower"],
                    mode="lines",
                    name="BB Lower",
                    line=dict(color="rgba(173, 216, 230, 0.5)", width=1),
                    fill="tonexty",
                    fillcolor="rgba(173, 216, 230, 0.2)",
                    hovertemplate="BB Lower: $%{y:.2f}<extra></extra>",
                ),
                row=1,
                col=1,
            )
            # Middle band
            if "BB_Middle" in merged_bb.columns:
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=merged_bb["BB_Middle"],
                        mode="lines",
                        name="BB Middle",
                        line=dict(color="rgba(100, 149, 237, 0.6)", width=1, dash="dash"),
                        hovertemplate="BB Middle: $%{y:.2f}<extra></extra>",
                    ),
                    row=1,
                    col=1,
                )

    # Add SMA overlays on price chart
    for key, ind_df in indicators.items():
        if key.startswith("SMA_") and ind_df is not None:
            period = key.split("_")[1]
            ind_df["Date"] = pd.to_datetime(ind_df["Date"])
            merged = pd.merge_asof(
                df[["Date"]].sort_values("Date"),
                ind_df.sort_values("Date"),
                on="Date",
                direction="nearest",
            )
            sma_col = f"SMA_{period}"
            if sma_col in merged.columns:
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=merged[sma_col],
                        mode="lines",
                        name=f"SMA {period}",
                        line=dict(width=1.5),
                        hovertemplate=f"SMA {period}: $%{{y:.2f}}<extra></extra>",
                    ),
                    row=1,
                    col=1,
                )

    # Add EMA overlays on price chart
    for key, ind_df in indicators.items():
        if key.startswith("EMA_") and ind_df is not None:
            period = key.split("_")[1]
            ind_df["Date"] = pd.to_datetime(ind_df["Date"])
            merged = pd.merge_asof(
                df[["Date"]].sort_values("Date"),
                ind_df.sort_values("Date"),
                on="Date",
                direction="nearest",
            )
            ema_col = f"EMA_{period}"
            if ema_col in merged.columns:
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=merged[ema_col],
                        mode="lines",
                        name=f"EMA {period}",
                        line=dict(width=1.5, dash="dot"),
                        hovertemplate=f"EMA {period}: $%{{y:.2f}}<extra></extra>",
                    ),
                    row=1,
                    col=1,
                )

    current_row = 2

    # Volume subplot
    if show_volume and "Volume" in df.columns:
        volume = df["Volume"].values.flatten() if hasattr(df["Volume"], "values") else df["Volume"].to_numpy()
        vol_colors = ["rgba(0, 150, 0, 0.6)" if c >= 0 else "rgba(150, 0, 0, 0.6)" for c in pct_change]
        fig.add_trace(
            go.Bar(
                x=dates,
                y=volume,
                name="Volume",
                marker_color=vol_colors,
                hovertemplate="Volume: %{y:,.0f}<extra></extra>",
            ),
            row=current_row,
            col=1,
        )
        fig.update_yaxes(title_text="Volume", row=current_row, col=1)
        current_row += 1

    # RSI subplot
    if has_rsi:
        rsi_df = indicators["RSI"]
        rsi_df["Date"] = pd.to_datetime(rsi_df["Date"])
        merged_rsi = pd.merge_asof(
            df[["Date"]].sort_values("Date"),
            rsi_df.sort_values("Date"),
            on="Date",
            direction="nearest",
        )
        if "RSI" in merged_rsi.columns:
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=merged_rsi["RSI"],
                    mode="lines",
                    name="RSI",
                    line=dict(color="purple", width=1.5),
                    hovertemplate="RSI: %{y:.1f}<extra></extra>",
                ),
                row=current_row,
                col=1,
            )
            # Add overbought/oversold lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=current_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=current_row, col=1)
            fig.update_yaxes(title_text="RSI", range=[0, 100], row=current_row, col=1)
            current_row += 1

    # MACD subplot
    if has_macd:
        macd_df = indicators["MACD"]
        macd_df["Date"] = pd.to_datetime(macd_df["Date"])
        merged_macd = pd.merge_asof(
            df[["Date"]].sort_values("Date"),
            macd_df.sort_values("Date"),
            on="Date",
            direction="nearest",
        )
        if "MACD" in merged_macd.columns:
            # MACD line
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=merged_macd["MACD"],
                    mode="lines",
                    name="MACD",
                    line=dict(color="blue", width=1.5),
                    hovertemplate="MACD: %{y:.3f}<extra></extra>",
                ),
                row=current_row,
                col=1,
            )
            # Signal line
            if "MACD_Signal" in merged_macd.columns:
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=merged_macd["MACD_Signal"],
                        mode="lines",
                        name="Signal",
                        line=dict(color="orange", width=1.5),
                        hovertemplate="Signal: %{y:.3f}<extra></extra>",
                    ),
                    row=current_row,
                    col=1,
                )
            # Histogram
            if "MACD_Hist" in merged_macd.columns:
                hist_colors = ["green" if v >= 0 else "red" for v in merged_macd["MACD_Hist"].fillna(0)]
                fig.add_trace(
                    go.Bar(
                        x=dates,
                        y=merged_macd["MACD_Hist"],
                        name="MACD Hist",
                        marker_color=hist_colors,
                        opacity=0.5,
                        hovertemplate="Histogram: %{y:.3f}<extra></extra>",
                    ),
                    row=current_row,
                    col=1,
                )
            fig.update_yaxes(title_text="MACD", row=current_row, col=1)
            fig.add_hline(y=0, line_dash="dash", line_color="gray", row=current_row, col=1)

    # Update price axis
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=num_subplots, col=1)

    # Calculate chart height based on number of subplots
    base_height = 400
    subplot_height = 150
    total_height = base_height + (num_subplots - 1) * subplot_height

    fig.update_layout(
        height=total_height,
        hovermode="x unified",
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=60, r=100, t=40, b=40),
    )

    return fig


def create_comparison_chart(
    dfs: dict[str, pd.DataFrame],
    normalize: bool = True,
    color_intensity: float = 0.15,
) -> go.Figure:
    """Create a comparison chart for multiple stocks."""
    fig = go.Figure()

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

    for i, (ticker, df) in enumerate(dfs.items()):
        dates = pd.to_datetime(df["Date"])
        close = df["Close"].values.flatten() if hasattr(df["Close"], "values") else df["Close"].to_numpy()

        if normalize:
            # Normalize to percentage change from first value
            base_price = close[0]
            y_values = ((close / base_price) - 1) * 100
            y_label = "% Change from Start"
        else:
            y_values = close
            y_label = "Price ($)"

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=y_values,
                mode="lines",
                name=ticker,
                line=dict(color=colors[i % len(colors)], width=2),
                hovertemplate=(
                    f"<b>{ticker}</b><br>"
                    "%{x|%Y-%m-%d}<br>"
                    f"{y_label}: %{{y:.2f}}{'%' if normalize else ''}<br>"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title="Stock Comparison",
        xaxis_title="Date",
        yaxis_title=y_label,
        height=500,
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    return fig


def create_pct_change_histogram(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Create histogram of percentage changes."""
    pct_change = df["pct_change"].dropna() * 100  # Convert to percentage

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x=pct_change,
            nbinsx=50,
            name="% Change Distribution",
            marker_color="rgba(100, 149, 237, 0.7)",
            hovertemplate="Range: %{x:.1f}%<br>Count: %{y}<extra></extra>",
        )
    )

    # Add vertical line at 0
    fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="0%")

    # Add mean line
    mean_pct = pct_change.mean()
    fig.add_vline(
        x=mean_pct,
        line_dash="dot",
        line_color="green",
        annotation_text=f"Mean: {mean_pct:.2f}%",
    )

    fig.update_layout(
        title=f"{ticker} - Distribution of % Change from Rolling High",
        xaxis_title="% Change from Rolling High",
        yaxis_title="Frequency",
        height=350,
        showlegend=False,
    )

    return fig


def display_live_quote(ticker: str):
    """Display real-time quote banner at the top."""
    quote = fetch_realtime_quote(ticker)

    if quote.get("price") is None:
        st.warning(f"Could not fetch live quote for {ticker}")
        return

    # Create a prominent live price display
    price = quote["price"]
    change = quote.get("change", 0) or 0
    change_pct = quote.get("change_pct", 0) or 0
    market_state = quote.get("market_state", "UNKNOWN")

    # Color based on change
    if change >= 0:
        color = "green"
        arrow = "▲"
    else:
        color = "red"
        arrow = "▼"

    # Market state indicator
    if market_state == "REGULAR":
        state_emoji = "🟢"
        state_text = "Market Open"
    elif market_state in ["PRE", "PREPRE"]:
        state_emoji = "🟡"
        state_text = "Pre-Market"
    elif market_state in ["POST", "POSTPOST"]:
        state_emoji = "🟡"
        state_text = "After Hours"
    else:
        state_emoji = "🔴"
        state_text = "Market Closed"

    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

    with col1:
        st.markdown(f"### 💵 ${price:.2f}")
        st.caption(f"Live Price • {quote['timestamp']}")

    with col2:
        st.markdown(f"### :{color}[{arrow} {abs(change):.2f} ({abs(change_pct):.2f}%)]")
        st.caption(f"Day Change (Prev Close: ${quote.get('prev_close', 0):.2f})")

    with col3:
        day_high = quote.get("day_high", 0) or 0
        day_low = quote.get("day_low", 0) or 0
        st.markdown(f"### ${day_low:.2f} - ${day_high:.2f}")
        st.caption("Day Range")

    with col4:
        vol = quote.get("volume", 0) or 0
        st.markdown(f"### {vol:,.0f}")
        st.caption(f"{state_emoji} {state_text}")

    st.divider()


def display_metrics(df: pd.DataFrame, ticker: str):
    """Display key metrics in columns."""
    close = df["Close"].values.flatten()[-1] if hasattr(df["Close"], "values") else df["Close"].iloc[-1]
    pct_change = df["pct_change"].values if "pct_change" in df.columns else []

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Last Close", f"${close:.2f}")

    with col2:
        if len(pct_change) > 0:
            current_pct = pct_change[-1]
            st.metric(
                "% from Rolling High",
                f"{current_pct:.2%}",
                delta=f"{current_pct:.2%}",
                delta_color="normal",
            )

    with col3:
        if len(pct_change) > 1:
            avg_pct = np.nanmean(pct_change)
            st.metric("Avg % from High", f"{avg_pct:.2%}")

    with col4:
        if len(pct_change) > 1:
            min_pct = np.nanmin(pct_change)
            st.metric("Max Drawdown", f"{min_pct:.2%}")

    with col5:
        days_data = len(df)
        st.metric("Trading Days", f"{days_data:,}")


# ============================================================================
# Drawdown Analysis Visualizations
# ============================================================================


def display_drawdown_metrics(df: pd.DataFrame, events: list[dict]):
    """Display drawdown-specific metrics."""
    col1, col2, col3, col4 = st.columns(4)

    current_drawdown = df["drawdown_from_ath"].iloc[-1] if "drawdown_from_ath" in df.columns else 0
    max_drawdown = df["drawdown_from_ath"].min() if "drawdown_from_ath" in df.columns else 0
    days_underwater = df["days_underwater"].iloc[-1] if "days_underwater" in df.columns else 0

    # Calculate average recovery time from events
    recovery_times = [e["days_to_recovery"] for e in events if e["days_to_recovery"] is not None]
    avg_recovery = np.mean(recovery_times) if recovery_times else None

    with col1:
        st.metric(
            "Current Drawdown",
            f"{current_drawdown:.1%}",
            delta=f"{current_drawdown:.1%}",
            delta_color="inverse",
        )

    with col2:
        st.metric("Max Historical Drawdown", f"{max_drawdown:.1%}")

    with col3:
        if avg_recovery is not None:
            st.metric("Avg Recovery Time", f"{avg_recovery:.0f} days")
        else:
            st.metric("Avg Recovery Time", "N/A")

    with col4:
        st.metric("Days Underwater", f"{days_underwater:,}")


def create_drawdown_chart(
    df: pd.DataFrame,
    ticker: str,
    annotate_major: bool = True,
    major_threshold: float = 0.15,
) -> go.Figure:
    """
    Create price chart with gradient coloring by drawdown depth.

    Args:
        df: DataFrame with drawdown_from_ath and cummax columns
        ticker: Stock ticker symbol
        annotate_major: Whether to annotate major drawdowns
        major_threshold: Threshold for major drawdown annotations (e.g., 0.15 = 15%)
    """
    dates = pd.to_datetime(df["Date"])
    close = df["Close"].values.flatten() if hasattr(df["Close"], "values") else df["Close"].to_numpy()
    drawdown = df["drawdown_from_ath"].values if "drawdown_from_ath" in df.columns else np.zeros(len(close))
    cummax = df["cummax"].values if "cummax" in df.columns else close

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
        subplot_titles=(f"{ticker} Price vs All-Time High", "Drawdown from ATH"),
    )

    # Main price trace with gradient coloring
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=close,
            mode="lines+markers",
            name="Price",
            line=dict(color="rgba(100, 100, 100, 0.3)", width=1),
            marker=dict(
                size=5,
                color=drawdown,
                colorscale="RdYlGn",
                cmin=-0.30,
                cmax=0,
                colorbar=dict(
                    title="Drawdown",
                    tickformat=".0%",
                    x=1.02,
                    len=0.5,
                    y=0.75,
                ),
                showscale=True,
            ),
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "Price: $%{y:.2f}<br>"
                "Drawdown: %{marker.color:.1%}<br>"
                "<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )

    # All-time high line
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=cummax,
            mode="lines",
            name="All-Time High",
            line=dict(color="rgba(255, 165, 0, 0.6)", width=1.5, dash="dash"),
            hovertemplate="ATH: $%{y:.2f}<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Drawdown chart (as filled area)
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=drawdown * 100,  # Convert to percentage
            mode="lines",
            name="Drawdown %",
            fill="tozeroy",
            fillcolor="rgba(255, 0, 0, 0.3)",
            line=dict(color="red", width=1),
            hovertemplate="Drawdown: %{y:.1f}%<extra></extra>",
        ),
        row=2,
        col=1,
    )

    # Add annotations for major drawdowns
    if annotate_major:
        major_events = [
            (i, drawdown[i]) for i in range(len(drawdown))
            if drawdown[i] < -major_threshold
        ]
        # Find local minima in major events
        annotated = set()
        for i, dd in major_events:
            # Check if this is a local minimum (within 20 days)
            is_min = True
            for j in range(max(0, i - 20), min(len(drawdown), i + 20)):
                if drawdown[j] < dd:
                    is_min = False
                    break
            if is_min and i not in annotated:
                fig.add_annotation(
                    x=dates.iloc[i],
                    y=dd * 100,
                    text=f"{dd:.0%}",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=1,
                    ax=0,
                    ay=-30,
                    font=dict(size=10, color="red"),
                    row=2,
                    col=1,
                )
                annotated.add(i)
                # Don't annotate nearby points
                for k in range(max(0, i - 30), min(len(drawdown), i + 30)):
                    annotated.add(k)

    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)

    fig.update_layout(
        height=600,
        hovermode="x unified",
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=60, r=100, t=40, b=40),
    )

    return fig


def create_drawdown_histogram(
    distribution_df: pd.DataFrame,
    ticker: str,
) -> go.Figure:
    """
    Create histogram showing time spent at each drawdown level.

    Args:
        distribution_df: DataFrame from compute_drawdown_time_distribution
        ticker: Stock ticker symbol
    """
    fig = go.Figure()

    # Color bars by severity
    colors = ["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c", "#8e44ad"]
    bar_colors = colors[: len(distribution_df)]

    fig.add_trace(
        go.Bar(
            x=distribution_df["bin_label"],
            y=distribution_df["pct_of_time"] * 100,
            marker_color=bar_colors,
            text=[f"{p:.1f}%" for p in distribution_df["pct_of_time"] * 100],
            textposition="auto",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Time: %{y:.1f}%<br>"
                "Days: %{customdata}<br>"
                "<extra></extra>"
            ),
            customdata=distribution_df["days"],
        )
    )

    fig.update_layout(
        title=f"{ticker} - Time Spent at Each Drawdown Level",
        xaxis_title="Drawdown Range",
        yaxis_title="% of Trading Days",
        height=350,
        showlegend=False,
    )

    return fig


def create_recovery_scatter(
    events: list[dict],
    ticker: str,
) -> go.Figure:
    """
    Create scatter plot showing drawdown depth vs recovery time.

    Args:
        events: List of drawdown events
        ticker: Stock ticker symbol
    """
    # Filter to events with recovery
    recovered = [e for e in events if e["days_to_recovery"] is not None]

    if not recovered:
        fig = go.Figure()
        fig.add_annotation(
            text="No recovered drawdown events to display",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        fig.update_layout(height=350, title=f"{ticker} - Recovery Time vs Drawdown Depth")
        return fig

    depths = [e["drawdown_pct"] * 100 for e in recovered]
    recovery_days = [e["days_to_recovery"] for e in recovered]
    peak_dates = [e["peak_date"].strftime("%Y-%m-%d") for e in recovered]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=depths,
            y=recovery_days,
            mode="markers",
            marker=dict(
                size=10,
                color=depths,
                colorscale="Reds",
                showscale=True,
                colorbar=dict(title="Depth %"),
            ),
            text=peak_dates,
            hovertemplate=(
                "<b>Peak: %{text}</b><br>"
                "Drawdown: %{x:.1f}%<br>"
                "Recovery: %{y} days<br>"
                "<extra></extra>"
            ),
        )
    )

    # Add trend line if enough points
    if len(depths) >= 3:
        z = np.polyfit(depths, recovery_days, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(depths), max(depths), 100)
        fig.add_trace(
            go.Scatter(
                x=x_line,
                y=p(x_line),
                mode="lines",
                name="Trend",
                line=dict(color="gray", dash="dash"),
                hoverinfo="skip",
            )
        )

    fig.update_layout(
        title=f"{ticker} - Recovery Time vs Drawdown Depth",
        xaxis_title="Drawdown Depth (%)",
        yaxis_title="Days to Recovery",
        height=350,
        showlegend=False,
    )

    return fig


def create_drawdown_events_table(events: list[dict]) -> pd.DataFrame:
    """
    Create a formatted DataFrame of drawdown events for display.

    Args:
        events: List of drawdown events

    Returns:
        Formatted DataFrame for display
    """
    if not events:
        return pd.DataFrame(columns=["Peak Date", "Trough Date", "Depth", "Days Down", "Recovery Date"])

    rows = []
    for e in events:
        rows.append({
            "Peak Date": e["peak_date"].strftime("%Y-%m-%d"),
            "Trough Date": e["trough_date"].strftime("%Y-%m-%d"),
            "Depth": f"{e['drawdown_pct']:.1%}",
            "Days Down": e["days_to_trough"],
            "Recovery Date": e["recovery_date"].strftime("%Y-%m-%d") if e["recovery_date"] else "Not Recovered",
            "Days to Recovery": e["days_to_recovery"] if e["days_to_recovery"] else "-",
        })

    return pd.DataFrame(rows)


# ============================================================================
# Put Options Learning Visualizations
# ============================================================================


def create_opportunity_chart(
    df: pd.DataFrame,
    windows: list[dict],
    ticker: str,
    entry_threshold: float,
) -> go.Figure:
    """
    Create price chart with highlighted opportunity zones.

    Args:
        df: DataFrame with price data
        windows: List of opportunity windows
        ticker: Stock ticker symbol
        entry_threshold: Entry threshold used
    """
    dates = pd.to_datetime(df["Date"])
    close = df["Close"].values.flatten() if hasattr(df["Close"], "values") else df["Close"].to_numpy()

    fig = go.Figure()

    # Add shaded regions for opportunity windows
    for w in windows:
        start = w["start_date"]
        end = w["end_date"] if w["end_date"] else dates.iloc[-1]

        fig.add_vrect(
            x0=start,
            x1=end,
            fillcolor="rgba(255, 193, 7, 0.3)",
            layer="below",
            line_width=0,
            annotation_text=f"{w['max_drawdown']:.0%}",
            annotation_position="top left",
            annotation_font_size=9,
        )

    # Price line
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=close,
            mode="lines",
            name="Price",
            line=dict(color="#1f77b4", width=2),
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Price: $%{y:.2f}<extra></extra>",
        )
    )

    # Add ATH line if available
    if "cummax" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=df["cummax"],
                mode="lines",
                name="All-Time High",
                line=dict(color="orange", width=1, dash="dash"),
                hovertemplate="ATH: $%{y:.2f}<extra></extra>",
            )
        )

    fig.update_layout(
        title=f"{ticker} - Opportunity Windows (>{entry_threshold:.0%} Drawdown)",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=450,
        hovermode="x unified",
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    return fig


def create_opportunity_stats_table(
    df: pd.DataFrame,
    thresholds: list[float] = None,
) -> pd.DataFrame:
    """
    Create opportunity statistics table for different drawdown levels.

    Args:
        df: DataFrame with drawdown data
        thresholds: List of drawdown thresholds to analyze

    Returns:
        DataFrame with opportunity statistics per threshold
    """
    if thresholds is None:
        thresholds = [0.05, 0.10, 0.15, 0.20]

    # Calculate years in dataset
    dates = pd.to_datetime(df["Date"])
    years = (dates.max() - dates.min()).days / 365.25
    total_days = len(df)

    rows = []
    for threshold in thresholds:
        # Compute windows for this threshold
        windows = compute_opportunity_windows(df, entry_threshold=threshold, exit_threshold=threshold / 2)

        if not windows:
            rows.append({
                "Drawdown Level": f">{threshold:.0%}",
                "Times/Year": "0",
                "Avg Duration": "-",
                "Max Duration": "-",
                "Avg Max Depth": "-",
            })
            continue

        stats = compute_opportunity_stats(windows, total_days, years)

        # Calculate average "further drop" - how much deeper it went after entry
        further_drops = [w["max_drawdown"] - w["entry_drawdown"] for w in windows]
        avg_further = np.mean(further_drops) if further_drops else 0

        rows.append({
            "Drawdown Level": f">{threshold:.0%}",
            "Times/Year": f"{stats['windows_per_year']:.1f}x",
            "Avg Duration": f"{stats['avg_duration']:.0f} days" if stats["avg_duration"] else "-",
            "Max Duration": f"{stats['max_duration']} days" if stats["max_duration"] else "-",
            "Avg Max Depth": f"{stats['avg_max_drawdown']:.1%}" if stats["avg_max_drawdown"] else "-",
            "Avg Further Drop": f"+{avg_further:.1%}",
        })

    return pd.DataFrame(rows)


def main():
    st.title("📈 Stock Analysis Dashboard")
    st.markdown(
        """
        Visualize stock prices with gradient colors showing the percentage change
        from the rolling high. **Red** indicates below the rolling high,
        **Green** indicates recovery or new highs.
        """
    )

    # Sidebar configuration
    st.sidebar.header("Configuration")

    # Mode selection
    mode = st.sidebar.radio("Mode", ["Single Stock", "Compare Stocks"])

    # Date range
    st.sidebar.subheader("Date Range")
    col1, col2 = st.sidebar.columns(2)

    default_start = datetime.now() - timedelta(days=365 * 3)
    default_end = datetime.now()

    with col1:
        start_date = st.date_input("Start", value=default_start)
    with col2:
        end_date = st.date_input("End", value=default_end)

    # Lookback period
    lookback_days = st.sidebar.slider(
        "Rolling High Lookback (days)",
        min_value=5,
        max_value=200,
        value=30,
        step=5,
        help="The highest price over this many trading days. Helps identify pullbacks & entry points. Short (5-30d) for swing trading, long (60-200d) for major trends.",
    )

    # Color intensity
    color_intensity = st.sidebar.slider(
        "Color Intensity",
        min_value=0.05,
        max_value=0.50,
        value=0.15,
        step=0.05,
        help="Controls gradient sensitivity. Green = at/above rolling high, Red = below. Higher values soften the colors; lower values make small deviations more visible.",
    )

    if mode == "Single Stock":
        # Ticker selection
        st.sidebar.subheader("Stock Selection")

        # Quick select from popular tickers
        category = st.sidebar.selectbox("Category", list(POPULAR_TICKERS.keys()))
        ticker = st.sidebar.selectbox("Select Stock", POPULAR_TICKERS[category])

        show_volume = st.sidebar.checkbox("Show Volume", value=True)

        # Technical Indicators section
        st.sidebar.subheader("Technical Indicators")

        # Indicator selection (all computed locally, no API key needed)
        enable_rsi = st.sidebar.checkbox("RSI", value=False)
        rsi_period = 14
        if enable_rsi:
            rsi_period = st.sidebar.number_input("RSI Period", min_value=2, max_value=50, value=14)

        enable_macd = st.sidebar.checkbox("MACD", value=False)

        enable_bbands = st.sidebar.checkbox("Bollinger Bands", value=False)
        bbands_period = 20
        if enable_bbands:
            bbands_period = st.sidebar.number_input("BB Period", min_value=5, max_value=50, value=20)

        enable_sma = st.sidebar.checkbox("SMA (Moving Averages)", value=False)
        sma_periods = [20]
        if enable_sma:
            sma_options = st.sidebar.multiselect(
                "SMA Periods", options=[20, 50, 100, 200], default=[20, 50]
            )
            sma_periods = sma_options if sma_options else [20]

        enable_ema = st.sidebar.checkbox("EMA (Exponential MA)", value=False)
        ema_periods = [12]
        if enable_ema:
            ema_options = st.sidebar.multiselect(
                "EMA Periods", options=[12, 26, 50], default=[12, 26]
            )
            ema_periods = ema_options if ema_options else [12]

        # Fetch and display data — only on explicit button click
        params_changed = (
            st.session_state.get("single_ticker") != ticker
            or st.session_state.get("single_start") != start_date.strftime("%Y-%m-%d")
            or st.session_state.get("single_end") != end_date.strftime("%Y-%m-%d")
            or st.session_state.get("single_lookback") != lookback_days
        )
        if params_changed and "single_df" in st.session_state:
            st.sidebar.info("Settings changed — click Load Data to update.")

        if st.sidebar.button("Load Data", type="primary"):
            with st.spinner(f"Fetching data for {ticker}..."):
                try:
                    df = fetch_stock_data(
                        ticker,
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d"),
                        lookback_days,
                    )
                    st.session_state.single_df = df
                    st.session_state.single_ticker = ticker
                    st.session_state.single_start = start_date.strftime("%Y-%m-%d")
                    st.session_state.single_end = end_date.strftime("%Y-%m-%d")
                    st.session_state.single_lookback = lookback_days
                except Exception as e:
                    st.error(f"Error fetching data: {e}")
                    return

        if "single_df" in st.session_state:
            df = st.session_state.single_df
            ticker = st.session_state.single_ticker

            # Display live quote banner (fetched fresh on each load)
            display_live_quote(ticker)

            # Display historical metrics
            display_metrics(df, ticker)

            st.divider()

            # Create tabs for different analysis views
            tab1, tab2, tab3 = st.tabs(["Price Analysis", "Drawdown Analysis", "Put Options Learning"])

            # ================================================================
            # Tab 1: Price Analysis (Original functionality)
            # ================================================================
            with tab1:
                # Compute technical indicators if enabled
                indicators = {}
                any_indicators = enable_rsi or enable_macd or enable_bbands or enable_sma or enable_ema

                if any_indicators:
                    with st.spinner("Computing technical indicators..."):
                        if enable_rsi:
                            indicators["RSI"] = fetch_indicator(df, "RSI", rsi_period)
                        if enable_macd:
                            indicators["MACD"] = fetch_indicator(df, "MACD")
                        if enable_bbands:
                            indicators["BBANDS"] = fetch_indicator(df, "BBANDS", bbands_period)
                        if enable_sma:
                            for period in sma_periods:
                                indicators[f"SMA_{period}"] = fetch_indicator(df, "SMA", period)
                        if enable_ema:
                            for period in ema_periods:
                                indicators[f"EMA_{period}"] = fetch_indicator(df, "EMA", period)

                # Main chart
                st.subheader(f"{ticker} Price Chart")

                # Use indicator chart if any indicators are enabled, otherwise use basic gradient chart
                if any_indicators and indicators:
                    fig = create_chart_with_indicators(df, ticker, indicators, show_volume, color_intensity)
                else:
                    fig = create_gradient_line_chart(df, ticker, show_volume, color_intensity)
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Green = at/above rolling high | Red = below rolling high | Intensity = distance from high")

                # Additional analysis
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("% Change Distribution")
                    hist_fig = create_pct_change_histogram(df, ticker)
                    st.plotly_chart(hist_fig, use_container_width=True)

                with col2:
                    st.subheader("Recent Data")
                    # Show last 10 rows
                    display_df = df[["Date", "Close", "Volume", "pct_change"]].tail(10).copy()
                    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
                    display_df["pct_change"] = display_df["pct_change"].apply(lambda x: f"{x:.2%}")
                    display_df.columns = ["Date", "Close", "Volume", "% from High"]
                    st.dataframe(display_df, use_container_width=True, hide_index=True)

            # ================================================================
            # Tab 2: Drawdown Analysis
            # ================================================================
            with tab2:
                # Compute drawdown metrics
                df_with_drawdown = compute_underwater_periods(df.copy())
                events = identify_drawdown_events(df_with_drawdown, min_drawdown_pct=0.05)

                # Display drawdown-specific metrics
                display_drawdown_metrics(df_with_drawdown, events)

                st.divider()

                # Drawdown chart
                st.subheader("Price vs All-Time High")
                drawdown_fig = create_drawdown_chart(df_with_drawdown, ticker)
                st.plotly_chart(drawdown_fig, use_container_width=True)

                # Two column layout for histogram and scatter
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Time at Each Drawdown Level")
                    distribution_df = compute_drawdown_time_distribution(df_with_drawdown)
                    hist_fig = create_drawdown_histogram(distribution_df, ticker)
                    st.plotly_chart(hist_fig, use_container_width=True)

                with col2:
                    st.subheader("Recovery Time vs Depth")
                    scatter_fig = create_recovery_scatter(events, ticker)
                    st.plotly_chart(scatter_fig, use_container_width=True)

                # Historical drawdown events table
                st.subheader("Historical Drawdown Events (>5%)")
                if events:
                    events_df = create_drawdown_events_table(events)
                    st.dataframe(events_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No significant drawdown events (>5%) found in this period.")

                # Recovery statistics
                st.subheader("Recovery Statistics by Depth")
                recovery_df = compute_recovery_stats(events)
                if not recovery_df.empty and recovery_df["count"].sum() > 0:
                    display_recovery = recovery_df[["threshold", "count", "avg_recovery_days", "median_recovery_days", "pct_recovered"]].copy()
                    display_recovery.columns = ["Depth", "Count", "Avg Recovery (days)", "Median Recovery (days)", "% Recovered"]
                    display_recovery["% Recovered"] = display_recovery["% Recovered"].apply(
                        lambda x: f"{x:.0%}" if x is not None else "-"
                    )
                    display_recovery["Avg Recovery (days)"] = display_recovery["Avg Recovery (days)"].apply(
                        lambda x: f"{x:.0f}" if x is not None else "-"
                    )
                    display_recovery["Median Recovery (days)"] = display_recovery["Median Recovery (days)"].apply(
                        lambda x: f"{x:.0f}" if x is not None else "-"
                    )
                    st.dataframe(display_recovery, use_container_width=True, hide_index=True)
                else:
                    st.info("Not enough drawdown events to compute recovery statistics.")

            # ================================================================
            # Tab 3: Put Options Learning
            # ================================================================
            with tab3:
                st.markdown("""
                ### Understanding Drawdowns for Put Options

                Drawdowns (periods when a stock trades below its previous high) create potential
                opportunities for put options strategies. This analysis helps you understand:

                - **How often** stocks reach different drawdown levels
                - **How long** they typically stay down
                - **How deep** drawdowns tend to go after initial entry

                This information is educational and helps build intuition about market behavior.
                """)

                st.divider()

                # Compute drawdown data if not already done
                if "drawdown_from_ath" not in df.columns:
                    df_analysis = compute_underwater_periods(df.copy())
                else:
                    df_analysis = df.copy()

                # Entry threshold selector
                col1, col2 = st.columns([1, 3])
                with col1:
                    entry_threshold_pct = st.slider(
                        "Entry Threshold",
                        min_value=5,
                        max_value=30,
                        value=10,
                        step=5,
                        format="%d%%",
                        help="Drawdown level that triggers an 'opportunity window'",
                    )
                    entry_threshold = entry_threshold_pct / 100.0

                # Compute opportunity windows
                windows = compute_opportunity_windows(
                    df_analysis,
                    entry_threshold=entry_threshold,
                    exit_threshold=entry_threshold / 2,
                )

                # Opportunity chart
                st.subheader(f"Opportunity Windows (>{entry_threshold:.0%} Drawdown)")
                opp_fig = create_opportunity_chart(df_analysis, windows, ticker, entry_threshold)
                st.plotly_chart(opp_fig, use_container_width=True)

                # Summary statistics
                dates = pd.to_datetime(df_analysis["Date"])
                years = (dates.max() - dates.min()).days / 365.25
                total_days = len(df_analysis)

                if windows:
                    stats = compute_opportunity_stats(windows, total_days, years)

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Windows", f"{stats['total_windows']}")
                    with col2:
                        st.metric("Windows/Year", f"{stats['windows_per_year']:.1f}")
                    with col3:
                        st.metric("Avg Duration", f"{stats['avg_duration']:.0f} days" if stats['avg_duration'] else "-")
                    with col4:
                        st.metric("% Time in Window", f"{stats['pct_time_in_window']:.1%}")

                st.divider()

                # Opportunity statistics table
                st.subheader("Opportunity Statistics by Drawdown Level")
                opp_stats_df = create_opportunity_stats_table(df_analysis)
                st.dataframe(opp_stats_df, use_container_width=True, hide_index=True)

                # Real options data overlay
                st.divider()
                has_options = ticker in available_options_tickers()
                if has_options:
                    st.subheader(f"{ticker} Historical Options During Drawdowns")
                    st.markdown("""
                    The charts below use **real historical options data** to show how put
                    premiums and implied volatility behaved during past drawdown periods.
                    """)

                    try:
                        opts_df = load_puts(
                            ticker,
                            start_date=start_date.strftime("%Y-%m-%d"),
                            end_date=end_date.strftime("%Y-%m-%d"),
                        )

                        if not opts_df.empty:
                            # Compute daily median IV for ATM puts (within 5% of close)
                            opts_df["date"] = pd.to_datetime(opts_df["date"])
                            price_by_date = df_analysis.set_index(
                                pd.to_datetime(df_analysis["Date"])
                            )["Close"]
                            # For each option date, find nearest close
                            opts_df = opts_df.merge(
                                price_by_date.rename("close_price").reset_index().rename(
                                    columns={"Date": "date"}
                                ),
                                on="date",
                                how="left",
                            )
                            opts_df = opts_df.dropna(subset=["close_price"])
                            # ATM filter: strike within 5% of close
                            opts_df["pct_from_atm"] = (
                                (opts_df["strike"] - opts_df["close_price"]) / opts_df["close_price"]
                            ).abs()
                            atm_opts = opts_df[opts_df["pct_from_atm"] <= 0.05]

                            if not atm_opts.empty:
                                daily_iv = (
                                    atm_opts.groupby("date")["implied_volatility"]
                                    .median()
                                    .reset_index()
                                )
                                daily_iv.columns = ["date", "median_iv"]

                                # Merge with drawdown data
                                dd_dates = df_analysis[["Date", "drawdown_from_ath"]].copy()
                                dd_dates["Date"] = pd.to_datetime(dd_dates["Date"])
                                merged = pd.merge_asof(
                                    daily_iv.sort_values("date"),
                                    dd_dates.sort_values("Date").rename(columns={"Date": "date"}),
                                    on="date",
                                    direction="nearest",
                                )

                                col1, col2 = st.columns(2)

                                with col1:
                                    # IV over time with drawdown shading
                                    iv_fig = go.Figure()
                                    iv_fig.add_trace(go.Scatter(
                                        x=merged["date"],
                                        y=merged["median_iv"] * 100,
                                        mode="lines",
                                        name="ATM Put IV",
                                        line=dict(color="purple", width=1.5),
                                        hovertemplate="%{x|%Y-%m-%d}<br>IV: %{y:.1f}%<extra></extra>",
                                    ))
                                    # Shade opportunity windows
                                    for w in windows:
                                        w_start = w["start_date"]
                                        w_end = w["end_date"] if w["end_date"] else merged["date"].max()
                                        iv_fig.add_vrect(
                                            x0=w_start, x1=w_end,
                                            fillcolor="rgba(255, 193, 7, 0.2)",
                                            layer="below", line_width=0,
                                        )
                                    iv_fig.update_layout(
                                        title="ATM Put Implied Volatility",
                                        xaxis_title="Date",
                                        yaxis_title="Implied Volatility (%)",
                                        height=400,
                                    )
                                    st.plotly_chart(iv_fig, use_container_width=True)
                                    st.caption(
                                        "Yellow shading shows drawdown opportunity windows. "
                                        "Notice how IV tends to spike during drawdowns."
                                    )

                                with col2:
                                    # Scatter: drawdown depth vs IV
                                    scatter_data = merged.dropna(subset=["drawdown_from_ath", "median_iv"])
                                    scatter_fig = go.Figure()
                                    scatter_fig.add_trace(go.Scatter(
                                        x=scatter_data["drawdown_from_ath"] * 100,
                                        y=scatter_data["median_iv"] * 100,
                                        mode="markers",
                                        marker=dict(
                                            size=4,
                                            color=scatter_data["drawdown_from_ath"] * 100,
                                            colorscale="RdYlGn",
                                            showscale=True,
                                            colorbar=dict(title="DD %"),
                                            opacity=0.5,
                                        ),
                                        hovertemplate="Drawdown: %{x:.1f}%<br>IV: %{y:.1f}%<extra></extra>",
                                    ))
                                    scatter_fig.update_layout(
                                        title="Drawdown Depth vs Put IV",
                                        xaxis_title="Drawdown from ATH (%)",
                                        yaxis_title="ATM Put IV (%)",
                                        height=400,
                                    )
                                    st.plotly_chart(scatter_fig, use_container_width=True)
                                    st.caption(
                                        "Deeper drawdowns generally correspond to higher implied volatility, "
                                        "meaning puts become more expensive during selloffs."
                                    )
                            else:
                                st.info("Not enough ATM options data to display IV analysis.")
                        else:
                            st.info("No options data found for the selected date range.")
                    except FileNotFoundError:
                        st.info(f"No options data file found for {ticker}.")
                else:
                    st.info(
                        f"No historical options data available for {ticker}. "
                        f"Options data is available for: {', '.join(available_options_tickers())}"
                    )

                # Educational content
                st.divider()
                with st.expander("How to Interpret This Data"):
                    st.markdown("""
                    **Key Metrics Explained:**

                    - **Times/Year**: How frequently the stock reaches this drawdown level on average
                    - **Avg Duration**: How long the stock typically stays below this level
                    - **Max Duration**: The longest observed period at this drawdown level
                    - **Avg Max Depth**: The average deepest point reached during these windows
                    - **Avg Further Drop**: How much deeper the stock typically falls after reaching the entry threshold

                    **For Put Options Learning:**

                    1. **Frequency** helps you understand how often opportunities arise
                    2. **Duration** affects time decay considerations for options
                    3. **Further Drop** helps estimate potential profit if buying puts at entry threshold

                    **Important Caveats:**

                    - Past behavior does not guarantee future results
                    - Options involve significant risk and complexity
                    - This analysis is for educational purposes only
                    - Consider consulting a financial advisor before trading options
                    """)

            # Download option (outside tabs)
            st.divider()
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name=f"{ticker}_data.csv",
                mime="text/csv",
            )

    else:  # Compare Stocks mode
        st.sidebar.subheader("Stock Selection")

        # Multi-select for comparison
        default_tickers = ["MSFT", "AAPL", "GOOGL"]
        tickers_input = st.sidebar.text_input(
            "Tickers (comma-separated)",
            value=", ".join(default_tickers),
        )
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

        normalize = st.sidebar.checkbox("Normalize (% change from start)", value=True)

        if st.sidebar.button("Load Data", type="primary") or "compare_dfs" not in st.session_state:
            dfs = {}
            progress = st.progress(0)

            for i, ticker in enumerate(tickers):
                with st.spinner(f"Fetching {ticker}..."):
                    try:
                        df = fetch_stock_data(
                            ticker,
                            start_date.strftime("%Y-%m-%d"),
                            end_date.strftime("%Y-%m-%d"),
                            lookback_days,
                        )
                        dfs[ticker] = df
                    except Exception as e:
                        st.warning(f"Could not fetch {ticker}: {e}")

                progress.progress((i + 1) / len(tickers))

            progress.empty()
            st.session_state.compare_dfs = dfs

        if "compare_dfs" in st.session_state and st.session_state.compare_dfs:
            dfs = st.session_state.compare_dfs

            # Comparison chart
            st.subheader("Stock Comparison")
            comp_fig = create_comparison_chart(dfs, normalize, color_intensity)
            st.plotly_chart(comp_fig, use_container_width=True)

            # Individual charts
            st.subheader("Individual Stock Charts")

            cols = st.columns(min(len(dfs), 2))
            for i, (ticker, df) in enumerate(dfs.items()):
                with cols[i % 2]:
                    st.markdown(f"**{ticker}**")
                    fig = create_gradient_line_chart(df, ticker, show_volume=False, color_intensity=color_intensity)
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)

    # Footer
    st.sidebar.divider()

    # Clear cache button
    if st.sidebar.button("🔄 Clear Cache & Refresh"):
        st.cache_data.clear()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.sidebar.caption(
        """
        Price data provided by Yahoo Finance via yfinance.
        Technical indicators computed locally.
        Colors indicate % change from the rolling high over the specified lookback period.
        """
    )


if __name__ == "__main__":
    main()
