/**
 * Drawdown Analysis Chart and Events Table
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

export function DrawdownChart({ ticker, drawdown }) {
  if (drawdown.loading) {
    return <div className="text-gray-500 text-center py-8">Loading drawdown data...</div>;
  }

  if (drawdown.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded p-4">
        <p className="text-red-800">Error loading drawdown data: {drawdown.error}</p>
      </div>
    );
  }

  if (!drawdown.data) {
    return <div className="text-gray-500 text-center py-8">No drawdown data available</div>;
  }

  const { underwater_data, events, summary } = drawdown.data;

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 text-gray-900">{ticker} Drawdown Analysis</h3>

      {/* Summary metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <MetricCard
          label="Total Events"
          value={summary.total_events}
        />
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

      {/* Underwater period chart */}
      <CardLg className="mb-6">
        <h4 className="text-md font-semibold mb-4 text-gray-900">Underwater Periods</h4>
        <p className="text-sm text-gray-600 mb-4">
          Shows how far the price is below its all-time high during the period.
        </p>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={underwater_data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} label={{ value: 'Drawdown %', angle: -90, position: 'insideLeft' }} />
            <Tooltip
              formatter={(value) => `${(value * 100).toFixed(2)}%`}
            />
            <Area
              type="monotone"
              dataKey="drawdown_pct"
              fill="#fecaca"
              stroke="#dc2626"
              name="Drawdown from ATH"
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardLg>

      {/* Drawdown events table */}
      <CardLg>
        <h4 className="text-md font-semibold mb-4 text-gray-900">Drawdown Events</h4>
        {events.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No significant drawdown events found</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-100 border-b border-gray-300">
                <tr>
                  <th className="px-4 py-2 text-left font-semibold">Peak Date</th>
                  <th className="px-4 py-2 text-left font-semibold">Peak Price</th>
                  <th className="px-4 py-2 text-left font-semibold">Trough Date</th>
                  <th className="px-4 py-2 text-left font-semibold">Trough Price</th>
                  <th className="px-4 py-2 text-left font-semibold">Drawdown %</th>
                  <th className="px-4 py-2 text-left font-semibold">Days to Trough</th>
                  <th className="px-4 py-2 text-left font-semibold">Days to Recovery</th>
                  <th className="px-4 py-2 text-left font-semibold">Recovery Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {events.map((event, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-2">{event.peak_date}</td>
                    <td className="px-4 py-2 font-mono">${event.peak_price.toFixed(2)}</td>
                    <td className="px-4 py-2">{event.trough_date}</td>
                    <td className="px-4 py-2 font-mono">${event.trough_price.toFixed(2)}</td>
                    <td className="px-4 py-2 font-semibold text-red-600">
                      {(event.drawdown_pct * 100).toFixed(1)}%
                    </td>
                    <td className="px-4 py-2">{event.days_to_trough}</td>
                    <td className="px-4 py-2">
                      {event.days_to_recovery ? event.days_to_recovery : '—'}
                    </td>
                    <td className="px-4 py-2">
                      {event.recovery_date || 'Not recovered'}
                    </td>
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
