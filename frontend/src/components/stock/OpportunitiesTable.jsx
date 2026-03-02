/**
 * Opportunities Table - dark theme
 */
import { Input } from '../common/Input';
import { CardLg, MetricCard } from '../common/Card';

export function OpportunitiesTable({
  ticker,
  opportunities,
  entryThreshold,
  exitThreshold,
  onThresholdChange,
}) {
  if (opportunities.loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="spinner-lg" />
        <span className="ml-3 text-slate-400 text-sm">Loading opportunities...</span>
      </div>
    );
  }

  if (opportunities.error) {
    return (
      <div className="error-box">
        <p className="text-slate-300">Error loading opportunities: {opportunities.error}</p>
      </div>
    );
  }

  if (!opportunities.data) {
    return <div className="text-slate-500 text-center py-8">No opportunity data available</div>;
  }

  const { windows, stats } = opportunities.data;

  return (
    <div>
      <h3 className="text-base font-semibold mb-2 text-slate-200">
        {ticker} Opportunity Windows
      </h3>
      <p className="text-sm text-slate-400 mb-6">
        Periods when the stock dropped below your entry threshold — potential put option opportunities.
      </p>

      {/* Summary metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <MetricCard label="Total Windows" value={stats.total_windows} />
        <MetricCard
          label="Avg Duration"
          value={`${stats.avg_duration ? stats.avg_duration.toFixed(0) : '\u2014'} days`}
        />
        <MetricCard
          label="Avg Max Drawdown"
          value={`${stats.avg_max_drawdown ? (stats.avg_max_drawdown * 100).toFixed(1) : '\u2014'}%`}
        />
        <MetricCard
          label="% Time in Window"
          value={`${(stats.pct_time_in_window * 100).toFixed(1)}%`}
        />
      </div>

      {/* Threshold filters */}
      <CardLg className="mb-6">
        <h4 className="text-sm font-semibold mb-4 text-slate-300">Adjust Thresholds</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Input
              label="Entry Threshold (% down)"
              value={(entryThreshold * 100).toFixed(1)}
              onChange={(v) => onThresholdChange(parseFloat(v) / 100, exitThreshold)}
              type="number"
              step="0.5"
              min="0"
              max="50"
            />
            <p className="text-xs text-slate-500 mt-1">Enter window when drawdown exceeds this</p>
          </div>
          <div>
            <Input
              label="Exit Threshold (% down)"
              value={(exitThreshold * 100).toFixed(1)}
              onChange={(v) => onThresholdChange(entryThreshold, parseFloat(v) / 100)}
              type="number"
              step="0.5"
              min="0"
              max="50"
            />
            <p className="text-xs text-slate-500 mt-1">Exit window when recovery exceeds this</p>
          </div>
        </div>
      </CardLg>

      {/* Windows table */}
      <CardLg>
        <h4 className="text-sm font-semibold mb-4 text-slate-300">Opportunity Windows</h4>
        {windows.length === 0 ? (
          <p className="text-slate-500 text-center py-8">
            No opportunity windows found with current thresholds
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Start Date</th>
                  <th>End Date</th>
                  <th>Duration</th>
                  <th>Entry Drawdown</th>
                  <th>Max Drawdown</th>
                  <th>Exit Drawdown</th>
                </tr>
              </thead>
              <tbody>
                {windows.map((window, index) => (
                  <tr key={index}>
                    <td>{window.start_date}</td>
                    <td>
                      {window.end_date || (
                        <span className="badge badge-yellow">Open</span>
                      )}
                    </td>
                    <td className="font-medium tabular-nums">{window.duration_days} days</td>
                    <td className="text-amber-400 tabular-nums">
                      {(window.entry_drawdown * 100).toFixed(1)}%
                    </td>
                    <td className="text-red-400 font-semibold tabular-nums">
                      {(window.max_drawdown * 100).toFixed(1)}%
                    </td>
                    <td className="text-emerald-400 tabular-nums">
                      {window.exit_drawdown
                        ? `${(window.exit_drawdown * 100).toFixed(1)}%`
                        : '\u2014'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardLg>

      {/* Note */}
      <div className="info-box mt-6">
        <p className="text-sm text-slate-300">
          <strong className="text-slate-100">How to use:</strong> These windows show historical periods
          when the stock was significantly down from its recent high. Put options would have been
          valuable defensively during these drawdowns.
        </p>
      </div>
    </div>
  );
}
