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

function getColor(pctChange) {
  if (pctChange >= 0) return '#10b981';     // emerald
  if (pctChange > -0.05) return '#fbbf24';  // amber
  if (pctChange > -0.1) return '#fb923c';   // orange
  return '#ef4444';                          // red
}

const TOOLTIP_STYLE = {
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  border: '1px solid #334155',
  borderRadius: '8px',
  backdropFilter: 'blur(8px)',
};

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
          <YAxis yAxisId="left" tick={{ fontSize: 11, fill: '#94a3b8' }} stroke="#334155" domain={['auto', 'auto']} />
          <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11, fill: '#64748b' }} stroke="#334155" />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            labelStyle={{ color: '#e2e8f0' }}
            itemStyle={{ color: '#cbd5e1' }}
            formatter={(value, name) => {
              if (name === 'Close Price') return [`$${value.toFixed(2)}`, 'Close'];
              if (name === 'Volume') return [`${(value / 1e6).toFixed(1)}M`, 'Volume'];
              return [value, name];
            }}
          />
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

      {/* Legend */}
      <div className="mt-5 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-slate-400">
        <div className="flex items-center gap-2">
          <div className="w-5 h-0.5 bg-emerald-500 rounded"></div>
          <span>At/Above High</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-5 h-0.5 bg-amber-400 rounded"></div>
          <span>-5% to 0%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-5 h-0.5 bg-orange-500 rounded"></div>
          <span>-10% to -5%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-5 h-0.5 bg-red-500 rounded"></div>
          <span>Below -10%</span>
        </div>
      </div>
    </div>
  );
}
