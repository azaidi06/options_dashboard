/**
 * Price Chart with gradient coloring based on distance from rolling high
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
} from 'recharts';

export function PriceChart({ data, ticker, lookbackDays }) {
  if (!data || data.length === 0) {
    return <div className="text-gray-500 text-center py-8">No data available</div>;
  }

  // Add color to each data point based on pct_change
  const chartData = data.map((item) => {
    const pctChange = item.pct_change || 0;

    let color = '#1f2937'; // default gray
    if (pctChange >= 0) {
      color = '#22c55e'; // green (at or above rolling high)
    } else if (pctChange > -0.05) {
      color = '#fbbf24'; // yellow (-5% to 0%)
    } else if (pctChange > -0.1) {
      color = '#fb923c'; // orange (-10% to -5%)
    } else {
      color = '#ef4444'; // red (below -10%)
    }

    return {
      ...item,
      lineColor: color,
    };
  });

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 text-gray-900">
        {ticker} Price Chart ({lookbackDays}-day lookback)
      </h3>

      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            stroke="#9ca3af"
          />
          <YAxis
            yAxisId="left"
            tick={{ fontSize: 12 }}
            stroke="#9ca3af"
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fontSize: 12 }}
            stroke="#d1d5db"
            label={{ value: 'Volume', angle: 90, position: 'insideRight', offset: -5 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
            }}
            formatter={(value, name) => {
              if (name === 'close') return [`$${value.toFixed(2)}`, 'Close'];
              if (name === 'volume') return [`${(value / 1e6).toFixed(1)}M`, 'Volume'];
              return [value.toFixed(2), name];
            }}
          />
          <Legend />

          {/* Price line with dynamic color based on pct_change */}
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="close"
            stroke="#2563eb"
            dot={false}
            isAnimationActive={false}
            strokeWidth={2}
            name="Close Price"
          />

          {/* Volume bars */}
          <Bar
            yAxisId="right"
            dataKey="volume"
            fill="#d1d5db"
            name="Volume"
            opacity={0.5}
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-green-500"></div>
          <span>At/Above High</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-yellow-400"></div>
          <span>-5% to 0%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-orange-500"></div>
          <span>-10% to -5%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-red-500"></div>
          <span>Below -10%</span>
        </div>
      </div>
    </div>
  );
}
