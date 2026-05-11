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
import { formatCurrency, formatPercent } from '../../utils/formatters';
import { useTheme } from '../../theme/ThemeContext';

/**
 * Compute period max-drawdown from a daily price series.
 * Uses close prices; expects ascending date order.
 */
function computePeriodMDD(rows) {
  if (!rows || rows.length === 0) return 0;
  let peak = -Infinity;
  let mdd = 0;
  for (const row of rows) {
    const c = row.close;
    if (c == null) continue;
    if (c > peak) peak = c;
    if (peak > 0) {
      const dd = (c - peak) / peak;
      if (dd < mdd) mdd = dd;
    }
  }
  return mdd; // negative number, e.g. -0.18
}

export function DrawdownChart({ ticker, drawdown, priceData = null }) {
  const t = useTheme().tokens;
  const TOOLTIP_STYLE = {
    backgroundColor: t.tooltipBg,
    border: `1px solid ${t.tooltipBorder}`,
    borderRadius: '8px',
  };
  if (drawdown.loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="spinner-lg" />
        <span className="ml-3 text-stone-600 dark:text-slate-400 text-sm">Loading drawdown data...</span>
      </div>
    );
  }

  if (drawdown.error) {
    return (
      <div className="error-box">
        <p className="text-stone-700 dark:text-slate-300">Error loading drawdown data: {drawdown.error}</p>
      </div>
    );
  }

  if (!drawdown.data) {
    return <div className="text-stone-500 dark:text-slate-500 text-center py-8">No drawdown data available</div>;
  }

  const { underwater_data, events, summary } = drawdown.data;

  const chartData = underwater_data.map((d) => ({
    ...d,
    drawdown_pct: -(d.drawdown_pct || 0),
  }));

  const periodMDD = computePeriodMDD(priceData || []);

  return (
    <div>
      <h3 className="text-base font-semibold mb-4 text-stone-800 dark:text-slate-200">{ticker} Drawdown Analysis</h3>

      {/* Summary metrics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <MetricCard label="Total Events" value={summary.total_events} />
        <MetricCard
          label="Max Event Drawdown"
          value={formatPercent(summary.max_drawdown_pct * 100, 1)}
        />
        <MetricCard
          label="Period MDD"
          value={priceData?.length ? formatPercent(periodMDD * 100, 1) : '—'}
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
        <h4 className="text-sm font-semibold mb-1 text-stone-700 dark:text-slate-300">Underwater Periods</h4>
        <p className="text-xs text-stone-500 dark:text-slate-500 mb-4">
          Distance below all-time high during the period.
        </p>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke={t.surfaceElev} />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: t.textMute }} stroke={t.border} />
            <YAxis
              tick={{ fontSize: 11, fill: t.textMute }}
              stroke={t.border}
              tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              domain={['auto', 0]}
            />
            <Tooltip
              contentStyle={TOOLTIP_STYLE}
              labelStyle={{ color: t.text }}
              formatter={(value) => [formatPercent(value * 100, 2), 'Drawdown']}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Area
              type="monotone"
              dataKey="drawdown_pct"
              fill="rgba(239, 68, 68, 0.15)"
              stroke={t.negative}
              name="Drawdown from ATH"
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardLg>

      {/* Events table */}
      <CardLg>
        <h4 className="text-sm font-semibold mb-4 text-stone-700 dark:text-slate-300">Drawdown Events</h4>
        {events.length === 0 ? (
          <p className="text-stone-500 dark:text-slate-500 text-center py-8">No significant drawdown events found</p>
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
                    <td className="font-mono tabular-nums">{formatCurrency(event.peak_price, 2)}</td>
                    <td>{event.trough_date}</td>
                    <td className="font-mono tabular-nums">{formatCurrency(event.trough_price, 2)}</td>
                    <td className="font-semibold text-red-700 dark:text-red-400 tabular-nums">
                      {formatPercent(event.drawdown_pct * 100, 1)}
                    </td>
                    <td className="tabular-nums">{event.days_to_trough}</td>
                    <td className="tabular-nums">
                      {event.days_to_recovery ? event.days_to_recovery : '—'}
                    </td>
                    <td>{event.recovery_date || <span className="text-stone-500 dark:text-slate-500">Not recovered</span>}</td>
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
