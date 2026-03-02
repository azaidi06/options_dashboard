/**
 * Calculator Panel - dark theme
 */
import { useState, useMemo } from 'react';
import { Tabs, Tab } from '../common/Tabs';
import { Input } from '../common/Input';
import { CardLg, MetricCard } from '../common/Card';
import {
  calculateTimeDecay,
  calculatePriceChangeImpact,
  classifyMoneyness,
  calculatePositionSize,
} from '../../utils/calculations';
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

const TOOLTIP_STYLE = {
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  border: '1px solid #334155',
  borderRadius: '8px',
};
const GRID_COLOR = '#1e293b';
const AXIS_TICK = { fontSize: 11, fill: '#94a3b8' };
const AXIS_STROKE = '#334155';

export function CalculatorPanel() {
  const [tdPremium, setTdPremium] = useState(2.5);
  const [tdTheta, setTdTheta] = useState(-0.05);
  const [tdDays, setTdDays] = useState(30);
  const timeDecay = useMemo(() => calculateTimeDecay(tdPremium, tdTheta, tdDays), [tdPremium, tdTheta, tdDays]);

  const [piPremium, setPiPremium] = useState(2.5);
  const [piDelta, setPiDelta] = useState(-0.45);
  const [piGamma, setPiGamma] = useState(0.02);
  const [piPriceChange, setPiPriceChange] = useState(-5);
  const priceImpact = useMemo(() => calculatePriceChangeImpact(piPremium, piDelta, piGamma, piPriceChange), [piPremium, piDelta, piGamma, piPriceChange]);

  const [mnStrike, setMnStrike] = useState(100);
  const [mnPrice, setMnPrice] = useState(102);
  const moneyness = useMemo(() => classifyMoneyness(mnStrike, mnPrice), [mnStrike, mnPrice]);

  const [psAccount, setPsAccount] = useState(10000);
  const [psRisk, setPsRisk] = useState(2);
  const [psPremium, setPsPremium] = useState(250);
  const positionSize = useMemo(() => calculatePositionSize(psAccount, psRisk, psPremium), [psAccount, psRisk, psPremium]);

  return (
    <div>
      <h3 className="text-base font-semibold mb-4 text-slate-200">Risk Calculators</h3>

      <Tabs defaultTab={0}>
        {/* Time Decay */}
        <Tab label="Time Decay">
          <CardLg>
            <h4 className="text-sm font-semibold mb-4 text-slate-300">Premium Decay Over Time</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <Input label="Initial Premium" value={tdPremium} onChange={(v) => setTdPremium(parseFloat(v) || 0)} type="number" step="0.10" />
              <Input label="Daily Theta" value={tdTheta} onChange={(v) => setTdTheta(parseFloat(v) || 0)} type="number" step="0.01" />
              <Input label="Days to Expiration" value={tdDays} onChange={(v) => setTdDays(parseInt(v) || 1)} type="number" />
            </div>

            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={timeDecay.data}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} />
                <XAxis dataKey="days_remaining" tick={AXIS_TICK} stroke={AXIS_STROKE} label={{ value: 'Days Remaining', position: 'insideBottomRight', offset: -5, fill: '#94a3b8', fontSize: 11 }} />
                <YAxis tick={AXIS_TICK} stroke={AXIS_STROKE} label={{ value: 'Premium ($)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
                <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={{ color: '#e2e8f0' }} formatter={(v) => `$${v.toFixed(2)}`} />
                <Legend wrapperStyle={{ color: '#94a3b8' }} />
                <Line type="monotone" dataKey="premium" stroke="#f59e0b" name="Projected Premium" isAnimationActive={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>

            <div className="warning-box mt-4">
              <p className="text-sm text-slate-300">
                <strong className="text-slate-100">Theta Effect:</strong> As expiration approaches, time
                decay accelerates. Daily theta decay of ${Math.abs(tdTheta).toFixed(3)}.
              </p>
            </div>
          </CardLg>
        </Tab>

        {/* Price Impact */}
        <Tab label="Price Impact">
          <CardLg>
            <h4 className="text-sm font-semibold mb-4 text-slate-300">Delta-Gamma Impact</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <Input label="Current Premium" value={piPremium} onChange={(v) => setPiPremium(parseFloat(v) || 0)} type="number" step="0.10" />
              <Input label="Delta" value={piDelta} onChange={(v) => setPiDelta(parseFloat(v) || 0)} type="number" step="0.01" />
              <Input label="Gamma" value={piGamma} onChange={(v) => setPiGamma(parseFloat(v) || 0)} type="number" step="0.001" />
              <Input label="Price Change ($)" value={piPriceChange} onChange={(v) => setPiPriceChange(parseFloat(v) || 0)} type="number" step="0.50" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <MetricCard label="Current Premium" value={`$${priceImpact.current_premium.toFixed(2)}`} />
              <MetricCard label="Estimated New" value={`$${priceImpact.estimated_premium.toFixed(2)}`} />
              <MetricCard
                label="P/L Change"
                value={`$${(priceImpact.estimated_premium - priceImpact.current_premium).toFixed(2)}`}
                deltaType={priceImpact.estimated_premium > priceImpact.current_premium ? 'positive' : 'negative'}
              />
            </div>

            <div className="info-box">
              <p className="text-sm text-slate-300">
                <strong className="text-slate-100">Delta Effect:</strong> ${priceImpact.delta_effect.toFixed(3)}
                <br /><strong className="text-slate-100">Gamma Effect:</strong> ${priceImpact.gamma_effect.toFixed(3)}
                <br /><strong className="text-slate-100">What it means:</strong> Shows how put value changes when
                stock price moves, accounting for both delta and gamma.
              </p>
            </div>
          </CardLg>
        </Tab>

        {/* Moneyness */}
        <Tab label="Moneyness">
          <CardLg>
            <h4 className="text-sm font-semibold mb-4 text-slate-300">Option Moneyness</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <Input label="Strike Price" value={mnStrike} onChange={(v) => setMnStrike(parseFloat(v) || 0)} type="number" step="0.50" />
              <Input label="Current Stock Price" value={mnPrice} onChange={(v) => setMnPrice(parseFloat(v) || 0)} type="number" step="0.50" />
            </div>

            <div className="text-center mb-6">
              <div className="text-sm text-slate-400 mb-2">Classification</div>
              <div className={`text-3xl font-bold ${
                moneyness.classification === 'ITM' ? 'text-emerald-400' :
                moneyness.classification === 'ATM' ? 'text-amber-400' : 'text-red-400'
              }`}>
                {moneyness.classification}
              </div>
              <div className="text-sm text-slate-400 mt-2">
                Difference: {(moneyness.pct_diff * 100).toFixed(2)}%
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <MetricCard label="Strike" value={`$${moneyness.strike.toFixed(2)}`} />
              <MetricCard label="Current Price" value={`$${moneyness.current_price.toFixed(2)}`} />
              <MetricCard label="% Difference" value={`${(moneyness.pct_diff * 100).toFixed(2)}%`} />
            </div>

            <div className="info-box">
              <p className="text-sm text-slate-300">
                <strong className="text-slate-100">For Put Options:</strong><br />
                <strong>ITM:</strong> Strike &gt; Stock Price (intrinsic value)<br />
                <strong>ATM:</strong> Strike ≈ Stock Price (sensitive to moves)<br />
                <strong>OTM:</strong> Strike &lt; Stock Price (time value only)
              </p>
            </div>
          </CardLg>
        </Tab>

        {/* Position Size */}
        <Tab label="Position Size">
          <CardLg>
            <h4 className="text-sm font-semibold mb-4 text-slate-300">Risk-Based Position Sizing</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <Input label="Account Value ($)" value={psAccount} onChange={(v) => setPsAccount(parseFloat(v) || 0)} type="number" step="1000" />
              <Input label="Risk per Trade (%)" value={psRisk} onChange={(v) => setPsRisk(parseFloat(v) || 0)} type="number" step="0.5" max="10" />
              <Input label="Premium per Contract ($)" value={psPremium} onChange={(v) => setPsPremium(parseFloat(v) || 0)} type="number" step="10" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <MetricCard label="Max Risk Amount" value={`$${positionSize.max_risk_dollars.toFixed(2)}`} />
              <MetricCard label="Max Contracts (Theoretical)" value={positionSize.max_contracts_theoretical.toFixed(2)} />
              <MetricCard label="Max Contracts (Actual)" value={positionSize.max_contracts_floored} />
            </div>

            <div className="info-box">
              <p className="text-sm text-slate-300">
                <strong className="text-slate-100">Position Sizing Rule:</strong> Risk no more than {psRisk}% per trade.
                With ${psAccount.toLocaleString()} and {psRisk}% risk: max {positionSize.max_contracts_floored} contracts
                at ${psPremium.toFixed(2)} each.
              </p>
            </div>
          </CardLg>
        </Tab>
      </Tabs>
    </div>
  );
}
