"""
Fresh Stock Analysis Dashboard - Home Page

A modern, themed Streamlit dashboard with comprehensive educational content
and improved visual styling.
"""

import streamlit as st

from theme import inject_custom_css, create_theme_toggle, get_palette

# Page configuration
st.set_page_config(
    page_title="Stock Analysis - Home",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject enhanced CSS
inject_custom_css()

# Additional home page specific CSS
def inject_home_css():
    palette = get_palette()
    st.markdown(f"""
    <style>
        /* Hero section */
        .hero-title {{
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, {palette.primary} 0%, {palette.chart_5} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }}

        .hero-subtitle {{
            font-size: 1.2rem;
            color: {palette.text_secondary};
            margin-bottom: 2rem;
        }}

        /* Feature cards */
        .feature-card {{
            background: linear-gradient(145deg, {palette.surface} 0%, {palette.surface_elevated} 100%);
            border: 1px solid {palette.border};
            border-radius: 16px;
            padding: 24px;
            height: 100%;
            transition: all 0.3s ease;
        }}

        .feature-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
            border-color: {palette.primary};
        }}

        .feature-icon {{
            font-size: 2.5rem;
            margin-bottom: 12px;
        }}

        .feature-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: {palette.text_primary};
            margin-bottom: 8px;
        }}

        .feature-desc {{
            color: {palette.text_secondary};
            font-size: 0.95rem;
            line-height: 1.6;
        }}

        /* Section headers */
        .section-header {{
            font-size: 1.5rem;
            font-weight: 600;
            color: {palette.text_primary};
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid {palette.primary};
            display: inline-block;
        }}

        /* Info boxes */
        .info-box {{
            background: linear-gradient(135deg, {palette.surface} 0%, rgba(99, 102, 241, 0.05) 100%);
            border-left: 4px solid {palette.primary};
            border-radius: 0 12px 12px 0;
            padding: 20px 24px;
            margin: 16px 0;
        }}

        .info-box-title {{
            font-weight: 600;
            color: {palette.primary};
            margin-bottom: 8px;
        }}

        /* Indicator badges */
        .indicator-badge {{
            display: inline-block;
            background: {palette.primary};
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            margin-right: 8px;
            margin-bottom: 8px;
        }}

        /* Color key boxes */
        .color-key {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            background: {palette.surface};
            border-radius: 8px;
            margin: 8px 0;
        }}

        .color-dot {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
        }}

        /* Quick start steps */
        .step-number {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            background: {palette.primary};
            color: white;
            border-radius: 50%;
            font-weight: 600;
            margin-right: 12px;
        }}

        .step-item {{
            display: flex;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid {palette.border};
        }}

        /* Reference links */
        .ref-link {{
            display: block;
            padding: 8px 12px;
            background: {palette.surface};
            border-radius: 8px;
            margin: 6px 0;
            border: 1px solid {palette.border};
            transition: all 0.2s ease;
        }}

        .ref-link:hover {{
            border-color: {palette.primary};
            background: {palette.surface_elevated};
        }}

        /* Metric explanation cards */
        .metric-explain {{
            text-align: center;
            padding: 20px;
            background: {palette.surface};
            border-radius: 12px;
            border: 1px solid {palette.border};
        }}

        .metric-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: {palette.primary};
        }}

        .metric-label {{
            font-size: 0.9rem;
            color: {palette.text_secondary};
            margin-top: 4px;
        }}

        /* Warning/disclaimer box */
        .disclaimer-box {{
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 20px;
            margin: 16px 0;
        }}

        /* Tab styling override */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            background: {palette.surface};
            padding: 4px;
            border-radius: 12px;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 500;
        }}

        .stTabs [aria-selected="true"] {{
            background: {palette.primary} !important;
            color: white !important;
        }}

        /* Expander styling */
        .streamlit-expanderHeader {{
            background: {palette.surface} !important;
            border-radius: 12px !important;
            font-weight: 500;
        }}

        .streamlit-expanderContent {{
            background: {palette.surface} !important;
            border-radius: 0 0 12px 12px !important;
        }}
    </style>
    """, unsafe_allow_html=True)

inject_home_css()

# =============================================================================
# REFERENCE LINKS
# =============================================================================
REFERENCES = {
    "rsi": {
        "beginner": [
            ("Investopedia: RSI Explained", "https://www.investopedia.com/terms/r/rsi.asp"),
            ("Fidelity: Understanding RSI", "https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/RSI"),
        ],
        "academic": [
            ("Original: Wilder's 'New Concepts in Technical Trading Systems'", "https://www.amazon.com/New-Concepts-Technical-Trading-Systems/dp/0894590278"),
        ],
    },
    "macd": {
        "beginner": [
            ("Investopedia: MACD Indicator", "https://www.investopedia.com/terms/m/macd.asp"),
            ("TradingView: MACD Guide", "https://www.tradingview.com/support/solutions/43000502344-macd-moving-average-convergence-divergence/"),
        ],
        "academic": [
            ("Gerald Appel: 'Technical Analysis Power Tools'", "https://www.amazon.com/Technical-Analysis-Power-Active-Investors/dp/0131479024"),
        ],
    },
    "bollinger": {
        "beginner": [
            ("Investopedia: Bollinger Bands", "https://www.investopedia.com/terms/b/bollingerbands.asp"),
            ("BollingerBands.com (Official)", "https://www.bollingerbands.com/"),
        ],
        "academic": [
            ("John Bollinger: 'Bollinger on Bollinger Bands'", "https://www.amazon.com/Bollinger-Bands-John/dp/0071373683"),
        ],
    },
    "options": {
        "beginner": [
            ("Investopedia: Put Options", "https://www.investopedia.com/terms/p/putoption.asp"),
            ("CBOE Options Institute", "https://www.cboe.com/education/"),
            ("Options Playbook", "https://www.optionsplaybook.com/"),
        ],
        "academic": [
            ("Black & Scholes (1973)", "https://www.jstor.org/stable/1831029"),
            ("Hull: 'Options, Futures, and Other Derivatives'", "https://www.amazon.com/Options-Futures-Other-Derivatives-10th/dp/013447208X"),
        ],
    },
}


def render_references(topic: str):
    """Render styled reference links."""
    if topic not in REFERENCES:
        return

    refs = REFERENCES[topic]
    palette = get_palette()

    if "beginner" in refs:
        st.markdown("**Beginner Resources:**")
        for name, url in refs["beginner"]:
            st.markdown(f'<a href="{url}" target="_blank" class="ref-link">{name}</a>', unsafe_allow_html=True)

    if "academic" in refs:
        st.markdown("**Academic/Professional:**")
        for name, url in refs["academic"]:
            st.markdown(f'<a href="{url}" target="_blank" class="ref-link">{name}</a>', unsafe_allow_html=True)


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("### Settings")
    create_theme_toggle()

    st.divider()

    st.markdown("### Navigation")
    st.page_link("fresh_app.py", label="Home", icon="🏠")
    st.page_link("pages/1_Stock_Analysis.py", label="Stock Analysis", icon="📈")
    st.page_link("pages/2_Put_Options.py", label="Put Options", icon="📉")

    st.divider()

    with st.expander("Quick Help"):
        st.markdown("""
        **Getting Started:**
        1. Go to **Stock Analysis**
        2. Select a ticker
        3. Click **Load Data**
        4. Explore the charts!
        """)


# =============================================================================
# HERO SECTION
# =============================================================================
st.markdown('<p class="hero-title">Stock Analysis Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Analyze stocks, understand drawdowns, and learn about options with real market data</p>', unsafe_allow_html=True)

# Feature cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📈</div>
        <div class="feature-title">Stock Analysis</div>
        <div class="feature-desc">
            Visualize prices with gradient colors showing distance from rolling highs.
            Includes RSI, MACD, and Bollinger Bands.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📉</div>
        <div class="feature-title">Drawdown Analysis</div>
        <div class="feature-desc">
            Track peak-to-trough declines, recovery times, and underwater periods
            using institutional-grade methodology.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Options Education</div>
        <div class="feature-desc">
            Learn put options with ~3M real AMD contracts. Interactive payoff
            diagrams, Greeks explanations, and risk calculators.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =============================================================================
# QUICK START
# =============================================================================
st.markdown('<p class="section-header">Quick Start</p>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <div class="info-box-title">How to Use This Dashboard</div>
    <div class="step-item"><span class="step-number">1</span> Select <b>Single Stock</b> or <b>Compare Stocks</b> mode</div>
    <div class="step-item"><span class="step-number">2</span> Enter a ticker symbol (e.g., AAPL, MSFT, NVDA)</div>
    <div class="step-item"><span class="step-number">3</span> Set your date range and lookback period</div>
    <div class="step-item"><span class="step-number">4</span> Click <b>Load Data</b> and explore the tabs</div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# GRADIENT COLORING EXPLANATION
# =============================================================================
st.markdown('<p class="section-header">Understanding the Gradient Colors</p>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    The price chart uses a **color gradient** to show how far the current price is from its rolling high.
    This technique is used by professional traders to quickly identify relative performance.

    **Why this matters:** A stock 5% from its high behaves very differently from one 30% from its high.
    Institutional investors constantly monitor "distance from highs" as a risk metric.
    """)

    st.markdown("""
    <div class="color-key">
        <div class="color-dot" style="background: #10B981;"></div>
        <span><b>Green</b> — At or above the rolling high (bullish momentum)</span>
    </div>
    <div class="color-key">
        <div class="color-dot" style="background: #F59E0B;"></div>
        <span><b>Yellow</b> — Slight pullback from high</span>
    </div>
    <div class="color-key">
        <div class="color-dot" style="background: #EF4444;"></div>
        <span><b>Red</b> — Significant drawdown from high</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-explain">
        <div class="metric-value">30</div>
        <div class="metric-label">Default Lookback (days)</div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Adjust the lookback period based on your investment horizon. Shorter for trading, longer for investing.")


# =============================================================================
# DRAWDOWN ANALYSIS
# =============================================================================
st.markdown('<p class="section-header">Drawdown Analysis</p>', unsafe_allow_html=True)

st.markdown("""
A **drawdown** measures the peak-to-trough decline before a new peak is achieved.
Understanding drawdowns helps you assess realistic downside risk, set appropriate position sizes,
and maintain psychological resilience during market declines.
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-explain">
        <div class="metric-value">ATH</div>
        <div class="metric-label">All-Time High</div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("The highest price reached in the period — your reference point.")

with col2:
    st.markdown("""
    <div class="metric-explain">
        <div class="metric-value" style="color: #EF4444;">-12%</div>
        <div class="metric-label">Current Drawdown</div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("How far below ATH the current price is.")

with col3:
    st.markdown("""
    <div class="metric-explain">
        <div class="metric-value" style="color: #EF4444;">-35%</div>
        <div class="metric-label">Max Drawdown</div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Worst historical decline — critical for stress testing.")

st.markdown("""
<div class="info-box">
    <div class="info-box-title">The Math of Losses is Asymmetric</div>
    A 50% loss requires a 100% gain to recover. A 75% loss requires 300%. This is why limiting drawdowns is crucial.
</div>
""", unsafe_allow_html=True)


# =============================================================================
# TECHNICAL INDICATORS
# =============================================================================
st.markdown('<p class="section-header">Technical Indicators</p>', unsafe_allow_html=True)

st.markdown("""
<span class="indicator-badge">RSI</span>
<span class="indicator-badge">MACD</span>
<span class="indicator-badge">Bollinger Bands</span>
<span class="indicator-badge">SMA</span>
<span class="indicator-badge">EMA</span>
""", unsafe_allow_html=True)

st.caption("Requires Alpha Vantage API key. Get a free key at [alphavantage.co](https://www.alphavantage.co/support/#api-key)")

tab1, tab2, tab3 = st.tabs(["RSI", "MACD", "Bollinger Bands"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **Relative Strength Index** — measures momentum by comparing recent gains to losses.

        - **Above 70:** Potentially overbought
        - **Below 30:** Potentially oversold
        - **50 level:** Neutral momentum

        *Created by J. Welles Wilder Jr. (1978)*
        """)
    with col2:
        render_references("rsi")

with tab2:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **Moving Average Convergence Divergence** — shows trend direction and momentum.

        - **MACD Line:** 12-EMA minus 26-EMA
        - **Signal Line:** 9-EMA of MACD
        - **Histogram:** Difference between the two

        *Created by Gerald Appel (1970s)*
        """)
    with col2:
        render_references("macd")

with tab3:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **Bollinger Bands** — volatility indicator showing price relative to recent range.

        - **Upper Band:** SMA + 2 standard deviations
        - **Lower Band:** SMA - 2 standard deviations
        - **Squeeze:** Low volatility, often precedes big moves

        *Created by John Bollinger (1980s)*
        """)
    with col2:
        render_references("bollinger")


# =============================================================================
# PUT OPTIONS
# =============================================================================
st.markdown('<p class="section-header">Put Options Education</p>', unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer-box">
    <b>Risk Disclaimer:</b> Options trading involves substantial risk and is not suitable for all investors.
    This dashboard is for <b>educational purposes only</b>. Always understand the product before trading,
    never risk more than you can afford to lose, and consider consulting a registered investment advisor.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **What is a Put Option?**

    A put gives you the right (not obligation) to **sell** a stock at a specific price
    before a specific date. You pay a premium for this right.

    **Why learn about puts?**
    - Portfolio protection (like insurance)
    - Profit from expected declines
    - Risk management
    """)

with col2:
    st.markdown("""
    **What You'll Learn:**

    1. Strike price, premium, expiration
    2. Intrinsic vs. extrinsic value
    3. Interactive payoff diagrams
    4. The Greeks (Delta, Gamma, Theta, Vega)
    5. Risk calculators and P/L scenarios
    """)

with st.expander("Reference Materials"):
    render_references("options")


# =============================================================================
# FAQ
# =============================================================================
st.markdown('<p class="section-header">FAQ</p>', unsafe_allow_html=True)

with st.expander("Why is my stock red even though it's up today?"):
    st.markdown("""
    The color reflects **distance from the rolling high**, not daily change.

    Example: Stock was $100 two weeks ago, dropped to $90, today rose to $93.
    It's up 3.3% today but still 7% below its rolling high — showing red.
    """)

with st.expander("What's the difference between Single Stock and Compare modes?"):
    st.markdown("""
    - **Single Stock:** Full analysis with drawdowns, indicators, and options learning
    - **Compare Stocks:** Side-by-side comparison of up to 4 stocks for relative strength analysis
    """)

with st.expander("How do I enable technical indicators?"):
    st.markdown("""
    1. Get a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
    2. Set environment variable: `export ALPHAVANTAGE_API_KEY="your_key"`
    3. Select indicators in the sidebar
    4. Click Load Data

    *Free tier: 5 calls/minute, 500 calls/day*
    """)


# =============================================================================
# FOOTER
# =============================================================================
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Navigate:** Stock Analysis | Put Options")

with col2:
    st.markdown("""
    **Resources:** [SEC Investor Education](https://www.investor.gov/) |
    [FINRA Tools](https://www.finra.org/investors) |
    [FRED Data](https://fred.stlouisfed.org/)
    """)
