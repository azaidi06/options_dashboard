/**
 * Put Options Page - Options analysis and education
 */
import { useState } from 'react';
import { Layout } from '../layout/Layout';
import { Card, CardLg } from '../common/Card';
import { Input, Select } from '../common/Input';
import { Button } from '../common/Button';
import { Tabs, Tab } from '../common/Tabs';
import { OptionChain } from '../options/OptionChain';
import { IVSmileChart } from '../options/IVSmileChart';
import { PayoffDiagram } from '../options/PayoffDiagram';
import { CalculatorPanel } from '../options/CalculatorPanel';
import { GreeksExplainer } from '../options/GreeksExplainer';
import { useTickers, useTickerDateRange, useOptionChain, useIVSmile } from '../../hooks/useOptionsData';

export function PutOptionsPage() {
  const [selectedTicker, setSelectedTicker] = useState('AMD');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedExpiration, setSelectedExpiration] = useState('');

  // Data hooks
  const tickers = useTickers();
  const dateRange = useTickerDateRange(selectedTicker);
  const optionChain = useOptionChain(selectedTicker, selectedDate, selectedExpiration);
  const ivSmile = useIVSmile(selectedTicker, selectedDate, selectedExpiration);

  // Get available expirations from option chain
  const expirations = optionChain.data
    ? [...new Set(optionChain.data.data.map((opt) => opt.expiration))].sort()
    : [];

  if (selectedExpiration && !expirations.includes(selectedExpiration)) {
    // Auto-select first expiration when ticker changes
    if (expirations.length > 0) {
      setSelectedExpiration(expirations[0]);
    }
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-gray-900">Put Options Analysis</h1>

        {/* Selection Controls */}
        <CardLg className="mb-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">Select Data</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Select
              label="Ticker"
              value={selectedTicker}
              onChange={setSelectedTicker}
              options={tickers.tickers.map((t) => ({ value: t, label: t }))}
              disabled={tickers.loading}
            />
            <Input
              label="Quote Date"
              value={selectedDate}
              onChange={setSelectedDate}
              type="date"
              disabled={dateRange.loading}
            />
            <Select
              label="Expiration Date"
              value={selectedExpiration}
              onChange={setSelectedExpiration}
              options={expirations.map((exp) => ({
                value: exp,
                label: new Date(exp).toLocaleDateString(),
              }))}
              disabled={!expirations.length || optionChain.loading}
            />
            <div className="flex items-end">
              <Button
                onClick={() => {}}
                disabled={optionChain.loading}
                className="w-full"
              >
                {optionChain.loading ? 'Loading...' : 'Load Data'}
              </Button>
            </div>
          </div>

          {dateRange.error && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded p-3">
              <p className="text-red-800 text-sm">{dateRange.error}</p>
            </div>
          )}
        </CardLg>

        {/* Error Messages */}
        {optionChain.error && (
          <Card className="mb-6 bg-red-50 border border-red-200">
            <p className="text-red-800">
              <strong>Error:</strong> {optionChain.error}
            </p>
          </Card>
        )}

        {/* Main Content Tabs */}
        {selectedExpiration && (
          <Tabs defaultTab={0}>
            <Tab label="📊 Option Chain">
              <CardLg>
                <OptionChain ticker={selectedTicker} optionData={optionChain.data} />
              </CardLg>
            </Tab>

            <Tab label="📈 IV Smile">
              <CardLg>
                <IVSmileChart ticker={selectedTicker} ivSmileData={ivSmile.data} />
              </CardLg>
            </Tab>

            <Tab label="💹 Payoff Diagram">
              <CardLg>
                <PayoffDiagram />
              </CardLg>
            </Tab>

            <Tab label="🧮 Calculators">
              <CardLg>
                <CalculatorPanel />
              </CardLg>
            </Tab>

            <Tab label="📚 Greeks Guide">
              <CardLg>
                <GreeksExplainer />
              </CardLg>
            </Tab>
          </Tabs>
        )}

        {/* Empty State */}
        {!selectedExpiration && (
          <Card className="text-center text-gray-500 py-12">
            <p className="text-lg">Select a ticker, date, and expiration to begin analysis</p>
          </Card>
        )}

        {/* Educational Note */}
        <div className="mt-12 bg-blue-50 border border-blue-200 rounded p-6">
          <h3 className="text-xl font-bold mb-3 text-gray-900">📚 Learning Put Options</h3>
          <div className="space-y-2 text-gray-700">
            <p>
              <strong>What's a Put Option?</strong> A contract giving you the right (but not obligation)
              to sell a stock at a specific price (strike) by a specific date (expiration).
            </p>
            <p>
              <strong>Why Use Puts?</strong> Protect against downside risk, speculate on price declines,
              or generate income by selling puts (advanced).
            </p>
            <p>
              <strong>Use This Dashboard To:</strong> Explore real option chains, understand how Greeks
              affect pricing, calculate payoff scenarios, and learn proper position sizing.
            </p>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-6 bg-red-50 border border-red-200 rounded p-6">
          <p className="text-red-900">
            <strong>⚠️ Disclaimer:</strong> This dashboard is for educational purposes only. It is not
            financial advice. Options trading involves significant risk and is not suitable for all
            investors. Always do your own research and consider consulting with a financial professional
            before trading options.
          </p>
        </div>
      </div>
    </Layout>
  );
}
