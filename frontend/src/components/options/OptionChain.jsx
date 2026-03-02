/**
 * Option Chain Table - dark theme
 */
import { useState, useMemo } from 'react';
import { Input } from '../common/Input';
import { CardLg } from '../common/Card';

export function OptionChain({ ticker, optionData }) {
  const [strikeFilter, setStrikeFilter] = useState('');
  const [deltaFilter, setDeltaFilter] = useState('');
  const [sortBy, setSortBy] = useState('strike');
  const [sortDir, setSortDir] = useState('asc');

  if (!optionData || !optionData.data) {
    return (
      <div className="text-slate-500 text-center py-8">
        Select a date and expiration to view the option chain
      </div>
    );
  }

  const filteredData = useMemo(() => {
    let filtered = optionData.data;

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

    filtered.sort((a, b) => {
      let aVal = a[sortBy] || 0;
      let bVal = b[sortBy] || 0;
      if (typeof aVal === 'string') aVal = parseFloat(aVal) || 0;
      if (typeof bVal === 'string') bVal = parseFloat(bVal) || 0;
      return sortDir === 'asc' ? aVal - bVal : bVal - aVal;
    });

    return filtered;
  }, [optionData.data, strikeFilter, deltaFilter, sortBy, sortDir]);

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
      </CardLg>

      {/* Results */}
      <CardLg>
        <div className="mb-4 text-sm text-slate-400">
          Showing {filteredData.length} of {optionData.data.length} contracts
        </div>

        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
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
                  <td colSpan="10" className="text-center text-slate-500 py-6">
                    No contracts match the selected filters
                  </td>
                </tr>
              ) : (
                filteredData.map((opt, idx) => (
                  <tr key={idx}>
                    <td className="font-semibold text-slate-200">${opt.strike?.toFixed(2)}</td>
                    <td className="font-mono">${opt.mark?.toFixed(2)}</td>
                    <td className="font-mono text-emerald-400">${opt.bid?.toFixed(2)}</td>
                    <td className="font-mono text-red-400">${opt.ask?.toFixed(2)}</td>
                    <td>{((opt.implied_volatility || 0) * 100).toFixed(1)}%</td>
                    <td className="text-blue-400">{(opt.delta || 0).toFixed(3)}</td>
                    <td className="text-purple-400">{(opt.gamma || 0).toFixed(4)}</td>
                    <td className="text-amber-400">{(opt.theta || 0).toFixed(4)}</td>
                    <td className="text-emerald-400">{(opt.vega || 0).toFixed(4)}</td>
                    <td>{opt.open_interest?.toLocaleString() || '\u2014'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Legend */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs text-slate-500 bg-slate-800/40 p-4 rounded-lg">
          <div><strong className="text-slate-400">Mark:</strong> Bid/ask mid-point</div>
          <div><strong className="text-slate-400">IV:</strong> Implied volatility %</div>
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
