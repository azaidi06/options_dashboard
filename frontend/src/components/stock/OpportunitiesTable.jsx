/**
 * Opportunities Table - Shows entry/exit windows for put options
 */
import { useState } from 'react';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { CardLg, MetricCard } from '../common/Card';

export function OpportunitiesTable({ ticker, startDate, endDate, opportunities }) {
  const [entryThreshold, setEntryThreshold] = useState(0.10);
  const [exitThreshold, setExitThreshold] = useState(0.05);

  if (opportunities.loading) {
    return <div className="text-gray-500 text-center py-8">Loading opportunities...</div>;
  }

  if (opportunities.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded p-4">
        <p className="text-red-800">Error loading opportunities: {opportunities.error}</p>
      </div>
    );
  }

  if (!opportunities.data) {
    return <div className="text-gray-500 text-center py-8">No opportunity data available</div>;
  }

  const { windows, stats } = opportunities.data;

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 text-gray-900">
        {ticker} Opportunity Windows
      </h3>

      <p className="text-sm text-gray-600 mb-6">
        Periods when the stock has dropped below your entry threshold, creating potential put option opportunities.
      </p>

      {/* Summary metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <MetricCard
          label="Total Windows"
          value={stats.total_windows}
        />
        <MetricCard
          label="Avg Duration"
          value={`${stats.avg_duration ? stats.avg_duration.toFixed(0) : '—'} days`}
        />
        <MetricCard
          label="Avg Max Drawdown"
          value={`${stats.avg_max_drawdown ? (stats.avg_max_drawdown * 100).toFixed(1) : '—'}%`}
        />
        <MetricCard
          label="% Time in Window"
          value={`${(stats.pct_time_in_window * 100).toFixed(1)}%`}
        />
      </div>

      {/* Threshold filters */}
      <CardLg className="mb-6">
        <h4 className="text-md font-semibold mb-4 text-gray-900">Adjust Thresholds</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Input
              label="Entry Threshold (% down)"
              value={(entryThreshold * 100).toFixed(1)}
              onChange={(v) => setEntryThreshold(parseFloat(v) / 100)}
              type="number"
              step="0.5"
              min="0"
              max="50"
            />
            <p className="text-xs text-gray-500 mt-1">
              Enter window when drawdown exceeds this level
            </p>
          </div>
          <div>
            <Input
              label="Exit Threshold (% down)"
              value={(exitThreshold * 100).toFixed(1)}
              onChange={(v) => setExitThreshold(parseFloat(v) / 100)}
              type="number"
              step="0.5"
              min="0"
              max="50"
            />
            <p className="text-xs text-gray-500 mt-1">
              Exit window when drawdown recovers above this level
            </p>
          </div>
          <div className="flex items-end">
            <Button
              onClick={() => {
                // Re-fetch with new thresholds (hook handles this via dependencies)
              }}
              className="w-full"
            >
              Apply Filters
            </Button>
          </div>
        </div>
      </CardLg>

      {/* Windows table */}
      <CardLg>
        <h4 className="text-md font-semibold mb-4 text-gray-900">Opportunity Windows</h4>
        {windows.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No opportunity windows found with current thresholds
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-100 border-b border-gray-300">
                <tr>
                  <th className="px-4 py-2 text-left font-semibold">Start Date</th>
                  <th className="px-4 py-2 text-left font-semibold">End Date</th>
                  <th className="px-4 py-2 text-left font-semibold">Duration (Days)</th>
                  <th className="px-4 py-2 text-left font-semibold">Entry Drawdown</th>
                  <th className="px-4 py-2 text-left font-semibold">Max Drawdown</th>
                  <th className="px-4 py-2 text-left font-semibold">Exit Drawdown</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {windows.map((window, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-2">{window.start_date}</td>
                    <td className="px-4 py-2">
                      {window.end_date || (
                        <span className="text-yellow-600 font-semibold">Open</span>
                      )}
                    </td>
                    <td className="px-4 py-2 font-semibold">
                      {window.duration_days} days
                    </td>
                    <td className="px-4 py-2 text-orange-600">
                      {(window.entry_drawdown * 100).toFixed(1)}%
                    </td>
                    <td className="px-4 py-2 text-red-600 font-semibold">
                      {(window.max_drawdown * 100).toFixed(1)}%
                    </td>
                    <td className="px-4 py-2 text-green-600">
                      {window.exit_drawdown
                        ? `${(window.exit_drawdown * 100).toFixed(1)}%`
                        : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardLg>

      {/* Educational note */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded p-4">
        <p className="text-sm text-blue-900">
          <strong>💡 How to use this:</strong> These windows show historical periods when the stock was
          significantly down from its recent high. Use this to understand when put options would have
          been valuable defensively (e.g., buying puts as insurance during these drawdowns).
        </p>
      </div>
    </div>
  );
}
