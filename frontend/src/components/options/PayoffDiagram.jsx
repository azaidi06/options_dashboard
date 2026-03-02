/**
 * Payoff Diagram - dark theme
 */
import { useState, useMemo } from 'react';
import {
  ComposedChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { Input } from '../common/Input';
import { CardLg, MetricCard } from '../common/Card';
import { calculatePayoff } from '../../utils/calculations';

const TOOLTIP_STYLE = {
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  border: '1px solid #334155',
  borderRadius: '8px',
};

export function PayoffDiagram() {
  const [strike, setStrike] = useState(100);
  const [premium, setPremium] = useState(2.5);
  const [minPrice, setMinPrice] = useState(70);
  const [maxPrice, setMaxPrice] = useState(130);

  const payoff = useMemo(
    () => calculatePayoff(strike, premium, minPrice, maxPrice, 50),
    [strike, premium, minPrice, maxPrice]
  );

  const { data, breakeven } = payoff;

  const chartData = data.map((d) => ({
    price: d.price,
    profit: d.pl_per_share >= 0 ? d.pl_per_share : 0,
    loss: d.pl_per_share < 0 ? d.pl_per_share : 0,
    pl_per_share: d.pl_per_share,
  }));

  return (
    <div>
      <h3 className="text-base font-semibold mb-4 text-slate-200">Long Put Payoff Diagram</h3>

      {/* Inputs */}
      <CardLg className="mb-6">
        <h4 className="text-sm font-semibold mb-4 text-slate-300">Configure Position</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Input label="Strike Price" value={strike} onChange={(v) => setStrike(parseFloat(v) || 0)} type="number" step="0.50" />
          <Input label="Premium Paid" value={premium} onChange={(v) => setPremium(parseFloat(v) || 0)} type="number" step="0.10" />
          <Input label="Min Stock Price" value={minPrice} onChange={(v) => setMinPrice(parseFloat(v) || 0)} type="number" step="1" />
          <Input label="Max Stock Price" value={maxPrice} onChange={(v) => setMaxPrice(parseFloat(v) || 0)} type="number" step="1" />
        </div>
      </CardLg>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <MetricCard label="Strike" value={`$${strike.toFixed(2)}`} />
        <MetricCard label="Premium" value={`$${premium.toFixed(2)}`} />
        <MetricCard label="Breakeven" value={`$${breakeven.toFixed(2)}`} />
        <MetricCard label="Max Profit" value={`$${(strike - premium).toFixed(2)}`} />
      </div>

      {/* Chart */}
      <CardLg className="mb-6">
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              dataKey="price"
              label={{ value: 'Stock Price at Expiration', position: 'insideBottomRight', offset: -5, fill: '#94a3b8', fontSize: 11 }}
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              stroke="#334155"
            />
            <YAxis
              label={{ value: 'P/L ($)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }}
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              stroke="#334155"
            />
            <Tooltip
              contentStyle={TOOLTIP_STYLE}
              labelStyle={{ color: '#e2e8f0' }}
              formatter={(value, name) => {
                if (name === 'pl_per_share') return [`$${value.toFixed(2)}`, 'P/L'];
                return null;
              }}
              labelFormatter={(label) => `Price: $${parseFloat(label).toFixed(2)}`}
              itemSorter={() => 0}
            />

            <ReferenceLine y={0} stroke="#475569" strokeWidth={1.5} />
            <ReferenceLine
              x={breakeven}
              stroke="#f59e0b"
              strokeDasharray="5 5"
              label={{ value: `BE: $${breakeven.toFixed(0)}`, position: 'top', fill: '#f59e0b', fontSize: 11 }}
            />
            <ReferenceLine
              x={strike}
              stroke="#818cf8"
              strokeDasharray="5 5"
              label={{ value: `Strike: $${strike.toFixed(0)}`, position: 'top', fill: '#818cf8', fontSize: 11 }}
            />

            <Area type="monotone" dataKey="profit" fill="rgba(16, 185, 129, 0.15)" stroke="none" isAnimationActive={false} legendType="none" />
            <Area type="monotone" dataKey="loss" fill="rgba(239, 68, 68, 0.15)" stroke="none" isAnimationActive={false} legendType="none" />
            <Area type="monotone" dataKey="pl_per_share" fill="none" stroke="#e2e8f0" strokeWidth={2} dot={false} isAnimationActive={false} name="P/L per Share" />
          </ComposedChart>
        </ResponsiveContainer>
      </CardLg>

      {/* Explanation */}
      <div className="info-box">
        <h4 className="text-sm font-semibold mb-3 text-slate-100">Long Put Payoff Structure</h4>
        <div className="space-y-2 text-sm text-slate-300">
          <p><strong className="text-slate-100">Profit Zone:</strong> When stock falls below breakeven (${breakeven.toFixed(2)}), you profit.</p>
          <p><strong className="text-slate-100">Max Profit:</strong> ${(strike - premium).toFixed(2)} per share (stock goes to $0)</p>
          <p><strong className="text-slate-100">Max Loss:</strong> ${premium.toFixed(2)} per share (premium paid, stock stays above ${strike.toFixed(2)})</p>
          <p><strong className="text-slate-100">Breakeven:</strong> ${breakeven.toFixed(2)} (strike minus premium)</p>
        </div>
      </div>
    </div>
  );
}
