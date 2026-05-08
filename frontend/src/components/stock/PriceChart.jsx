/**
 * Price Chart with gradient coloring - dark theme
 */
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { formatCurrency, formatVolume, formatPercent } from '../../utils/formatters';

function getColor(pctChange) {
  if (pctChange >= 0) return '#10b981';     // emerald
  if (pctChange > -0.05) return '#fbbf24';  // amber
  if (pctChange > -0.1) return '#fb923c';   // orange
  return '#ef4444';                          // red
}

function PriceTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  const row = payload[0]?.payload;
  if (!row) return null;
  const distFromHigh = row.pct_change != null ? row.pct_change * 100 : null;
  return (
    <div className="bg-slate-900/95 backdrop-blur border border-slate-700 rounded-lg shadow-xl px-3 py-2 text-xs">
      <div className="font-semibold text-slate-100 mb-1">{label}</div>
      {row.open != null && (
        <div className="text-slate-300 tabular-nums">
          O: {formatCurrency(row.open, 2)} &nbsp; H: {formatCurrency(row.high, 2)} &nbsp;
          L: {formatCurrency(row.low, 2)} &nbsp; C: {formatCurrency(row.close, 2)}
        </div>
      )}
      {row.open == null && row.close != null && (
        <div className="text-slate-300 tabular-nums">
          Close: {formatCurrency(row.close, 2)}
        </div>
      )}
      {row.volume != null && (
        <div className="text-slate-400 tabular-nums">
          Vol: {formatVolume(row.volume, 1)}
        </div>
      )}
      {distFromHigh != null && (
        <div className="text-slate-400 tabular-nums">
          Distance from {row.lookback_days || ''} rolling high: {formatPercent(distFromHigh, 1)}
        </div>
      )}
    </div>
  );
}

export function PriceChart({ data, ticker, lookbackDays }) {
  if (!data || data.length === 0) {
    return <div className="text-slate-500 text-center py-8">No data available</div>;
  }

  const chartData = data.map((item, i) => {
    const pctChange = item.pct_change || 0;
    const prevClose = i > 0 ? data[i - 1].close : item.close;
    const dailyChange = item.close - prevClose;
    return {
      ...item,
      lookback_days: lookbackDays,
      lineColor: getColor(pctChange),
      volumeColor: dailyChange >= 0 ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)',
    };
  });

  const gradientStops = chartData.map((d, i) => ({
    offset: `${(i / (chartData.length - 1)) * 100}%`,
    color: d.lineColor,
  }));

  return (
    <div>
      <h3 className="text-base font-semibold mb-4 text-slate-200">
        {ticker} Price Chart
        <span className="text-slate-500 font-normal ml-2 text-sm">({lookbackDays}-day lookback)</span>
      </h3>

      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="priceGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              {gradientStops.map((stop, i) => (
                <stop key={i} offset={stop.offset} stopColor={stop.color} />
              ))}
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#94a3b8' }} stroke="#334155" />
          <YAxis
            yAxisId="left"
            tick={{ fontSize: 11, fill: '#94a3b8' }}
            stroke="#334155"
            domain={['auto', 'auto']}
            tickFormatter={(v) => `$${Number(v).toFixed(0)}`}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fontSize: 11, fill: '#64748b' }}
            stroke="#334155"
            tickFormatter={(v) => formatVolume(v, 0)}
          />
          <Tooltip content={<PriceTooltip />} />
          <Legend wrapperStyle={{ color: '#94a3b8' }} />

          <Bar yAxisId="right" dataKey="volume" name="Volume" opacity={0.4} isAnimationActive={false}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.volumeColor} />
            ))}
          </Bar>

          <Line
            yAxisId="left"
            type="monotone"
            dataKey="close"
            stroke="url(#priceGradient)"
            dot={false}
            isAnimationActive={false}
            strokeWidth={2}
            name="Close Price"
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Legend + gradient bar */}
      <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-400">
        <div className="grid grid-cols-2 gap-3">
          <div className="flex items-center gap-2">
            <div className="w-5 h-0.5 bg-emerald-500 rounded" />
            <span>At/Above High</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-5 h-0.5 bg-amber-400 rounded" />
            <span>-5% to 0%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-5 h-0.5 bg-orange-500 rounded" />
            <span>-10% to -5%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-5 h-0.5 bg-red-500 rounded" />
            <span>Below -10%</span>
          </div>
        </div>

        {/* Inline gradient legend explaining the price line colour-bar */}
        <div className="flex flex-col gap-1">
          <span className="text-xs text-slate-500">Distance from rolling high</span>
          <div
            className="h-2 rounded"
            style={{
              background:
                'linear-gradient(to right, #10b981 0%, #fbbf24 50%, #fb923c 75%, #ef4444 100%)',
            }}
            aria-hidden="true"
          />
          <div className="flex justify-between text-xs text-slate-500 tabular-nums">
            <span>0% (green)</span>
            <span>−30% (red)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
