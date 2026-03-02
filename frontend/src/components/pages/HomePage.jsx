/**
 * Home Page - Welcome and navigation
 */
import { Link } from 'react-router-dom';
import { Layout } from '../layout/Layout';
import { CardLg } from '../common/Card';

export function HomePage() {
  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-gray-900">Options Dashboard</h1>

        <p className="text-lg text-gray-600 mb-12">
          Analyze stocks and understand put options with real-time data and technical indicators.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          {/* Stock Analysis Card */}
          <Link to="/stock" className="group">
            <CardLg className="h-full group-hover:shadow-lg transition-shadow">
              <div className="text-4xl mb-4">📈</div>
              <h2 className="text-2xl font-bold mb-2 group-hover:text-blue-600 transition-colors">
                Stock Analysis
              </h2>
              <p className="text-gray-600 mb-4">
                Analyze individual stocks with price charts, technical indicators, drawdown analysis,
                and opportunity windows.
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>✓ OHLCV data with rolling highs</li>
                <li>✓ RSI, MACD, Bollinger Bands</li>
                <li>✓ Drawdown analysis and recovery stats</li>
                <li>✓ Opportunity windows for entries</li>
              </ul>
            </CardLg>
          </Link>

          {/* Put Options Card */}
          <Link to="/options" className="group">
            <CardLg className="h-full group-hover:shadow-lg transition-shadow">
              <div className="text-4xl mb-4">💰</div>
              <h2 className="text-2xl font-bold mb-2 group-hover:text-blue-600 transition-colors">
                Put Options
              </h2>
              <p className="text-gray-600 mb-4">
                Learn about put options, explore option chains, and use interactive calculators for
                Greeks and risk analysis.
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>✓ Option chain explorer</li>
                <li>✓ IV smile visualization</li>
                <li>✓ Payoff diagrams</li>
                <li>✓ Greeks and risk calculators</li>
              </ul>
            </CardLg>
          </Link>
        </div>

        {/* Getting Started */}
        <CardLg className="bg-blue-50 border border-blue-200">
          <h2 className="text-2xl font-bold mb-4 text-gray-900">Getting Started</h2>
          <ol className="space-y-3 text-gray-700">
            <li>
              <strong>1. Stock Analysis:</strong> Select a ticker (e.g., AAPL) and date range, then
              explore price charts and technical indicators to understand recent trends.
            </li>
            <li>
              <strong>2. Understand Drawdowns:</strong> Review the Drawdown Analysis tab to see
              historical periods when the stock was significantly down.
            </li>
            <li>
              <strong>3. Identify Opportunities:</strong> Check the Opportunities tab to see when
              the stock entered significant drawdowns — these are periods when put options would have
              been valuable.
            </li>
            <li>
              <strong>4. Learn Put Options:</strong> Visit the Put Options page to explore option
              chains and use calculators to understand Greeks, payoffs, and position sizing.
            </li>
          </ol>
        </CardLg>

        {/* Disclaimer */}
        <div className="mt-12 bg-red-50 border border-red-200 rounded p-6">
          <p className="text-red-900">
            <strong>⚠️ Disclaimer:</strong> This dashboard is for educational purposes only. It is not
            financial advice. Options trading involves significant risk. Always do your own research
            and consider consulting with a financial professional before trading.
          </p>
        </div>
      </div>
    </Layout>
  );
}
