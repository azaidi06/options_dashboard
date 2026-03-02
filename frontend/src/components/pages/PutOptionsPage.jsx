/**
 * Put Options Page - dark theme
 */
import { useState, useEffect } from 'react';
import { Layout } from '../layout/Layout';
import { Card, CardLg } from '../common/Card';
import { Input, Select } from '../common/Input';
import { Button } from '../common/Button';
import { Tabs, Tab } from '../common/Tabs';
import { ErrorCard } from '../common/ErrorCard';
import { OptionChain } from '../options/OptionChain';
import { IVSmileChart } from '../options/IVSmileChart';
import { PayoffDiagram } from '../options/PayoffDiagram';
import { CalculatorPanel } from '../options/CalculatorPanel';
import { GreeksExplainer } from '../options/GreeksExplainer';
import { useTickers, useTickerDateRange, useOptionChain, useIVSmile } from '../../hooks/useOptionsData';

export function PutOptionsPage() {
  const [selectedTicker, setSelectedTicker] = useState('AMD');
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedExpiration, setSelectedExpiration] = useState('');

  // Data hooks
  const tickers = useTickers();
  const dateRange = useTickerDateRange(selectedTicker);

  // Fetch chain with just ticker + date (expiration is optional for getting available expirations)
  const optionChain = useOptionChain(selectedTicker, selectedDate, selectedExpiration);
  const ivSmile = useIVSmile(selectedTicker, selectedDate, selectedExpiration);

  // Set date to max available when dateRange loads
  useEffect(() => {
    if (dateRange.data?.max_date && !selectedDate) {
      setSelectedDate(dateRange.data.max_date);
    }
  }, [dateRange.data]);

  // Extract available expirations from chain data
  const expirations = optionChain.data?.data
    ? [...new Set(optionChain.data.data.map((opt) => opt.expiration))].sort()
    : [];

  // Auto-select first expiration when list populates and none is selected
  useEffect(() => {
    if (expirations.length > 0 && !selectedExpiration) {
      setSelectedExpiration(expirations[0]);
    }
  }, [expirations.length]);

  // Filter chain data to selected expiration for display
  const filteredChainData = optionChain.data && selectedExpiration
    ? {
        ...optionChain.data,
        data: optionChain.data.data.filter((opt) => opt.expiration === selectedExpiration),
      }
    : optionChain.data;

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Selection Controls */}
        <CardLg className="mb-6">
          <h2 className="text-base font-semibold mb-4 text-slate-200">Select Data</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Select
              label="Ticker"
              value={selectedTicker}
              onChange={(v) => {
                setSelectedTicker(v);
                setSelectedDate('');
                setSelectedExpiration('');
              }}
              options={
                tickers.tickers.length > 0
                  ? tickers.tickers.map((t) => ({ value: t, label: t }))
                  : [{ value: selectedTicker, label: selectedTicker }]
              }
              disabled={tickers.loading}
            />
            <Input
              label="Quote Date"
              value={selectedDate}
              onChange={(v) => {
                setSelectedDate(v);
                setSelectedExpiration('');
              }}
              type="date"
              disabled={dateRange.loading}
            />
            <Select
              label="Expiration Date"
              value={selectedExpiration}
              onChange={setSelectedExpiration}
              options={expirations.map((exp) => ({
                value: exp,
                label: exp.split(' ')[0],
              }))}
              disabled={!expirations.length || optionChain.loading}
            />
            <div className="flex items-end">
              <Button
                onClick={() => optionChain.refetch()}
                disabled={optionChain.loading || !selectedDate}
                className="w-full"
              >
                {optionChain.loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="spinner" /> Loading...
                  </span>
                ) : (
                  'Load Data'
                )}
              </Button>
            </div>
          </div>

          {dateRange.data && (
            <p className="mt-3 text-xs text-slate-500">
              Data available: {dateRange.data.min_date} to {dateRange.data.max_date}
            </p>
          )}

          {dateRange.error && (
            <div className="mt-4">
              <ErrorCard error={dateRange.error} />
            </div>
          )}
        </CardLg>

        {/* Error Messages */}
        {optionChain.error && (
          <ErrorCard error={optionChain.error} onRetry={() => optionChain.refetch()} />
        )}

        {/* Loading state */}
        {optionChain.loading && (
          <div className="flex items-center justify-center py-16">
            <div className="text-center">
              <div className="spinner-lg mx-auto mb-3" />
              <p className="text-slate-400 text-sm">Loading options data...</p>
            </div>
          </div>
        )}

        {/* Main Content Tabs */}
        <Tabs defaultTab={0}>
          <Tab label="Option Chain">
            {filteredChainData?.data?.length ? (
              <CardLg>
                <OptionChain ticker={selectedTicker} optionData={filteredChainData} />
              </CardLg>
            ) : (
              <div className="flex items-center justify-center py-16">
                <div className="text-center">
                  <div className="text-4xl mb-3 text-slate-600">◆</div>
                  <p className="text-slate-400">
                    {!selectedDate
                      ? 'Loading date range...'
                      : 'Select a ticker and date to view the option chain'}
                  </p>
                </div>
              </div>
            )}
          </Tab>

          <Tab label="IV Smile">
            {ivSmile.data?.data?.length ? (
              <CardLg>
                <IVSmileChart ticker={selectedTicker} ivSmileData={ivSmile.data} />
              </CardLg>
            ) : (
              <div className="flex items-center justify-center py-16">
                <div className="text-center">
                  <div className="text-4xl mb-3 text-slate-600">◆</div>
                  <p className="text-slate-400">Select data and expiration to view the IV smile</p>
                </div>
              </div>
            )}
          </Tab>

          <Tab label="Payoff Diagram">
            <CardLg>
              <PayoffDiagram />
            </CardLg>
          </Tab>

          <Tab label="Calculators">
            <CardLg>
              <CalculatorPanel />
            </CardLg>
          </Tab>

          <Tab label="Greeks Guide">
            <CardLg>
              <GreeksExplainer />
            </CardLg>
          </Tab>
        </Tabs>

        {/* Educational Note */}
        <div className="info-box mt-10">
          <h3 className="text-lg font-bold mb-3 text-slate-100">Learning Put Options</h3>
          <div className="space-y-2 text-sm text-slate-300 leading-relaxed">
            <p>
              <strong className="text-slate-100">What's a Put Option?</strong> A contract giving you
              the right (but not obligation) to sell a stock at a specific price (strike) by a specific
              date (expiration).
            </p>
            <p>
              <strong className="text-slate-100">Why Use Puts?</strong> Protect against downside risk,
              speculate on price declines, or generate income by selling puts (advanced).
            </p>
            <p>
              <strong className="text-slate-100">Use This Dashboard To:</strong> Explore real option chains,
              understand how Greeks affect pricing, calculate payoff scenarios, and learn proper position sizing.
            </p>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="warning-box mt-5">
          <p className="text-sm text-slate-300">
            <strong className="text-amber-400">Disclaimer:</strong> This dashboard is for educational
            purposes only. Options trading involves significant risk and is not suitable for all investors.
            Always do your own research and consider consulting with a financial professional.
          </p>
        </div>
      </div>
    </Layout>
  );
}
