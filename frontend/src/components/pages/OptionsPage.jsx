/**
 * Options Page - dark theme.
 * Supports both Put and Call options via a Put/Call toggle.
 * (Renamed from PutOptionsPage when calls support landed.)
 */
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { FileSearch, ChevronsRight } from 'lucide-react';
import { Layout } from '../layout/Layout';
import { CardLg } from '../common/Card';
import { Input, Select } from '../common/Input';
import { Button } from '../common/Button';
import { Tabs, Tab } from '../common/Tabs';
import { ErrorCard } from '../common/ErrorCard';
import { OptionChain } from '../options/OptionChain';
import { IVSmileChart } from '../options/IVSmileChart';
import { PayoffDiagram } from '../options/PayoffDiagram';
import { CalculatorPanel } from '../options/CalculatorPanel';
import { GreeksExplainer } from '../options/GreeksExplainer';
import { useTickers, useTickerDateRange, useOptionChain, useIVSmile, useUnderlyingOHLC, useUnderlyingLatest, useUnderlyingDaily } from '../../hooks/useOptionsData';
import { formatCurrency, formatPercent } from '../../utils/formatters';
import { recordRecentTicker } from './HomePage';

/**
 * Compact OHLC strip for the underlying on the selected quote date.
 * Helps users compare option premiums against where the stock actually
 * traded that day.
 */
function UnderlyingOHLCStrip({ ticker, date, ohlc, latest, expirationDate, expirationOhlc, loading, error }) {
  if (!date) return null;

  const cells = [
    { label: 'Open', value: ohlc?.open },
    { label: 'High', value: ohlc?.high },
    { label: 'Low', value: ohlc?.low },
    { label: 'Close', value: ohlc?.close },
  ];
  const range = ohlc?.high != null && ohlc?.low != null ? ohlc.high - ohlc.low : null;

  // Decide which comparison to show. If we know the expiration is in the
  // past (parent only sets expirationDate in that case), show the close on
  // expiry; otherwise show today's close. This means the comparison panel
  // is *always* meaningful for the selected chain — there's no state
  // where it silently disappears just because the expiration auto-select
  // hasn't fired yet, which was the source of the "card no longer
  // populates after I change the quote date" complaint.
  const isExpired = !!expirationDate;
  const compareSource = isExpired ? expirationOhlc : latest;
  const compareLoading = isExpired
    ? expirationDate && (expirationOhlc?.close == null)
    : !latest?.close;
  const compareDate = compareSource?.date;
  const compareClose = compareSource?.close;
  // Hide the comparison when there's literally nothing to compare against
  // (e.g., quote date is the most recent bar we have for an unexpired
  // chain, so latest.date === date — the move is zero by definition).
  const sameDay = compareDate && compareDate === date;
  const showCompare = !sameDay && (compareLoading || compareClose != null);

  const pctMove =
    compareClose != null && ohlc?.close != null && ohlc.close !== 0
      ? ((compareClose - ohlc.close) / ohlc.close) * 100
      : null;
  const moveColor =
    pctMove == null
      ? 'text-slate-400'
      : pctMove > 0
        ? 'text-emerald-400'
        : pctMove < 0
          ? 'text-rose-400'
          : 'text-slate-400';
  const moveArrow = pctMove == null ? '·' : pctMove > 0 ? '▲' : pctMove < 0 ? '▼' : '·';

  return (
    <CardLg className="mb-6">
      <div className="flex items-baseline justify-between mb-3 gap-3 flex-wrap">
        <h3 className="text-sm font-semibold text-slate-300">
          {ticker} on {date}
          {range != null && (
            <span className="ml-2 text-xs font-normal text-slate-500">
              · range {formatCurrency(range)}
            </span>
          )}
        </h3>
        <span className="text-xs text-slate-500">Underlying daily OHLC</span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {cells.map(({ label, value }) => (
          <div key={label} className="metric-card p-3">
            <div className="metric-label">{label}</div>
            {loading ? (
              <div className="skeleton h-6 w-2/3" />
            ) : value != null ? (
              <div className="metric-value text-lg">{formatCurrency(value)}</div>
            ) : (
              <div className="text-slate-500 text-sm">—</div>
            )}
          </div>
        ))}
      </div>
      {showCompare && (
        <div className="mt-4 pt-4 border-t border-slate-800/80">
          <div className="flex items-baseline justify-between gap-4 flex-wrap">
            <div>
              <div className="metric-label mb-1">
                {isExpired ? 'Price at expiration' : 'Price today'}
              </div>
              {compareLoading ? (
                <div className="skeleton h-7 w-32" />
              ) : (
                <div className="flex items-baseline gap-3 flex-wrap">
                  <span className="metric-value text-2xl">
                    {compareClose != null ? formatCurrency(compareClose) : '—'}
                  </span>
                  {compareDate && (
                    <span className="text-xs text-slate-500">on {compareDate}</span>
                  )}
                </div>
              )}
            </div>
            {pctMove != null && (
              <div className="text-right">
                <div className="metric-label mb-1">
                  vs {date} close
                </div>
                <div className={`text-lg font-semibold ${moveColor}`}>
                  {moveArrow} {pctMove >= 0 ? '+' : ''}{pctMove.toFixed(2)}%
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      {error && (
        <p className="mt-3 text-xs text-amber-400">
          Could not load underlying price for this date: {error}
        </p>
      )}
    </CardLg>
  );
}

/**
 * Put/Call segmented control.
 * Indigo-glow active style matching the AppSwitcher.
 */
function OptionTypeToggle({ value, onChange }) {
  const items = [
    { id: 'call', label: 'Calls' },
    { id: 'put', label: 'Puts' },
  ];
  return (
    <div
      role="tablist"
      aria-label="Option type"
      className="flex items-center gap-1 rounded-full border border-slate-700/60 bg-slate-900/60 backdrop-blur px-1 py-1 w-fit"
    >
      {items.map((item) => {
        const active = item.id === value;
        return (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={active}
            onClick={() => onChange(item.id)}
            className={
              'px-4 py-1 text-xs font-semibold rounded-full transition-colors ' +
              (active
                ? 'bg-indigo-500/20 text-indigo-300 ring-1 ring-indigo-500/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40')
            }
          >
            {item.label}
          </button>
        );
      })}
    </div>
  );
}

export function OptionsPage() {
  const [searchParams] = useSearchParams();
  const queryTicker = searchParams.get('ticker');

  const [selectedTicker, setSelectedTicker] = useState(queryTicker || 'AMD');
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedExpiration, setSelectedExpiration] = useState('');
  const [optionType, setOptionType] = useState('put');

  // React to ?ticker= changes
  useEffect(() => {
    if (queryTicker && queryTicker !== selectedTicker) {
      setSelectedTicker(queryTicker);
      setSelectedDate('');
      setSelectedExpiration('');
    }
  }, [queryTicker]);

  // Data hooks
  const tickers = useTickers();
  const dateRange = useTickerDateRange(selectedTicker);

  // Fetch chain with just ticker + date (expiration is optional for getting available expirations)
  const optionChain = useOptionChain(selectedTicker, selectedDate, selectedExpiration, optionType);
  const ivSmile = useIVSmile(selectedTicker, selectedDate, selectedExpiration, optionType);
  const underlying = useUnderlyingOHLC(selectedTicker, selectedDate);
  const underlyingLatest = useUnderlyingLatest(selectedTicker);

  // Expiration is stored as a timestamp string ("2024-12-20 00:00:00");
  // peel off just the date for downstream API calls.
  const expirationDateOnly = selectedExpiration ? selectedExpiration.split(' ')[0] : '';
  const todayStr = new Date().toISOString().slice(0, 10);
  const expirationInPast = expirationDateOnly && expirationDateOnly < todayStr;

  const expirationOhlc = useUnderlyingOHLC(
    expirationInPast ? selectedTicker : null,
    expirationInPast ? expirationDateOnly : ''
  );
  const lifetimeDaily = useUnderlyingDaily(
    expirationInPast ? selectedTicker : null,
    expirationInPast ? selectedDate : '',
    expirationInPast ? expirationDateOnly : ''
  );

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

  // Auto-select first expiration whenever the list of expirations changes
  // and the user hasn't picked one. Keying on a stable join (not just
  // length) is important: chains for different quote dates often have the
  // same NUMBER of expirations but different contents, and a length-only
  // dep would silently skip the re-select, leaving the page stuck in a
  // half-loaded state that only a hard refresh recovers from.
  const expirationsKey = expirations.join(',');
  useEffect(() => {
    if (expirations.length > 0 && !selectedExpiration) {
      setSelectedExpiration(expirations[0]);
    }
  }, [expirationsKey, selectedExpiration]);

  // Reset expiration when option type changes (chain repopulates)
  useEffect(() => {
    setSelectedExpiration('');
  }, [optionType]);

  // Record recent ticker visit
  useEffect(() => {
    if (selectedTicker) recordRecentTicker(selectedTicker);
  }, [selectedTicker]);

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
          <div className="flex items-center justify-between mb-4 gap-4 flex-wrap">
            <h2 className="text-base font-semibold text-slate-200">Select Data</h2>
            <OptionTypeToggle value={optionType} onChange={setOptionType} />
          </div>
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
              {' · '}
              <span className="text-indigo-400">{optionType === 'call' ? 'Calls' : 'Puts'}</span>
            </p>
          )}

          {dateRange.error && (
            <div className="mt-4">
              <ErrorCard error={dateRange.error} />
            </div>
          )}
        </CardLg>

        {/* Underlying OHLC for the selected quote date */}
        <UnderlyingOHLCStrip
          ticker={selectedTicker}
          date={selectedDate}
          ohlc={underlying.data}
          latest={underlyingLatest.data}
          expirationDate={expirationInPast ? expirationDateOnly : null}
          expirationOhlc={expirationOhlc.data}
          loading={underlying.loading}
          error={underlying.error}
        />

        {/* Error Messages */}
        {optionChain.error && (
          <ErrorCard error={optionChain.error} onRetry={() => optionChain.refetch()} />
        )}

        {/* Loading skeleton — keeps tab strip visible during refetch */}
        {optionChain.loading && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="metric-card">
                <div className="metric-label">&nbsp;</div>
                <div className="skeleton h-6 w-3/4" />
              </div>
            ))}
          </div>
        )}

        {/* Main Content Tabs */}
        <Tabs defaultTab={0}>
          <Tab label="Option Chain">
            {filteredChainData?.data?.length ? (
              <CardLg>
                <OptionChain
                  ticker={selectedTicker}
                  optionData={filteredChainData}
                  optionType={optionType}
                  dailyCloses={expirationInPast ? lifetimeDaily.data : null}
                  expirationDate={expirationInPast ? expirationDateOnly : null}
                  quoteDate={expirationInPast ? selectedDate : null}
                  quoteClose={underlying.data?.close ?? null}
                />
              </CardLg>
            ) : (
              <CardLg>
                <div className="flex items-center justify-center py-16">
                  <div className="text-center max-w-md">
                    <FileSearch className="w-12 h-12 text-slate-600 mx-auto mb-4" strokeWidth={1.5} />
                    <p className="text-slate-300 font-semibold mb-1">
                      {!selectedDate ? 'Loading available dates…' : 'No chain loaded yet'}
                    </p>
                    <p className="text-slate-500 text-sm">
                      Pick a ticker, quote date, and expiration above, then click Load Data.
                    </p>
                  </div>
                </div>
              </CardLg>
            )}
          </Tab>

          <Tab label="IV Smile">
            {ivSmile.data?.data?.length ? (
              <CardLg>
                <IVSmileChart ticker={selectedTicker} ivSmileData={ivSmile.data} />
              </CardLg>
            ) : (
              <CardLg>
                <div className="flex items-center justify-center py-16">
                  <div className="text-center max-w-md">
                    <ChevronsRight className="w-12 h-12 text-slate-600 mx-auto mb-4" strokeWidth={1.5} />
                    <p className="text-slate-300 font-semibold mb-1">No IV smile yet</p>
                    <p className="text-slate-500 text-sm">
                      Select a ticker, quote date, and expiration to view the IV smile.
                    </p>
                  </div>
                </div>
              </CardLg>
            )}
          </Tab>

          <Tab label="Payoff Diagram">
            <CardLg>
              <PayoffDiagram chainData={filteredChainData} optionType={optionType} />
            </CardLg>
          </Tab>

          <Tab label="Calculators">
            <CardLg>
              <CalculatorPanel optionType={optionType} />
            </CardLg>
          </Tab>

          <Tab label="Greeks Guide">
            <CardLg>
              <GreeksExplainer />
            </CardLg>
          </Tab>
        </Tabs>

        {/* Disclaimer */}
        <div className="warning-box mt-8">
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
