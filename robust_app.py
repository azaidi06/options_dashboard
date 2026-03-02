"""
Welcome page and user guide for the Stock Analysis Dashboard.

Enhanced version with comprehensive educational resources and references.
"""

import streamlit as st

st.set_page_config(
    page_title="Stock Analysis - Home",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# REFERENCE LINKS - Organized by topic for maintainability
# =============================================================================
REFERENCES = {
    "rsi": {
        "beginner": [
            ("Investopedia: RSI Explained", "https://www.investopedia.com/terms/r/rsi.asp"),
            ("Fidelity: Understanding RSI", "https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/RSI"),
            ("StockCharts: RSI Introduction", "https://school.stockcharts.com/doku.php?id=technical_indicators:relative_strength_index_rsi"),
        ],
        "academic": [
            ("Original Paper: J. Welles Wilder, 'New Concepts in Technical Trading Systems' (1978)", "https://www.amazon.com/New-Concepts-Technical-Trading-Systems/dp/0894590278"),
            ("SSRN: 'Technical Analysis and Liquidity Provision'", "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1745284"),
            ("Journal of Finance: 'Foundations of Technical Analysis'", "https://www.jstor.org/stable/222481"),
        ],
    },
    "macd": {
        "beginner": [
            ("Investopedia: MACD Indicator", "https://www.investopedia.com/terms/m/macd.asp"),
            ("TradingView: MACD Guide", "https://www.tradingview.com/support/solutions/43000502344-macd-moving-average-convergence-divergence/"),
            ("Charles Schwab: Using MACD", "https://www.schwab.com/learn/story/how-to-use-macd-indicator"),
        ],
        "academic": [
            ("Gerald Appel, 'Technical Analysis: Power Tools for Active Investors'", "https://www.amazon.com/Technical-Analysis-Power-Active-Investors/dp/0131479024"),
            ("Chong & Ng (2008): 'Technical Analysis and the London Stock Exchange'", "https://doi.org/10.1080/13504850600993598"),
            ("Anghel (2015): 'Data-Snooping Bias in Tests of the Relative Performance of Multiple Forecasting Models'", "https://doi.org/10.1016/j.intfin.2015.07.001"),
        ],
    },
    "bollinger": {
        "beginner": [
            ("Investopedia: Bollinger Bands", "https://www.investopedia.com/terms/b/bollingerbands.asp"),
            ("BollingerBands.com (Official)", "https://www.bollingerbands.com/"),
            ("Fidelity: Using Bollinger Bands", "https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/bollinger-bands"),
        ],
        "academic": [
            ("John Bollinger, 'Bollinger on Bollinger Bands' (2001)", "https://www.amazon.com/Bollinger-Bands-John/dp/0071373683"),
            ("Poon & Granger (2003): 'Forecasting Volatility in Financial Markets'", "https://doi.org/10.1016/S0304-4076(03)00004-0"),
            ("Park & Irwin (2007): 'What Do We Know About the Profitability of Technical Analysis?'", "https://doi.org/10.1016/j.jebo.2007.02.003"),
        ],
    },
    "moving_averages": {
        "beginner": [
            ("Investopedia: Moving Averages", "https://www.investopedia.com/terms/m/movingaverage.asp"),
            ("StockCharts: Moving Average Guide", "https://school.stockcharts.com/doku.php?id=technical_indicators:moving_averages"),
            ("Schwab: SMA vs EMA", "https://www.schwab.com/learn/story/moving-averages"),
        ],
        "academic": [
            ("Brock, Lakonishok & LeBaron (1992): 'Simple Technical Trading Rules'", "https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x"),
            ("Sullivan, Timmermann & White (1999): 'Data-Snooping, Technical Trading Rule Performance, and the Bootstrap'", "https://doi.org/10.1111/0022-1082.00163"),
            ("Han, Yang & Zhou (2013): 'A New Anomaly: The Cross-Sectional Profitability of Technical Analysis'", "https://doi.org/10.1017/S0022109013000586"),
        ],
    },
    "drawdown": {
        "beginner": [
            ("Investopedia: Maximum Drawdown", "https://www.investopedia.com/terms/m/maximum-drawdown-mdd.asp"),
            ("Morningstar: Understanding Drawdowns", "https://www.morningstar.com/articles/347327/understanding-maximum-drawdown"),
            ("Portfolio Visualizer: Drawdown Analysis", "https://www.portfoliovisualizer.com/"),
        ],
        "academic": [
            ("Magdon-Ismail & Atiya (2004): 'Maximum Drawdown'", "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=874069"),
            ("Chekhlov, Uryasev & Zabarankin (2005): 'Drawdown Measure in Portfolio Optimization'", "https://doi.org/10.1142/S0219024905002767"),
            ("Grossman & Zhou (1993): 'Optimal Investment Strategies for Controlling Drawdowns'", "https://doi.org/10.1111/j.1540-6261.1993.tb04702.x"),
        ],
    },
    "options": {
        "beginner": [
            ("Investopedia: Put Options Explained", "https://www.investopedia.com/terms/p/putoption.asp"),
            ("CBOE Options Institute", "https://www.cboe.com/education/"),
            ("Options Playbook (Free Guide)", "https://www.optionsplaybook.com/"),
            ("tastytrade: Options Basics", "https://www.tastylive.com/concepts-strategies/options"),
        ],
        "academic": [
            ("Black & Scholes (1973): 'The Pricing of Options'", "https://www.jstor.org/stable/1831029"),
            ("Hull, 'Options, Futures, and Other Derivatives' (Textbook)", "https://www.amazon.com/Options-Futures-Other-Derivatives-10th/dp/013447208X"),
            ("Natenberg, 'Option Volatility and Pricing'", "https://www.amazon.com/Option-Volatility-Pricing-Strategies-Techniques/dp/0071818774"),
            ("Journal of Derivatives: Research Papers", "https://jod.pm-research.com/"),
        ],
    },
    "greeks": {
        "beginner": [
            ("Investopedia: The Greeks", "https://www.investopedia.com/trading/getting-to-know-the-greeks/"),
            ("CBOE: Understanding Greeks", "https://www.cboe.com/education/options-basics/greeks/"),
            ("Fidelity: Options Greeks Guide", "https://www.fidelity.com/learning-center/investment-products/options/options-greeks"),
        ],
        "academic": [
            ("Taleb, 'Dynamic Hedging' (Professional Reference)", "https://www.amazon.com/Dynamic-Hedging-Managing-Vanilla-Options/dp/0471152803"),
            ("Bakshi, Cao & Chen (1997): 'Empirical Performance of Alternative Option Pricing Models'", "https://doi.org/10.1111/0022-1082.00042"),
            ("Hull & White (2017): 'Optimal Delta Hedging for Options'", "https://doi.org/10.1016/j.jbankfin.2017.01.006"),
        ],
    },
}


def render_references(topic: str, show_beginner: bool = True, show_academic: bool = True):
    """Render reference links for a given topic."""
    if topic not in REFERENCES:
        return

    refs = REFERENCES[topic]

    if show_beginner and "beginner" in refs:
        st.markdown("**Learn More (Beginner-Friendly):**")
        for name, url in refs["beginner"]:
            st.markdown(f"- [{name}]({url})")

    if show_academic and "academic" in refs:
        st.markdown("**Deep Dive (Academic/Professional):**")
        for name, url in refs["academic"]:
            st.markdown(f"- [{name}]({url})")


# =============================================================================
# MAIN PAGE CONTENT
# =============================================================================

st.title("📊 Stock Analysis Dashboard")
st.markdown("""
Welcome! This dashboard helps you analyze stocks, understand drawdowns, and learn about put options
using real market data and institutional-grade analytical techniques.

**Use the sidebar to navigate between pages:**
- **Stock Analysis** - Analyze individual stocks with gradient charts and technical indicators
- **Put Options** - Learn about put options using real historical options data across multiple tickers
""")

# Educational Philosophy
with st.expander("About This Dashboard's Educational Approach"):
    st.markdown("""
    This dashboard combines **practical visualization tools** with **educational content** at two levels:

    1. **Beginner Resources** - Blog posts and tutorials from Investopedia, CBOE, Fidelity, and
       other trusted financial education sites for building intuitive understanding
    2. **Academic Sources** - Peer-reviewed papers, foundational books, and professional references
       for rigorous quantitative depth

    Each concept includes curated links so you can learn at your own pace and depth.
    """)

# =============================================================================
# 1. GETTING STARTED
# =============================================================================
st.header("1. Getting Started")
st.markdown("""
**What this dashboard does:**
- Visualizes stock prices with gradient colors showing distance from rolling highs (a technique
  used by professional traders to quickly identify relative performance)
- Analyzes drawdowns and recovery patterns using the same methodology employed by hedge funds
  and risk managers
- Identifies potential put option opportunities based on historical volatility patterns
- Displays technical indicators (RSI, MACD, Bollinger Bands) - the same tools used by
  institutional traders worldwide

**Quick Start:**
1. Select **Single Stock** or **Compare Stocks** mode in the sidebar
2. Enter a stock ticker (e.g., AAPL, MSFT, GOOGL)
3. Set your desired date range
4. Click **Load Data**
5. Explore the different analysis tabs
""")

with st.expander("New to Stock Analysis? Start Here"):
    st.markdown("""
    **Recommended Learning Path:**

    1. **Understand the basics of stock charts** - How price and volume are displayed
    2. **Learn about moving averages** - The foundation of trend analysis
    3. **Study drawdowns** - Critical for understanding risk
    4. **Explore technical indicators** - RSI and MACD for momentum analysis
    5. **Graduate to options** - Only after solid stock fundamentals

    **Beginner Resources:**
    - [Investopedia: Stock Basics](https://www.investopedia.com/stocks-4427785)
    - [Khan Academy: Stocks and Bonds](https://www.khanacademy.org/economics-finance-domain/core-finance/stock-and-bonds)
    - [SEC: Introduction to Investing](https://www.investor.gov/introduction-investing)
    """)

st.divider()

# =============================================================================
# 2. STOCK ANALYSIS PAGE
# =============================================================================
st.header("2. Stock Analysis Page")
st.markdown("*Go to **Stock Analysis** in the sidebar to use these features.*")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gradient Coloring")
    st.markdown("""
    The price chart uses a color gradient to show how far the current price is from the rolling high.
    This visualization technique helps you instantly identify the stock's position relative to recent
    performance - a key concept in **relative strength analysis**.

    **Color Interpretation:**
    - **Green shades** = Price is at or near the rolling high (strong relative position)
    - **Red shades** = Price is below the rolling high (pullback/correction territory)
    - **Color intensity** = Magnitude of deviation (darker = further from high)

    **What this reveals:**
    - New highs and breakouts (bright green) - Potential momentum continuation
    - Pullbacks (light red) - Possible buying opportunities in uptrends
    - Major drawdowns (dark red) - Elevated risk, but also potential value if fundamentals are intact

    **Why this matters:** Institutional investors constantly monitor "distance from highs" as a
    risk metric. A stock 5% from its high behaves very differently from one 30% from its high.
    """)

    with st.expander("Learn More: Relative Strength & Momentum"):
        st.markdown("""
        **Concept:** Relative strength measures how a stock performs compared to a benchmark
        (here, its own recent high). Stocks showing relative strength during market weakness
        often outperform when markets recover.

        **Beginner Reading:**
        - [Investopedia: Relative Strength](https://www.investopedia.com/terms/r/relativestrength.asp)
        - [StockCharts: Relative Strength Explained](https://school.stockcharts.com/doku.php?id=technical_indicators:relative_strength)

        **Academic Foundation:**
        - Jegadeesh & Titman (1993): "Returns to Buying Winners and Selling Losers"
          [Journal of Finance](https://www.jstor.org/stable/2328882) - The seminal paper on
          momentum investing
        - Asness et al. (2013): "Value and Momentum Everywhere"
          [Journal of Finance](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12021)
        """)

with col2:
    st.subheader("Rolling High Lookback")
    st.markdown("""
    The **Rolling High Lookback** setting controls the window for calculating the reference high.
    This is analogous to how professional traders set different timeframes for their analysis.

    **Lookback Period Guidelines:**
    - **Short lookback (5-30 days)**: Captures minor pullbacks, good for swing trading.
      More signals, but also more noise.
    - **Medium lookback (30-60 days)**: Balanced view showing intermediate trends.
      Popular among position traders.
    - **Long lookback (60-200 days)**: Reveals major trends and significant drawdowns.
      Used by longer-term investors and for risk assessment.

    **Practical Example:**
    With a 30-day lookback, if a stock hit $100 two weeks ago but trades at $95 today,
    it shows as 5% below the rolling high (light red). If the 30-day high was $120,
    that same $95 would show as 21% below (darker red).

    **Pro Tip:** Compare different lookback periods to understand how the stock behaves
    across timeframes. Stocks that are near highs on multiple timeframes show strong momentum.
    """)

    with st.expander("Learn More: Time Horizons in Technical Analysis"):
        st.markdown("""
        **Concept:** Different investors use different time horizons. Day traders might use
        5-day lookbacks, while pension funds might use 200-day periods. Understanding your
        time horizon is crucial for interpreting any technical indicator.

        **Beginner Reading:**
        - [Investopedia: Trading Time Frames](https://www.investopedia.com/articles/trading/11/trading-time-frames.asp)
        - [CME Group: Time Frames for Trading](https://www.cmegroup.com/education/courses/introduction-to-technical-analysis/time-frames.html)

        **Academic Foundation:**
        - Lo, Mamaysky & Wang (2000): "Foundations of Technical Analysis"
          [Journal of Finance](https://www.jstor.org/stable/222481) - Rigorous statistical
          foundation for pattern recognition across timeframes
        """)

st.markdown("""
**Volume Bars:** The lower section shows trading volume. Volume is the "fuel" of price
movements - higher volume during price moves indicates stronger conviction and often
more sustainable trends. Professional traders always confirm price signals with volume.
""")

with st.expander("Learn More: Volume Analysis"):
    st.markdown("""
    **Why Volume Matters:**
    Volume represents the number of shares traded. High volume indicates high interest
    and conviction. Key volume principles:
    - Price rise + high volume = Strong bullish signal
    - Price rise + low volume = Weak move, possible reversal
    - Price drop + high volume = Strong selling pressure
    - Price drop + low volume = Lack of conviction in sellers

    **Beginner Reading:**
    - [Investopedia: Volume Analysis](https://www.investopedia.com/terms/v/volume.asp)
    - [StockCharts: Volume Indicators](https://school.stockcharts.com/doku.php?id=technical_indicators:volume)

    **Academic Foundation:**
    - Karpoff (1987): "The Relation Between Price Changes and Trading Volume"
      [Journal of Financial and Quantitative Analysis](https://www.jstor.org/stable/2330874)
    - Campbell, Grossman & Wang (1993): "Trading Volume and Serial Correlation in Stock Returns"
      [Quarterly Journal of Economics](https://academic.oup.com/qje/article-abstract/108/4/905/1881846)
    """)

st.divider()

# =============================================================================
# 3. DRAWDOWN ANALYSIS
# =============================================================================
st.header("3. Drawdown Analysis Tab")
st.markdown("""
Drawdown analysis is one of the most important risk management tools used by professional
investors. A **drawdown** measures the peak-to-trough decline before a new peak is achieved.
Understanding drawdowns helps you:
- Assess realistic downside risk (not just volatility)
- Set appropriate position sizes
- Maintain psychological resilience during market declines

**Key Metrics Explained:**
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("All-Time High (ATH)", "Example: $150")
    st.caption("""
    The highest price reached in the selected period. This is your reference point.
    Being aware of the ATH helps contextualize current prices.
    """)

with col2:
    st.metric("Current Drawdown", "Example: -12%")
    st.caption("""
    How far below the ATH the current price is. A stock at $132 with ATH of $150
    has a 12% drawdown. This tells you how much recovery is needed to break even.
    """)

with col3:
    st.metric("Max Drawdown", "Example: -35%")
    st.caption("""
    The largest peak-to-trough decline in the period. This is the worst-case
    historical scenario - crucial for stress testing your portfolio.
    """)

st.markdown("""
**Underwater Chart:**
Shows how long the stock spent below its previous high. Longer "underwater" periods
indicate extended recovery times. For example, the S&P 500 took 7 years to recover
from the 2000 dot-com crash. Understanding typical recovery times helps set realistic
expectations.

**Recovery Statistics:**
- Average time to recover from drawdowns of various depths
- Number of drawdown events (how often do 10%+ drops occur?)
- Distribution of drawdown depths (most drawdowns are small, but tail events matter)
""")

with st.expander("Learn More: Drawdown Analysis"):
    st.markdown("""
    **Why Drawdowns Matter More Than Volatility:**
    Volatility (standard deviation) treats upside and downside equally. Drawdowns focus
    specifically on losses - what actually hurts investors. A fund with 20% annual volatility
    might have very different drawdown profiles depending on how that volatility is distributed.

    **Key Insight:** The math of losses is asymmetric. A 50% loss requires a 100% gain to
    recover. A 75% loss requires a 300% gain. This is why limiting drawdowns is crucial.

    | Drawdown | Gain Needed to Recover |
    |----------|------------------------|
    | -10%     | +11.1%                 |
    | -20%     | +25.0%                 |
    | -30%     | +42.9%                 |
    | -50%     | +100.0%                |
    | -75%     | +300.0%                |

    **Survivorship Bias Warning:** This dashboard analyzes stocks that are currently prominent
    and publicly traded (e.g., AAPL, MSFT, NVDA). These are survivors — companies that
    recovered from drawdowns and thrived. Many stocks experience drawdowns they never recover
    from (e.g., Enron, Lehman Brothers, Bed Bath & Beyond). Historical drawdown recovery
    statistics from surviving companies overstate the probability of recovery in general.
    Always consider the possibility that a drawdown may be permanent.
    """)
    render_references("drawdown")

st.divider()

# =============================================================================
# 4. PUT OPTIONS EDUCATION
# =============================================================================
st.header("4. Put Options Education")
st.info("**Go to the Put Options page** in the sidebar for a comprehensive put options education dashboard with real historical options data across multiple tickers (AAPL, MSFT, TSLA, NVDA, AMD, and more).")

st.warning("""
**Risk Disclaimer:** Options trading involves substantial risk of loss and is not suitable
for all investors. **Buying** options (puts or calls) risks the entire premium paid.
**Selling** options can expose you to losses far exceeding your initial margin — potentially
unlimited for uncovered positions. This dashboard is for **educational purposes only**. Always:
- Understand the product before trading
- Never risk more than you can afford to lose
- Consider consulting a registered investment advisor
- Paper trade first to gain experience
""")

st.markdown("""
The **Put Options** page teaches you about put options using real historical contracts across multiple tickers:

**What is a Put Option?**
A put option gives you the right (but not obligation) to **sell** a stock at a specific price
(strike price) before a specific date (expiration). You pay a premium for this right.

**Why Learn About Puts?**
- **Portfolio Protection**: Puts act like insurance against stock declines
- **Profit from Declines**: Bearish speculation without shorting
- **Income Generation**: Advanced strategies like cash-secured puts (note: this involves
  *selling* puts, which carries different and greater risk than buying them)
- **Risk Management**: Understanding options helps understand market dynamics

**Key Concept - Moneyness:**
- **In-the-Money (ITM)**: Strike price is above the current stock price (for puts). The option
  has intrinsic value.
- **At-the-Money (ATM)**: Strike price equals (or is very near) the current stock price.
- **Out-of-the-Money (OTM)**: Strike price is below the current stock price (for puts). The
  option has no intrinsic value — only time/extrinsic value.

**What You'll Learn:**
1. **Fundamentals**: Strike price, premium, expiration, moneyness, intrinsic vs. extrinsic value
2. **Payoff Diagrams**: Interactive visualizations of profit/loss at expiration
3. **The Greeks**: Delta, Gamma, Theta, Vega, Rho - how options prices change
4. **Risk Calculators**: Break-even analysis, position sizing, P/L scenarios
5. **Option Chains**: How to read and interpret real market data
""")

with st.expander("Learn More: Put Options"):
    render_references("options")

with st.expander("Learn More: The Greeks (Delta, Theta, Gamma, Vega)"):
    st.markdown("""
    The "Greeks" measure how option prices change in response to various factors:

    | Greek | Measures | Intuition |
    |-------|----------|-----------|
    | **Delta** | Price sensitivity to stock movement | "How much does my option move if the stock moves $1?" |
    | **Gamma** | Rate of change of delta | "How stable is my delta?" (acceleration) |
    | **Theta** | Time decay | "How much value do I lose each day?" |
    | **Vega** | Volatility sensitivity | "How much does my option move if volatility changes?" |
    | **Rho** | Interest rate sensitivity | "How does my option react to rate changes?" |

    **Practical Example:**
    A put with Delta = -0.40 will gain approximately $0.40 for every $1 the stock drops.
    But Theta = -0.05 means you lose $5 per day (for 1 contract = 100 shares) just from time passing.

    **Important: Theta is non-linear.** Time decay accelerates sharply in the final 30-45 days
    before expiration. An option 90 days out loses time value slowly, but the same option with
    15 days left decays much faster per day. This is why many options strategies focus on the
    final month of an option's life.
    """)
    render_references("greeks")

st.divider()

# =============================================================================
# 5. TECHNICAL INDICATORS
# =============================================================================
st.header("5. Technical Indicators")
st.markdown("""
Technical indicators require an Alpha Vantage API key for real-time data.
Get a free key at [alphavantage.co](https://www.alphavantage.co/support/#api-key)
(free tier: 5 calls/minute, 500 calls/day).

**What Are Technical Indicators?**
Technical indicators are mathematical calculations based on price, volume, or open interest.
They help identify trends, momentum, volatility, and potential reversal points. While no
indicator is perfect, they provide objective frameworks for analysis.
""")

tab1, tab2, tab3, tab4 = st.tabs(["RSI", "MACD", "Bollinger Bands", "Moving Averages"])

with tab1:
    st.subheader("RSI (Relative Strength Index)")
    st.markdown("""
    **Creator:** J. Welles Wilder Jr. (1978)

    **What it measures:** Momentum - specifically, the speed and magnitude of recent price
    changes to evaluate overbought or oversold conditions.

    **The Math (Simplified):**
    RSI = 100 - (100 / (1 + RS)), where RS = Average Gain / Average Loss over N periods

    **Standard Interpretation:**
    - **Above 70**: Potentially overbought - the stock has risen quickly and may be due for a pullback
    - **Below 30**: Potentially oversold - the stock has fallen quickly and may be due for a bounce
    - **50 level**: Neutral momentum - often acts as support/resistance

    **Advanced Uses:**
    - **Divergences**: Price makes new high but RSI doesn't = bearish divergence (weakening momentum)
    - **Failure Swings**: RSI breaks above 70, pulls back, then fails to exceed prior RSI high = reversal signal
    - **Trend Confirmation**: In strong uptrends, RSI tends to stay between 40-80; in downtrends, 20-60

    **Limitations:**
    - Can stay overbought/oversold for extended periods in strong trends
    - Works better in ranging markets than trending markets
    - Different assets may require different thresholds (crypto often uses 80/20)
    """)
    with st.expander("References: RSI"):
        render_references("rsi")

with tab2:
    st.subheader("MACD (Moving Average Convergence Divergence)")
    st.markdown("""
    **Creator:** Gerald Appel (1970s)

    **What it measures:** Trend direction, momentum, and potential trend reversals by showing
    the relationship between two moving averages of price.

    **Components:**
    - **MACD Line**: 12-period EMA minus 26-period EMA (shows momentum)
    - **Signal Line**: 9-period EMA of the MACD line (smoothed trigger)
    - **Histogram**: MACD Line minus Signal Line (visualizes the difference)

    **Standard Interpretation:**
    - **MACD crosses above Signal Line**: Bullish signal - momentum turning positive
    - **MACD crosses below Signal Line**: Bearish signal - momentum turning negative
    - **Histogram increasing**: Momentum strengthening in current direction
    - **Zero line crossover**: MACD crossing zero indicates trend change

    **Advanced Uses:**
    - **Divergences**: Price makes new high but MACD doesn't = potential reversal
    - **Histogram reversals**: Histogram shrinking before signal line cross = early warning
    - **Multiple timeframes**: Confirm signals across daily and weekly charts

    **Limitations:**
    - Lagging indicator (based on moving averages)
    - Can generate false signals in choppy/ranging markets
    - Default parameters (12, 26, 9) may not suit all assets or timeframes
    """)
    with st.expander("References: MACD"):
        render_references("macd")

with tab3:
    st.subheader("Bollinger Bands")
    st.markdown("""
    **Creator:** John Bollinger (1980s)

    **What it measures:** Volatility and relative price levels. The bands expand during
    volatile periods and contract during calm periods.

    **Components:**
    - **Middle Band**: 20-period simple moving average (the trend)
    - **Upper Band**: Middle band + 2 standard deviations
    - **Lower Band**: Middle band - 2 standard deviations

    **Statistical Foundation:**
    Under a normal distribution, ~95% of observations fall within 2 standard deviations.
    However, stock returns exhibit **fat tails** (leptokurtosis) — extreme moves occur
    significantly more often than a normal distribution predicts. In practice, prices
    breach the bands more frequently than 5% of the time. Bollinger Bands are best
    understood as a relative volatility framework, not a probabilistic prediction interval.

    **Standard Interpretation:**
    - **Price near upper band**: Relatively high (not necessarily overbought)
    - **Price near lower band**: Relatively low (not necessarily oversold)
    - **Bands widening**: Volatility increasing - often follows breakouts
    - **Bands narrowing (squeeze)**: Volatility decreasing - often precedes big moves

    **Advanced Uses:**
    - **W-Bottoms**: Price touches lower band, bounces, makes lower low (but not outside band) = bullish
    - **M-Tops**: Opposite pattern at upper band = bearish
    - **Walking the bands**: In strong trends, price can "walk" along upper/lower band

    **Limitations:**
    - Not a standalone system - best combined with other indicators
    - Band touches are not automatic buy/sell signals
    - Standard 20-period, 2-std may not suit all markets
    """)
    with st.expander("References: Bollinger Bands"):
        render_references("bollinger")

with tab4:
    st.subheader("Moving Averages (SMA & EMA)")
    st.markdown("""
    **What they are:** The foundation of most technical indicators. Moving averages smooth
    price data to identify trends by filtering out short-term noise.

    **Types:**
    - **SMA (Simple Moving Average)**: Equal weight to all prices in the period.
      Formula: Sum of last N prices / N
    - **EMA (Exponential Moving Average)**: More weight to recent prices, reacts faster.
      Uses a multiplier: 2 / (N + 1)

    **Common Periods and Their Uses:**
    | Period | Timeframe | Common Use |
    |--------|-----------|------------|
    | 10-day | Very short | Short-term swing trading, momentum |
    | 20-day | Short | Swing trading, Bollinger middle band |
    | 50-day | Medium | Institutional benchmark, trend confirmation |
    | 100-day | Medium-long | Less common, between 50 and 200 |
    | 200-day | Long | Institutional benchmark, bull/bear market definition |

    **Key Signals:**
    - **Price above MA**: Generally bullish - price is above average
    - **Price below MA**: Generally bearish - price is below average
    - **Golden Cross**: 50-day crosses above 200-day - traditionally considered bullish
    - **Death Cross**: 50-day crosses below 200-day - traditionally considered bearish

    **Note:** Academic evidence for Golden/Death Cross reliability is mixed. These signals
    are lagging by nature, and many studies suggest their predictive power is limited after
    accounting for transaction costs. They are best used as trend context, not trade triggers.

    **Why 50 and 200 Day?**
    50 trading days ≈ 10 weeks (~2.5 months) captures intermediate trends, while
    200 trading days ≈ 40 weeks (~10 months) captures long-term trends. These periods
    became institutional standards partly through convention — many algorithms and fund
    mandates reference them, creating self-fulfilling support/resistance levels.

    **Limitations:**
    - Lagging indicators by definition
    - Whipsaws in choppy markets generate false signals
    - No single MA period works for all stocks or market conditions
    """)
    with st.expander("References: Moving Averages"):
        render_references("moving_averages")

st.divider()

# =============================================================================
# 6. LIMITATIONS OF TECHNICAL ANALYSIS
# =============================================================================
st.header("6. What Technical Analysis Can't Do")
st.markdown("""
Technical analysis is a useful framework, but it has well-documented limitations:

- **No predictive guarantee**: Patterns and indicators describe past behavior. Markets are
  influenced by news, earnings, policy changes, and other events that no chart can anticipate.
- **Efficient Market Hypothesis (EMH)**: Academic research suggests that publicly available
  information is rapidly reflected in prices. Under strong-form EMH, technical analysis
  provides no edge. Even under weaker forms, consistent profits from technical signals alone
  are debated.
- **Data mining risk**: With enough indicators, timeframes, and parameters, you can find
  "patterns" in random data. Many published strategies fail out-of-sample.
- **Self-fulfilling vs. self-defeating**: Popular signals (e.g., 200-day MA) may work because
  many traders act on them — but widespread adoption can also erode their effectiveness.
- **No substitute for fundamentals**: Technicals show *what* is happening to price; they
  don't explain *why*. A stock can look bullish on every indicator and still collapse on an
  earnings miss.

**Bottom line:** Use technical indicators as one input among many — not as a decision-making
system in isolation.
""")

st.divider()

# =============================================================================
# 7. TIPS & FAQ
# =============================================================================
st.header("7. Tips & FAQ")

st.subheader("Best Practices")
st.markdown("""
**For Analysis:**
- **Start with longer timeframes** (3+ years) to understand historical patterns before zooming in
- **Adjust the lookback period** based on your investment horizon (longer for investing, shorter for trading)
- **Compare multiple stocks** to understand relative performance within sectors
- **Use technical indicators for confirmation**, not as standalone signals
- **Always consider fundamentals** - technicals show what IS happening, fundamentals explain WHY

**For Learning:**
- **Paper trade first** - Practice with simulated money before risking real capital
- **Keep a trading journal** - Document your decisions and review them
- **Study mistakes** - Losses teach more than wins if you analyze them honestly
- **Be patient** - Skill develops over months and years, not days
""")

st.subheader("Frequently Asked Questions")

with st.expander("Why is my stock showing red even though it's up today?"):
    st.markdown("""
    The color reflects the distance from the **rolling high**, not the daily change.

    **Example:** A stock was at $100 two weeks ago (the rolling high), dropped to $90, and
    today rose from $90 to $93. It's up 3.3% today (bullish daily move) but still 7% below
    its rolling high (showing red in the gradient).

    This distinction is important: a stock can have positive daily momentum while still being
    in a pullback/correction relative to its recent highs.
    """)

with st.expander("What's the difference between Single Stock and Compare modes?"):
    st.markdown("""
    - **Single Stock**: Deep-dive analysis of one stock with all features (drawdown analysis,
      put options learning, full technical indicators)
    - **Compare Stocks**: Side-by-side comparison of up to 4 stocks - great for:
        - Comparing companies in the same sector (AAPL vs MSFT vs GOOGL)
        - Evaluating relative strength (which stock is holding up better?)
        - Sector rotation analysis (tech vs financials vs energy)
    """)

with st.expander("How do I get technical indicators to work?"):
    st.markdown("""
    1. Get a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
    2. Enter the key in the Technical Indicators section
    3. Select your desired indicators
    4. Click Load Data

    **Note:** Free tier limits:
    - 5 API calls per minute
    - 500 API calls per day

    If you hit rate limits, wait a minute and try again. For heavy usage, consider their
    premium plans or alternative data providers (Yahoo Finance, IEX Cloud, Polygon.io).
    """)

with st.expander("Can I use this for real trading decisions?"):
    st.markdown("""
    This dashboard is for **educational and informational purposes only**. It should not be
    considered financial advice.

    **Before trading real money:**
    - Understand the risks involved in any investment
    - Do your own research beyond what any dashboard shows
    - Consider consulting a registered investment advisor or financial professional
    - Paper trade to build experience without risking capital
    - Never invest more than you can afford to lose
    - Understand that past performance does not guarantee future results

    **For options specifically:**
    - Options involve substantial risk including the loss of all invested capital
    - Options are not suitable for all investors
    - Ensure you understand the characteristics and risks of options before trading
    - Read the Options Disclosure Document (ODD) available from your broker
    """)

with st.expander("Where does the options data come from?"):
    st.markdown("""
    The Put Options page uses millions of historical options contracts across multiple
    tickers including AAPL, MSFT, GOOGL, AMZN, META, TSLA, NFLX, NVDA, AMD, and more.
    Data spans from as early as 2010 to present and includes:
    - Daily snapshots of available put and call options
    - Strike prices, expiration dates, bid/ask prices
    - Volume and open interest
    - Implied volatility and Greeks (Delta, Gamma, Theta, Vega, Rho)

    **Why multiple tickers?**
    Different stocks exhibit different options characteristics:
    - **High-beta names** (TSLA, NVDA) = higher IV, wider premium swings
    - **Mega-caps** (AAPL, MSFT) = deep liquidity, tighter spreads
    - **Recent IPOs** (ARM, CRWV) = shorter history, different dynamics
    - Comparing across tickers builds deeper intuition about options pricing
    """)

st.divider()

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("*Navigate to **Stock Analysis** or **Put Options** using the sidebar.*")

with col2:
    st.markdown("""
    **Additional Resources:**
    - [SEC Investor Education](https://www.investor.gov/)
    - [FINRA Investor Tools](https://www.finra.org/investors)
    - [Federal Reserve Economic Data](https://fred.stlouisfed.org/)
    """)
