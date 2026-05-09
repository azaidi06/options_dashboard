/**
 * Option Chain Table - dark theme.
 * Filters out illiquid/sentinel rows by default and surfaces a quality badge.
 */
import { useState, useMemo, Fragment } from 'react';
import { LineChart, Line, ReferenceLine, Tooltip, ResponsiveContainer, YAxis } from 'recharts';
import { Input } from '../common/Input';
import { CardLg } from '../common/Card';
import { formatCurrency, formatPercent, formatGreek } from '../../utils/formatters';
import { useContractHistory } from '../../hooks/useOptionsData';

function isITM(close, strike, optionType) {
  if (close == null || strike == null) return false;
  return optionType === 'call' ? close > strike : close < strike;
}

function ItmSparkline({
  ticker,
  dailyCloses,
  strike,
  optionType,
  expirationDate,
  quoteDate,
  entryMark,
  entryAsk,
}) {
  const series = dailyCloses.map((r) => ({
    date: r.date,
    close: r.close,
    itm: isITM(r.close, strike, optionType),
  }));
  const itmCount = series.filter((p) => p.itm).length;
  const total = series.length;
  const expirationItm = total > 0 && series[total - 1].itm;

  // Fetch the per-day premium history for this contract. The hook is
  // wired to its own SWR key, so each row that gets expanded fetches
  // independently and is cached for 5 minutes.
  const history = useContractHistory(
    ticker,
    strike,
    expirationDate,
    optionType,
    quoteDate,
    expirationDate
  );

  return (
    <div>
      <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1 mb-2 text-xs">
        <span className="text-slate-300">
          Strike <span className="font-semibold">{formatCurrency(strike, 2)}</span>
        </span>
        <span className="text-slate-400">
          Closed ITM on{' '}
          <span className="text-emerald-400 font-semibold">{itmCount}</span> of {total} trading
          days ({formatPercent(total ? (itmCount / total) * 100 : 0, 0)})
        </span>
        {expirationDate && (
          <span className="text-slate-400">
            At expiry:{' '}
            <span
              className={
                expirationItm ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold'
              }
            >
              {expirationItm ? 'ITM' : 'OTM'}
            </span>
          </span>
        )}
      </div>
      <div style={{ width: '100%', height: 120 }}>
        <ResponsiveContainer>
          <LineChart data={series} margin={{ top: 8, right: 12, left: 12, bottom: 8 }}>
            <YAxis
              domain={['auto', 'auto']}
              hide
            />
            <Tooltip
              contentStyle={{
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: 6,
                fontSize: 12,
              }}
              labelStyle={{ color: '#cbd5e1' }}
              formatter={(value) => [formatCurrency(value, 2), 'Close']}
            />
            <ReferenceLine
              y={strike}
              stroke="#f59e0b"
              strokeDasharray="4 4"
              label={{
                value: `Strike ${formatCurrency(strike, 2)}`,
                position: 'right',
                fill: '#f59e0b',
                fontSize: 11,
              }}
            />
            <Line
              type="monotone"
              dataKey="close"
              stroke="#6366f1"
              strokeWidth={2}
              dot={(props) => {
                const { cx, cy, payload } = props;
                if (cx == null || cy == null) return null;
                return (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={2.5}
                    fill={payload.itm ? '#10b981' : '#475569'}
                    stroke="none"
                  />
                );
              }}
              activeDot={{ r: 4 }}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <PnlSparkline
        history={history}
        entryMark={entryMark}
        entryAsk={entryAsk}
        expirationDate={expirationDate}
      />
    </div>
  );
}

function PnlSparkline({ history, entryMark, entryAsk, expirationDate }) {
  // Use mid (mark) as the "entry premium" by default; users buying long
  // would actually pay closer to ask, so we surface both summaries.
  const entry = entryMark != null && entryMark > 0 ? entryMark : entryAsk;
  const rows = history.data?.data || [];

  if (history.loading) {
    return <div className="mt-3 text-xs text-slate-500">Loading P/L history…</div>;
  }
  if (history.error) {
    return (
      <div className="mt-3 text-xs text-amber-400">
        Could not load P/L history: {history.error}
      </div>
    );
  }
  if (!entry || rows.length === 0) {
    return (
      <div className="mt-3 text-xs text-slate-500">
        No premium history available for this contract.
      </div>
    );
  }

  const series = rows
    .filter((r) => r.mark != null)
    .map((r) => ({
      date: r.date,
      premium: r.mark,
      // P/L per share if you'd sold on this day, in dollars
      plShare: r.mark - entry,
      // P/L per contract (1 contract = 100 shares)
      plContract: (r.mark - entry) * 100,
    }));

  if (series.length === 0) {
    return (
      <div className="mt-3 text-xs text-slate-500">
        No usable premium quotes in this window.
      </div>
    );
  }

  // Use ask as a more conservative buy price for the secondary "long buyer
  // bought at ask" framing. Sellers would typically receive bid; we keep
  // the bid framing implicit (the user can read the chart's premium line).
  const finalRow = series[series.length - 1];
  const plAtExpiry = finalRow.plContract;
  const best = series.reduce((acc, p) => (p.plContract > acc.plContract ? p : acc), series[0]);
  const worst = series.reduce((acc, p) => (p.plContract < acc.plContract ? p : acc), series[0]);
  const plPctAtExpiry = entry > 0 ? (finalRow.plShare / entry) * 100 : null;

  const plColor = (v) =>
    v == null
      ? 'text-slate-400'
      : v > 0
        ? 'text-emerald-400'
        : v < 0
          ? 'text-rose-400'
          : 'text-slate-400';
  const sign = (v) => (v == null ? '' : v >= 0 ? '+' : '');

  return (
    <div className="mt-4 pt-4 border-t border-slate-800/80">
      <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1 mb-2 text-xs">
        <span className="text-slate-300">
          Entered at{' '}
          <span className="font-semibold">{formatCurrency(entry, 2)}</span>
          <span className="text-slate-500"> /sh · ${(entry * 100).toFixed(0)} /contract</span>
        </span>
        <span className={plColor(plAtExpiry) + ' font-semibold'}>
          At expiry{expirationDate ? ` (${expirationDate})` : ''}: {sign(plAtExpiry)}
          {formatCurrency(plAtExpiry, 0)}
          {plPctAtExpiry != null && (
            <span className="text-slate-500 ml-1 font-normal">
              ({sign(plPctAtExpiry)}{plPctAtExpiry.toFixed(1)}%)
            </span>
          )}
        </span>
        <span className={plColor(best.plContract)}>
          Best: {sign(best.plContract)}
          {formatCurrency(best.plContract, 0)}
          <span className="text-slate-500 ml-1">on {best.date}</span>
        </span>
        <span className={plColor(worst.plContract)}>
          Worst: {sign(worst.plContract)}
          {formatCurrency(worst.plContract, 0)}
          <span className="text-slate-500 ml-1">on {worst.date}</span>
        </span>
      </div>
      <div style={{ width: '100%', height: 110 }}>
        <ResponsiveContainer>
          <LineChart data={series} margin={{ top: 8, right: 12, left: 12, bottom: 8 }}>
            <YAxis domain={['auto', 'auto']} hide />
            <Tooltip
              contentStyle={{
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: 6,
                fontSize: 12,
              }}
              labelStyle={{ color: '#cbd5e1' }}
              formatter={(value, key) => {
                if (key === 'premium') return [formatCurrency(value, 2), 'Premium'];
                if (key === 'plContract') {
                  return [
                    `${value >= 0 ? '+' : ''}${formatCurrency(value, 0)} /contract`,
                    'P/L if sold',
                  ];
                }
                return [value, key];
              }}
            />
            <ReferenceLine
              y={0}
              stroke="#475569"
              strokeDasharray="4 4"
              label={{
                value: 'Break-even',
                position: 'right',
                fill: '#64748b',
                fontSize: 11,
              }}
            />
            <Line
              type="monotone"
              dataKey="plContract"
              stroke="#10b981"
              strokeWidth={2}
              dot={(props) => {
                const { cx, cy, payload } = props;
                if (cx == null || cy == null) return null;
                return (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={2.5}
                    fill={payload.plContract >= 0 ? '#10b981' : '#f43f5e'}
                    stroke="none"
                  />
                );
              }}
              activeDot={{ r: 4 }}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function isStaleRow(opt) {
  const iv = (opt.implied_volatility || 0) * 100;
  const bid = opt.bid || 0;
  const ask = opt.ask || 0;
  return iv > 200 || (bid === 0 && ask < 0.05);
}

function isLiquidRow(opt) {
  const oi = opt.open_interest || 0;
  const iv = (opt.implied_volatility || 0) * 100;
  return oi > 50 && iv < 100;
}

function breakEvenFor(strike, premium, optionType) {
  if (strike == null || premium == null) return null;
  return optionType === 'call' ? strike + premium : strike - premium;
}

export function OptionChain({
  ticker,
  optionData,
  optionType = 'put',
  dailyCloses = null,
  expirationDate = null,
  quoteDate = null,
  quoteClose = null,
}) {
  const [strikeFilter, setStrikeFilter] = useState('');
  const [deltaFilter, setDeltaFilter] = useState('');
  const [sortBy, setSortBy] = useState('strike');
  const [sortDir, setSortDir] = useState('asc');
  const [showStale, setShowStale] = useState(false);
  const [expandedStrike, setExpandedStrike] = useState(null);

  const showItmColumn = Array.isArray(dailyCloses) && dailyCloses.length > 0;
  const showBreakEvenColumn = quoteClose != null && quoteClose > 0;

  if (!optionData || !optionData.data) {
    return (
      <div className="text-slate-500 text-center py-8">
        Select a date and expiration to view the option chain
      </div>
    );
  }

  // Apply quality filter first; everything downstream operates on the visible set.
  const { qualityFiltered, hiddenCount } = useMemo(() => {
    const all = optionData.data || [];
    if (showStale) return { qualityFiltered: all, hiddenCount: 0 };
    const visible = all.filter((opt) => !isStaleRow(opt));
    return { qualityFiltered: visible, hiddenCount: all.length - visible.length };
  }, [optionData.data, showStale]);

  const filteredData = useMemo(() => {
    let filtered = qualityFiltered;

    if (strikeFilter) {
      const strikeVal = parseFloat(strikeFilter);
      filtered = filtered.filter((opt) => opt.strike >= strikeVal - 5 && opt.strike <= strikeVal + 5);
    }

    if (deltaFilter) {
      const deltaVal = parseFloat(deltaFilter);
      filtered = filtered.filter((opt) => {
        const d = Math.abs(opt.delta || 0);
        return d >= deltaVal - 0.1 && d <= deltaVal + 0.1;
      });
    }

    filtered = [...filtered].sort((a, b) => {
      let aVal = a[sortBy] || 0;
      let bVal = b[sortBy] || 0;
      if (typeof aVal === 'string') aVal = parseFloat(aVal) || 0;
      if (typeof bVal === 'string') bVal = parseFloat(bVal) || 0;
      return sortDir === 'asc' ? aVal - bVal : bVal - aVal;
    });

    return filtered;
  }, [qualityFiltered, strikeFilter, deltaFilter, sortBy, sortDir]);

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortDir('asc');
    }
  };

  const SortIcon = ({ column }) => {
    if (sortBy !== column) return <span className="text-slate-600">↕</span>;
    return <span className="text-indigo-400">{sortDir === 'asc' ? '↑' : '↓'}</span>;
  };

  return (
    <div>
      <h3 className="text-base font-semibold mb-4 text-slate-200">{ticker} Option Chain</h3>

      {/* Filters */}
      <CardLg className="mb-6">
        <h4 className="text-sm font-semibold mb-4 text-slate-300">Filters</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            label="Strike Filter (±$5)"
            value={strikeFilter}
            onChange={setStrikeFilter}
            type="number"
            placeholder="e.g., 100"
          />
          <Input
            label="Delta Filter (±0.1)"
            value={deltaFilter}
            onChange={setDeltaFilter}
            type="number"
            step="0.05"
            placeholder="e.g., 0.50"
            min="0"
            max="1"
          />
          <div className="flex items-end">
            <button
              onClick={() => { setStrikeFilter(''); setDeltaFilter(''); }}
              className="btn-secondary w-full"
            >
              Clear Filters
            </button>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={showStale}
              onChange={(e) => setShowStale(e.target.checked)}
              className="w-4 h-4 rounded border-slate-600 bg-slate-800 text-indigo-500 focus:ring-indigo-500/50"
            />
            <span>Show stale/illiquid options</span>
          </label>
          {hiddenCount > 0 && !showStale && (
            <span className="badge badge-yellow">
              {hiddenCount} row{hiddenCount === 1 ? '' : 's'} hidden by quality filter
            </span>
          )}
          <span className="text-xs text-slate-500">
            Quality filter hides rows with IV &gt; 200% or bid=0 &amp; ask&lt;$0.05.
          </span>
        </div>
      </CardLg>

      {/* Results */}
      <CardLg>
        <div className="mb-4 text-sm text-slate-400">
          Showing {filteredData.length} of {qualityFiltered.length}
          {!showStale && hiddenCount > 0 && (
            <span className="text-slate-500"> (after quality filter; {optionData.data.length} total)</span>
          )}{' '}
          contracts
        </div>

        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Quality</th>
                {[
                  ['strike', 'Strike'],
                  ['mark', 'Mark'],
                  ['bid', 'Bid'],
                  ['ask', 'Ask'],
                ].map(([key, label]) => (
                  <th
                    key={key}
                    onClick={() => handleSort(key)}
                    className="cursor-pointer hover:text-slate-200 select-none"
                  >
                    {label} <SortIcon column={key} />
                  </th>
                ))}
                {showBreakEvenColumn && (
                  <th title={`Break-even = ${optionType === 'call' ? 'strike + mark' : 'strike − mark'}; % shows move from underlying close on the quote date needed to reach it`}>
                    BE / %
                  </th>
                )}
                {[
                  ['implied_volatility', 'IV'],
                  ['delta', 'Delta'],
                  ['gamma', 'Gamma'],
                  ['theta', 'Theta'],
                  ['vega', 'Vega'],
                ].map(([key, label]) => (
                  <th
                    key={key}
                    onClick={() => handleSort(key)}
                    className="cursor-pointer hover:text-slate-200 select-none"
                  >
                    {label} <SortIcon column={key} />
                  </th>
                ))}
                <th>OI</th>
                {showItmColumn && <th title="Days the underlying closed ITM during the option's lifetime">ITM days</th>}
              </tr>
            </thead>
            <tbody>
              {filteredData.length === 0 ? (
                <tr>
                  <td colSpan={11 + (showItmColumn ? 1 : 0) + (showBreakEvenColumn ? 1 : 0)} className="text-center text-slate-500 py-6">
                    No contracts match the selected filters
                  </td>
                </tr>
              ) : (
                filteredData.map((opt, idx) => {
                  const liquid = isLiquidRow(opt);
                  const ivPct = (opt.implied_volatility || 0) * 100;
                  const bid = opt.bid || 0;
                  const ask = opt.ask || 0;
                  const noQuote = bid === 0 && ask === 0;
                  const itmCount = showItmColumn
                    ? dailyCloses.reduce(
                        (n, r) => n + (isITM(r.close, opt.strike, optionType) ? 1 : 0),
                        0
                      )
                    : null;
                  const totalDays = showItmColumn ? dailyCloses.length : null;
                  const itmPct = totalDays ? (itmCount / totalDays) * 100 : null;
                  const isExpanded = expandedStrike === opt.strike;
                  return (
                    <Fragment key={idx}>
                      <tr
                        onClick={() =>
                          showItmColumn
                            ? setExpandedStrike(isExpanded ? null : opt.strike)
                            : null
                        }
                        className={
                          showItmColumn
                            ? 'cursor-pointer hover:bg-slate-800/40 transition-colors'
                            : ''
                        }
                      >
                        <td>
                          <span
                            className={`inline-block w-2.5 h-2.5 rounded-full ${
                              liquid ? 'bg-emerald-500' : 'bg-slate-500'
                            }`}
                            title={liquid ? 'Liquid (OI > 50, IV < 100%)' : 'Stale or illiquid'}
                          />
                        </td>
                        <td className="font-semibold text-slate-200">
                          {showItmColumn && (
                            <span className="inline-block w-3 text-slate-500 mr-1">
                              {isExpanded ? '▾' : '▸'}
                            </span>
                          )}
                          {formatCurrency(opt.strike, 2)}
                        </td>
                        <td className="font-mono">
                          {noQuote ? '—' : formatCurrency(opt.mark, 2)}
                        </td>
                        <td className="font-mono text-emerald-400">
                          {noQuote ? '—' : formatCurrency(opt.bid, 2)}
                        </td>
                        <td className="font-mono text-red-400">
                          {noQuote ? '—' : formatCurrency(opt.ask, 2)}
                        </td>
                        {showBreakEvenColumn && (() => {
                          const be = breakEvenFor(opt.strike, opt.mark, optionType);
                          if (be == null || noQuote) {
                            return <td className="text-slate-500">—</td>;
                          }
                          const pct = ((be - quoteClose) / quoteClose) * 100;
                          // For a long buyer to reach BE, the underlying
                          // needs to move toward BE. "Toward" means up for
                          // calls, down for puts; render that direction
                          // with a sign that matches the user's mental
                          // model: positive => stock needs to rise, negative
                          // => stock needs to fall.
                          const directional =
                            optionType === 'call' ? pct : -pct;
                          const alreadyPast = directional <= 0;
                          const colorClass = alreadyPast
                            ? 'text-emerald-400'
                            : 'text-amber-400';
                          const arrow =
                            optionType === 'call' ? '▲' : '▼';
                          return (
                            <td className="font-mono">
                              <span className="text-slate-200">
                                {formatCurrency(be, 2)}
                              </span>
                              <span className={`ml-2 text-xs ${colorClass}`}>
                                {alreadyPast ? '✓ past' : (
                                  <>
                                    {arrow} {Math.abs(directional).toFixed(2)}%
                                  </>
                                )}
                              </span>
                            </td>
                          );
                        })()}
                        <td>
                          {ivPct > 200
                            ? formatPercent(ivPct, 0)
                            : formatPercent(ivPct, 1)}
                        </td>
                        <td className="text-blue-400">{formatGreek(opt.delta, 'delta')}</td>
                        <td className="text-purple-400">{formatGreek(opt.gamma, 'gamma')}</td>
                        <td className="text-amber-400">{formatGreek(opt.theta, 'theta')}</td>
                        <td className="text-emerald-400">{formatGreek(opt.vega, 'vega')}</td>
                        <td>
                          {opt.open_interest != null
                            ? Number(opt.open_interest).toLocaleString()
                            : '—'}
                        </td>
                        {showItmColumn && (
                          <td className="font-mono">
                            <span className={itmCount > 0 ? 'text-emerald-400' : 'text-slate-500'}>
                              {itmCount}
                            </span>
                            <span className="text-slate-600"> / {totalDays}</span>
                            <span className="text-slate-500 ml-1">
                              ({formatPercent(itmPct, 0)})
                            </span>
                          </td>
                        )}
                      </tr>
                      {showItmColumn && isExpanded && (
                        <tr className="bg-slate-900/40">
                          <td colSpan={11 + (showItmColumn ? 1 : 0) + (showBreakEvenColumn ? 1 : 0)} className="p-4">
                            <ItmSparkline
                              ticker={ticker}
                              dailyCloses={dailyCloses}
                              strike={opt.strike}
                              optionType={optionType}
                              expirationDate={expirationDate}
                              quoteDate={quoteDate}
                              entryMark={opt.mark}
                              entryAsk={opt.ask}
                            />
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Legend */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs text-slate-500 bg-slate-800/40 p-4 rounded-lg">
          <div>
            <strong className="text-slate-400">Quality:</strong>{' '}
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 align-middle mr-1" />
            liquid /{' '}
            <span className="inline-block w-2 h-2 rounded-full bg-slate-500 align-middle mx-1" />
            stale
          </div>
          <div><strong className="text-slate-400">Mark:</strong> Bid/ask mid-point</div>
          <div><strong className="text-slate-400">IV:</strong> Implied volatility</div>
          <div><strong className="text-slate-400">Delta:</strong> Price sensitivity</div>
          <div><strong className="text-slate-400">Gamma:</strong> Delta change rate</div>
          <div><strong className="text-slate-400">Theta:</strong> Daily time decay</div>
          <div><strong className="text-slate-400">Vega:</strong> Volatility sensitivity</div>
          <div><strong className="text-slate-400">OI:</strong> Open interest</div>
        </div>
      </CardLg>
    </div>
  );
}
