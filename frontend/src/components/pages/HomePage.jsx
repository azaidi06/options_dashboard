/**
 * Home Page - Comprehensive educational resource and navigation
 * Ported from robust_app.py (Streamlit)
 */
import { Link } from 'react-router-dom';
import { Layout } from '../layout/Layout';
import { Tabs, Tab } from '../common/Tabs';

// ─── Reference Links ───
const REFERENCES = {
  rsi: {
    beginner: [
      ['Investopedia: RSI Explained', 'https://www.investopedia.com/terms/r/rsi.asp'],
      ['Fidelity: Understanding RSI', 'https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/RSI'],
      ['StockCharts: RSI Introduction', 'https://school.stockcharts.com/doku.php?id=technical_indicators:relative_strength_index_rsi'],
    ],
    academic: [
      ["Original Paper: J. Welles Wilder, 'New Concepts in Technical Trading Systems' (1978)", 'https://www.amazon.com/New-Concepts-Technical-Trading-Systems/dp/0894590278'],
      ["SSRN: 'Technical Analysis and Liquidity Provision'", 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1745284'],
      ["Journal of Finance: 'Foundations of Technical Analysis'", 'https://www.jstor.org/stable/222481'],
    ],
  },
  macd: {
    beginner: [
      ['Investopedia: MACD Indicator', 'https://www.investopedia.com/terms/m/macd.asp'],
      ['TradingView: MACD Guide', 'https://www.tradingview.com/support/solutions/43000502344-macd-moving-average-convergence-divergence/'],
      ['Charles Schwab: Using MACD', 'https://www.schwab.com/learn/story/how-to-use-macd-indicator'],
    ],
    academic: [
      ["Gerald Appel, 'Technical Analysis: Power Tools for Active Investors'", 'https://www.amazon.com/Technical-Analysis-Power-Active-Investors/dp/0131479024'],
      ["Chong & Ng (2008): 'Technical Analysis and the London Stock Exchange'", 'https://doi.org/10.1080/13504850600993598'],
      ["Anghel (2015): 'Data-Snooping Bias in Tests of the Relative Performance of Multiple Forecasting Models'", 'https://doi.org/10.1016/j.intfin.2015.07.001'],
    ],
  },
  bollinger: {
    beginner: [
      ['Investopedia: Bollinger Bands', 'https://www.investopedia.com/terms/b/bollingerbands.asp'],
      ['BollingerBands.com (Official)', 'https://www.bollingerbands.com/'],
      ['Fidelity: Using Bollinger Bands', 'https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/bollinger-bands'],
    ],
    academic: [
      ["John Bollinger, 'Bollinger on Bollinger Bands' (2001)", 'https://www.amazon.com/Bollinger-Bands-John/dp/0071373683'],
      ["Poon & Granger (2003): 'Forecasting Volatility in Financial Markets'", 'https://doi.org/10.1016/S0304-4076(03)00004-0'],
      ["Park & Irwin (2007): 'What Do We Know About the Profitability of Technical Analysis?'", 'https://doi.org/10.1016/j.jebo.2007.02.003'],
    ],
  },
  moving_averages: {
    beginner: [
      ['Investopedia: Moving Averages', 'https://www.investopedia.com/terms/m/movingaverage.asp'],
      ['StockCharts: Moving Average Guide', 'https://school.stockcharts.com/doku.php?id=technical_indicators:moving_averages'],
      ['Schwab: SMA vs EMA', 'https://www.schwab.com/learn/story/moving-averages'],
    ],
    academic: [
      ["Brock, Lakonishok & LeBaron (1992): 'Simple Technical Trading Rules'", 'https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x'],
      ["Sullivan, Timmermann & White (1999): 'Data-Snooping, Technical Trading Rule Performance, and the Bootstrap'", 'https://doi.org/10.1111/0022-1082.00163'],
      ["Han, Yang & Zhou (2013): 'A New Anomaly: The Cross-Sectional Profitability of Technical Analysis'", 'https://doi.org/10.1017/S0022109013000586'],
    ],
  },
  drawdown: {
    beginner: [
      ['Investopedia: Maximum Drawdown', 'https://www.investopedia.com/terms/m/maximum-drawdown-mdd.asp'],
      ['Morningstar: Understanding Drawdowns', 'https://www.morningstar.com/articles/347327/understanding-maximum-drawdown'],
      ['Portfolio Visualizer: Drawdown Analysis', 'https://www.portfoliovisualizer.com/'],
    ],
    academic: [
      ["Magdon-Ismail & Atiya (2004): 'Maximum Drawdown'", 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=874069'],
      ["Chekhlov, Uryasev & Zabarankin (2005): 'Drawdown Measure in Portfolio Optimization'", 'https://doi.org/10.1142/S0219024905002767'],
      ["Grossman & Zhou (1993): 'Optimal Investment Strategies for Controlling Drawdowns'", 'https://doi.org/10.1111/j.1540-6261.1993.tb04702.x'],
    ],
  },
  options: {
    beginner: [
      ['Investopedia: Put Options Explained', 'https://www.investopedia.com/terms/p/putoption.asp'],
      ['CBOE Options Institute', 'https://www.cboe.com/education/'],
      ['Options Playbook (Free Guide)', 'https://www.optionsplaybook.com/'],
      ['tastytrade: Options Basics', 'https://www.tastylive.com/concepts-strategies/options'],
    ],
    academic: [
      ["Black & Scholes (1973): 'The Pricing of Options'", 'https://www.jstor.org/stable/1831029'],
      ["Hull, 'Options, Futures, and Other Derivatives' (Textbook)", 'https://www.amazon.com/Options-Futures-Other-Derivatives-10th/dp/013447208X'],
      ["Natenberg, 'Option Volatility and Pricing'", 'https://www.amazon.com/Option-Volatility-Pricing-Strategies-Techniques/dp/0071818774'],
      ['Journal of Derivatives: Research Papers', 'https://jod.pm-research.com/'],
    ],
  },
  greeks: {
    beginner: [
      ['Investopedia: The Greeks', 'https://www.investopedia.com/trading/getting-to-know-the-greeks/'],
      ['CBOE: Understanding Greeks', 'https://www.cboe.com/education/options-basics/greeks/'],
      ['Fidelity: Options Greeks Guide', 'https://www.fidelity.com/learning-center/investment-products/options/options-greeks'],
    ],
    academic: [
      ["Taleb, 'Dynamic Hedging' (Professional Reference)", 'https://www.amazon.com/Dynamic-Hedging-Managing-Vanilla-Options/dp/0471152803'],
      ["Bakshi, Cao & Chen (1997): 'Empirical Performance of Alternative Option Pricing Models'", 'https://doi.org/10.1111/0022-1082.00042'],
      ["Hull & White (2017): 'Optimal Delta Hedging for Options'", 'https://doi.org/10.1016/j.jbankfin.2017.01.006'],
    ],
  },
};

function RefLinks({ topic, showBeginner = true, showAcademic = true }) {
  const refs = REFERENCES[topic];
  if (!refs) return null;
  return (
    <div className="space-y-3 mt-3">
      {showBeginner && refs.beginner && (
        <div>
          <p className="font-semibold text-slate-200 mb-2">Learn More (Beginner-Friendly):</p>
          <div className="space-y-1.5">
            {refs.beginner.map(([name, url]) => (
              <a key={url} href={url} target="_blank" rel="noopener noreferrer" className="ref-link">
                {name}
              </a>
            ))}
          </div>
        </div>
      )}
      {showAcademic && refs.academic && (
        <div>
          <p className="font-semibold text-slate-200 mb-2">Deep Dive (Academic/Professional):</p>
          <div className="space-y-1.5">
            {refs.academic.map(([name, url]) => (
              <a key={url} href={url} target="_blank" rel="noopener noreferrer" className="ref-link">
                {name}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function HomePage() {
  return (
    <Layout>
      <div className="max-w-5xl mx-auto">
        {/* ─── Hero ─── */}
        <div className="mb-8">
          <h1 className="text-4xl font-extrabold mb-3 gradient-text">Stock Analysis Dashboard</h1>
          <p className="text-lg text-slate-400 max-w-3xl">
            Welcome! This dashboard helps you analyze stocks, understand drawdowns, and learn about
            put options using real market data and institutional-grade analytical techniques.
          </p>
          <p className="text-slate-400 mt-3">
            <strong className="text-slate-200">Use the navigation to switch between pages:</strong>
          </p>
          <ul className="text-slate-400 mt-1 space-y-1 text-sm">
            <li><strong className="text-indigo-400">Stock Analysis</strong> &mdash; Analyze individual stocks with gradient charts and technical indicators</li>
            <li><strong className="text-purple-400">Put Options</strong> &mdash; Learn about put options using real historical options data across multiple tickers</li>
          </ul>
        </div>

        {/* ─── Navigation Cards ─── */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Link to="/stock" className="group">
            <div className="card-lg h-full border-slate-800 hover:border-indigo-500/30 transition-all duration-300 group-hover:shadow-lg group-hover:shadow-indigo-500/5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-indigo-600/15 flex items-center justify-center">
                  <span className="text-indigo-400 text-lg">&#9670;</span>
                </div>
                <h2 className="text-xl font-bold text-slate-100 group-hover:text-indigo-400 transition-colors">
                  Stock Analysis
                </h2>
              </div>
              <p className="text-slate-400 mb-4 text-sm leading-relaxed">
                Analyze individual stocks with price charts, technical indicators, drawdown analysis,
                and opportunity windows.
              </p>
              <ul className="text-sm text-slate-500 space-y-1.5">
                <li className="flex items-center gap-2"><span className="text-emerald-500">&#10003;</span> OHLCV data with rolling highs</li>
                <li className="flex items-center gap-2"><span className="text-emerald-500">&#10003;</span> RSI, MACD, Bollinger Bands</li>
                <li className="flex items-center gap-2"><span className="text-emerald-500">&#10003;</span> Drawdown analysis and recovery stats</li>
                <li className="flex items-center gap-2"><span className="text-emerald-500">&#10003;</span> Opportunity windows for entries</li>
              </ul>
            </div>
          </Link>

          <Link to="/options" className="group">
            <div className="card-lg h-full border-slate-800 hover:border-purple-500/30 transition-all duration-300 group-hover:shadow-lg group-hover:shadow-purple-500/5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-purple-600/15 flex items-center justify-center">
                  <span className="text-purple-400 text-lg">&#9670;</span>
                </div>
                <h2 className="text-xl font-bold text-slate-100 group-hover:text-purple-400 transition-colors">
                  Put Options
                </h2>
              </div>
              <p className="text-slate-400 mb-4 text-sm leading-relaxed">
                Learn about put options, explore option chains, and use interactive calculators for
                Greeks and risk analysis.
              </p>
              <ul className="text-sm text-slate-500 space-y-1.5">
                <li className="flex items-center gap-2"><span className="text-emerald-500">&#10003;</span> Option chain explorer</li>
                <li className="flex items-center gap-2"><span className="text-emerald-500">&#10003;</span> IV smile visualization</li>
                <li className="flex items-center gap-2"><span className="text-emerald-500">&#10003;</span> Payoff diagrams</li>
                <li className="flex items-center gap-2"><span className="text-emerald-500">&#10003;</span> Greeks and risk calculators</li>
              </ul>
            </div>
          </Link>
        </div>

        {/* ─── Educational Philosophy ─── */}
        <details className="mb-6">
          <summary>About This Dashboard's Educational Approach</summary>
          <div className="details-content">
            <p>This dashboard combines <strong className="text-slate-100">practical visualization tools</strong> with <strong className="text-slate-100">educational content</strong> at two levels:</p>
            <ol className="list-decimal list-inside mt-3 space-y-2">
              <li><strong className="text-slate-100">Beginner Resources</strong> &mdash; Blog posts and tutorials from Investopedia, CBOE, Fidelity, and other trusted financial education sites for building intuitive understanding</li>
              <li><strong className="text-slate-100">Academic Sources</strong> &mdash; Peer-reviewed papers, foundational books, and professional references for rigorous quantitative depth</li>
            </ol>
            <p className="mt-3">Each concept includes curated links so you can learn at your own pace and depth.</p>
          </div>
        </details>

        {/* ═══════════════════════════════════════════════════════════════════ */}
        {/* 1. GETTING STARTED */}
        {/* ═══════════════════════════════════════════════════════════════════ */}
        <div className="section-divider" />
        <h2 className="text-2xl font-bold text-slate-100 mb-4">1. Getting Started</h2>

        <div className="text-sm text-slate-300 leading-relaxed space-y-3 mb-5">
          <p><strong className="text-slate-100">What this dashboard does:</strong></p>
          <ul className="list-disc list-inside space-y-1.5 ml-2">
            <li>Visualizes stock prices with gradient colors showing distance from rolling highs (a technique used by professional traders to quickly identify relative performance)</li>
            <li>Analyzes drawdowns and recovery patterns using the same methodology employed by hedge funds and risk managers</li>
            <li>Identifies potential put option opportunities based on historical volatility patterns</li>
            <li>Displays technical indicators (RSI, MACD, Bollinger Bands) &mdash; the same tools used by institutional traders worldwide</li>
          </ul>

          <p><strong className="text-slate-100">Quick Start:</strong></p>
          <ol className="list-decimal list-inside space-y-1.5 ml-2">
            <li>Select <strong className="text-slate-100">Single Stock</strong> or <strong className="text-slate-100">Compare Stocks</strong> mode in the sidebar</li>
            <li>Enter a stock ticker (e.g., AAPL, MSFT, GOOGL)</li>
            <li>Set your desired date range</li>
            <li>Click <strong className="text-slate-100">Load Data</strong></li>
            <li>Explore the different analysis tabs</li>
          </ol>
        </div>

        <details className="mb-6">
          <summary>New to Stock Analysis? Start Here</summary>
          <div className="details-content space-y-3">
            <p><strong className="text-slate-100">Recommended Learning Path:</strong></p>
            <ol className="list-decimal list-inside space-y-1.5">
              <li><strong className="text-slate-100">Understand the basics of stock charts</strong> &mdash; How price and volume are displayed</li>
              <li><strong className="text-slate-100">Learn about moving averages</strong> &mdash; The foundation of trend analysis</li>
              <li><strong className="text-slate-100">Study drawdowns</strong> &mdash; Critical for understanding risk</li>
              <li><strong className="text-slate-100">Explore technical indicators</strong> &mdash; RSI and MACD for momentum analysis</li>
              <li><strong className="text-slate-100">Graduate to options</strong> &mdash; Only after solid stock fundamentals</li>
            </ol>
            <p className="mt-3"><strong className="text-slate-100">Beginner Resources:</strong></p>
            <div className="space-y-1.5">
              <a href="https://www.investopedia.com/stocks-4427785" target="_blank" rel="noopener noreferrer" className="ref-link">Investopedia: Stock Basics</a>
              <a href="https://www.khanacademy.org/economics-finance-domain/core-finance/stock-and-bonds" target="_blank" rel="noopener noreferrer" className="ref-link">Khan Academy: Stocks and Bonds</a>
              <a href="https://www.investor.gov/introduction-investing" target="_blank" rel="noopener noreferrer" className="ref-link">SEC: Introduction to Investing</a>
            </div>
          </div>
        </details>

        {/* ═══════════════════════════════════════════════════════════════════ */}
        {/* 2. STOCK ANALYSIS PAGE */}
        {/* ═══════════════════════════════════════════════════════════════════ */}
        <div className="section-divider" />
        <h2 className="text-2xl font-bold text-slate-100 mb-2">2. Stock Analysis Page</h2>
        <p className="text-sm text-slate-400 mb-5 italic">Go to Stock Analysis to use these features.</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Gradient Coloring */}
          <div>
            <h3 className="text-lg font-semibold text-slate-100 mb-3">Gradient Coloring</h3>
            <div className="text-sm text-slate-300 leading-relaxed space-y-3">
              <p>
                The price chart uses a color gradient to show how far the current price is from the rolling high.
                This visualization technique helps you instantly identify the stock's position relative to recent
                performance &mdash; a key concept in <strong className="text-slate-100">relative strength analysis</strong>.
              </p>
              <p><strong className="text-slate-100">Color Interpretation:</strong></p>
              <ul className="space-y-1.5 ml-2">
                <li><span className="inline-block w-3 h-3 rounded-full bg-emerald-500 mr-2 align-middle" /><strong className="text-emerald-400">Green shades</strong> = Price is at or near the rolling high (strong relative position)</li>
                <li><span className="inline-block w-3 h-3 rounded-full bg-red-500 mr-2 align-middle" /><strong className="text-red-400">Red shades</strong> = Price is below the rolling high (pullback/correction territory)</li>
                <li>Color intensity = Magnitude of deviation (darker = further from high)</li>
              </ul>
              <p><strong className="text-slate-100">What this reveals:</strong></p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>New highs and breakouts (bright green) &mdash; Potential momentum continuation</li>
                <li>Pullbacks (light red) &mdash; Possible buying opportunities in uptrends</li>
                <li>Major drawdowns (dark red) &mdash; Elevated risk, but also potential value if fundamentals are intact</li>
              </ul>
              <p>
                <strong className="text-slate-100">Why this matters:</strong> Institutional investors constantly monitor
                "distance from highs" as a risk metric. A stock 5% from its high behaves very differently from one
                30% from its high.
              </p>
            </div>

            <details className="mt-4">
              <summary>Learn More: Relative Strength & Momentum</summary>
              <div className="details-content space-y-3">
                <p><strong className="text-slate-100">Concept:</strong> Relative strength measures how a stock performs compared to a benchmark (here, its own recent high). Stocks showing relative strength during market weakness often outperform when markets recover.</p>
                <p><strong className="text-slate-100">Beginner Reading:</strong></p>
                <div className="space-y-1.5">
                  <a href="https://www.investopedia.com/terms/r/relativestrength.asp" target="_blank" rel="noopener noreferrer" className="ref-link">Investopedia: Relative Strength</a>
                  <a href="https://school.stockcharts.com/doku.php?id=technical_indicators:relative_strength" target="_blank" rel="noopener noreferrer" className="ref-link">StockCharts: Relative Strength Explained</a>
                </div>
                <p><strong className="text-slate-100">Academic Foundation:</strong></p>
                <div className="space-y-1.5">
                  <a href="https://www.jstor.org/stable/2328882" target="_blank" rel="noopener noreferrer" className="ref-link">Jegadeesh & Titman (1993): "Returns to Buying Winners and Selling Losers" &mdash; The seminal paper on momentum investing</a>
                  <a href="https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12021" target="_blank" rel="noopener noreferrer" className="ref-link">Asness et al. (2013): "Value and Momentum Everywhere"</a>
                </div>
              </div>
            </details>
          </div>

          {/* Rolling High Lookback */}
          <div>
            <h3 className="text-lg font-semibold text-slate-100 mb-3">Rolling High Lookback</h3>
            <div className="text-sm text-slate-300 leading-relaxed space-y-3">
              <p>
                The <strong className="text-slate-100">Rolling High Lookback</strong> setting controls the window for
                calculating the reference high. This is analogous to how professional traders set different timeframes
                for their analysis.
              </p>
              <p><strong className="text-slate-100">Lookback Period Guidelines:</strong></p>
              <ul className="list-disc list-inside space-y-1.5 ml-2">
                <li><strong className="text-slate-100">Short lookback (5-30 days):</strong> Captures minor pullbacks, good for swing trading. More signals, but also more noise.</li>
                <li><strong className="text-slate-100">Medium lookback (30-60 days):</strong> Balanced view showing intermediate trends. Popular among position traders.</li>
                <li><strong className="text-slate-100">Long lookback (60-200 days):</strong> Reveals major trends and significant drawdowns. Used by longer-term investors and for risk assessment.</li>
              </ul>
              <p>
                <strong className="text-slate-100">Practical Example:</strong> With a 30-day lookback, if a stock hit $100
                two weeks ago but trades at $95 today, it shows as 5% below the rolling high (light red). If the 30-day
                high was $120, that same $95 would show as 21% below (darker red).
              </p>
              <p className="text-indigo-300">
                <strong>Pro Tip:</strong> Compare different lookback periods to understand how the stock behaves across
                timeframes. Stocks that are near highs on multiple timeframes show strong momentum.
              </p>
            </div>

            <details className="mt-4">
              <summary>Learn More: Time Horizons in Technical Analysis</summary>
              <div className="details-content space-y-3">
                <p><strong className="text-slate-100">Concept:</strong> Different investors use different time horizons. Day traders might use 5-day lookbacks, while pension funds might use 200-day periods. Understanding your time horizon is crucial for interpreting any technical indicator.</p>
                <p><strong className="text-slate-100">Beginner Reading:</strong></p>
                <div className="space-y-1.5">
                  <a href="https://www.investopedia.com/articles/trading/11/trading-time-frames.asp" target="_blank" rel="noopener noreferrer" className="ref-link">Investopedia: Trading Time Frames</a>
                  <a href="https://www.cmegroup.com/education/courses/introduction-to-technical-analysis/time-frames.html" target="_blank" rel="noopener noreferrer" className="ref-link">CME Group: Time Frames for Trading</a>
                </div>
                <p><strong className="text-slate-100">Academic Foundation:</strong></p>
                <a href="https://www.jstor.org/stable/222481" target="_blank" rel="noopener noreferrer" className="ref-link">Lo, Mamaysky & Wang (2000): "Foundations of Technical Analysis" &mdash; Rigorous statistical foundation for pattern recognition across timeframes</a>
              </div>
            </details>
          </div>
        </div>

        {/* Volume */}
        <div className="text-sm text-slate-300 leading-relaxed mb-4">
          <p>
            <strong className="text-slate-100">Volume Bars:</strong> The lower section shows trading volume. Volume is
            the "fuel" of price movements &mdash; higher volume during price moves indicates stronger conviction and often
            more sustainable trends. Professional traders always confirm price signals with volume.
          </p>
        </div>

        <details className="mb-6">
          <summary>Learn More: Volume Analysis</summary>
          <div className="details-content space-y-3">
            <p><strong className="text-slate-100">Why Volume Matters:</strong></p>
            <p>Volume represents the number of shares traded. High volume indicates high interest and conviction. Key volume principles:</p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li>Price rise + high volume = Strong bullish signal</li>
              <li>Price rise + low volume = Weak move, possible reversal</li>
              <li>Price drop + high volume = Strong selling pressure</li>
              <li>Price drop + low volume = Lack of conviction in sellers</li>
            </ul>
            <p><strong className="text-slate-100">Beginner Reading:</strong></p>
            <div className="space-y-1.5">
              <a href="https://www.investopedia.com/terms/v/volume.asp" target="_blank" rel="noopener noreferrer" className="ref-link">Investopedia: Volume Analysis</a>
              <a href="https://school.stockcharts.com/doku.php?id=technical_indicators:volume" target="_blank" rel="noopener noreferrer" className="ref-link">StockCharts: Volume Indicators</a>
            </div>
            <p><strong className="text-slate-100">Academic Foundation:</strong></p>
            <div className="space-y-1.5">
              <a href="https://www.jstor.org/stable/2330874" target="_blank" rel="noopener noreferrer" className="ref-link">Karpoff (1987): "The Relation Between Price Changes and Trading Volume"</a>
              <a href="https://academic.oup.com/qje/article-abstract/108/4/905/1881846" target="_blank" rel="noopener noreferrer" className="ref-link">Campbell, Grossman & Wang (1993): "Trading Volume and Serial Correlation in Stock Returns"</a>
            </div>
          </div>
        </details>

        {/* ═══════════════════════════════════════════════════════════════════ */}
        {/* 3. DRAWDOWN ANALYSIS */}
        {/* ═══════════════════════════════════════════════════════════════════ */}
        <div className="section-divider" />
        <h2 className="text-2xl font-bold text-slate-100 mb-4">3. Drawdown Analysis Tab</h2>

        <div className="text-sm text-slate-300 leading-relaxed space-y-3 mb-6">
          <p>
            Drawdown analysis is one of the most important risk management tools used by professional investors. A{' '}
            <strong className="text-slate-100">drawdown</strong> measures the peak-to-trough decline before a new peak is
            achieved. Understanding drawdowns helps you:
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Assess realistic downside risk (not just volatility)</li>
            <li>Set appropriate position sizes</li>
            <li>Maintain psychological resilience during market declines</li>
          </ul>
          <p><strong className="text-slate-100">Key Metrics Explained:</strong></p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="metric-explain">
            <div className="metric-val">ATH</div>
            <div className="metric-lbl">All-Time High</div>
            <p className="text-xs text-slate-400 mt-2">
              The highest price reached in the selected period. This is your reference point.
              Being aware of the ATH helps contextualize current prices.
            </p>
          </div>
          <div className="metric-explain">
            <div className="metric-val text-red-400">-12%</div>
            <div className="metric-lbl">Current Drawdown</div>
            <p className="text-xs text-slate-400 mt-2">
              How far below the ATH the current price is. A stock at $132 with ATH of $150
              has a 12% drawdown. This tells you how much recovery is needed to break even.
            </p>
          </div>
          <div className="metric-explain">
            <div className="metric-val text-red-400">-35%</div>
            <div className="metric-lbl">Max Drawdown</div>
            <p className="text-xs text-slate-400 mt-2">
              The largest peak-to-trough decline in the period. This is the worst-case
              historical scenario &mdash; crucial for stress testing your portfolio.
            </p>
          </div>
        </div>

        <div className="text-sm text-slate-300 leading-relaxed space-y-3 mb-5">
          <p>
            <strong className="text-slate-100">Underwater Chart:</strong> Shows how long the stock spent below its previous
            high. Longer "underwater" periods indicate extended recovery times. For example, the S&P 500 took 7 years to
            recover from the 2000 dot-com crash. Understanding typical recovery times helps set realistic expectations.
          </p>
          <p>
            <strong className="text-slate-100">Recovery Statistics:</strong>
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Average time to recover from drawdowns of various depths</li>
            <li>Number of drawdown events (how often do 10%+ drops occur?)</li>
            <li>Distribution of drawdown depths (most drawdowns are small, but tail events matter)</li>
          </ul>
        </div>

        <details className="mb-6">
          <summary>Learn More: Drawdown Analysis</summary>
          <div className="details-content space-y-3">
            <p><strong className="text-slate-100">Why Drawdowns Matter More Than Volatility:</strong></p>
            <p>
              Volatility (standard deviation) treats upside and downside equally. Drawdowns focus specifically on
              losses &mdash; what actually hurts investors. A fund with 20% annual volatility might have very different
              drawdown profiles depending on how that volatility is distributed.
            </p>

            <p><strong className="text-slate-100">Key Insight:</strong> The math of losses is asymmetric. A 50% loss requires a 100% gain to recover. A 75% loss requires a 300% gain. This is why limiting drawdowns is crucial.</p>

            <div className="overflow-x-auto mt-3">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Drawdown</th>
                    <th>Gain Needed to Recover</th>
                  </tr>
                </thead>
                <tbody>
                  <tr><td>-10%</td><td>+11.1%</td></tr>
                  <tr><td>-20%</td><td>+25.0%</td></tr>
                  <tr><td>-30%</td><td>+42.9%</td></tr>
                  <tr><td>-50%</td><td>+100.0%</td></tr>
                  <tr><td>-75%</td><td>+300.0%</td></tr>
                </tbody>
              </table>
            </div>

            <div className="warning-box mt-4">
              <p className="text-sm">
                <strong className="text-amber-400">Survivorship Bias Warning:</strong> This dashboard analyzes stocks that
                are currently prominent and publicly traded (e.g., AAPL, MSFT, NVDA). These are survivors &mdash; companies
                that recovered from drawdowns and thrived. Many stocks experience drawdowns they never recover from (e.g.,
                Enron, Lehman Brothers, Bed Bath & Beyond). Historical drawdown recovery statistics from surviving companies
                overstate the probability of recovery in general. Always consider the possibility that a drawdown may be permanent.
              </p>
            </div>

            <RefLinks topic="drawdown" />
          </div>
        </details>

        {/* ═══════════════════════════════════════════════════════════════════ */}
        {/* 4. PUT OPTIONS EDUCATION */}
        {/* ═══════════════════════════════════════════════════════════════════ */}
        <div className="section-divider" />
        <h2 className="text-2xl font-bold text-slate-100 mb-4">4. Put Options Education</h2>

        <div className="info-box mb-5">
          <p className="text-sm text-slate-200">
            <strong>Go to the <Link to="/options" className="text-purple-400 hover:text-purple-300 underline">Put Options page</Link></strong> for
            a comprehensive put options education dashboard with real historical options data across multiple tickers
            (AAPL, MSFT, TSLA, NVDA, AMD, and more).
          </p>
        </div>

        <div className="warning-box mb-5">
          <p className="text-sm">
            <strong className="text-amber-400">Risk Disclaimer:</strong> Options trading involves substantial risk of
            loss and is not suitable for all investors. <strong className="text-slate-100">Buying</strong> options (puts
            or calls) risks the entire premium paid. <strong className="text-slate-100">Selling</strong> options can expose
            you to losses far exceeding your initial margin &mdash; potentially unlimited for uncovered positions. This
            dashboard is for <strong className="text-slate-100">educational purposes only</strong>. Always:
          </p>
          <ul className="list-disc list-inside mt-2 text-sm space-y-1">
            <li>Understand the product before trading</li>
            <li>Never risk more than you can afford to lose</li>
            <li>Consider consulting a registered investment advisor</li>
            <li>Paper trade first to gain experience</li>
          </ul>
        </div>

        <div className="text-sm text-slate-300 leading-relaxed space-y-3 mb-5">
          <p><strong className="text-slate-100">What is a Put Option?</strong></p>
          <p>
            A put option gives you the right (but not obligation) to <strong className="text-slate-100">sell</strong> a stock
            at a specific price (strike price) before a specific date (expiration). You pay a premium for this right.
          </p>

          <p><strong className="text-slate-100">Why Learn About Puts?</strong></p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li><strong className="text-slate-100">Portfolio Protection:</strong> Puts act like insurance against stock declines</li>
            <li><strong className="text-slate-100">Profit from Declines:</strong> Bearish speculation without shorting</li>
            <li><strong className="text-slate-100">Income Generation:</strong> Advanced strategies like cash-secured puts (note: this involves <em>selling</em> puts, which carries different and greater risk than buying them)</li>
            <li><strong className="text-slate-100">Risk Management:</strong> Understanding options helps understand market dynamics</li>
          </ul>

          <p><strong className="text-slate-100">Key Concept &mdash; Moneyness:</strong></p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li><strong className="text-slate-100">In-the-Money (ITM):</strong> Strike price is above the current stock price (for puts). The option has intrinsic value.</li>
            <li><strong className="text-slate-100">At-the-Money (ATM):</strong> Strike price equals (or is very near) the current stock price.</li>
            <li><strong className="text-slate-100">Out-of-the-Money (OTM):</strong> Strike price is below the current stock price (for puts). The option has no intrinsic value &mdash; only time/extrinsic value.</li>
          </ul>

          <p><strong className="text-slate-100">What You'll Learn:</strong></p>
          <ol className="list-decimal list-inside space-y-1 ml-2">
            <li><strong className="text-slate-100">Fundamentals:</strong> Strike price, premium, expiration, moneyness, intrinsic vs. extrinsic value</li>
            <li><strong className="text-slate-100">Payoff Diagrams:</strong> Interactive visualizations of profit/loss at expiration</li>
            <li><strong className="text-slate-100">The Greeks:</strong> Delta, Gamma, Theta, Vega, Rho &mdash; how options prices change</li>
            <li><strong className="text-slate-100">Risk Calculators:</strong> Break-even analysis, position sizing, P/L scenarios</li>
            <li><strong className="text-slate-100">Option Chains:</strong> How to read and interpret real market data</li>
          </ol>
        </div>

        <details className="mb-4">
          <summary>Learn More: Put Options</summary>
          <div className="details-content">
            <RefLinks topic="options" />
          </div>
        </details>

        <details className="mb-6">
          <summary>Learn More: The Greeks (Delta, Theta, Gamma, Vega)</summary>
          <div className="details-content space-y-3">
            <p>The "Greeks" measure how option prices change in response to various factors:</p>

            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Greek</th>
                    <th>Measures</th>
                    <th>Intuition</th>
                  </tr>
                </thead>
                <tbody>
                  <tr><td><strong className="text-slate-100">Delta</strong></td><td>Price sensitivity to stock movement</td><td>"How much does my option move if the stock moves $1?"</td></tr>
                  <tr><td><strong className="text-slate-100">Gamma</strong></td><td>Rate of change of delta</td><td>"How stable is my delta?" (acceleration)</td></tr>
                  <tr><td><strong className="text-slate-100">Theta</strong></td><td>Time decay</td><td>"How much value do I lose each day?"</td></tr>
                  <tr><td><strong className="text-slate-100">Vega</strong></td><td>Volatility sensitivity</td><td>"How much does my option move if volatility changes?"</td></tr>
                  <tr><td><strong className="text-slate-100">Rho</strong></td><td>Interest rate sensitivity</td><td>"How does my option react to rate changes?"</td></tr>
                </tbody>
              </table>
            </div>

            <p className="mt-3"><strong className="text-slate-100">Practical Example:</strong></p>
            <p>
              A put with Delta = -0.40 will gain approximately $0.40 for every $1 the stock drops. But Theta = -0.05 means
              you lose $5 per day (for 1 contract = 100 shares) just from time passing.
            </p>

            <p>
              <strong className="text-slate-100">Important: Theta is non-linear.</strong> Time decay accelerates sharply in
              the final 30-45 days before expiration. An option 90 days out loses time value slowly, but the same option with
              15 days left decays much faster per day. This is why many options strategies focus on the final month of an option's life.
            </p>

            <RefLinks topic="greeks" />
          </div>
        </details>

        {/* ═══════════════════════════════════════════════════════════════════ */}
        {/* 5. TECHNICAL INDICATORS */}
        {/* ═══════════════════════════════════════════════════════════════════ */}
        <div className="section-divider" />
        <h2 className="text-2xl font-bold text-slate-100 mb-4">5. Technical Indicators</h2>

        <div className="text-sm text-slate-300 leading-relaxed space-y-2 mb-5">
          <p>
            Technical indicators require an Alpha Vantage API key for real-time data. Get a free key at{' '}
            <a href="https://www.alphavantage.co/support/#api-key" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 underline">alphavantage.co</a>{' '}
            (free tier: 5 calls/minute, 500 calls/day).
          </p>
          <p><strong className="text-slate-100">What Are Technical Indicators?</strong></p>
          <p>
            Technical indicators are mathematical calculations based on price, volume, or open interest. They help
            identify trends, momentum, volatility, and potential reversal points. While no indicator is perfect, they
            provide objective frameworks for analysis.
          </p>
        </div>

        <Tabs defaultTab={0}>
          {/* RSI */}
          <Tab label="RSI">
            <div className="card-lg">
              <h3 className="text-lg font-semibold text-slate-100 mb-3">RSI (Relative Strength Index)</h3>
              <div className="text-sm text-slate-300 leading-relaxed space-y-3">
                <p><strong className="text-slate-100">Creator:</strong> J. Welles Wilder Jr. (1978)</p>
                <p><strong className="text-slate-100">What it measures:</strong> Momentum &mdash; specifically, the speed and magnitude of recent price changes to evaluate overbought or oversold conditions.</p>
                <p><strong className="text-slate-100">The Math (Simplified):</strong></p>
                <p className="font-mono text-xs bg-slate-800/60 p-2 rounded">RSI = 100 - (100 / (1 + RS)), where RS = Average Gain / Average Loss over N periods</p>
                <p><strong className="text-slate-100">Standard Interpretation:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong className="text-slate-100">Above 70:</strong> Potentially overbought &mdash; the stock has risen quickly and may be due for a pullback</li>
                  <li><strong className="text-slate-100">Below 30:</strong> Potentially oversold &mdash; the stock has fallen quickly and may be due for a bounce</li>
                  <li><strong className="text-slate-100">50 level:</strong> Neutral momentum &mdash; often acts as support/resistance</li>
                </ul>
                <p><strong className="text-slate-100">Advanced Uses:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong className="text-slate-100">Divergences:</strong> Price makes new high but RSI doesn't = bearish divergence (weakening momentum)</li>
                  <li><strong className="text-slate-100">Failure Swings:</strong> RSI breaks above 70, pulls back, then fails to exceed prior RSI high = reversal signal</li>
                  <li><strong className="text-slate-100">Trend Confirmation:</strong> In strong uptrends, RSI tends to stay between 40-80; in downtrends, 20-60</li>
                </ul>
                <p><strong className="text-slate-100">Limitations:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Can stay overbought/oversold for extended periods in strong trends</li>
                  <li>Works better in ranging markets than trending markets</li>
                  <li>Different assets may require different thresholds (crypto often uses 80/20)</li>
                </ul>
              </div>
              <details className="mt-4">
                <summary>References: RSI</summary>
                <div className="details-content"><RefLinks topic="rsi" /></div>
              </details>
            </div>
          </Tab>

          {/* MACD */}
          <Tab label="MACD">
            <div className="card-lg">
              <h3 className="text-lg font-semibold text-slate-100 mb-3">MACD (Moving Average Convergence Divergence)</h3>
              <div className="text-sm text-slate-300 leading-relaxed space-y-3">
                <p><strong className="text-slate-100">Creator:</strong> Gerald Appel (1970s)</p>
                <p><strong className="text-slate-100">What it measures:</strong> Trend direction, momentum, and potential trend reversals by showing the relationship between two moving averages of price.</p>
                <p><strong className="text-slate-100">Components:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong className="text-slate-100">MACD Line:</strong> 12-period EMA minus 26-period EMA (shows momentum)</li>
                  <li><strong className="text-slate-100">Signal Line:</strong> 9-period EMA of the MACD line (smoothed trigger)</li>
                  <li><strong className="text-slate-100">Histogram:</strong> MACD Line minus Signal Line (visualizes the difference)</li>
                </ul>
                <p><strong className="text-slate-100">Standard Interpretation:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong className="text-slate-100">MACD crosses above Signal Line:</strong> Bullish signal &mdash; momentum turning positive</li>
                  <li><strong className="text-slate-100">MACD crosses below Signal Line:</strong> Bearish signal &mdash; momentum turning negative</li>
                  <li><strong className="text-slate-100">Histogram increasing:</strong> Momentum strengthening in current direction</li>
                  <li><strong className="text-slate-100">Zero line crossover:</strong> MACD crossing zero indicates trend change</li>
                </ul>
                <p><strong className="text-slate-100">Limitations:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Lagging indicator (based on moving averages)</li>
                  <li>Can generate false signals in choppy/ranging markets</li>
                  <li>Default parameters (12, 26, 9) may not suit all assets or timeframes</li>
                </ul>
              </div>
              <details className="mt-4">
                <summary>References: MACD</summary>
                <div className="details-content"><RefLinks topic="macd" /></div>
              </details>
            </div>
          </Tab>

          {/* Bollinger Bands */}
          <Tab label="Bollinger Bands">
            <div className="card-lg">
              <h3 className="text-lg font-semibold text-slate-100 mb-3">Bollinger Bands</h3>
              <div className="text-sm text-slate-300 leading-relaxed space-y-3">
                <p><strong className="text-slate-100">Creator:</strong> John Bollinger (1980s)</p>
                <p><strong className="text-slate-100">What it measures:</strong> Volatility and relative price levels. The bands expand during volatile periods and contract during calm periods.</p>
                <p><strong className="text-slate-100">Components:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong className="text-slate-100">Middle Band:</strong> 20-period simple moving average (the trend)</li>
                  <li><strong className="text-slate-100">Upper Band:</strong> Middle band + 2 standard deviations</li>
                  <li><strong className="text-slate-100">Lower Band:</strong> Middle band - 2 standard deviations</li>
                </ul>
                <p><strong className="text-slate-100">Statistical Foundation:</strong></p>
                <p>
                  Under a normal distribution, ~95% of observations fall within 2 standard deviations. However, stock returns
                  exhibit <strong className="text-slate-100">fat tails</strong> (leptokurtosis) &mdash; extreme moves occur significantly
                  more often than a normal distribution predicts. In practice, prices breach the bands more frequently than 5% of
                  the time. Bollinger Bands are best understood as a relative volatility framework, not a probabilistic prediction interval.
                </p>
                <p><strong className="text-slate-100">Standard Interpretation:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong className="text-slate-100">Price near upper band:</strong> Relatively high (not necessarily overbought)</li>
                  <li><strong className="text-slate-100">Price near lower band:</strong> Relatively low (not necessarily oversold)</li>
                  <li><strong className="text-slate-100">Bands widening:</strong> Volatility increasing &mdash; often follows breakouts</li>
                  <li><strong className="text-slate-100">Bands narrowing (squeeze):</strong> Volatility decreasing &mdash; often precedes big moves</li>
                </ul>
                <p><strong className="text-slate-100">Limitations:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Not a standalone system &mdash; best combined with other indicators</li>
                  <li>Band touches are not automatic buy/sell signals</li>
                  <li>Standard 20-period, 2-std may not suit all markets</li>
                </ul>
              </div>
              <details className="mt-4">
                <summary>References: Bollinger Bands</summary>
                <div className="details-content"><RefLinks topic="bollinger" /></div>
              </details>
            </div>
          </Tab>

          {/* Moving Averages */}
          <Tab label="Moving Averages">
            <div className="card-lg">
              <h3 className="text-lg font-semibold text-slate-100 mb-3">Moving Averages (SMA & EMA)</h3>
              <div className="text-sm text-slate-300 leading-relaxed space-y-3">
                <p><strong className="text-slate-100">What they are:</strong> The foundation of most technical indicators. Moving averages smooth price data to identify trends by filtering out short-term noise.</p>

                <p><strong className="text-slate-100">Types:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong className="text-slate-100">SMA (Simple Moving Average):</strong> Equal weight to all prices in the period. Formula: Sum of last N prices / N</li>
                  <li><strong className="text-slate-100">EMA (Exponential Moving Average):</strong> More weight to recent prices, reacts faster. Uses a multiplier: 2 / (N + 1)</li>
                </ul>

                <p><strong className="text-slate-100">Common Periods and Their Uses:</strong></p>
                <div className="overflow-x-auto">
                  <table className="data-table">
                    <thead>
                      <tr><th>Period</th><th>Timeframe</th><th>Common Use</th></tr>
                    </thead>
                    <tbody>
                      <tr><td>10-day</td><td>Very short</td><td>Short-term swing trading, momentum</td></tr>
                      <tr><td>20-day</td><td>Short</td><td>Swing trading, Bollinger middle band</td></tr>
                      <tr><td>50-day</td><td>Medium</td><td>Institutional benchmark, trend confirmation</td></tr>
                      <tr><td>100-day</td><td>Medium-long</td><td>Less common, between 50 and 200</td></tr>
                      <tr><td>200-day</td><td>Long</td><td>Institutional benchmark, bull/bear market definition</td></tr>
                    </tbody>
                  </table>
                </div>

                <p><strong className="text-slate-100">Key Signals:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong className="text-slate-100">Price above MA:</strong> Generally bullish &mdash; price is above average</li>
                  <li><strong className="text-slate-100">Price below MA:</strong> Generally bearish &mdash; price is below average</li>
                  <li><strong className="text-slate-100">Golden Cross:</strong> 50-day crosses above 200-day &mdash; traditionally considered bullish</li>
                  <li><strong className="text-slate-100">Death Cross:</strong> 50-day crosses below 200-day &mdash; traditionally considered bearish</li>
                </ul>

                <p><strong className="text-slate-100">Note:</strong> Academic evidence for Golden/Death Cross reliability is mixed. These signals are lagging by nature, and many studies suggest their predictive power is limited after accounting for transaction costs. They are best used as trend context, not trade triggers.</p>

                <p><strong className="text-slate-100">Why 50 and 200 Day?</strong></p>
                <p>
                  50 trading days = ~10 weeks (~2.5 months) captures intermediate trends, while 200 trading days = ~40 weeks
                  (~10 months) captures long-term trends. These periods became institutional standards partly through convention &mdash;
                  many algorithms and fund mandates reference them, creating self-fulfilling support/resistance levels.
                </p>

                <p><strong className="text-slate-100">Limitations:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Lagging indicators by definition</li>
                  <li>Whipsaws in choppy markets generate false signals</li>
                  <li>No single MA period works for all stocks or market conditions</li>
                </ul>
              </div>
              <details className="mt-4">
                <summary>References: Moving Averages</summary>
                <div className="details-content"><RefLinks topic="moving_averages" /></div>
              </details>
            </div>
          </Tab>
        </Tabs>

        {/* ═══════════════════════════════════════════════════════════════════ */}
        {/* 6. LIMITATIONS OF TECHNICAL ANALYSIS */}
        {/* ═══════════════════════════════════════════════════════════════════ */}
        <div className="section-divider" />
        <h2 className="text-2xl font-bold text-slate-100 mb-4">6. What Technical Analysis Can't Do</h2>

        <div className="text-sm text-slate-300 leading-relaxed space-y-3 mb-6">
          <p>Technical analysis is a useful framework, but it has well-documented limitations:</p>
          <ul className="list-disc list-inside space-y-2 ml-2">
            <li>
              <strong className="text-slate-100">No predictive guarantee:</strong> Patterns and indicators describe past behavior.
              Markets are influenced by news, earnings, policy changes, and other events that no chart can anticipate.
            </li>
            <li>
              <strong className="text-slate-100">Efficient Market Hypothesis (EMH):</strong> Academic research suggests that publicly
              available information is rapidly reflected in prices. Under strong-form EMH, technical analysis provides no edge.
              Even under weaker forms, consistent profits from technical signals alone are debated.
            </li>
            <li>
              <strong className="text-slate-100">Data mining risk:</strong> With enough indicators, timeframes, and parameters, you
              can find "patterns" in random data. Many published strategies fail out-of-sample.
            </li>
            <li>
              <strong className="text-slate-100">Self-fulfilling vs. self-defeating:</strong> Popular signals (e.g., 200-day MA) may
              work because many traders act on them &mdash; but widespread adoption can also erode their effectiveness.
            </li>
            <li>
              <strong className="text-slate-100">No substitute for fundamentals:</strong> Technicals show <em>what</em> is happening
              to price; they don't explain <em>why</em>. A stock can look bullish on every indicator and still collapse on an
              earnings miss.
            </li>
          </ul>
          <p>
            <strong className="text-slate-100">Bottom line:</strong> Use technical indicators as one input among many &mdash; not as
            a decision-making system in isolation.
          </p>
        </div>

        {/* ═══════════════════════════════════════════════════════════════════ */}
        {/* 7. TIPS & FAQ */}
        {/* ═══════════════════════════════════════════════════════════════════ */}
        <div className="section-divider" />
        <h2 className="text-2xl font-bold text-slate-100 mb-4">7. Tips & FAQ</h2>

        <h3 className="text-lg font-semibold text-slate-100 mb-3">Best Practices</h3>
        <div className="text-sm text-slate-300 leading-relaxed space-y-3 mb-6">
          <p><strong className="text-slate-100">For Analysis:</strong></p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li><strong className="text-slate-100">Start with longer timeframes</strong> (3+ years) to understand historical patterns before zooming in</li>
            <li><strong className="text-slate-100">Adjust the lookback period</strong> based on your investment horizon (longer for investing, shorter for trading)</li>
            <li><strong className="text-slate-100">Compare multiple stocks</strong> to understand relative performance within sectors</li>
            <li><strong className="text-slate-100">Use technical indicators for confirmation</strong>, not as standalone signals</li>
            <li><strong className="text-slate-100">Always consider fundamentals</strong> &mdash; technicals show what IS happening, fundamentals explain WHY</li>
          </ul>

          <p><strong className="text-slate-100">For Learning:</strong></p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li><strong className="text-slate-100">Paper trade first</strong> &mdash; Practice with simulated money before risking real capital</li>
            <li><strong className="text-slate-100">Keep a trading journal</strong> &mdash; Document your decisions and review them</li>
            <li><strong className="text-slate-100">Study mistakes</strong> &mdash; Losses teach more than wins if you analyze them honestly</li>
            <li><strong className="text-slate-100">Be patient</strong> &mdash; Skill develops over months and years, not days</li>
          </ul>
        </div>

        <h3 className="text-lg font-semibold text-slate-100 mb-3">Frequently Asked Questions</h3>

        <div className="space-y-3 mb-8">
          <details>
            <summary>Why is my stock showing red even though it's up today?</summary>
            <div className="details-content space-y-2">
              <p>The color reflects the distance from the <strong className="text-slate-100">rolling high</strong>, not the daily change.</p>
              <p>
                <strong className="text-slate-100">Example:</strong> A stock was at $100 two weeks ago (the rolling high), dropped
                to $90, and today rose from $90 to $93. It's up 3.3% today (bullish daily move) but still 7% below its rolling
                high (showing red in the gradient).
              </p>
              <p>
                This distinction is important: a stock can have positive daily momentum while still being in a pullback/correction
                relative to its recent highs.
              </p>
            </div>
          </details>

          <details>
            <summary>What's the difference between Single Stock and Compare modes?</summary>
            <div className="details-content space-y-2">
              <ul className="list-disc list-inside space-y-1.5">
                <li><strong className="text-slate-100">Single Stock:</strong> Deep-dive analysis of one stock with all features (drawdown analysis, put options learning, full technical indicators)</li>
                <li><strong className="text-slate-100">Compare Stocks:</strong> Side-by-side comparison of up to 4 stocks &mdash; great for:
                  <ul className="list-disc list-inside ml-5 mt-1 space-y-0.5">
                    <li>Comparing companies in the same sector (AAPL vs MSFT vs GOOGL)</li>
                    <li>Evaluating relative strength (which stock is holding up better?)</li>
                    <li>Sector rotation analysis (tech vs financials vs energy)</li>
                  </ul>
                </li>
              </ul>
            </div>
          </details>

          <details>
            <summary>How do I get technical indicators to work?</summary>
            <div className="details-content space-y-2">
              <ol className="list-decimal list-inside space-y-1.5">
                <li>Get a free API key from <a href="https://www.alphavantage.co/support/#api-key" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 underline">Alpha Vantage</a></li>
                <li>Enter the key in the Technical Indicators section</li>
                <li>Select your desired indicators</li>
                <li>Click Load Data</li>
              </ol>
              <p className="mt-2"><strong className="text-slate-100">Note:</strong> Free tier limits: 5 API calls per minute, 500 API calls per day.</p>
              <p>If you hit rate limits, wait a minute and try again. For heavy usage, consider their premium plans or alternative data providers (Yahoo Finance, IEX Cloud, Polygon.io).</p>
            </div>
          </details>

          <details>
            <summary>Can I use this for real trading decisions?</summary>
            <div className="details-content space-y-2">
              <p>This dashboard is for <strong className="text-slate-100">educational and informational purposes only</strong>. It should not be considered financial advice.</p>
              <p><strong className="text-slate-100">Before trading real money:</strong></p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Understand the risks involved in any investment</li>
                <li>Do your own research beyond what any dashboard shows</li>
                <li>Consider consulting a registered investment advisor or financial professional</li>
                <li>Paper trade to build experience without risking capital</li>
                <li>Never invest more than you can afford to lose</li>
                <li>Understand that past performance does not guarantee future results</li>
              </ul>
              <p className="mt-2"><strong className="text-slate-100">For options specifically:</strong></p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Options involve substantial risk including the loss of all invested capital</li>
                <li>Options are not suitable for all investors</li>
                <li>Ensure you understand the characteristics and risks of options before trading</li>
                <li>Read the Options Disclosure Document (ODD) available from your broker</li>
              </ul>
            </div>
          </details>

          <details>
            <summary>Where does the options data come from?</summary>
            <div className="details-content space-y-2">
              <p>
                The Put Options page uses millions of historical options contracts across multiple tickers including
                AAPL, MSFT, GOOGL, AMZN, META, TSLA, NFLX, NVDA, AMD, and more. Data spans from as early as 2010
                to present and includes:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Daily snapshots of available put and call options</li>
                <li>Strike prices, expiration dates, bid/ask prices</li>
                <li>Volume and open interest</li>
                <li>Implied volatility and Greeks (Delta, Gamma, Theta, Vega, Rho)</li>
              </ul>
              <p className="mt-2"><strong className="text-slate-100">Why multiple tickers?</strong></p>
              <p>Different stocks exhibit different options characteristics:</p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li><strong className="text-slate-100">High-beta names</strong> (TSLA, NVDA) = higher IV, wider premium swings</li>
                <li><strong className="text-slate-100">Mega-caps</strong> (AAPL, MSFT) = deep liquidity, tighter spreads</li>
                <li><strong className="text-slate-100">Recent IPOs</strong> (ARM, CRWV) = shorter history, different dynamics</li>
                <li>Comparing across tickers builds deeper intuition about options pricing</li>
              </ul>
            </div>
          </details>
        </div>

        {/* ─── Footer ─── */}
        <div className="section-divider" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-8">
          <p className="text-sm text-slate-400 italic">
            Navigate to{' '}
            <Link to="/stock" className="text-indigo-400 hover:text-indigo-300 underline">Stock Analysis</Link> or{' '}
            <Link to="/options" className="text-purple-400 hover:text-purple-300 underline">Put Options</Link> using
            the navigation bar.
          </p>
          <div className="text-sm text-slate-400">
            <strong className="text-slate-300">Additional Resources:</strong>
            <div className="space-y-1 mt-1">
              <a href="https://www.investor.gov/" target="_blank" rel="noopener noreferrer" className="ref-link">SEC Investor Education</a>
              <a href="https://www.finra.org/investors" target="_blank" rel="noopener noreferrer" className="ref-link">FINRA Investor Tools</a>
              <a href="https://fred.stlouisfed.org/" target="_blank" rel="noopener noreferrer" className="ref-link">Federal Reserve Economic Data (FRED)</a>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
