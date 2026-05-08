/**
 * Payoff Diagram - dark theme.
 * When given chainData, defaults strike to the ATM strike from the chain
 * and premium to that strike's mid (bid+ask)/2.
 */
import { useState, useMemo, useEffect } from 'react';
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
import { formatCurrency } from '../../utils/formatters';

const TOOLTIP_STYLE = {
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  border: '1px solid #334155',
  borderRadius: '8px',
  backdropFilter: 'blur(8px)',
};

function PayoffTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  const row = payload.find((p) => p.dataKey === 'pl_per_share') || payload[0];
  if (!row) return null;
  return (
    <div className="bg-slate-900/95 backdrop-blur border border-slate-700 rounded-lg shadow-xl px-3 py-2 text-xs">
      <div className="font-semibold text-slate-100 mb-1 tabular-nums">
        Stock @ {formatCurrency(parseFloat(label), 2)}
      </div>
      <div className="text-slate-300 tabular-nums">
        P/L: {formatCurrency(row.value, 2)}
      </div>
    </div>
  );
}

/**
 * Pick an ATM strike from the chain data.
 * Heuristic: contract with delta closest to -0.5 (puts) or 0.5 (calls).
 * Falls back to the median strike if delta isn't reliable.
 */
function pickATMContract(chainRows) {
  if (!chainRows || !chainRows.length) return null;
  const usable = chainRows.filter(
    (r) => r && r.strike != null && (r.delta != null || r.bid != null || r.ask != null),
  );
  if (!usable.length) return null;

  // Delta-based pick (most accurate for live ATM)
  const withDelta = usable.filter((r) => r.delta != null && Math.abs(r.delta) > 0);
  if (withDelta.length) {
    let best = withDelta[0];
    let bestDist = Math.abs(Math.abs(best.delta) - 0.5);
    for (const r of withDelta) {
      const dist = Math.abs(Math.abs(r.delta) - 0.5);
      if (dist < bestDist) {
        best = r;
        bestDist = dist;
      }
    }
    return best;
  }

  // Fallback: median strike
  const sorted = [...usable].sort((a, b) => a.strike - b.strike);
  return sorted[Math.floor(sorted.length / 2)];
}

export function PayoffDiagram({ chainData = null, optionType = 'put' }) {
  const isCall = String(optionType).toLowerCase() === 'call';
  const positionLabel = isCall ? 'Long Call' : 'Long Put';
  const [strike, setStrike] = useState(100);
  const [premium, setPremium] = useState(2.5);
  const [minPrice, setMinPrice] = useState(70);
  const [maxPrice, setMaxPrice] = useState(130);
  const [autoSeeded, setAutoSeeded] = useState(false);

  // Seed defaults from the loaded chain ONCE per chain payload.
  useEffect(() => {
    if (autoSeeded) return;
    const rows = chainData?.data;
    if (!rows || !rows.length) return;
    const atm = pickATMContract(rows);
    if (!atm) return;
    const k = Number(atm.strike);
    if (!Number.isFinite(k) || k <= 0) return;
    const bid = Number(atm.bid) || 0;
    const ask = Number(atm.ask) || 0;
    let mid = bid > 0 && ask > 0 ? (bid + ask) / 2 : Number(atm.mark) || (bid || ask);
    if (!Number.isFinite(mid) || mid <= 0) mid = Math.max(0.05, k * 0.02);
    setStrike(Math.round(k * 100) / 100);
    setPremium(Math.round(mid * 100) / 100);
    setMinPrice(Math.round(k * 0.7));
    setMaxPrice(Math.round(k * 1.3));
    setAutoSeeded(true);
  }, [chainData, autoSeeded]);

  // Reset auto-seed flag if a fresh chain (different ticker/date/option_type) arrives.
  // We track payload identity via length + first strike, which is cheap.
  const seedKey = chainData?.data?.length
    ? `${chainData.data.length}-${chainData.data[0]?.strike}-${chainData.data[0]?.expiration}-${optionType}`
    : optionType;
  useEffect(() => {
    setAutoSeeded(false);
  }, [seedKey]);

  const payoff = useMemo(
    () => calculatePayoff(strike, premium, minPrice, maxPrice, 50, optionType),
    [strike, premium, minPrice, maxPrice, optionType],
  );

  const { data, breakeven } = payoff;

  const chartData = data.map((d) => ({
    price: d.price,
    profit: d.pl_per_share >= 0 ? d.pl_per_share : 0,
    loss: d.pl_per_share < 0 ? d.pl_per_share : 0,
    pl_per_share: d.pl_per_share,
  }));

  // Max profit differs by direction:
  // - Long put: capped at strike - premium (when stock goes to 0)
  // - Long call: theoretically unbounded; we report "Unlimited"
  const maxProfit = isCall ? null : strike - premium;
  const maxProfitText = isCall ? 'Unlimited' : formatCurrency(maxProfit, 2);

  return (
    <div>
      <h3 className="text-base font-semibold mb-4 text-slate-200">{positionLabel} Payoff Diagram</h3>

      {/* Inputs */}
      <CardLg className="mb-6">
        <h4 className="text-sm font-semibold mb-4 text-slate-300">Configure Position</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Input label="Strike Price" value={strike} onChange={(v) => setStrike(parseFloat(v) || 0)} type="number" step="0.50" />
          <Input label="Premium Paid" value={premium} onChange={(v) => setPremium(parseFloat(v) || 0)} type="number" step="0.10" />
          <Input label="Min Stock Price" value={minPrice} onChange={(v) => setMinPrice(parseFloat(v) || 0)} type="number" step="1" />
          <Input label="Max Stock Price" value={maxPrice} onChange={(v) => setMaxPrice(parseFloat(v) || 0)} type="number" step="1" />
        </div>
        {chainData?.data?.length ? (
          <p className="mt-3 text-xs text-slate-500">
            Defaults seeded from the loaded option chain (ATM strike, bid/ask mid).
          </p>
        ) : null}
      </CardLg>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <MetricCard label="Strike" value={formatCurrency(strike, 2)} />
        <MetricCard label="Premium" value={formatCurrency(premium, 2)} />
        <MetricCard label="Breakeven" value={formatCurrency(breakeven, 2)} />
        <MetricCard label={isCall ? 'Max Profit' : 'Max Loss'} value={isCall ? maxProfitText : formatCurrency(-premium, 2)} />
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
              tickFormatter={(v) => `$${Number(v).toFixed(0)}`}
            />
            <YAxis
              label={{ value: 'P/L ($)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }}
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              stroke="#334155"
              tickFormatter={(v) => `$${Number(v).toFixed(0)}`}
            />
            <Tooltip content={<PayoffTooltip />} contentStyle={TOOLTIP_STYLE} />

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
        <h4 className="text-sm font-semibold mb-3 text-slate-100">{positionLabel} Payoff Structure</h4>
        {isCall ? (
          <div className="space-y-2 text-sm text-slate-300">
            <p><strong className="text-slate-100">Profit Zone:</strong> When stock rises above breakeven ({formatCurrency(breakeven, 2)}), you profit.</p>
            <p><strong className="text-slate-100">Max Profit:</strong> Unlimited (no cap as stock keeps rising)</p>
            <p><strong className="text-slate-100">Max Loss:</strong> {formatCurrency(premium, 2)} per share (premium paid, stock stays below {formatCurrency(strike, 2)})</p>
            <p><strong className="text-slate-100">Breakeven:</strong> {formatCurrency(breakeven, 2)} (strike plus premium)</p>
          </div>
        ) : (
          <div className="space-y-2 text-sm text-slate-300">
            <p><strong className="text-slate-100">Profit Zone:</strong> When stock falls below breakeven ({formatCurrency(breakeven, 2)}), you profit.</p>
            <p><strong className="text-slate-100">Max Profit:</strong> {formatCurrency(strike - premium, 2)} per share (stock goes to $0)</p>
            <p><strong className="text-slate-100">Max Loss:</strong> {formatCurrency(premium, 2)} per share (premium paid, stock stays above {formatCurrency(strike, 2)})</p>
            <p><strong className="text-slate-100">Breakeven:</strong> {formatCurrency(breakeven, 2)} (strike minus premium)</p>
          </div>
        )}
      </div>
    </div>
  );
}
