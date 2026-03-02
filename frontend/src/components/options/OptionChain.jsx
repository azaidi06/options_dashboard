/**
 * Option Chain Table - Display and explore option chain data
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
      <div className="text-gray-500 text-center py-8">
        Select a date and expiration to view the option chain
      </div>
    );
  }

  // Filter and sort data
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

    // Sort
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
    if (sortBy !== column) return <span className="text-gray-300">↕</span>;
    return <span>{sortDir === 'asc' ? '↑' : '↓'}</span>;
  };

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 text-gray-900">
        {ticker} Option Chain
      </h3>

      {/* Filters */}
      <CardLg className="mb-6">
        <h4 className="text-md font-semibold mb-4 text-gray-900">Filters</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            label="Strike Filter (±$5 range)"
            value={strikeFilter}
            onChange={setStrikeFilter}
            type="number"
            placeholder="e.g., 100"
          />
          <Input
            label="Delta Filter (±0.1 range)"
            value={deltaFilter}
            onChange={setDeltaFilter}
            type="number"
            step="0.05"
            placeholder="e.g., 0.50"
            min="0"
            max="1"
          />
          <button
            onClick={() => {
              setStrikeFilter('');
              setDeltaFilter('');
            }}
            className="btn-secondary h-10 mt-6"
          >
            Clear Filters
          </button>
        </div>
      </CardLg>

      {/* Results */}
      <CardLg>
        <div className="mb-4 text-sm text-gray-600">
          Showing {filteredData.length} of {optionData.data.length} contracts
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-100 border-b border-gray-300 sticky top-0">
              <tr>
                <th
                  onClick={() => handleSort('strike')}
                  className="px-4 py-2 text-left font-semibold cursor-pointer hover:bg-gray-200"
                >
                  Strike <SortIcon column="strike" />
                </th>
                <th
                  onClick={() => handleSort('mark')}
                  className="px-4 py-2 text-left font-semibold cursor-pointer hover:bg-gray-200"
                >
                  Mark <SortIcon column="mark" />
                </th>
                <th
                  onClick={() => handleSort('bid')}
                  className="px-4 py-2 text-left font-semibold cursor-pointer hover:bg-gray-200"
                >
                  Bid <SortIcon column="bid" />
                </th>
                <th
                  onClick={() => handleSort('ask')}
                  className="px-4 py-2 text-left font-semibold cursor-pointer hover:bg-gray-200"
                >
                  Ask <SortIcon column="ask" />
                </th>
                <th
                  onClick={() => handleSort('implied_volatility')}
                  className="px-4 py-2 text-left font-semibold cursor-pointer hover:bg-gray-200"
                >
                  IV <SortIcon column="implied_volatility" />
                </th>
                <th
                  onClick={() => handleSort('delta')}
                  className="px-4 py-2 text-left font-semibold cursor-pointer hover:bg-gray-200"
                >
                  Delta <SortIcon column="delta" />
                </th>
                <th
                  onClick={() => handleSort('gamma')}
                  className="px-4 py-2 text-left font-semibold cursor-pointer hover:bg-gray-200"
                >
                  Gamma <SortIcon column="gamma" />
                </th>
                <th
                  onClick={() => handleSort('theta')}
                  className="px-4 py-2 text-left font-semibold cursor-pointer hover:bg-gray-200"
                >
                  Theta <SortIcon column="theta" />
                </th>
                <th
                  onClick={() => handleSort('vega')}
                  className="px-4 py-2 text-left font-semibold cursor-pointer hover:bg-gray-200"
                >
                  Vega <SortIcon column="vega" />
                </th>
                <th className="px-4 py-2 text-left font-semibold">OI</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredData.length === 0 ? (
                <tr>
                  <td colSpan="10" className="px-4 py-4 text-center text-gray-500">
                    No contracts match the selected filters
                  </td>
                </tr>
              ) : (
                filteredData.map((opt, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-2 font-semibold">${opt.strike?.toFixed(2)}</td>
                    <td className="px-4 py-2 font-mono">${opt.mark?.toFixed(2)}</td>
                    <td className="px-4 py-2 font-mono text-green-600">
                      ${opt.bid?.toFixed(2)}
                    </td>
                    <td className="px-4 py-2 font-mono text-red-600">
                      ${opt.ask?.toFixed(2)}
                    </td>
                    <td className="px-4 py-2">{((opt.implied_volatility || 0) * 100).toFixed(1)}%</td>
                    <td className="px-4 py-2 text-blue-600">
                      {(opt.delta || 0).toFixed(3)}
                    </td>
                    <td className="px-4 py-2 text-purple-600">
                      {(opt.gamma || 0).toFixed(4)}
                    </td>
                    <td className="px-4 py-2 text-orange-600">
                      {(opt.theta || 0).toFixed(4)}
                    </td>
                    <td className="px-4 py-2 text-green-600">
                      {(opt.vega || 0).toFixed(4)}
                    </td>
                    <td className="px-4 py-2">{opt.open_interest?.toLocaleString() || '—'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Legend */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-5 gap-4 text-xs text-gray-600 bg-gray-50 p-4 rounded">
          <div><strong>Mark:</strong> Mid-point of bid/ask</div>
          <div><strong>IV:</strong> Implied volatility %</div>
          <div><strong>Delta:</strong> Price sensitivity (negative for puts)</div>
          <div><strong>Gamma:</strong> Delta change rate</div>
          <div><strong>Theta:</strong> Daily time decay</div>
          <div><strong>Vega:</strong> Volatility sensitivity</div>
          <div><strong>OI:</strong> Open interest (contracts)</div>
        </div>
      </CardLg>
    </div>
  );
}
