/**
 * Option Chain Table - dark theme.
 * Filters out illiquid/sentinel rows by default and surfaces a quality badge.
 */
import { useState, useMemo } from 'react';
import { Input } from '../common/Input';
import { CardLg } from '../common/Card';
import { formatCurrency, formatPercent, formatGreek } from '../../utils/formatters';

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

export function OptionChain({ ticker, optionData }) {
  const [strikeFilter, setStrikeFilter] = useState('');
  const [deltaFilter, setDeltaFilter] = useState('');
  const [sortBy, setSortBy] = useState('strike');
  const [sortDir, setSortDir] = useState('asc');
  const [showStale, setShowStale] = useState(false);

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
              </tr>
            </thead>
            <tbody>
              {filteredData.length === 0 ? (
                <tr>
                  <td colSpan="11" className="text-center text-slate-500 py-6">
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
                  return (
                    <tr key={idx}>
                      <td>
                        <span
                          className={`inline-block w-2.5 h-2.5 rounded-full ${
                            liquid ? 'bg-emerald-500' : 'bg-slate-500'
                          }`}
                          title={liquid ? 'Liquid (OI > 50, IV < 100%)' : 'Stale or illiquid'}
                        />
                      </td>
                      <td className="font-semibold text-slate-200">
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
                    </tr>
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
