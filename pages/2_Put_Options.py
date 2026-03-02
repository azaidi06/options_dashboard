"""
Put Options Education Dashboard

A beginner-friendly interactive dashboard for learning about put options
using real AMD historical options data.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Optional

from utils import get_realtime_quote
from options_utils import (
    load_puts,
    available_tickers,
    classify_moneyness,
    calculate_break_even,
    calculate_position_size,
    estimate_put_value_change,
    calculate_time_decay,
    calculate_pl_scenarios,
    get_iv_smile_data,
    EDUCATIONAL_LINKS,
)

# Page config
st.set_page_config(
    page_title="Put Options Education",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Risk disclaimer
RISK_DISCLAIMER = """
**Risk Disclaimer:** Options trading involves substantial risk and is not suitable for all investors.
This dashboard is for **educational purposes only**. Past performance does not guarantee future results.
Consult a qualified financial professional before trading options.
"""


@st.cache_data(ttl=300)
def fetch_puts(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Cached wrapper for loading puts data for any ticker."""
    return load_puts(ticker, start_date=start_date, end_date=end_date)


@st.cache_data(ttl=60)
def fetch_quote(ticker: str) -> dict:
    """Cached wrapper for fetching live quote."""
    return get_realtime_quote(ticker)


def display_live_quote_banner(ticker: str = "AMD"):
    """Display live quote banner at the top."""
    quote = fetch_quote(ticker)

    if quote.get("price") is None:
        st.warning("Could not fetch live AMD quote")
        return quote.get("price", 100.0)

    price = quote["price"]
    change = quote.get("change", 0) or 0
    change_pct = quote.get("change_pct", 0) or 0
    market_state = quote.get("market_state", "UNKNOWN")

    # Color based on change
    if change >= 0:
        color = "green"
        arrow = "+"
    else:
        color = "red"
        arrow = ""

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
        st.markdown(f"### {ticker}: ${price:.2f}")
        st.caption(f"Live Price | {quote['timestamp']}")

    with col2:
        st.markdown(f"### :{color}[{arrow}{change:.2f} ({arrow}{abs(change_pct):.2f}%)]")
        st.caption("Day Change")

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
    return price


def create_payoff_diagram(strike: float, premium: float) -> go.Figure:
    """Create interactive payoff diagram for a long put."""
    prices = np.linspace(strike * 0.5, strike * 1.5, 100)

    profits = []
    for p in prices:
        if p < strike:
            profit = strike - p - premium
        else:
            profit = -premium
        profits.append(profit)

    fig = go.Figure()

    # Profit/loss line
    fig.add_trace(go.Scatter(
        x=prices,
        y=profits,
        mode="lines",
        name="P/L at Expiration",
        line=dict(color="blue", width=2),
        hovertemplate="Stock: $%{x:.2f}<br>P/L: $%{y:.2f}<extra></extra>",
    ))

    # Break-even line
    break_even = strike - premium
    fig.add_vline(x=break_even, line_dash="dash", line_color="orange",
                  annotation_text=f"Break-even: ${break_even:.2f}")

    # Strike line
    fig.add_vline(x=strike, line_dash="dot", line_color="gray",
                  annotation_text=f"Strike: ${strike:.2f}")

    # Zero line
    fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=0.5)

    # Shade profit/loss regions
    fig.add_trace(go.Scatter(
        x=prices[profits >= np.array(0)],
        y=[p if p >= 0 else 0 for p in profits],
        fill="tozeroy",
        fillcolor="rgba(0, 255, 0, 0.2)",
        line=dict(width=0),
        name="Profit Zone",
        hoverinfo="skip",
    ))

    fig.add_trace(go.Scatter(
        x=prices,
        y=[p if p < 0 else 0 for p in profits],
        fill="tozeroy",
        fillcolor="rgba(255, 0, 0, 0.2)",
        line=dict(width=0),
        name="Loss Zone",
        hoverinfo="skip",
    ))

    fig.update_layout(
        title="Long Put Payoff Diagram",
        xaxis_title="Stock Price at Expiration ($)",
        yaxis_title="Profit/Loss per Share ($)",
        height=400,
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
    )

    return fig


def create_premium_vs_strike_chart(df: pd.DataFrame) -> go.Figure:
    """Create chart showing premium vs strike price relationship."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["strike"],
        y=df["mark"],
        mode="markers",
        marker=dict(
            size=8,
            color=df["volume"],
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Volume"),
        ),
        hovertemplate=(
            "Strike: $%{x:.2f}<br>"
            "Premium: $%{y:.2f}<br>"
            "Volume: %{marker.color:,.0f}<extra></extra>"
        ),
    ))

    fig.update_layout(
        title="Put Premium vs Strike Price",
        xaxis_title="Strike Price ($)",
        yaxis_title="Premium (Mark) ($)",
        height=400,
    )

    return fig


def create_iv_smile_chart(df: pd.DataFrame, current_price: float) -> go.Figure:
    """Create IV smile/skew visualization."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["strike"],
        y=df["implied_volatility"] * 100,
        mode="lines+markers",
        name="Implied Volatility",
        line=dict(color="purple", width=2),
        marker=dict(size=6),
        hovertemplate="Strike: $%{x:.2f}<br>IV: %{y:.1f}%<extra></extra>",
    ))

    # Current price line
    fig.add_vline(x=current_price, line_dash="dash", line_color="green",
                  annotation_text=f"Current: ${current_price:.2f}")

    fig.update_layout(
        title="Implied Volatility Smile/Skew",
        xaxis_title="Strike Price ($)",
        yaxis_title="Implied Volatility (%)",
        height=400,
    )

    return fig


def create_time_decay_chart(days: int, theta: float, premium: float) -> go.Figure:
    """Create time decay visualization."""
    decay_df = calculate_time_decay(days, theta, premium)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=decay_df["days_remaining"],
        y=decay_df["premium"],
        mode="lines+markers",
        name="Projected Premium",
        line=dict(color="red", width=2),
        marker=dict(size=4),
        hovertemplate="Days Left: %{x}<br>Premium: $%{y:.2f}<extra></extra>",
    ))

    fig.update_layout(
        title="Time Decay Projection (Theta Impact)",
        xaxis_title="Days to Expiration",
        yaxis_title="Estimated Premium ($)",
        height=350,
        xaxis=dict(autorange="reversed"),
    )

    return fig


def create_greeks_sensitivity_chart(
    base_premium: float,
    delta: float,
    gamma: float,
    price_range: tuple = (-10, 10),
) -> go.Figure:
    """Create Greeks sensitivity visualization."""
    changes = np.linspace(price_range[0], price_range[1], 50)

    # Calculate premium changes
    delta_only = [base_premium + delta * c for c in changes]
    delta_gamma = [estimate_put_value_change(c, delta, gamma, base_premium) for c in changes]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=changes,
        y=delta_only,
        mode="lines",
        name="Delta Only (Linear)",
        line=dict(color="blue", dash="dash"),
    ))

    fig.add_trace(go.Scatter(
        x=changes,
        y=delta_gamma,
        mode="lines",
        name="Delta + Gamma (Curved)",
        line=dict(color="green", width=2),
    ))

    fig.add_vline(x=0, line_dash="dot", line_color="gray")
    fig.add_hline(y=base_premium, line_dash="dot", line_color="gray",
                  annotation_text=f"Current: ${base_premium:.2f}")

    fig.update_layout(
        title="Put Value Sensitivity to Stock Price Changes",
        xaxis_title="Stock Price Change ($)",
        yaxis_title="Estimated Put Premium ($)",
        height=400,
        showlegend=True,
    )

    return fig


def main():
    st.title("📉 Put Options Education Dashboard")

    # Sidebar configuration
    st.sidebar.header("Configuration")

    # Ticker selection
    tickers = available_tickers()
    if not tickers:
        st.error("No options data found. Run the data extraction scripts first.")
        return

    st.sidebar.subheader("Stock Selection")
    ticker = st.sidebar.selectbox(
        "Ticker",
        tickers,
        index=tickers.index("AMD") if "AMD" in tickers else 0,
    )

    st.markdown(f"""
    Learn about put options using **real {ticker} historical options data**.
    This interactive dashboard helps beginners understand put option mechanics, pricing, and risk.
    """)

    # Display live quote
    current_price = display_live_quote_banner(ticker)
    if current_price is None:
        current_price = 100.0

    with st.sidebar.expander("About This Dashboard", expanded=False):
        st.markdown(f"""
        This dashboard uses historical options data to teach:
        - Put option basics
        - Greeks (Delta, Theta, Gamma, Vega)
        - Risk management
        - Option pricing dynamics

        **Available tickers:** {', '.join(tickers)}
        """)

    st.sidebar.subheader("Date Range")
    col1, col2 = st.sidebar.columns(2)

    default_start = datetime.now() - timedelta(days=365)
    default_end = datetime.now()

    with col1:
        start_date = st.date_input("Start", value=default_start)
    with col2:
        end_date = st.date_input("End", value=default_end)

    # Load data
    with st.spinner(f"Loading {ticker} options data..."):
        try:
            df = fetch_puts(
                ticker,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
            )
            if df.empty:
                st.error("No data found for the selected date range.")
                return
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return

    # Get unique dates and expirations for filters
    unique_dates = sorted(df["date"].dt.strftime("%Y-%m-%d").unique())
    unique_expirations = sorted(df["expiration"].dt.strftime("%Y-%m-%d").unique())

    st.sidebar.subheader("Option Filters")
    selected_date = st.sidebar.selectbox(
        "Quote Date",
        unique_dates,
        index=len(unique_dates) - 1 if unique_dates else 0,
    )

    # Filter expirations available for selected date
    date_filtered = df[df["date"] == pd.to_datetime(selected_date)]
    available_expirations = sorted(date_filtered["expiration"].dt.strftime("%Y-%m-%d").unique())

    selected_expiration = st.sidebar.selectbox(
        "Expiration",
        available_expirations,
        index=0 if available_expirations else 0,
    )

    st.sidebar.divider()
    st.sidebar.markdown(f"**Data loaded:** {len(df):,} put contracts")

    with st.sidebar.expander("Quick Links"):
        st.markdown(f"""
        - [What is a Put Option?]({EDUCATIONAL_LINKS['put_options_intro']})
        - [CBOE Education]({EDUCATIONAL_LINKS['cboe_education']})
        - [Long Put Strategy]({EDUCATIONAL_LINKS['long_put_strategy']})
        """)

    # Filter data for selected date and expiration
    mask = (
        (df["date"] == pd.to_datetime(selected_date)) &
        (df["expiration"] == pd.to_datetime(selected_expiration))
    )
    filtered_df = df.loc[mask].copy()

    # Add moneyness classification
    if not filtered_df.empty:
        filtered_df["moneyness"] = filtered_df["strike"].apply(
            lambda x: classify_moneyness(x, current_price)
        )

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Put Options 101",
        "AMD Option Chain",
        "Risk Calculators",
        "Greeks Deep Dive",
    ])

    # =========================================================================
    # Tab 1: Put Options 101
    # =========================================================================
    with tab1:
        st.header("Put Options 101")

        col1, col2 = st.columns(2)

        with col1:
            with st.expander("What is a Put Option?", expanded=True):
                st.markdown(f"""
                A **put option** gives you the **right (but not obligation)** to
                **sell** a stock at a specific price (strike) before a certain date (expiration).

                **Why buy puts?**
                - **Protection:** Hedge against stock price declines
                - **Speculation:** Profit from expected price drops
                - **Income:** Part of complex strategies

                **Key concept:** Puts gain value when the stock price **falls**.
                Explore real {ticker} put contracts in the Option Chain tab.

                [Learn more at Investopedia]({EDUCATIONAL_LINKS['put_options_intro']})
                """)

            with st.expander("Key Terms Glossary"):
                st.markdown(f"""
                | Term | Definition |
                |------|------------|
                | **Strike Price** | The price at which you can sell the stock |
                | **Premium** | The cost to buy the option |
                | **Expiration** | Date when the option contract ends |
                | **ITM** | In-the-money: Strike > Stock Price (for puts) |
                | **ATM** | At-the-money: Strike ≈ Stock Price |
                | **OTM** | Out-of-the-money: Strike < Stock Price (for puts) |
                | **Intrinsic Value** | Max(Strike - Stock Price, 0) |
                | **Time Value** | Premium - Intrinsic Value |

                [CBOE Options Education]({EDUCATIONAL_LINKS['cboe_education']})
                """)

        with col2:
            with st.expander("Risk Profile", expanded=True):
                st.markdown("""
                **Long Put Risk/Reward:**

                | | |
                |---|---|
                | **Max Loss** | Premium paid (if stock stays above strike) |
                | **Max Gain** | Strike - Premium (if stock goes to $0) |
                | **Break-even** | Strike Price - Premium |

                **Example:** Buy a $100 put for $5
                - Max loss: $5 per share ($500 per contract)
                - Break-even: $95
                - Max gain: $95 per share (if AMD goes to $0)
                """)

            with st.expander("When to Consider Puts"):
                st.markdown(f"""
                **Buying puts may be appropriate when:**
                - You expect the stock to decline
                - You want to protect existing stock holdings
                - You want defined-risk bearish exposure

                **Risks to consider:**
                - Time decay works against you
                - Need stock to move enough to overcome premium
                - Can lose 100% of premium paid

                [Long Put Strategy Guide]({EDUCATIONAL_LINKS['long_put_strategy']})
                """)

        st.divider()

        # Interactive Payoff Diagram
        st.subheader("Interactive Payoff Diagram")

        col1, col2 = st.columns([1, 3])

        with col1:
            diagram_strike = st.number_input(
                "Strike Price ($)",
                min_value=10.0,
                max_value=300.0,
                value=float(round(current_price, 0)),
                step=5.0,
                key="payoff_strike",
            )
            diagram_premium = st.number_input(
                "Premium ($)",
                min_value=0.10,
                max_value=50.0,
                value=5.0,
                step=0.50,
                key="payoff_premium",
            )

            break_even = calculate_break_even(diagram_strike, diagram_premium)
            st.metric("Break-Even Price", f"${break_even:.2f}")
            st.metric("Max Loss", f"${diagram_premium:.2f}/share")
            st.metric("Max Gain", f"${break_even:.2f}/share")

        with col2:
            payoff_fig = create_payoff_diagram(diagram_strike, diagram_premium)
            st.plotly_chart(payoff_fig, use_container_width=True)

        st.info("""
        **Reading the diagram:** The blue line shows your profit/loss at different stock prices
        when the option expires. Green shading = profit zone, Red shading = loss zone.
        The put becomes profitable when the stock falls below the break-even price.
        """)

    # =========================================================================
    # Tab 2: AMD Option Chain Explorer
    # =========================================================================
    with tab2:
        st.header(f"{ticker} Option Chain Explorer")

        st.markdown(f"""
        Viewing puts for **{selected_date}** expiring **{selected_expiration}**
        ({ticker} current price: **${current_price:.2f}**)
        """)

        if filtered_df.empty:
            st.warning("No data available for selected date/expiration.")
        else:
            # Moneyness filter
            moneyness_filter = st.multiselect(
                "Filter by Moneyness",
                ["ITM", "ATM", "OTM"],
                default=["ITM", "ATM", "OTM"],
            )

            display_df = filtered_df[filtered_df["moneyness"].isin(moneyness_filter)]

            # Option chain table
            st.subheader("Put Option Chain")

            table_cols = [
                "strike", "mark", "bid", "ask", "volume", "open_interest",
                "implied_volatility", "delta", "gamma", "theta", "vega", "moneyness"
            ]
            table_df = display_df[table_cols].copy()
            table_df = table_df.sort_values("strike", ascending=False)

            # Format for display
            table_df["implied_volatility"] = table_df["implied_volatility"].apply(
                lambda x: f"{x*100:.1f}%" if pd.notna(x) else "-"
            )
            table_df["delta"] = table_df["delta"].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "-")
            table_df["gamma"] = table_df["gamma"].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "-")
            table_df["theta"] = table_df["theta"].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "-")
            table_df["vega"] = table_df["vega"].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "-")

            table_df.columns = [
                "Strike", "Mark", "Bid", "Ask", "Volume", "Open Int",
                "IV", "Delta", "Gamma", "Theta", "Vega", "Moneyness"
            ]

            st.dataframe(table_df, use_container_width=True, hide_index=True, height=400)

            st.divider()

            # Charts
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Premium vs Strike")
                premium_fig = create_premium_vs_strike_chart(display_df)
                st.plotly_chart(premium_fig, use_container_width=True)

                st.caption("""
                Higher strike puts cost more because they have more intrinsic value.
                Color shows trading volume - more liquid options have higher volume.
                """)

            with col2:
                st.subheader("IV Smile/Skew")
                iv_data = get_iv_smile_data(df, selected_date, selected_expiration)
                if not iv_data.empty:
                    iv_fig = create_iv_smile_chart(iv_data, current_price)
                    st.plotly_chart(iv_fig, use_container_width=True)

                    st.caption("""
                    The 'volatility skew' shows puts with lower strikes often have higher IV,
                    reflecting demand for downside protection.
                    """)
                else:
                    st.info("No IV data available for this selection.")

    # =========================================================================
    # Tab 3: Risk Calculators
    # =========================================================================
    with tab3:
        st.header("Risk Calculators")

        st.warning(RISK_DISCLAIMER)

        col1, col2 = st.columns(2)

        # Break-Even Calculator
        with col1:
            st.subheader("1. Break-Even Calculator")

            be_strike = st.number_input(
                "Strike Price ($)",
                min_value=1.0,
                max_value=500.0,
                value=float(round(current_price, 0)),
                step=1.0,
                key="be_strike",
            )
            be_premium = st.number_input(
                "Premium Paid ($)",
                min_value=0.01,
                max_value=100.0,
                value=5.0,
                step=0.25,
                key="be_premium",
            )

            be_price = calculate_break_even(be_strike, be_premium)

            st.success(f"""
            **Break-Even Price: ${be_price:.2f}**

            The stock must fall below ${be_price:.2f} for this put to be profitable at expiration.

            *Formula: Break-even = Strike (${be_strike:.2f}) - Premium (${be_premium:.2f})*
            """)

        # Position Sizing
        with col2:
            st.subheader("2. Position Sizing Tool")

            account_size = st.number_input(
                "Account Value ($)",
                min_value=1000,
                max_value=10000000,
                value=25000,
                step=1000,
            )
            risk_pct = st.slider(
                "Max Risk (%)",
                min_value=1,
                max_value=10,
                value=2,
                help="Maximum percentage of account to risk on this trade",
            )
            contract_premium = st.number_input(
                "Premium per Share ($)",
                min_value=0.01,
                max_value=100.0,
                value=5.0,
                step=0.25,
                key="ps_premium",
            )

            max_contracts = calculate_position_size(
                account_size, risk_pct, contract_premium * 100
            )
            max_risk = account_size * (risk_pct / 100)
            total_cost = max_contracts * contract_premium * 100

            st.success(f"""
            **Maximum Contracts: {max_contracts}**

            - Max risk ({risk_pct}% of ${account_size:,}): **${max_risk:,.2f}**
            - Cost for {max_contracts} contracts: **${total_cost:,.2f}**

            *Each contract = 100 shares*
            """)

        st.divider()

        # What-If Simulator
        st.subheader("3. What-If Simulator")

        col1, col2, col3 = st.columns(3)

        with col1:
            wif_premium = st.number_input(
                "Current Premium ($)",
                min_value=0.10,
                max_value=100.0,
                value=5.0,
                step=0.25,
                key="wif_premium",
            )
            wif_delta = st.number_input(
                "Delta",
                min_value=-1.0,
                max_value=0.0,
                value=-0.40,
                step=0.05,
                help="Put delta is negative",
            )

        with col2:
            wif_gamma = st.number_input(
                "Gamma",
                min_value=0.0,
                max_value=0.5,
                value=0.05,
                step=0.01,
            )
            wif_price_change = st.slider(
                "Stock Price Change ($)",
                min_value=-20.0,
                max_value=20.0,
                value=-5.0,
                step=0.5,
            )

        with col3:
            new_premium = estimate_put_value_change(
                wif_price_change, wif_delta, wif_gamma, wif_premium
            )
            premium_change = new_premium - wif_premium
            pct_change = (premium_change / wif_premium) * 100 if wif_premium > 0 else 0

            st.metric(
                "Estimated New Premium",
                f"${new_premium:.2f}",
                delta=f"${premium_change:+.2f} ({pct_change:+.1f}%)",
            )

            st.caption("""
            Uses delta-gamma approximation:
            New ≈ Old + (Δ × Change) + (½ × Γ × Change²)
            """)

        st.divider()

        # P/L Scenario Table
        st.subheader("4. P/L Scenario Table")

        col1, col2 = st.columns([1, 2])

        with col1:
            pl_strike = st.number_input(
                "Strike ($)",
                min_value=10.0,
                max_value=300.0,
                value=float(round(current_price, 0)),
                step=5.0,
                key="pl_strike",
            )
            pl_premium = st.number_input(
                "Premium ($)",
                min_value=0.10,
                max_value=50.0,
                value=5.0,
                step=0.50,
                key="pl_premium",
            )

        with col2:
            pl_df = calculate_pl_scenarios(pl_strike, pl_premium)

            # Color code the P/L
            def color_pl(val):
                if val > 0:
                    return "background-color: rgba(0, 255, 0, 0.2)"
                elif val < 0:
                    return "background-color: rgba(255, 0, 0, 0.2)"
                return ""

            styled_df = pl_df.style.applymap(color_pl, subset=["pl_per_share", "pl_per_contract"])
            styled_df = styled_df.format({
                "stock_price": "${:.2f}",
                "pl_per_share": "${:+.2f}",
                "pl_per_contract": "${:+.2f}",
            })

            st.dataframe(styled_df, use_container_width=True, hide_index=True)

        st.divider()

        # Time Decay Visualizer
        st.subheader("5. Time Decay Visualizer")

        col1, col2 = st.columns([1, 2])

        with col1:
            td_days = st.slider(
                "Days to Expiration",
                min_value=1,
                max_value=90,
                value=30,
            )
            td_theta = st.number_input(
                "Theta (daily decay)",
                min_value=-1.0,
                max_value=0.0,
                value=-0.05,
                step=0.01,
                help="Theta is negative for long options",
            )
            td_premium = st.number_input(
                "Current Premium ($)",
                min_value=0.10,
                max_value=50.0,
                value=5.0,
                step=0.50,
                key="td_premium",
            )

        with col2:
            decay_fig = create_time_decay_chart(td_days, td_theta, td_premium)
            st.plotly_chart(decay_fig, use_container_width=True)

        st.info("""
        **Time decay accelerates** as expiration approaches.
        This is why long options lose value faster in the final weeks before expiration.
        """)

    # =========================================================================
    # Tab 4: Greeks Deep Dive
    # =========================================================================
    with tab4:
        st.header("Greeks Deep Dive")

        st.markdown("""
        The **Greeks** measure how an option's price changes in response to various factors.
        Understanding Greeks helps you assess risk and predict option behavior.
        """)

        # Select a real option for examples
        if not filtered_df.empty:
            atm_options = filtered_df[filtered_df["moneyness"] == "ATM"]
            if atm_options.empty:
                example_option = filtered_df.iloc[len(filtered_df)//2]
            else:
                example_option = atm_options.iloc[len(atm_options)//2]
        else:
            example_option = None

        col1, col2 = st.columns(2)

        # Delta
        with col1:
            with st.expander("Delta (Δ) - Direction Exposure", expanded=True):
                st.markdown(f"""
                **What it measures:** How much the option price changes for a $1 move in the stock.

                **For puts:**
                - Delta ranges from **-1 to 0**
                - Deep ITM puts: Delta near -1
                - ATM puts: Delta near -0.5
                - Deep OTM puts: Delta near 0

                **Interpretation:**
                - Delta of -0.40 means: if stock rises $1, put loses ~$0.40
                - Also approximates probability of expiring ITM

                [Learn more about Delta]({EDUCATIONAL_LINKS['delta']})
                """)

                if example_option is not None:
                    st.info(f"""
                    **Real Example:** {ticker} ${example_option['strike']:.2f} Put

                    Delta: **{example_option['delta']:.3f}**

                    This put would lose ~${abs(example_option['delta']):.2f} if {ticker} rises $1.
                    """)

        # Theta
        with col2:
            with st.expander("Theta (Θ) - Time Decay", expanded=True):
                st.markdown(f"""
                **What it measures:** How much value the option loses each day.

                **For long puts:**
                - Theta is always **negative** (time works against you)
                - Accelerates as expiration approaches
                - ATM options have highest theta

                **Interpretation:**
                - Theta of -0.05 means: option loses ~$0.05 per day
                - Weekend decay is priced in gradually

                [Learn more about Theta]({EDUCATIONAL_LINKS['theta']})
                """)

                if example_option is not None:
                    st.info(f"""
                    **Real Example:** {ticker} ${example_option['strike']:.2f} Put

                    Theta: **{example_option['theta']:.4f}**

                    This put loses ~${abs(example_option['theta']):.4f}/day to time decay.
                    """)

        col1, col2 = st.columns(2)

        # Gamma
        with col1:
            with st.expander("Gamma (Γ) - Delta Acceleration", expanded=True):
                st.markdown(f"""
                **What it measures:** How fast delta changes as the stock moves.

                **For puts:**
                - Gamma is always **positive**
                - Highest for ATM options
                - Increases near expiration

                **Interpretation:**
                - High gamma = delta changes rapidly
                - ATM options are most sensitive to stock moves

                [Learn more about Gamma]({EDUCATIONAL_LINKS['gamma']})
                """)

                if example_option is not None:
                    st.info(f"""
                    **Real Example:** {ticker} ${example_option['strike']:.2f} Put

                    Gamma: **{example_option['gamma']:.4f}**

                    If {ticker} moves $1, delta changes by ~{example_option['gamma']:.4f}
                    """)

        # Vega
        with col2:
            with st.expander("Vega (ν) - Volatility Sensitivity", expanded=True):
                st.markdown(f"""
                **What it measures:** How much option price changes for 1% change in IV.

                **For puts:**
                - Vega is always **positive** for long options
                - Higher IV = higher option prices
                - ATM options have highest vega

                **Interpretation:**
                - Vega of 0.10 means: if IV rises 1%, put gains ~$0.10
                - Important during earnings, market events

                [Learn more about Vega]({EDUCATIONAL_LINKS['vega']})
                """)

                if example_option is not None:
                    st.info(f"""
                    **Real Example:** {ticker} ${example_option['strike']:.2f} Put

                    Vega: **{example_option['vega']:.4f}**

                    If {ticker}'s IV rises 1%, this put gains ~${example_option['vega']:.4f}
                    """)

        st.divider()

        # Interactive Greeks Visualization
        st.subheader("Interactive Greeks Sensitivity")

        col1, col2 = st.columns([1, 2])

        with col1:
            viz_premium = st.number_input(
                "Starting Premium ($)",
                min_value=0.10,
                max_value=50.0,
                value=5.0,
                step=0.50,
                key="viz_premium",
            )
            viz_delta = st.slider(
                "Delta",
                min_value=-1.0,
                max_value=0.0,
                value=-0.40,
                step=0.05,
                key="viz_delta",
            )
            viz_gamma = st.slider(
                "Gamma",
                min_value=0.0,
                max_value=0.20,
                value=0.05,
                step=0.01,
                key="viz_gamma",
            )

        with col2:
            sens_fig = create_greeks_sensitivity_chart(
                viz_premium, viz_delta, viz_gamma, (-15, 15)
            )
            st.plotly_chart(sens_fig, use_container_width=True)

        st.info("""
        **Blue dashed line:** Linear approximation using only Delta.
        **Green solid line:** More accurate approximation using Delta + Gamma.

        Notice how Gamma causes the curve to bend - this is why ATM options
        can move more than Delta alone would suggest for larger stock moves.
        """)

        # Greeks Summary Table
        if not filtered_df.empty:
            st.divider()
            st.subheader("Greeks by Moneyness (Current Chain)")

            greeks_summary = filtered_df.groupby("moneyness").agg({
                "delta": "mean",
                "gamma": "mean",
                "theta": "mean",
                "vega": "mean",
                "implied_volatility": "mean",
            }).round(4)

            greeks_summary.columns = ["Avg Delta", "Avg Gamma", "Avg Theta", "Avg Vega", "Avg IV"]
            greeks_summary["Avg IV"] = greeks_summary["Avg IV"].apply(lambda x: f"{x*100:.1f}%")

            st.dataframe(greeks_summary, use_container_width=True)

    # Footer
    st.divider()
    st.caption(f"""
    **Data Source:** Historical {ticker} options data.
    Live quotes via Yahoo Finance.
    This dashboard is for educational purposes only.
    """)


if __name__ == "__main__":
    main()
