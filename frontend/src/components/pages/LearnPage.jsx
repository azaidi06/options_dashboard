/**
 * Learn Page - educational content extracted from HomePage.
 * Sticky right-rail TOC; section anchors for deep-linking.
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

const TOC_SECTIONS = [
  { id: 'getting-started', label: '1. Getting Started' },
  { id: 'stock-analysis', label: '2. Stock Analysis' },
  { id: 'drawdown', label: '3. Drawdown Analysis' },
  { id: 'options', label: '4. Put Options' },
  { id: 'indicators', label: '5. Technical Indicators' },
  { id: 'rsi', label: '5a. RSI' },
  { id: 'macd', label: '5b. MACD' },
  { id: 'bollinger', label: '5c. Bollinger Bands' },
  { id: 'moving-averages', label: '5d. Moving Averages' },
  { id: 'limitations', label: "6. What TA Can't Do" },
  { id: 'faq', label: '7. Tips & FAQ' },
];

export function LearnPage() {
  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-extrabold mb-3 gradient-text">Learn</h1>
          <p className="text-slate-400 max-w-3xl">
            Reference material for the dashboard&apos;s analytics &mdash; deep-dives into the indicators
            and concepts the data pages use, with curated beginner and academic sources for each.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_220px] gap-8">
          {/* Main column */}
          <div>
            {/* ═══════════════════════ */}
            {/* 1. GETTING STARTED */}
            {/* ═══════════════════════ */}
            <h2 id="getting-started" className="text-2xl font-bold text-slate-100 mb-4 scroll-mt-24">
              1. Getting Started
            </h2>

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
                <li>Pick <strong className="text-slate-100">Stock Analysis</strong> or <strong className="text-slate-100">Put Options</strong> from the sidebar</li>
                <li>Enter a stock ticker (e.g., AAPL, MSFT, GOOGL) &mdash; or use the quick-switch in the header (press <kbd className="px-1 bg-slate-800 rounded">/</kbd>)</li>
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

            <div className="section-divider" />

            {/* ═══════════════════════ */}
            {/* 2. STOCK ANALYSIS */}
            {/* ═══════════════════════ */}
            <h2 id="stock-analysis" className="text-2xl font-bold text-slate-100 mb-2 scroll-mt-24">
              2. Stock Analysis Page
            </h2>
            <p className="text-sm text-slate-400 mb-5 italic">
              Go to <Link to="/stock" className="text-indigo-400 hover:text-indigo-300 underline">Stock Analysis</Link> to use these features.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="text-lg font-semibold text-slate-100 mb-3">Gradient Coloring</h3>
                <div className="text-sm text-slate-300 leading-relaxed space-y-3">
                  <p>The price chart uses a color gradient to show how far the current price is from the rolling high. This visualization technique helps you instantly identify the stock's position relative to recent performance &mdash; a key concept in <strong className="text-slate-100">relative strength analysis</strong>.</p>
                  <p><strong className="text-slate-100">Color Interpretation:</strong></p>
                  <ul className="space-y-1.5 ml-2">
                    <li><span className="inline-block w-3 h-3 rounded-full bg-emerald-500 mr-2 align-middle" /><strong className="text-emerald-400">Green shades</strong> = Price is at or near the rolling high (strong relative position)</li>
                    <li><span className="inline-block w-3 h-3 rounded-full bg-red-500 mr-2 align-middle" /><strong className="text-red-400">Red shades</strong> = Price is below the rolling high (pullback/correction territory)</li>
                    <li>Color intensity = Magnitude of deviation (darker = further from high)</li>
                  </ul>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-slate-100 mb-3">Rolling High Lookback</h3>
                <div className="text-sm text-slate-300 leading-relaxed space-y-3">
                  <p>The <strong className="text-slate-100">Rolling High Lookback</strong> setting controls the window for calculating the reference high.</p>
                  <ul className="list-disc list-inside space-y-1.5 ml-2">
                    <li><strong className="text-slate-100">Short (5-30 days):</strong> Captures minor pullbacks, swing trading.</li>
                    <li><strong className="text-slate-100">Medium (30-60 days):</strong> Balanced view; position traders.</li>
                    <li><strong className="text-slate-100">Long (60-200 days):</strong> Major trends and significant drawdowns.</li>
                  </ul>
                </div>
              </div>
            </div>

            <p className="text-sm text-slate-300 leading-relaxed mb-6">
              <strong className="text-slate-100">Volume Bars:</strong> The lower section shows trading volume. Volume is the &quot;fuel&quot; of price movements &mdash; higher volume during price moves indicates stronger conviction and often more sustainable trends.
            </p>

            <div className="section-divider" />

            {/* ═══════════════════════ */}
            {/* 3. DRAWDOWN */}
            {/* ═══════════════════════ */}
            <h2 id="drawdown" className="text-2xl font-bold text-slate-100 mb-4 scroll-mt-24">
              3. Drawdown Analysis Tab
            </h2>

            <div className="text-sm text-slate-300 leading-relaxed space-y-3 mb-6">
              <p>Drawdown analysis is one of the most important risk management tools. A <strong className="text-slate-100">drawdown</strong> measures the peak-to-trough decline before a new peak is achieved.</p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Assess realistic downside risk (not just volatility)</li>
                <li>Set appropriate position sizes</li>
                <li>Maintain psychological resilience during market declines</li>
              </ul>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="metric-explain">
                <div className="metric-val">ATH</div>
                <div className="metric-lbl">All-Time High</div>
                <p className="text-xs text-slate-400 mt-2">The highest price reached in the selected period.</p>
              </div>
              <div className="metric-explain">
                <div className="metric-val text-red-400">-12%</div>
                <div className="metric-lbl">Current Drawdown</div>
                <p className="text-xs text-slate-400 mt-2">How far below the ATH the current price is.</p>
              </div>
              <div className="metric-explain">
                <div className="metric-val text-red-400">-35%</div>
                <div className="metric-lbl">Max Drawdown</div>
                <p className="text-xs text-slate-400 mt-2">The largest peak-to-trough decline in the period.</p>
              </div>
            </div>

            <details className="mb-6">
              <summary>Why Drawdowns Matter More Than Volatility</summary>
              <div className="details-content space-y-3">
                <p>Volatility (standard deviation) treats upside and downside equally. Drawdowns focus specifically on losses &mdash; what actually hurts investors.</p>
                <p><strong className="text-slate-100">Key Insight:</strong> The math of losses is asymmetric. A 50% loss requires a 100% gain to recover.</p>
                <div className="overflow-x-auto mt-3">
                  <table className="data-table">
                    <thead><tr><th>Drawdown</th><th>Gain Needed to Recover</th></tr></thead>
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
                    <strong className="text-amber-400">Survivorship Bias:</strong> This dashboard analyzes prominent publicly-traded stocks. These are survivors. Many stocks experience drawdowns they never recover from.
                  </p>
                </div>
                <RefLinks topic="drawdown" />
              </div>
            </details>

            <div className="section-divider" />

            {/* ═══════════════════════ */}
            {/* 4. PUT OPTIONS */}
            {/* ═══════════════════════ */}
            <h2 id="options" className="text-2xl font-bold text-slate-100 mb-4 scroll-mt-24">
              4. Put Options
            </h2>

            <div className="info-box mb-5">
              <p className="text-sm text-slate-200">
                Visit the <Link to="/options" className="text-purple-400 hover:text-purple-300 underline">Put Options page</Link> to explore real historical option chains, IV smiles, payoffs, and Greek calculators.
              </p>
            </div>

            <div className="warning-box mb-5">
              <p className="text-sm">
                <strong className="text-amber-400">Risk Disclaimer:</strong> Options trading involves substantial risk of loss. Buying options risks the entire premium; selling options can expose you to losses far exceeding margin. This dashboard is for <strong className="text-slate-100">educational purposes only</strong>.
              </p>
            </div>

            <div className="text-sm text-slate-300 leading-relaxed space-y-3 mb-5">
              <p><strong className="text-slate-100">What is a Put Option?</strong> A put option gives you the right (but not obligation) to <strong className="text-slate-100">sell</strong> a stock at a specific price (strike) before a specific date (expiration). You pay a premium for this right.</p>

              <p><strong className="text-slate-100">Key Concept &mdash; Moneyness:</strong></p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li><strong className="text-slate-100">ITM:</strong> Strike above stock price (for puts) &mdash; intrinsic value.</li>
                <li><strong className="text-slate-100">ATM:</strong> Strike near stock price.</li>
                <li><strong className="text-slate-100">OTM:</strong> Strike below stock price (for puts) &mdash; only time value.</li>
              </ul>
            </div>

            <details className="mb-4">
              <summary>References: Put Options</summary>
              <div className="details-content"><RefLinks topic="options" /></div>
            </details>

            <details id="greeks" className="mb-6 scroll-mt-24">
              <summary>The Greeks (Delta, Theta, Gamma, Vega)</summary>
              <div className="details-content space-y-3">
                <div className="overflow-x-auto">
                  <table className="data-table">
                    <thead>
                      <tr><th>Greek</th><th>Measures</th><th>Intuition</th></tr>
                    </thead>
                    <tbody>
                      <tr><td><strong className="text-slate-100">Delta</strong></td><td>Price sensitivity to stock movement</td><td>&quot;How much does my option move if the stock moves $1?&quot;</td></tr>
                      <tr><td><strong className="text-slate-100">Gamma</strong></td><td>Rate of change of delta</td><td>&quot;How stable is my delta?&quot;</td></tr>
                      <tr><td><strong className="text-slate-100">Theta</strong></td><td>Time decay</td><td>&quot;How much value do I lose each day?&quot;</td></tr>
                      <tr><td><strong className="text-slate-100">Vega</strong></td><td>Volatility sensitivity</td><td>&quot;How much does my option move if volatility changes?&quot;</td></tr>
                      <tr><td><strong className="text-slate-100">Rho</strong></td><td>Interest rate sensitivity</td><td>&quot;How does my option react to rate changes?&quot;</td></tr>
                    </tbody>
                  </table>
                </div>
                <p>
                  <strong className="text-slate-100">Important: Theta is non-linear.</strong> Time decay accelerates sharply in the final 30-45 days before expiration. Black-Scholes models this with a square-root-of-time relationship; the dashboard&apos;s Time Decay calculator uses a linear approximation for clarity.
                </p>
                <RefLinks topic="greeks" />
              </div>
            </details>

            <div className="section-divider" />

            {/* ═══════════════════════ */}
            {/* 5. INDICATORS */}
            {/* ═══════════════════════ */}
            <h2 id="indicators" className="text-2xl font-bold text-slate-100 mb-4 scroll-mt-24">
              5. Technical Indicators
            </h2>

            <p className="text-sm text-slate-300 leading-relaxed mb-5">
              Technical indicators are mathematical calculations based on price, volume, or open interest. They help identify trends, momentum, volatility, and potential reversal points.
            </p>

            {/* Anchored sub-sections so /learn#rsi etc. work directly */}
            <h3 id="rsi" className="text-lg font-semibold text-slate-100 mb-3 scroll-mt-24">RSI (Relative Strength Index)</h3>
            <div className="card-lg mb-6">
              <div className="text-sm text-slate-300 leading-relaxed space-y-3">
                <p><strong className="text-slate-100">Creator:</strong> J. Welles Wilder Jr. (1978)</p>
                <p><strong className="text-slate-100">Math (Simplified):</strong></p>
                <p className="font-mono text-xs bg-slate-800/60 p-2 rounded">RSI = 100 - (100 / (1 + RS)), where RS = Average Gain / Average Loss over N periods</p>
                <p><strong className="text-slate-100">Interpretation:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong>Above 70:</strong> Potentially overbought.</li>
                  <li><strong>Below 30:</strong> Potentially oversold.</li>
                  <li><strong>50:</strong> Neutral momentum.</li>
                </ul>
              </div>
              <details className="mt-4"><summary>References: RSI</summary><div className="details-content"><RefLinks topic="rsi" /></div></details>
            </div>

            <h3 id="macd" className="text-lg font-semibold text-slate-100 mb-3 scroll-mt-24">MACD</h3>
            <div className="card-lg mb-6">
              <div className="text-sm text-slate-300 leading-relaxed space-y-3">
                <p><strong className="text-slate-100">Creator:</strong> Gerald Appel (1970s)</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong>MACD Line:</strong> 12-period EMA minus 26-period EMA.</li>
                  <li><strong>Signal Line:</strong> 9-period EMA of the MACD line.</li>
                  <li><strong>Histogram:</strong> MACD Line minus Signal Line.</li>
                </ul>
              </div>
              <details className="mt-4"><summary>References: MACD</summary><div className="details-content"><RefLinks topic="macd" /></div></details>
            </div>

            <h3 id="bollinger" className="text-lg font-semibold text-slate-100 mb-3 scroll-mt-24">Bollinger Bands</h3>
            <div className="card-lg mb-6">
              <div className="text-sm text-slate-300 leading-relaxed space-y-3">
                <p><strong className="text-slate-100">Creator:</strong> John Bollinger (1980s)</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong>Middle Band:</strong> 20-period simple moving average.</li>
                  <li><strong>Upper Band:</strong> Middle band + 2 standard deviations.</li>
                  <li><strong>Lower Band:</strong> Middle band &minus; 2 standard deviations.</li>
                </ul>
                <p>Stock returns exhibit fat tails &mdash; prices breach the bands more frequently than 5% of the time. Treat them as a relative volatility framework, not a probabilistic prediction.</p>
              </div>
              <details className="mt-4"><summary>References: Bollinger Bands</summary><div className="details-content"><RefLinks topic="bollinger" /></div></details>
            </div>

            <h3 id="moving-averages" className="text-lg font-semibold text-slate-100 mb-3 scroll-mt-24">Moving Averages</h3>
            <div className="card-lg mb-6">
              <div className="text-sm text-slate-300 leading-relaxed space-y-3">
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong>SMA:</strong> Equal weight to all prices in the period.</li>
                  <li><strong>EMA:</strong> More weight to recent prices, reacts faster.</li>
                </ul>
                <div className="overflow-x-auto">
                  <table className="data-table">
                    <thead><tr><th>Period</th><th>Timeframe</th><th>Common Use</th></tr></thead>
                    <tbody>
                      <tr><td>10-day</td><td>Very short</td><td>Short-term swing trading, momentum</td></tr>
                      <tr><td>20-day</td><td>Short</td><td>Swing trading, Bollinger middle band</td></tr>
                      <tr><td>50-day</td><td>Medium</td><td>Institutional benchmark, trend confirmation</td></tr>
                      <tr><td>100-day</td><td>Medium-long</td><td>Less common, between 50 and 200</td></tr>
                      <tr><td>200-day</td><td>Long</td><td>Institutional benchmark, bull/bear market definition</td></tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <details className="mt-4"><summary>References: Moving Averages</summary><div className="details-content"><RefLinks topic="moving_averages" /></div></details>
            </div>

            <div className="section-divider" />

            {/* ═══════════════════════ */}
            {/* 6. LIMITATIONS */}
            {/* ═══════════════════════ */}
            <h2 id="limitations" className="text-2xl font-bold text-slate-100 mb-4 scroll-mt-24">
              6. What Technical Analysis Can&apos;t Do
            </h2>

            <div className="text-sm text-slate-300 leading-relaxed space-y-3 mb-6">
              <ul className="list-disc list-inside space-y-2 ml-2">
                <li><strong className="text-slate-100">No predictive guarantee:</strong> Patterns describe past behaviour. Markets respond to news, earnings, policy changes.</li>
                <li><strong className="text-slate-100">Efficient Market Hypothesis:</strong> Public information is rapidly priced in.</li>
                <li><strong className="text-slate-100">Data mining risk:</strong> With enough indicators and parameters, you can find &quot;patterns&quot; in random data.</li>
                <li><strong className="text-slate-100">Self-fulfilling vs self-defeating:</strong> Popular signals (200-day MA) work partly because traders act on them &mdash; widespread adoption can erode effectiveness.</li>
                <li><strong className="text-slate-100">No substitute for fundamentals:</strong> Technicals show <em>what</em>, not <em>why</em>.</li>
              </ul>
            </div>

            <div className="section-divider" />

            {/* ═══════════════════════ */}
            {/* 7. FAQ */}
            {/* ═══════════════════════ */}
            <h2 id="faq" className="text-2xl font-bold text-slate-100 mb-4 scroll-mt-24">
              7. Tips &amp; FAQ
            </h2>

            <div className="space-y-3 mb-8">
              <details>
                <summary>Why is my stock showing red even though it&apos;s up today?</summary>
                <div className="details-content space-y-2">
                  <p>The colour reflects the distance from the <strong className="text-slate-100">rolling high</strong>, not the daily change.</p>
                  <p><strong className="text-slate-100">Example:</strong> A stock at $100 two weeks ago, dropped to $90, today at $93 is up 3.3% but still 7% below the rolling high (red).</p>
                </div>
              </details>

              <details>
                <summary>How do I get technical indicators to work?</summary>
                <div className="details-content space-y-2">
                  <ol className="list-decimal list-inside space-y-1.5">
                    <li>Get a free API key from <a href="https://www.alphavantage.co/support/#api-key" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 underline">Alpha Vantage</a></li>
                    <li>Enter the key in the Technical Indicators section</li>
                    <li>Select indicators &amp; click Load Data</li>
                  </ol>
                  <p className="mt-2"><strong className="text-slate-100">Free tier:</strong> 5 calls/min, 500 calls/day.</p>
                </div>
              </details>

              <details>
                <summary>Can I use this for real trading decisions?</summary>
                <div className="details-content space-y-2">
                  <p>This dashboard is for <strong className="text-slate-100">educational purposes only</strong>. It is not financial advice.</p>
                  <ul className="list-disc list-inside space-y-1 ml-2">
                    <li>Do your own research</li>
                    <li>Consult a registered financial professional</li>
                    <li>Paper trade first</li>
                    <li>Never invest more than you can afford to lose</li>
                  </ul>
                </div>
              </details>

              <details>
                <summary>Where does the options data come from?</summary>
                <div className="details-content space-y-2">
                  <p>Historical options chains across many tickers (AAPL, MSFT, GOOGL, AMZN, META, TSLA, NFLX, NVDA, AMD, etc.). Daily snapshots include strikes, expirations, bid/ask, volume, OI, IV, and Greeks.</p>
                </div>
              </details>
            </div>
          </div>

          {/* Sticky right-rail TOC */}
          <aside className="hidden lg:block">
            <div className="sticky top-24">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                On This Page
              </p>
              <nav className="space-y-1 text-sm">
                {TOC_SECTIONS.map((s) => (
                  <a
                    key={s.id}
                    href={`#${s.id}`}
                    className="block px-3 py-1.5 rounded-md text-slate-400 hover:text-indigo-400 hover:bg-slate-800/40 transition-colors"
                  >
                    {s.label}
                  </a>
                ))}
              </nav>
            </div>
          </aside>
        </div>
      </div>
    </Layout>
  );
}
