/**
 * Greeks Explainer - dark theme
 */
import { CardLg } from '../common/Card';

const GREEK_COLORS = {
  blue: { border: '#818cf8', text: 'text-blue-400', bg: 'bg-blue-500/10' },
  purple: { border: '#a78bfa', text: 'text-purple-400', bg: 'bg-purple-500/10' },
  orange: { border: '#f59e0b', text: 'text-amber-400', bg: 'bg-amber-500/10' },
  green: { border: '#10b981', text: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  indigo: { border: '#6366f1', text: 'text-indigo-400', bg: 'bg-indigo-500/10' },
};

export function GreeksExplainer() {
  const greeks = [
    {
      name: 'Delta (Δ)', symbol: 'Δ', color: 'blue',
      description: 'Price sensitivity of the option',
      details: [
        'Measures how much the option price changes when stock price moves $1',
        'For puts, delta is negative (protective)',
        'Range: -1.0 to 0.0 for puts',
        'ATM puts typically have delta around -0.50',
        'Deep ITM puts approach -1.0 (move 1:1 with stock)',
        'Deep OTM puts approach 0.0 (minimal movement)',
      ],
      example: 'Put with delta -0.45: If stock drops $1, put value increases ~$0.45',
      use: 'Predict how much profit/loss you make from stock price moves',
    },
    {
      name: 'Gamma (Γ)', symbol: 'Γ', color: 'purple',
      description: 'Rate of delta change (acceleration)',
      details: [
        'Measures how much delta changes when stock price moves',
        'Highest for ATM options (most sensitive to moves)',
        'Lowest for deep ITM/OTM options',
        'Positive for long options (benefits from large moves)',
        'As expiration approaches, ATM gamma increases significantly',
      ],
      example: 'Put with gamma 0.03: Delta moves from -0.45 to -0.48 after $1 move',
      use: 'Understand how fast your hedge effectiveness changes',
    },
    {
      name: 'Theta (Θ)', symbol: 'Θ', color: 'orange',
      description: 'Time decay (daily loss from passing time)',
      details: [
        'Negative for long options (you lose money each day)',
        'Usually expressed as per day decay',
        'Accelerates as expiration approaches',
        'ATM options decay fastest',
        'OTM options decay slower but lose all value at expiration',
      ],
      example: 'Put with theta -0.05: You lose $0.05 per day from time decay alone',
      use: 'Factor in daily costs of holding the position',
    },
    {
      name: 'Vega (ν)', symbol: 'ν', color: 'green',
      description: 'Volatility sensitivity',
      details: [
        'Measures option price change per 1% change in IV',
        'Positive for long options (higher IV = higher price)',
        'Highest for ATM options',
        'Increases with time to expiration',
        'Can create unexpected losses if IV drops (IV crush)',
      ],
      example: 'Put with vega 0.10: If IV drops 1%, put value drops ~$0.10',
      use: 'Anticipate impact of volatility changes on your position',
    },
    {
      name: 'Rho (ρ)', symbol: 'ρ', color: 'indigo',
      description: 'Interest rate sensitivity (usually small)',
      details: [
        'Less important than delta, gamma, theta, vega',
        'Matters more for long-dated options',
        'For puts, rho is typically negative',
      ],
      example: 'Put with rho -0.05: If rates rise 1%, put value drops ~$0.05',
      use: 'Minor adjustment for macro environment (mostly ignored)',
    },
  ];

  return (
    <div>
      <h3 className="text-base font-semibold mb-4 text-slate-200">Options Greeks Guide</h3>

      <div className="info-box mb-6">
        <h4 className="text-sm font-semibold mb-2 text-slate-100">What are the Greeks?</h4>
        <p className="text-sm text-slate-300">
          Mathematical measures of how option prices change in response to different factors.
          Think of them as your option's sensitivity dials.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
        {greeks.map((greek, idx) => {
          const colors = GREEK_COLORS[greek.color];
          return (
            <CardLg
              key={idx}
              className="border-l-4"
              style={{ borderLeftColor: colors.border }}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="text-base font-bold text-slate-100">{greek.name}</h4>
                  <p className="text-sm text-slate-400 mt-1">{greek.description}</p>
                </div>
                <div className={`text-3xl font-bold ${colors.text}`}>{greek.symbol}</div>
              </div>

              <div className="mt-4 space-y-3">
                <div>
                  <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Key Points</h5>
                  <ul className="text-sm text-slate-300 space-y-1">
                    {greek.details.map((detail, i) => (
                      <li key={i} className="flex gap-2">
                        <span className="text-slate-600 flex-shrink-0">•</span>
                        <span>{detail}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
                  <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Example</h5>
                  <p className="text-sm text-slate-300 font-mono">{greek.example}</p>
                </div>

                <div className={`${colors.bg} p-3 rounded-lg border border-slate-700/30`}>
                  <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Why it matters</h5>
                  <p className="text-sm text-slate-300">{greek.use}</p>
                </div>
              </div>
            </CardLg>
          );
        })}
      </div>

      {/* Quick Reference Table */}
      <CardLg>
        <h4 className="text-sm font-semibold mb-4 text-slate-300">Quick Reference: Moneyness Impact</h4>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Greek</th>
                <th>ITM Put</th>
                <th>ATM Put</th>
                <th>OTM Put</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="font-semibold text-slate-200">Delta</td>
                <td className="text-emerald-400 font-mono">-0.8 to -1.0</td>
                <td className="text-amber-400 font-mono">-0.4 to -0.6</td>
                <td className="text-red-400 font-mono">-0.0 to -0.3</td>
              </tr>
              <tr>
                <td className="font-semibold text-slate-200">Gamma</td>
                <td>Low</td>
                <td className="font-bold text-slate-100">Highest</td>
                <td>Low</td>
              </tr>
              <tr>
                <td className="font-semibold text-slate-200">Theta</td>
                <td>Moderate</td>
                <td className="font-bold text-slate-100">Highest (decay)</td>
                <td>Fast (to zero)</td>
              </tr>
              <tr>
                <td className="font-semibold text-slate-200">Vega</td>
                <td>Moderate</td>
                <td className="font-bold text-slate-100">Highest</td>
                <td>Low</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="info-box mt-4">
          <p className="text-sm text-slate-300">
            <strong className="text-slate-100">Key Insight:</strong> ATM options are most sensitive to
            everything: largest gamma, largest theta decay, and largest vega. This makes ATM options
            riskier but with more opportunity.
          </p>
        </div>
      </CardLg>
    </div>
  );
}
