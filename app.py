"""Welcome page and user guide for the Stock Analysis Dashboard."""

import streamlit as st

st.set_page_config(
    page_title="Stock Analysis - Home",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Stock Analysis Dashboard")
st.markdown("""
Welcome! This dashboard helps you analyze stocks, understand drawdowns, and learn about put options.

**Use the sidebar to navigate between pages:**
- **Stock Analysis** - Analyze individual stocks with gradient charts and technical indicators
- **Put Options** - Learn about put options using real AMD historical data
""")

# Getting Started
st.header("1. Getting Started")
st.markdown("""
**What this dashboard does:**
- Visualizes stock prices with gradient colors showing distance from rolling highs
- Analyzes drawdowns and recovery patterns
- Identifies potential put option opportunities
- Displays technical indicators (RSI, MACD, Bollinger Bands)

**Quick Start:**
1. Select **Single Stock** or **Compare Stocks** mode in the sidebar
2. Enter a stock ticker (e.g., AAPL, MSFT, GOOGL)
3. Set your desired date range
4. Click **Load Data**
5. Explore the different analysis tabs
""")

st.divider()

# Stock Analysis Page
st.header("2. Stock Analysis Page")
st.markdown("*Go to **Stock Analysis** in the sidebar to use these features.*")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gradient Coloring")
    st.markdown("""
    The price chart uses a color gradient to show how far the current price is from the rolling high:

    - **Green shades** = Price is at or above the rolling high (bullish)
    - **Red shades** = Price is below the rolling high (pullback/correction)
    - **Color intensity** = How far from the high (darker = further)

    This helps you quickly identify:
    - New highs and breakouts (bright green)
    - Pullbacks and corrections (light red)
    - Major drawdowns (dark red)
    """)

with col2:
    st.subheader("Rolling High Lookback")
    st.markdown("""
    The **Rolling High Lookback** setting controls the window for calculating the reference high:

    - **Short lookback (5-30 days)**: More sensitive, shows minor pullbacks
    - **Medium lookback (30-60 days)**: Balanced view of trends
    - **Long lookback (60-200 days)**: Shows major trends and significant drawdowns

    **Example:** With a 30-day lookback, the chart compares today's price to the highest price in the last 30 trading days.
    """)

st.markdown("""
**Volume Bars:** The lower section shows trading volume. Higher volume during price moves often indicates stronger conviction.
""")

st.divider()

# Drawdown Analysis Tab
st.header("3. Drawdown Analysis Tab")
st.markdown("""
This tab helps you understand historical drawdowns (peak-to-trough declines):

**Key Metrics:**
- **All-Time High (ATH)**: The highest price ever reached in the selected period
- **Current Drawdown**: How far below the ATH the current price is
- **Max Drawdown**: The largest peak-to-trough decline in the period

**Underwater Chart:**
Shows how long the stock spent below its previous high. Longer "underwater" periods indicate extended recovery times.

**Recovery Statistics:**
- Average time to recover from drawdowns
- Number of drawdown events
- Distribution of drawdown depths
""")

st.divider()

# Put Options Education
st.header("4. Put Options Education")
st.info("**Go to the Put Options page** in the sidebar for a comprehensive put options education dashboard with real AMD data.")

st.warning("**Disclaimer:** This is for educational purposes only. Options trading involves significant risk. Always do your own research and consider consulting a financial advisor.")

st.markdown("""
The **Put Options** page teaches you about put options using ~3 million real AMD contracts (2018-2026):

**What you'll learn:**
- Put option fundamentals (strike, premium, expiration, Greeks)
- Interactive payoff diagrams
- Risk calculators (break-even, position sizing, P/L scenarios)
- How to read option chains
- Understanding Delta, Theta, Gamma, and Vega

**Stock Analysis also has a Put Options Learning tab** that shows historical drawdown-based opportunities.
""")

st.divider()

# Technical Indicators
st.header("5. Technical Indicators")
st.markdown("Technical indicators require an Alpha Vantage API key. Get a free key at [alphavantage.co](https://www.alphavantage.co/support/#api-key)")

tab1, tab2, tab3, tab4 = st.tabs(["RSI", "MACD", "Bollinger Bands", "Moving Averages"])

with tab1:
    st.subheader("RSI (Relative Strength Index)")
    st.markdown("""
    **What it measures:** Momentum - whether a stock is overbought or oversold

    **How to read it:**
    - **Above 70**: Potentially overbought (may pull back)
    - **Below 30**: Potentially oversold (may bounce)
    - **50 level**: Neutral momentum

    **Common uses:**
    - Identify potential reversal points
    - Confirm trend strength
    - Spot divergences between price and momentum
    """)

with tab2:
    st.subheader("MACD (Moving Average Convergence Divergence)")
    st.markdown("""
    **What it measures:** Trend direction and momentum

    **Components:**
    - **MACD Line**: Difference between 12 and 26 period EMAs
    - **Signal Line**: 9-period EMA of MACD line
    - **Histogram**: Difference between MACD and Signal lines

    **How to read it:**
    - **MACD crosses above Signal**: Bullish signal
    - **MACD crosses below Signal**: Bearish signal
    - **Histogram increasing**: Momentum strengthening
    """)

with tab3:
    st.subheader("Bollinger Bands")
    st.markdown("""
    **What it measures:** Volatility and potential price extremes

    **Components:**
    - **Middle Band**: 20-period simple moving average
    - **Upper Band**: Middle band + 2 standard deviations
    - **Lower Band**: Middle band - 2 standard deviations

    **How to read it:**
    - **Price near upper band**: Potentially overbought
    - **Price near lower band**: Potentially oversold
    - **Bands widening**: Increasing volatility
    - **Bands narrowing**: Decreasing volatility (potential breakout coming)
    """)

with tab4:
    st.subheader("Moving Averages (SMA & EMA)")
    st.markdown("""
    **SMA (Simple Moving Average):** Equal weight to all prices in the period

    **EMA (Exponential Moving Average):** More weight to recent prices (reacts faster)

    **Common periods:**
    - **20-day**: Short-term trend
    - **50-day**: Medium-term trend
    - **200-day**: Long-term trend

    **How to read it:**
    - **Price above MA**: Uptrend
    - **Price below MA**: Downtrend
    - **Golden Cross** (50 crosses above 200): Bullish signal
    - **Death Cross** (50 crosses below 200): Bearish signal
    """)

st.divider()

# Tips & FAQ
st.header("6. Tips & FAQ")

st.subheader("Best Practices")
st.markdown("""
- **Start with longer timeframes** (3+ years) to understand historical patterns
- **Adjust the lookback period** based on your investment horizon
- **Compare multiple stocks** to understand relative performance
- **Use technical indicators** to confirm signals from the price analysis
""")

st.subheader("Frequently Asked Questions")

with st.expander("Why is my stock showing red even though it's up today?"):
    st.markdown("""
    The color reflects the distance from the **rolling high**, not daily change.
    A stock can be up today but still below its recent high, showing red.
    """)

with st.expander("What's the difference between Single Stock and Compare modes?"):
    st.markdown("""
    - **Single Stock**: Detailed analysis of one stock with all features
    - **Compare Stocks**: Side-by-side comparison of multiple stocks (up to 4)
    """)

with st.expander("How do I get technical indicators to work?"):
    st.markdown("""
    1. Get a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
    2. Enter the key in the Technical Indicators section
    3. Select your desired indicators
    4. Click Load Data

    Note: Free tier has rate limits (5 calls/minute, 500 calls/day)
    """)

with st.expander("Can I use this for real trading decisions?"):
    st.markdown("""
    This dashboard is for **educational and informational purposes only**.
    It should not be considered financial advice. Always:
    - Do your own research
    - Understand the risks involved
    - Consider consulting a financial professional
    - Never invest more than you can afford to lose
    """)

st.divider()
st.markdown("*Navigate to **Stock Analysis** or **Put Options** using the sidebar.*")
