/**
 * Stock Analysis Page - dark theme
 */
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { FileSearch } from 'lucide-react';
import { useStockData, useIndicators, useDrawdown, useOpportunities, useTickers } from '../../hooks/useStockData';
import { Layout } from '../layout/Layout';
import { CardLg, MetricCard } from '../common/Card';
import { Input, Select } from '../common/Input';
import { Button } from '../common/Button';
import { Tabs, Tab } from '../common/Tabs';
import { ErrorCard } from '../common/ErrorCard';
import { PriceChart } from '../stock/PriceChart';
import { IndicatorsPanel } from '../stock/IndicatorsPanel';
import { DrawdownChart } from '../stock/DrawdownChart';
import { OpportunitiesTable } from '../stock/OpportunitiesTable';
import { formatCurrency, formatVolume } from '../../utils/formatters';
import { recordRecentTicker } from './HomePage';

const DEFAULT_TICKER = 'AAPL';
const DEFAULT_LOOKBACK = 30;

export function StockAnalysisPage() {
  const [searchParams] = useSearchParams();
  const queryTicker = searchParams.get('ticker');

  const [ticker, setTicker] = useState(queryTicker || DEFAULT_TICKER);
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [lookbackDays, setLookbackDays] = useState(DEFAULT_LOOKBACK);
  const [activeTab, setActiveTab] = useState(0);
  const [entryThreshold, setEntryThreshold] = useState(0.10);
  const [exitThreshold, setExitThreshold] = useState(0.05);

  // React to ?ticker= changes (e.g. from header quick-switch)
  useEffect(() => {
    if (queryTicker && queryTicker !== ticker) setTicker(queryTicker);
  }, [queryTicker]);

  // Record recent ticker visit
  useEffect(() => {
    if (ticker) recordRecentTicker(ticker);
  }, [ticker]);

  // Data hooks
  const { tickers } = useTickers();
  const stockData = useStockData(ticker, startDate, endDate, lookbackDays);
  const indicators = useIndicators(ticker, startDate, endDate);
  const drawdown = useDrawdown(ticker, startDate, endDate);
  const opportunities = useOpportunities(ticker, startDate, endDate, entryThreshold, exitThreshold);

  const isLoading = stockData.loading;
  const hasData = !!stockData.data;

  // Derived metric values (kept here so the skeleton path can render the strip too)
  let latestClose = null;
  let periodHigh = null;
  let periodLow = null;
  let totalVolume = null;
  if (hasData) {
    const rows = stockData.data.data;
    latestClose = rows[rows.length - 1]?.close;
    periodHigh = Math.max(...rows.map((d) => d.high));
    periodLow = Math.min(...rows.map((d) => d.low));
    totalVolume = rows.reduce((sum, d) => sum + d.volume, 0);
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Input Controls */}
        <CardLg className="mb-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <Select
              label="Ticker"
              value={ticker}
              onChange={(v) => setTicker(v)}
              options={
                tickers.length > 0
                  ? tickers.map((t) => ({ value: t, label: t }))
                  : [{ value: ticker, label: ticker }]
              }
              disabled={isLoading}
            />
            <Input
              label="Start Date"
              value={startDate}
              onChange={setStartDate}
              type="date"
              disabled={isLoading}
            />
            <Input
              label="End Date"
              value={endDate}
              onChange={setEndDate}
              type="date"
              disabled={isLoading}
            />
            <Select
              label="Lookback Days"
              value={lookbackDays}
              onChange={(v) => setLookbackDays(parseInt(v))}
              options={[
                { value: 5, label: '5 Days' },
                { value: 10, label: '10 Days' },
                { value: 20, label: '20 Days' },
                { value: 30, label: '30 Days' },
                { value: 60, label: '60 Days' },
                { value: 200, label: '200 Days' },
              ]}
              disabled={isLoading}
            />
            <div className="flex items-end">
              <Button
                onClick={() => stockData.refetch()}
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="spinner" /> Loading...
                  </span>
                ) : (
                  'Load Data'
                )}
              </Button>
            </div>
          </div>
        </CardLg>

        {/* Error messages */}
        {stockData.error && (
          <ErrorCard error={stockData.error} onRetry={() => stockData.refetch()} />
        )}

        {/* Skeleton metric strip while loading (keeps content shape stable) */}
        {isLoading && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {['Latest Close', 'Period High', 'Period Low', 'Total Volume'].map((label) => (
              <div key={label} className="metric-card">
                <div className="metric-label">{label}</div>
                <div className="skeleton h-7 w-3/4 mt-1" />
              </div>
            ))}
          </div>
        )}

        {/* Data display */}
        {hasData && !isLoading && (
          <>
            {/* Summary metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <MetricCard label="Latest Close" value={formatCurrency(latestClose, 2)} />
              <MetricCard label="Period High" value={formatCurrency(periodHigh, 2)} />
              <MetricCard label="Period Low" value={formatCurrency(periodLow, 2)} />
              <MetricCard label="Total Volume" value={formatVolume(totalVolume, 1)} />
            </div>

            {/* Tabs */}
            <Tabs defaultTab={activeTab}>
              <Tab label="Price Chart">
                <CardLg>
                  <PriceChart
                    data={stockData.data.data}
                    ticker={ticker}
                    lookbackDays={lookbackDays}
                  />
                </CardLg>
              </Tab>

              <Tab label="Indicators">
                <CardLg>
                  <IndicatorsPanel
                    ticker={ticker}
                    startDate={startDate}
                    endDate={endDate}
                    indicators={indicators}
                    stockData={stockData.data}
                  />
                </CardLg>
              </Tab>

              <Tab label="Drawdown">
                <CardLg>
                  <DrawdownChart
                    ticker={ticker}
                    startDate={startDate}
                    endDate={endDate}
                    drawdown={drawdown}
                    priceData={stockData.data.data}
                  />
                </CardLg>
              </Tab>

              <Tab label="Opportunities">
                <CardLg>
                  <OpportunitiesTable
                    ticker={ticker}
                    startDate={startDate}
                    endDate={endDate}
                    opportunities={opportunities}
                    entryThreshold={entryThreshold}
                    exitThreshold={exitThreshold}
                    onThresholdChange={(entry, exit) => {
                      setEntryThreshold(entry);
                      setExitThreshold(exit);
                    }}
                  />
                </CardLg>
              </Tab>
            </Tabs>
          </>
        )}

        {/* Empty state */}
        {!isLoading && !stockData.data && !stockData.error && (
          <CardLg>
            <div className="flex items-center justify-center py-16">
              <div className="text-center max-w-md">
                <FileSearch className="w-12 h-12 text-slate-600 mx-auto mb-4" strokeWidth={1.5} />
                <p className="text-slate-300 font-semibold mb-1">No data loaded yet</p>
                <p className="text-slate-500 text-sm">
                  Enter a ticker and click <strong>Load Data</strong> to begin analysis.
                </p>
              </div>
            </div>
          </CardLg>
        )}
      </div>
    </Layout>
  );
}
