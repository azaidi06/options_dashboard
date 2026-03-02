/**
 * Technical Indicators Panel with tabs for RSI, MACD, Bollinger Bands, etc.
 */
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Tabs, Tab } from '../common/Tabs';

export function IndicatorsPanel({ ticker, indicators, stockData }) {
  if (indicators.loading) {
    return <div className="text-gray-500 text-center py-8">Loading indicators...</div>;
  }

  if (indicators.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded p-4">
        <p className="text-red-800">Error loading indicators: {indicators.error}</p>
      </div>
    );
  }

  if (!indicators.data || !indicators.data.data || indicators.data.data.length === 0) {
    return (
      <div className="text-gray-500 text-center py-8">No indicator data available</div>
    );
  }

  const data = indicators.data.data;

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 text-gray-900">
        {ticker} Technical Indicators
      </h3>

      <Tabs defaultTab={0}>
        <Tab label="📈 RSI (Relative Strength Index)">
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-4">
              RSI measures momentum. Values above 70 suggest overbought, below 30 suggest oversold.
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="rsi"
                  stroke="#f59e0b"
                  dot={false}
                  isAnimationActive={false}
                  name="RSI (14)"
                />
                {/* Overbought/Oversold lines */}
                <Line type="monotone" dataKey={() => 70} stroke="#ef4444" strokeDasharray="5 5" name="Overbought (70)" />
                <Line type="monotone" dataKey={() => 30} stroke="#10b981" strokeDasharray="5 5" name="Oversold (30)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Tab>

        <Tab label="📊 MACD">
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-4">
              MACD shows trend direction. Bullish when MACD crosses above signal line.
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="macd" stroke="#2563eb" dot={false} isAnimationActive={false} name="MACD" />
                <Line
                  type="monotone"
                  dataKey="macd_signal"
                  stroke="#f59e0b"
                  dot={false}
                  isAnimationActive={false}
                  name="Signal"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Tab>

        <Tab label="🎯 Bollinger Bands">
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-4">
              Price near upper band suggests overbought, near lower band suggests oversold.
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="bb_upper" fill="#dbeafe" stroke="#2563eb" name="Upper Band" />
                <Area type="monotone" dataKey="bb_lower" fill="#dbeafe" stroke="#2563eb" name="Lower Band" />
                <Line type="monotone" dataKey="bb_middle" stroke="#f59e0b" name="Middle (SMA 20)" isAnimationActive={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Tab>

        <Tab label="📉 Moving Averages">
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-4">
              Price above MA = uptrend, below MA = downtrend. Golden Cross (50 above 200) is bullish.
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="sma_20" stroke="#ec4899" dot={false} isAnimationActive={false} name="SMA 20" />
                <Line type="monotone" dataKey="sma_50" stroke="#f59e0b" dot={false} isAnimationActive={false} name="SMA 50" />
                <Line type="monotone" dataKey="sma_200" stroke="#10b981" dot={false} isAnimationActive={false} name="SMA 200" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Tab>

        <Tab label="⚡ EMA">
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-4">
              EMA reacts faster to price changes than SMA. Good for short-term trends.
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="ema_20" stroke="#3b82f6" dot={false} isAnimationActive={false} name="EMA 20" />
                <Line type="monotone" dataKey="ema_50" stroke="#8b5cf6" dot={false} isAnimationActive={false} name="EMA 50" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Tab>
      </Tabs>
    </div>
  );
}
