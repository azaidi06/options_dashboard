/**
 * Stock Analysis Page - dark theme
 */
import { useState } from 'react';
import { useStockData, useIndicators, useDrawdown, useOpportunities, useTickers } from '../../hooks/useStockData';
import { Layout } from '../layout/Layout';
import { Card, CardLg, MetricCard } from '../common/Card';
import { Input, Select } from '../common/Input';
import { Button } from '../common/Button';
import { Tabs, Tab } from '../common/Tabs';
import { ErrorCard } from '../common/ErrorCard';
import { PriceChart } from '../stock/PriceChart';
import { IndicatorsPanel } from '../stock/IndicatorsPanel';
import { DrawdownChart } from '../stock/DrawdownChart';
import { OpportunitiesTable } from '../stock/OpportunitiesTable';

const DEFAULT_TICKER = 'AAPL';
const DEFAULT_LOOKBACK = 30;

export function StockAnalysisPage() {
  const [ticker, setTicker] = useState(DEFAULT_TICKER);
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [lookbackDays, setLookbackDays] = useState(DEFAULT_LOOKBACK);
  const [activeTab, setActiveTab] = useState(0);
  const [entryThreshold, setEntryThreshold] = useState(0.10);
  const [exitThreshold, setExitThreshold] = useState(0.05);

  // Data hooks
  const { tickers } = useTickers();
  const stockData = useStockData(ticker, startDate, endDate, lookbackDays);
  const indicators = useIndicators(ticker, startDate, endDate);
  const drawdown = useDrawdown(ticker, startDate, endDate);
  const opportunities = useOpportunities(ticker, startDate, endDate, entryThreshold, exitThreshold);

  const isLoading = stockData.loading;

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

        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="spinner-lg mx-auto mb-3" />
              <p className="text-slate-400 text-sm">Loading stock data...</p>
            </div>
          </div>
        )}

        {/* Data display */}
        {stockData.data && !isLoading && (
          <>
            {/* Summary metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <MetricCard
                label="Latest Close"
                value={`$${stockData.data.data[stockData.data.data.length - 1]?.close.toFixed(2)}`}
              />
              <MetricCard
                label="Period High"
                value={`$${Math.max(...stockData.data.data.map((d) => d.high)).toFixed(2)}`}
              />
              <MetricCard
                label="Period Low"
                value={`$${Math.min(...stockData.data.data.map((d) => d.low)).toFixed(2)}`}
              />
              <MetricCard
                label="Total Volume"
                value={`${(
                  stockData.data.data.reduce((sum, d) => sum + d.volume, 0) / 1e6
                ).toFixed(1)}M`}
              />
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
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="text-4xl mb-3 text-slate-600">◈</div>
              <p className="text-slate-400">Enter a ticker and click "Load Data" to begin analysis</p>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
