/**
 * IV Smile Chart - Implied Volatility vs Strike Price
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
import { CardLg } from '../common/Card';

export function IVSmileChart({ ticker, ivSmileData }) {
  if (!ivSmileData || !ivSmileData.data || ivSmileData.data.length === 0) {
    return (
      <div className="text-gray-500 text-center py-8">
        No IV smile data available
      </div>
    );
  }

  const data = ivSmileData.data.map((item) => ({
    ...item,
    iv_percent: (item.implied_volatility || 0) * 100,
  }));

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 text-gray-900">
        {ticker} IV Smile
      </h3>

      <CardLg className="mb-6">
        <p className="text-sm text-gray-600 mb-4">
          The IV Smile shows how implied volatility varies across different strike prices.
          A "smile" pattern indicates higher volatility at out-of-the-money strikes (risk reversal).
        </p>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="strike" tick={{ fontSize: 12 }} />
            <YAxis
              label={{ value: 'IV %', angle: -90, position: 'insideLeft' }}
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              formatter={(value) => `${(value).toFixed(2)}%`}
              labelFormatter={(label) => `Strike: $${label.toFixed(2)}`}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="iv_percent"
              stroke="#2563eb"
              dot={{ fill: '#2563eb', r: 4 }}
              activeDot={{ r: 6 }}
              name="Implied Volatility"
              isAnimationActive={false}
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardLg>

      {/* Statistics */}
      <CardLg className="bg-blue-50">
        <h4 className="text-md font-semibold mb-4 text-gray-900">IV Statistics</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-gray-600">Highest IV</div>
            <div className="text-2xl font-bold text-blue-600">
              {Math.max(...data.map((d) => d.iv_percent)).toFixed(2)}%
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Average IV</div>
            <div className="text-2xl font-bold text-blue-600">
              {(
                data.reduce((sum, d) => sum + d.iv_percent, 0) / data.length
              ).toFixed(2)}
              %
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Lowest IV</div>
            <div className="text-2xl font-bold text-blue-600">
              {Math.min(...data.map((d) => d.iv_percent)).toFixed(2)}%
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-blue-200">
          <p className="text-sm text-gray-700">
            <strong>💡 What it means:</strong> Higher IV at out-of-the-money puts (lower strikes)
            suggests the market expects larger downside moves. Lower IV at at-the-money strikes
            suggests stability.
          </p>
        </div>
      </CardLg>
    </div>
  );
}
