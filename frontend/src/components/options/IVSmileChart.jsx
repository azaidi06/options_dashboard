/**
 * IV Smile Chart - dark theme.
 * Filters bad rows, caps Y-axis at 95th percentile, marks outliers as dots above the cap.
 */
import {
  ComposedChart,
  Line,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { CardLg, MetricCard } from '../common/Card';
import { formatPercent, formatCurrency, formatGreek } from '../../utils/formatters';
import { useTheme } from '../../theme/ThemeContext';

function percentile(sorted, p) {
  if (!sorted.length) return 0;
  const idx = (sorted.length - 1) * p;
  const lo = Math.floor(idx);
  const hi = Math.ceil(idx);
  if (lo === hi) return sorted[lo];
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
}

function IVSmileTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  const row = payload[0]?.payload;
  if (!row) return null;
  return (
    <div className="bg-white/95 dark:bg-slate-900/95 backdrop-blur border border-stone-300 dark:border-slate-700 rounded-lg shadow-xl px-3 py-2 text-xs">
      <div className="font-semibold text-stone-900 dark:text-slate-100 mb-1 tabular-nums">
        Strike {formatCurrency(row.strike, 2)}
      </div>
      <div className="text-stone-700 dark:text-slate-300 tabular-nums">
        IV: {formatPercent(row.iv_percent, 2)}
        {row.is_outlier ? <span className="text-amber-700 dark:text-amber-400"> (outlier)</span> : null}
      </div>
      {row.delta != null && (
        <div className="text-stone-600 dark:text-slate-400 tabular-nums">Delta: {formatGreek(row.delta, 'delta')}</div>
      )}
    </div>
  );
}

export function IVSmileChart({ ticker, ivSmileData }) {
  const t = useTheme().tokens;
  if (!ivSmileData || !ivSmileData.data || ivSmileData.data.length === 0) {
    return (
      <div className="text-stone-500 dark:text-slate-500 text-center py-8">No IV smile data available</div>
    );
  }

  // Drop nulls/NaNs and obviously-broken rows for the metric display.
  const cleaned = ivSmileData.data
    .map((item) => ({
      ...item,
      iv_percent:
        item.implied_volatility == null || Number.isNaN(item.implied_volatility)
          ? null
          : item.implied_volatility * 100,
    }))
    .filter(
      (d) =>
        d.iv_percent != null &&
        Number.isFinite(d.iv_percent) &&
        d.iv_percent > 0 &&
        d.iv_percent <= 200, // post-filter excludes the sentinel 999% values
    );

  // Compute cap from cleaned set so outliers don't dominate the axis.
  const sortedIVs = [...cleaned.map((d) => d.iv_percent)].sort((a, b) => a - b);
  const cap = sortedIVs.length ? Math.max(percentile(sortedIVs, 0.95), 5) : 100;
  const yMax = Math.ceil(cap * 1.1); // 10% headroom above the cap

  const data = cleaned.map((d) => ({
    ...d,
    is_outlier: d.iv_percent > cap,
    // For the line series we replace outliers with null so connectNulls={false} skips them.
    iv_line: d.iv_percent > cap ? null : d.iv_percent,
    // Outliers render as scatter points pinned to yMax.
    iv_outlier: d.iv_percent > cap ? yMax : null,
  }));

  const outlierCount = data.filter((d) => d.is_outlier).length;
  const validCount = cleaned.length;

  const highest = validCount ? Math.max(...cleaned.map((d) => d.iv_percent)) : 0;
  const average = validCount
    ? cleaned.reduce((s, d) => s + d.iv_percent, 0) / validCount
    : 0;
  const lowest = validCount ? Math.min(...cleaned.map((d) => d.iv_percent)) : 0;

  return (
    <div>
      <h3 className="text-base font-semibold mb-4 text-stone-800 dark:text-slate-200">{ticker} IV Smile</h3>

      <CardLg className="mb-6">
        <p className="text-sm text-stone-600 dark:text-slate-400 mb-2">
          The IV Smile shows how implied volatility varies across different strike prices.
          A &quot;smile&quot; pattern indicates higher volatility at out-of-the-money strikes.
        </p>
        {outlierCount > 0 && (
          <p className="text-xs text-amber-700 dark:text-amber-400 mb-3">
            {outlierCount} outlier{outlierCount === 1 ? '' : 's'} above the {cap.toFixed(0)}% cap rendered as dots at the top of the chart.
          </p>
        )}

        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={t.surfaceElev} />
            <XAxis
              dataKey="strike"
              tick={{ fontSize: 11, fill: t.textMute }}
              stroke={t.border}
              tickFormatter={(v) => `$${Number(v).toFixed(0)}`}
            />
            <YAxis
              label={{ value: 'IV %', angle: -90, position: 'insideLeft', fill: t.textMute }}
              tick={{ fontSize: 11, fill: t.textMute }}
              stroke={t.border}
              domain={[0, yMax]}
              allowDataOverflow={true}
              tickFormatter={(v) => `${Number(v).toFixed(0)}%`}
            />
            <Tooltip content={<IVSmileTooltip />} />
            <Legend wrapperStyle={{ color: t.textMute }} />
            <ReferenceLine
              y={cap}
              stroke={t.warning}
              strokeDasharray="4 4"
              label={{
                value: `95th pct: ${cap.toFixed(0)}%`,
                position: 'right',
                fill: t.warning,
                fontSize: 10,
              }}
            />
            <Line
              type="monotone"
              dataKey="iv_line"
              stroke={t.indigo}
              dot={{ fill: t.indigo, r: 3 }}
              activeDot={{ r: 5, fill: t.indigoFaint }}
              name="Implied Volatility"
              isAnimationActive={false}
              strokeWidth={2}
              connectNulls={false}
            />
            <Scatter
              dataKey="iv_outlier"
              fill={t.warning}
              name="Outlier (> cap)"
              isAnimationActive={false}
              shape="circle"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </CardLg>

      {/* Statistics — computed on the post-filter data only */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <MetricCard
          label="Highest IV (filtered)"
          value={validCount ? formatPercent(highest, 2) : '—'}
        />
        <MetricCard
          label="Average IV (filtered)"
          value={validCount ? formatPercent(average, 2) : '—'}
        />
        <MetricCard
          label="Lowest IV (filtered)"
          value={validCount ? formatPercent(lowest, 2) : '—'}
        />
      </div>

      <div className="info-box">
        <p className="text-sm text-stone-700 dark:text-slate-300">
          <strong className="text-stone-900 dark:text-slate-100">What it means:</strong> Higher IV at out-of-the-money
          puts (lower strikes) suggests the market expects larger downside moves. The chart drops
          rows where IV is missing or above 200% (typically 1-day options where the IV solver
          fails); the Y-axis is capped at the 95th percentile of valid values.
        </p>
      </div>
    </div>
  );
}
