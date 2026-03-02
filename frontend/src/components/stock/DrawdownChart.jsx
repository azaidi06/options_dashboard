/**
 * Drawdown Analysis - dark theme
 */
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { CardLg, MetricCard } from '../common/Card';

const TOOLTIP_STYLE = {
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  border: '1px solid #334155',
  borderRadius: '8px',
};

export function DrawdownChart({ ticker, drawdown }) {
  if (drawdown.loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="spinner-lg" />
        <span className="ml-3 text-slate-400 text-sm">Loading drawdown data...</span>
      </div>
    );
  }

  if (drawdown.error) {
    return (
      <div className="error-box">
        <p className="text-slate-300">Error loading drawdown data: {drawdown.error}</p>
      </div>
    );
  }

  if (!drawdown.data) {
    return <div className="text-slate-500 text-center py-8">No drawdown data available</div>;
  }

  const { underwater_data, events, summary } = drawdown.data;

  const chartData = underwater_data.map((d) => ({
    ...d,
    drawdown_pct: -(d.drawdown_pct || 0),
  }));

  return (
    <div>
      <h3 className="text-base font-semibold mb-4 text-slate-200">{ticker} Drawdown Analysis</h3>

      {/* Summary metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <MetricCard label="Total Events" value={summary.total_events} />
        <MetricCard
          label="Max Drawdown"
          value={`${(summary.max_drawdown_pct * 100).toFixed(1)}%`}
        />
        <MetricCard
          label="Avg Recovery Days"
          value={summary.avg_recovery_days ? summary.avg_recovery_days.toFixed(0) : 'N/A'}
        />
        <MetricCard
          label="Min Threshold"
          value={`${(summary.min_event_threshold * 100).toFixed(0)}%`}
        />
      </div>

      {/* Underwater chart */}
      <CardLg className="mb-6">
        <h4 className="text-sm font-semibold mb-1 text-slate-300">Underwater Periods</h4>
        <p className="text-xs text-slate-500 mb-4">
          Distance below all-time high during the period.
        </p>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#94a3b8' }} stroke="#334155" />
            <YAxis
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              stroke="#334155"
              tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              domain={['auto', 0]}
            />
            <Tooltip
              contentStyle={TOOLTIP_STYLE}
              labelStyle={{ color: '#e2e8f0' }}
              formatter={(value) => [`${(value * 100).toFixed(2)}%`, 'Drawdown']}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Area
              type="monotone"
              dataKey="drawdown_pct"
              fill="rgba(239, 68, 68, 0.15)"
              stroke="#ef4444"
              name="Drawdown from ATH"
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardLg>

      {/* Events table */}
      <CardLg>
        <h4 className="text-sm font-semibold mb-4 text-slate-300">Drawdown Events</h4>
        {events.length === 0 ? (
          <p className="text-slate-500 text-center py-8">No significant drawdown events found</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Peak Date</th>
                  <th>Peak Price</th>
                  <th>Trough Date</th>
                  <th>Trough Price</th>
                  <th>Drawdown %</th>
                  <th>Days to Trough</th>
                  <th>Days to Recovery</th>
                  <th>Recovery Date</th>
                </tr>
              </thead>
              <tbody>
                {events.map((event, index) => (
                  <tr key={index}>
                    <td>{event.peak_date}</td>
                    <td className="font-mono tabular-nums">${event.peak_price.toFixed(2)}</td>
                    <td>{event.trough_date}</td>
                    <td className="font-mono tabular-nums">${event.trough_price.toFixed(2)}</td>
                    <td className="font-semibold text-red-400 tabular-nums">
                      {(event.drawdown_pct * 100).toFixed(1)}%
                    </td>
                    <td className="tabular-nums">{event.days_to_trough}</td>
                    <td className="tabular-nums">
                      {event.days_to_recovery ? event.days_to_recovery : '\u2014'}
                    </td>
                    <td>{event.recovery_date || <span className="text-slate-500">Not recovered</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardLg>
    </div>
  );
}
