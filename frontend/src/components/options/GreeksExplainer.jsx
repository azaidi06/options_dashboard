/**
 * Greeks Explainer - Educational reference for options Greeks
 */
import { CardLg } from '../common/Card';

export function GreeksExplainer() {
  const greeks = [
    {
      name: 'Delta (Δ)',
      symbol: 'Δ',
      color: 'blue',
      description: 'Price sensitivity of the option',
      details: [
        'Measures how much the option price changes when stock price moves $1',
        'For puts, delta is negative (negative for put = protective)',
        'Range: -1.0 to 0.0 for puts',
        'ATM puts typically have delta around -0.50',
        'Deep ITM puts approach -1.0 (move 1:1 with stock)',
        'Deep OTM puts approach 0.0 (minimal movement)',
      ],
      example: 'Put with delta -0.45: If stock drops $1, put value increases ~$0.45',
      use: 'Predict how much profit/loss you make from stock price moves',
    },
    {
      name: 'Gamma (Γ)',
      symbol: 'Γ',
      color: 'purple',
      description: 'Rate of delta change (acceleration)',
      details: [
        'Measures how much delta changes when stock price moves',
        'Highest for ATM options (most sensitive to moves)',
        'Lowest for deep ITM/OTM options (more predictable)',
        'Positive for long options (benefits from large moves)',
        'As expiration approaches, ATM gamma increases significantly',
      ],
      example: 'Put with gamma 0.03: If delta is -0.45, moving to delta -0.48 after $1 move',
      use: 'Understand how fast your hedge effectiveness changes',
    },
    {
      name: 'Theta (Θ)',
      symbol: 'Θ',
      color: 'orange',
      description: 'Time decay (daily loss from passing time)',
      details: [
        'Negative for long options (you lose money each day)',
        'Usually expressed as per day decay',
        'Accelerates as expiration approaches (last week is critical)',
        'ATM options decay fastest',
        'OTM options decay slower but lose all value at expiration',
      ],
      example: 'Put with theta -0.05: You lose $0.05 per day from time decay alone',
      use: 'Factor in daily costs of holding the position',
    },
    {
      name: 'Vega (ν)',
      symbol: 'ν',
      color: 'green',
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
      name: 'Rho (ρ)',
      symbol: 'ρ',
      color: 'indigo',
      description: 'Interest rate sensitivity (usually small)',
      details: [
        'Less important than delta, gamma, theta, vega',
        'Matters more for long-dated options',
        'For puts, rho is typically negative (inverse to rates)',
      ],
      example: 'Put with rho -0.05: If rates rise 1%, put value drops ~$0.05',
      use: 'Minor adjustment for macro environment (mostly ignored)',
    },
  ];

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 text-gray-900">Options Greeks Guide</h3>

      <CardLg className="mb-6 bg-blue-50 border border-blue-200">
        <h4 className="text-md font-semibold mb-3 text-gray-900">What are the Greeks?</h4>
        <p className="text-gray-700">
          The Greeks are mathematical measures of how option prices change in response to different factors.
          They help you understand the risk and exposure of your position. Think of them as your option's
          sensitivity dials.
        </p>
      </CardLg>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {greeks.map((greek, idx) => (
          <CardLg key={idx} className="border-l-4" style={{ borderLeftColor: getColor(greek.color) }}>
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="text-lg font-bold text-gray-900">{greek.name}</h4>
                <p className="text-sm text-gray-600 mt-1">{greek.description}</p>
              </div>
              <div className={`text-4xl font-bold text-${greek.color}-600`}>{greek.symbol}</div>
            </div>

            <div className="mt-4 space-y-3">
              <div>
                <h5 className="text-sm font-semibold text-gray-700 mb-2">Key Points:</h5>
                <ul className="text-sm text-gray-700 space-y-1">
                  {greek.details.map((detail, i) => (
                    <li key={i} className="flex gap-2">
                      <span className="text-gray-400 flex-shrink-0">•</span>
                      <span>{detail}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-gray-50 p-3 rounded border border-gray-200">
                <h5 className="text-sm font-semibold text-gray-700 mb-1">Example:</h5>
                <p className="text-sm text-gray-700 font-mono">{greek.example}</p>
              </div>

              <div className="bg-yellow-50 p-3 rounded border border-yellow-200">
                <h5 className="text-sm font-semibold text-gray-700 mb-1">💡 Why it matters:</h5>
                <p className="text-sm text-gray-700">{greek.use}</p>
              </div>
            </div>
          </CardLg>
        ))}
      </div>

      {/* Quick Reference Table */}
      <CardLg>
        <h4 className="text-md font-semibold mb-4 text-gray-900">Quick Reference: Moneyness Impact</h4>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-100 border-b border-gray-300">
              <tr>
                <th className="px-4 py-2 text-left font-semibold">Greek</th>
                <th className="px-4 py-2 text-left font-semibold">ITM Put</th>
                <th className="px-4 py-2 text-left font-semibold">ATM Put</th>
                <th className="px-4 py-2 text-left font-semibold">OTM Put</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              <tr>
                <td className="px-4 py-2 font-semibold">Delta</td>
                <td className="px-4 py-2 text-green-600 font-mono">-0.8 to -1.0</td>
                <td className="px-4 py-2 text-yellow-600 font-mono">-0.4 to -0.6</td>
                <td className="px-4 py-2 text-red-600 font-mono">-0.0 to -0.3</td>
              </tr>
              <tr>
                <td className="px-4 py-2 font-semibold">Gamma</td>
                <td className="px-4 py-2">Low</td>
                <td className="px-4 py-2 font-bold">Highest</td>
                <td className="px-4 py-2">Low</td>
              </tr>
              <tr>
                <td className="px-4 py-2 font-semibold">Theta</td>
                <td className="px-4 py-2">Moderate</td>
                <td className="px-4 py-2 font-bold">Highest (decay)</td>
                <td className="px-4 py-2">Fast (to zero)</td>
              </tr>
              <tr>
                <td className="px-4 py-2 font-semibold">Vega</td>
                <td className="px-4 py-2">Moderate</td>
                <td className="px-4 py-2 font-bold">Highest</td>
                <td className="px-4 py-2">Low</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="mt-4 text-sm text-gray-700 bg-gray-50 p-4 rounded">
          <p>
            <strong>Key Insight:</strong> ATM (at-the-money) options are most sensitive to everything:
            largest gamma (fastest changing), largest theta decay, and largest vega (volatility impact).
            This is why trading ATM options is riskier but offers more opportunity.
          </p>
        </div>
      </CardLg>
    </div>
  );
}

function getColor(colorName) {
  const colors = {
    blue: '#2563eb',
    purple: '#a855f7',
    orange: '#f59e0b',
    green: '#10b981',
    indigo: '#4f46e5',
  };
  return colors[colorName] || '#6b7280';
}
