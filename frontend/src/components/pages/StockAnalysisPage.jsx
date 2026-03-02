/**
 * Stock Analysis Page - Main page for stock analysis
 */
import { useState } from 'react';
import { useStockData, useIndicators, useDrawdown, useOpportunities } from '../../hooks/useStockData';
import { Layout } from '../layout/Layout';
import { Card, CardLg, MetricCard } from '../common/Card';
import { Input, Select } from '../common/Input';
import { Button } from '../common/Button';
import { Tabs, Tab } from '../common/Tabs';
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

  // Data hooks
  const stockData = useStockData(ticker, startDate, endDate, lookbackDays);
  const indicators = useIndicators(ticker, startDate, endDate);
  const drawdown = useDrawdown(ticker, startDate, endDate);
  const opportunities = useOpportunities(ticker, startDate, endDate);

  const handleLoadData = () => {
    // Trigger refetch by updating state (hooks will re-fetch)
    setActiveTab(0);
  };

  const isLoading = stockData.loading;

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-gray-900">Stock Analysis</h1>

        {/* Input Controls */}
        <CardLg className="mb-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div>
              <Input
                label="Ticker"
                value={ticker}
                onChange={setTicker}
                placeholder="e.g., AAPL"
                disabled={isLoading}
              />
            </div>
            <div>
              <Input
                label="Start Date"
                value={startDate}
                onChange={setStartDate}
                type="date"
                disabled={isLoading}
              />
            </div>
            <div>
              <Input
                label="End Date"
                value={endDate}
                onChange={setEndDate}
                type="date"
                disabled={isLoading}
              />
            </div>
            <div>
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
            </div>
            <div className="flex items-end">
              <Button
                onClick={handleLoadData}
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? 'Loading...' : 'Load Data'}
              </Button>
            </div>
          </div>
        </CardLg>

        {/* Error messages */}
        {stockData.error && (
          <Card className="mb-6 bg-red-50 border border-red-200">
            <p className="text-red-800">
              <strong>Error:</strong> {stockData.error}
            </p>
          </Card>
        )}

        {/* Loading state */}
        {isLoading && (
          <Card className="mb-6 text-center">
            <p className="text-gray-600">Loading stock data...</p>
          </Card>
        )}

        {/* Data display */}
        {stockData.data && !isLoading && (
          <>
            {/* Summary metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
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
              <Tab label="📈 Price Chart">
                <CardLg>
                  <PriceChart
                    data={stockData.data.data}
                    ticker={ticker}
                    lookbackDays={lookbackDays}
                  />
                </CardLg>
              </Tab>

              <Tab label="📊 Indicators">
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

              <Tab label="📉 Drawdown Analysis">
                <CardLg>
                  <DrawdownChart
                    ticker={ticker}
                    startDate={startDate}
                    endDate={endDate}
                    drawdown={drawdown}
                  />
                </CardLg>
              </Tab>

              <Tab label="🎯 Opportunities">
                <CardLg>
                  <OpportunitiesTable
                    ticker={ticker}
                    startDate={startDate}
                    endDate={endDate}
                    opportunities={opportunities}
                  />
                </CardLg>
              </Tab>
            </Tabs>
          </>
        )}

        {/* Empty state */}
        {!isLoading && !stockData.data && (
          <Card className="text-center text-gray-500">
            <p>Enter a ticker and click "Load Data" to begin analysis</p>
          </Card>
        )}
      </div>
    </Layout>
  );
}
