/**
 * IV Smile Chart - dark theme
 */
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { CardLg, MetricCard } from '../common/Card';

const TOOLTIP_STYLE = {
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  border: '1px solid #334155',
  borderRadius: '8px',
};

export function IVSmileChart({ ticker, ivSmileData }) {
  if (!ivSmileData || !ivSmileData.data || ivSmileData.data.length === 0) {
    return (
      <div className="text-slate-500 text-center py-8">No IV smile data available</div>
    );
  }

  const data = ivSmileData.data.map((item) => ({
    ...item,
    iv_percent: (item.implied_volatility || 0) * 100,
  }));

  return (
    <div>
      <h3 className="text-base font-semibold mb-4 text-slate-200">{ticker} IV Smile</h3>

      <CardLg className="mb-6">
        <p className="text-sm text-slate-400 mb-4">
          The IV Smile shows how implied volatility varies across different strike prices.
          A "smile" pattern indicates higher volatility at out-of-the-money strikes.
        </p>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="strike" tick={{ fontSize: 11, fill: '#94a3b8' }} stroke="#334155" />
            <YAxis
              label={{ value: 'IV %', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              stroke="#334155"
            />
            <Tooltip
              contentStyle={TOOLTIP_STYLE}
              labelStyle={{ color: '#e2e8f0' }}
              itemStyle={{ color: '#cbd5e1' }}
              formatter={(value) => `${value.toFixed(2)}%`}
              labelFormatter={(label) => `Strike: $${label.toFixed(2)}`}
            />
            <Legend wrapperStyle={{ color: '#94a3b8' }} />
            <Line
              type="monotone"
              dataKey="iv_percent"
              stroke="#818cf8"
              dot={{ fill: '#818cf8', r: 3 }}
              activeDot={{ r: 5, fill: '#a5b4fc' }}
              name="Implied Volatility"
              isAnimationActive={false}
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardLg>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <MetricCard
          label="Highest IV"
          value={`${Math.max(...data.map((d) => d.iv_percent)).toFixed(2)}%`}
        />
        <MetricCard
          label="Average IV"
          value={`${(data.reduce((sum, d) => sum + d.iv_percent, 0) / data.length).toFixed(2)}%`}
        />
        <MetricCard
          label="Lowest IV"
          value={`${Math.min(...data.map((d) => d.iv_percent)).toFixed(2)}%`}
        />
      </div>

      <div className="info-box">
        <p className="text-sm text-slate-300">
          <strong className="text-slate-100">What it means:</strong> Higher IV at out-of-the-money
          puts (lower strikes) suggests the market expects larger downside moves. Lower IV at
          at-the-money strikes suggests stability.
        </p>
      </div>
    </div>
  );
}
