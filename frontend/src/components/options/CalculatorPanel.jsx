/**
 * Calculator Panel - Risk calculators for options
 */
import { useState } from 'react';
import { Tabs, Tab } from '../common/Tabs';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { CardLg, MetricCard } from '../common/Card';
import {
  useTimeDecay,
  usePriceChangeImpact,
  useMoneyness,
  usePositionSize,
} from '../../hooks/useOptionsData';
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

export function CalculatorPanel() {
  // Time Decay Calculator
  const [tdPremium, setTdPremium] = useState(2.5);
  const [tdTheta, setTdTheta] = useState(-0.05);
  const [tdDays, setTdDays] = useState(30);
  const timeDecay = useTimeDecay(tdPremium, tdTheta, tdDays);

  // Price Change Impact Calculator
  const [piPremium, setPiPremium] = useState(2.5);
  const [piDelta, setPiDelta] = useState(-0.45);
  const [piGamma, setPiGamma] = useState(0.02);
  const [piPriceChange, setPiPriceChange] = useState(-5);
  const priceImpact = usePriceChangeImpact(piPremium, piDelta, piGamma, piPriceChange);

  // Moneyness Calculator
  const [mnStrike, setMnStrike] = useState(100);
  const [mnPrice, setMnPrice] = useState(102);
  const moneyness = useMoneyness(mnStrike, mnPrice);

  // Position Size Calculator
  const [psAccount, setPsAccount] = useState(10000);
  const [psRisk, setPsRisk] = useState(2);
  const [psPremium, setPsPremium] = useState(250);
  const positionSize = usePositionSize(psAccount, psRisk, psPremium);

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 text-gray-900">Risk Calculators</h3>

      <Tabs defaultTab={0}>
        {/* Time Decay Calculator */}
        <Tab label="⏱️ Time Decay">
          <CardLg>
            <h4 className="text-md font-semibold mb-4 text-gray-900">Premium Decay Over Time</h4>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <Input
                label="Initial Premium"
                value={tdPremium}
                onChange={(v) => setTdPremium(parseFloat(v))}
                type="number"
                step="0.10"
              />
              <Input
                label="Daily Theta"
                value={tdTheta}
                onChange={(v) => setTdTheta(parseFloat(v))}
                type="number"
                step="0.01"
              />
              <Input
                label="Days to Expiration"
                value={tdDays}
                onChange={(v) => setTdDays(parseInt(v))}
                type="number"
              />
              <div className="flex items-end">
                <Button onClick={() => {}} className="w-full">
                  Calculate
                </Button>
              </div>
            </div>

            {timeDecay.loading ? (
              <p className="text-gray-500">Calculating...</p>
            ) : timeDecay.data ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={timeDecay.data.data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="days_remaining" label={{ value: 'Days Remaining', position: 'insideBottomRight', offset: -5 }} />
                  <YAxis label={{ value: 'Premium ($)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip formatter={(v) => `$${v.toFixed(2)}`} />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="premium"
                    stroke="#f59e0b"
                    name="Projected Premium"
                    isAnimationActive={false}
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : null}

            <div className="mt-4 text-sm text-gray-700 bg-yellow-50 p-4 rounded">
              <p>
                <strong>💡 Theta Effect:</strong> As expiration approaches, time decay accelerates.
                This calculator shows how premium value erodes over time with daily theta decay of $
                {Math.abs(tdTheta).toFixed(3)}.
              </p>
            </div>
          </CardLg>
        </Tab>

        {/* Price Change Impact */}
        <Tab label="📈 Price Change Impact">
          <CardLg>
            <h4 className="text-md font-semibold mb-4 text-gray-900">Delta-Gamma Impact</h4>

            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
              <Input
                label="Current Premium"
                value={piPremium}
                onChange={(v) => setPiPremium(parseFloat(v))}
                type="number"
                step="0.10"
              />
              <Input
                label="Delta"
                value={piDelta}
                onChange={(v) => setPiDelta(parseFloat(v))}
                type="number"
                step="0.01"
              />
              <Input
                label="Gamma"
                value={piGamma}
                onChange={(v) => setPiGamma(parseFloat(v))}
                type="number"
                step="0.001"
              />
              <Input
                label="Price Change ($)"
                value={piPriceChange}
                onChange={(v) => setPiPriceChange(parseFloat(v))}
                type="number"
                step="0.50"
              />
              <div className="flex items-end">
                <Button onClick={() => {}} className="w-full">
                  Calculate
                </Button>
              </div>
            </div>

            {priceImpact.loading ? (
              <p className="text-gray-500">Calculating...</p>
            ) : priceImpact.data ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <MetricCard
                  label="Current Premium"
                  value={`$${priceImpact.data.current_premium.toFixed(2)}`}
                />
                <MetricCard
                  label="Estimated New Premium"
                  value={`$${priceImpact.data.estimated_premium.toFixed(2)}`}
                />
                <MetricCard
                  label="P/L Change"
                  value={`$${(priceImpact.data.estimated_premium - priceImpact.data.current_premium).toFixed(2)}`}
                  className={priceImpact.data.estimated_premium > priceImpact.data.current_premium ? 'bg-green-100' : 'bg-red-100'}
                />
              </div>
            ) : null}

            <div className="mt-4 space-y-2 text-sm text-gray-700 bg-blue-50 p-4 rounded">
              <p>
                <strong>Delta Effect:</strong> ${priceImpact.data?.delta_effect.toFixed(3) || '—'} (price sensitivity)
              </p>
              <p>
                <strong>Gamma Effect:</strong> ${priceImpact.data?.gamma_effect.toFixed(3) || '—'} (acceleration)
              </p>
              <p>
                <strong>💡 What it means:</strong> Shows how put value changes when stock price moves,
                accounting for both delta (directional exposure) and gamma (accelerating moves).
              </p>
            </div>
          </CardLg>
        </Tab>

        {/* Moneyness */}
        <Tab label="💰 Moneyness">
          <CardLg>
            <h4 className="text-md font-semibold mb-4 text-gray-900">Option Moneyness</h4>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <Input
                label="Strike Price"
                value={mnStrike}
                onChange={(v) => setMnStrike(parseFloat(v))}
                type="number"
                step="0.50"
              />
              <Input
                label="Current Stock Price"
                value={mnPrice}
                onChange={(v) => setMnPrice(parseFloat(v))}
                type="number"
                step="0.50"
              />
              <div className="flex items-end">
                <Button onClick={() => {}} className="w-full">
                  Classify
                </Button>
              </div>
            </div>

            {moneyness.data ? (
              <div className="space-y-4">
                <div className="text-center">
                  <div className="text-sm text-gray-600 mb-2">Classification</div>
                  <div className={`text-3xl font-bold ${
                    moneyness.data.classification === 'ITM'
                      ? 'text-green-600'
                      : moneyness.data.classification === 'ATM'
                      ? 'text-yellow-600'
                      : 'text-red-600'
                  }`}>
                    {moneyness.data.classification}
                  </div>
                  <div className="text-sm text-gray-600 mt-2">
                    Difference: {((moneyness.data.pct_diff || 0) * 100).toFixed(2)}%
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <MetricCard
                    label="Strike"
                    value={`$${moneyness.data.strike.toFixed(2)}`}
                  />
                  <MetricCard
                    label="Current Price"
                    value={`$${moneyness.data.current_price.toFixed(2)}`}
                  />
                  <MetricCard
                    label="% Difference"
                    value={`${((moneyness.data.pct_diff || 0) * 100).toFixed(2)}%`}
                  />
                </div>

                <div className="text-sm text-gray-700 bg-gray-50 p-4 rounded">
                  <p>
                    <strong>For Put Options:</strong>
                    <br />• <strong>ITM (In-the-Money):</strong> Strike &gt; Stock Price (intrinsic value)
                    <br />• <strong>ATM (At-the-Money):</strong> Strike ≈ Stock Price (sensitive to moves)
                    <br />• <strong>OTM (Out-of-the-Money):</strong> Strike &lt; Stock Price (time value only)
                  </p>
                </div>
              </div>
            ) : null}
          </CardLg>
        </Tab>

        {/* Position Sizing */}
        <Tab label="📊 Position Size">
          <CardLg>
            <h4 className="text-md font-semibold mb-4 text-gray-900">Risk-Based Position Sizing</h4>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <Input
                label="Account Value ($)"
                value={psAccount}
                onChange={(v) => setPsAccount(parseFloat(v))}
                type="number"
                step="1000"
              />
              <Input
                label="Risk per Trade (%)"
                value={psRisk}
                onChange={(v) => setPsRisk(parseFloat(v))}
                type="number"
                step="0.5"
                max="10"
              />
              <Input
                label="Premium per Contract ($)"
                value={psPremium}
                onChange={(v) => setPsPremium(parseFloat(v))}
                type="number"
                step="10"
              />
              <div className="flex items-end">
                <Button onClick={() => {}} className="w-full">
                  Calculate
                </Button>
              </div>
            </div>

            {positionSize.data ? (
              <div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <MetricCard
                    label="Max Risk Amount"
                    value={`$${positionSize.data.max_risk_dollars.toFixed(2)}`}
                  />
                  <MetricCard
                    label="Max Contracts (Theoretical)"
                    value={positionSize.data.max_contracts_theoretical.toFixed(2)}
                  />
                  <MetricCard
                    label="Max Contracts (Actual)"
                    value={positionSize.data.max_contracts_floored}
                    className="bg-green-100"
                  />
                </div>

                <div className="text-sm text-gray-700 bg-green-50 p-4 rounded">
                  <p>
                    <strong>Position Sizing Rule:</strong> Risk no more than {psRisk}% of your
                    account per trade. With ${psAccount.toLocaleString()} and {psRisk}% risk tolerance:
                  </p>
                  <ul className="mt-2 ml-4 list-disc space-y-1">
                    <li>
                      Max risk per trade: ${positionSize.data.max_risk_dollars.toFixed(2)}
                    </li>
                    <li>
                      Max contracts you can buy: {positionSize.data.max_contracts_floored}
                    </li>
                    <li>
                      This assumes premium per contract of ${psPremium.toFixed(2)}
                    </li>
                  </ul>
                </div>
              </div>
            ) : null}
          </CardLg>
        </Tab>
      </Tabs>
    </div>
  );
}
