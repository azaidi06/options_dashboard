/**
 * Payoff Diagram - Long Put Profit/Loss visualization
 */
import { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { CardLg, MetricCard } from '../common/Card';
import { usePayoffDiagram } from '../../hooks/useOptionsData';

export function PayoffDiagram() {
  const [strike, setStrike] = useState(100);
  const [premium, setPremium] = useState(2.5);
  const [minPrice, setMinPrice] = useState(70);
  const [maxPrice, setMaxPrice] = useState(130);

  const payoff = usePayoffDiagram(strike, premium, minPrice, maxPrice);

  if (payoff.loading) {
    return <div className="text-gray-500 text-center py-8">Calculating payoff diagram...</div>;
  }

  if (payoff.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded p-4">
        <p className="text-red-800">Error: {payoff.error}</p>
      </div>
    );
  }

  if (!payoff.data) {
    return <div className="text-gray-500 text-center py-8">Enter values to generate payoff diagram</div>;
  }

  const { data, breakeven } = payoff.data;

  // Add a zero line for reference
  const chartData = data.map((d) => ({
    ...d,
    zero: 0,
  }));

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 text-gray-900">Long Put Payoff Diagram</h3>

      {/* Inputs */}
      <CardLg className="mb-6 bg-blue-50">
        <h4 className="text-md font-semibold mb-4 text-gray-900">Configure Position</h4>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Input
            label="Strike Price"
            value={strike}
            onChange={(v) => setStrike(parseFloat(v))}
            type="number"
            step="0.50"
          />
          <Input
            label="Premium Paid"
            value={premium}
            onChange={(v) => setPremium(parseFloat(v))}
            type="number"
            step="0.10"
          />
          <Input
            label="Min Stock Price"
            value={minPrice}
            onChange={(v) => setMinPrice(parseFloat(v))}
            type="number"
            step="1"
          />
          <Input
            label="Max Stock Price"
            value={maxPrice}
            onChange={(v) => setMaxPrice(parseFloat(v))}
            type="number"
            step="1"
          />
          <div className="flex items-end">
            <Button onClick={() => {}} className="w-full">
              Recalculate
            </Button>
          </div>
        </div>
      </CardLg>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <MetricCard label="Strike" value={`$${strike.toFixed(2)}`} />
        <MetricCard label="Premium" value={`$${premium.toFixed(2)}`} />
        <MetricCard label="Breakeven" value={`$${breakeven.toFixed(2)}`} />
        <MetricCard
          label="Max Profit"
          value={`$${(strike - premium).toFixed(2)}`}
        />
      </div>

      {/* Payoff Chart */}
      <CardLg className="mb-6">
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="price"
              label={{ value: 'Stock Price at Expiration', position: 'insideBottomRight', offset: -5 }}
              tick={{ fontSize: 12 }}
            />
            <YAxis
              label={{ value: 'P/L Per Share ($)', angle: -90, position: 'insideLeft' }}
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              formatter={(value) => `$${value.toFixed(2)}`}
              labelFormatter={(label) => `Price: $${label.toFixed(2)}`}
            />
            <Legend />

            {/* Reference lines */}
            <ReferenceLine y={0} stroke="#d1d5db" strokeDasharray="5 5" />
            <ReferenceLine
              x={breakeven}
              stroke="#f59e0b"
              strokeDasharray="5 5"
              label={{ value: `Breakeven: $${breakeven.toFixed(2)}`, position: 'top', fill: '#f59e0b' }}
            />
            <ReferenceLine
              x={strike}
              stroke="#3b82f6"
              strokeDasharray="5 5"
              label={{ value: `Strike: $${strike.toFixed(2)}`, position: 'top', fill: '#3b82f6' }}
            />

            {/* Payoff line */}
            <Line
              type="monotone"
              dataKey="pl_per_share"
              stroke="#10b981"
              strokeWidth={3}
              dot={false}
              isAnimationActive={false}
              name="Profit/Loss per Share"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardLg>

      {/* Explanation */}
      <CardLg className="bg-green-50 border border-green-200">
        <h4 className="text-md font-semibold mb-3 text-gray-900">Long Put Payoff Structure</h4>
        <div className="space-y-2 text-sm text-gray-700">
          <p>
            <strong>Profit Zone (above $0):</strong> When stock price falls below the breakeven
            price (${breakeven.toFixed(2)}), you make a profit.
          </p>
          <p>
            <strong>Max Profit:</strong> ${(strike - premium).toFixed(2)} per share (when stock price
            ≤ ${strike.toFixed(2)})
          </p>
          <p>
            <strong>Max Loss:</strong> ${premium.toFixed(2)} per share (the premium paid - occurs
            if stock price ≥ ${strike.toFixed(2)})
          </p>
          <p>
            <strong>Breakeven:</strong> ${breakeven.toFixed(2)} (strike price minus premium paid)
          </p>
        </div>
      </CardLg>
    </div>
  );
}
