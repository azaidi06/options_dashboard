/**
 * Technical Indicators Panel - dark theme
 */
import {
  LineChart,
  ComposedChart,
  Line,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from 'recharts';
import { Tabs, Tab } from '../common/Tabs';

const TOOLTIP_STYLE = {
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  border: '1px solid #334155',
  borderRadius: '8px',
};

const GRID_COLOR = '#1e293b';
const AXIS_TICK = { fontSize: 11, fill: '#94a3b8' };
const AXIS_STROKE = '#334155';

export function IndicatorsPanel({ ticker, indicators, stockData }) {
  if (indicators.loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="spinner-lg" />
        <span className="ml-3 text-slate-400 text-sm">Loading indicators...</span>
      </div>
    );
  }

  if (indicators.error) {
    return (
      <div className="error-box">
        <p className="text-slate-300">Error loading indicators: {indicators.error}</p>
      </div>
    );
  }

  if (!indicators.data || !indicators.data.data || indicators.data.data.length === 0) {
    return <div className="text-slate-500 text-center py-8">No indicator data available</div>;
  }

  const data = indicators.data.data;

  return (
    <div>
      <h3 className="text-base font-semibold mb-4 text-slate-200">
        {ticker} Technical Indicators
      </h3>

      <Tabs defaultTab={0}>
        <Tab label="RSI">
          <div className="mt-2">
            <p className="text-sm text-slate-400 mb-4">
              RSI measures momentum. Values above 70 suggest overbought, below 30 suggest oversold.
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} />
                <XAxis dataKey="date" tick={AXIS_TICK} stroke={AXIS_STROKE} />
                <YAxis domain={[0, 100]} tick={AXIS_TICK} stroke={AXIS_STROKE} />
                <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={{ color: '#e2e8f0' }} itemStyle={{ color: '#cbd5e1' }} />
                <Legend wrapperStyle={{ color: '#94a3b8' }} />
                <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="5 5" label={{ value: '70', position: 'right', fill: '#ef4444', fontSize: 11 }} />
                <ReferenceLine y={30} stroke="#10b981" strokeDasharray="5 5" label={{ value: '30', position: 'right', fill: '#10b981', fontSize: 11 }} />
                <Line type="monotone" dataKey="rsi" stroke="#f59e0b" dot={false} isAnimationActive={false} name="RSI (14)" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Tab>

        <Tab label="MACD">
          <div className="mt-2">
            <p className="text-sm text-slate-400 mb-4">
              MACD shows trend direction. Bullish when MACD crosses above signal line.
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} />
                <XAxis dataKey="date" tick={AXIS_TICK} stroke={AXIS_STROKE} />
                <YAxis tick={AXIS_TICK} stroke={AXIS_STROKE} />
                <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={{ color: '#e2e8f0' }} itemStyle={{ color: '#cbd5e1' }} />
                <Legend wrapperStyle={{ color: '#94a3b8' }} />
                <ReferenceLine y={0} stroke="#475569" />
                <Bar dataKey="macd_hist" name="Histogram" isAnimationActive={false}>
                  {data.map((entry, i) => (
                    <Cell key={i} fill={entry.macd_hist >= 0 ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)'} />
                  ))}
                </Bar>
                <Line type="monotone" dataKey="macd" stroke="#818cf8" dot={false} isAnimationActive={false} name="MACD" strokeWidth={2} />
                <Line type="monotone" dataKey="macd_signal" stroke="#f59e0b" dot={false} isAnimationActive={false} name="Signal" strokeWidth={2} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </Tab>

        <Tab label="Bollinger Bands">
          <div className="mt-2">
            <p className="text-sm text-slate-400 mb-4">
              Price near upper band suggests overbought, near lower band suggests oversold.
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} />
                <XAxis dataKey="date" tick={AXIS_TICK} stroke={AXIS_STROKE} />
                <YAxis tick={AXIS_TICK} stroke={AXIS_STROKE} />
                <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={{ color: '#e2e8f0' }} itemStyle={{ color: '#cbd5e1' }} />
                <Legend wrapperStyle={{ color: '#94a3b8' }} />
                <Area type="monotone" dataKey="bb_upper" fill="rgba(99, 102, 241, 0.1)" stroke="#818cf8" name="Upper Band" />
                <Area type="monotone" dataKey="bb_lower" fill="rgba(99, 102, 241, 0.1)" stroke="#818cf8" name="Lower Band" />
                <Line type="monotone" dataKey="bb_middle" stroke="#f59e0b" name="Middle (SMA 20)" isAnimationActive={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Tab>

        <Tab label="Moving Averages">
          <div className="mt-2">
            <p className="text-sm text-slate-400 mb-4">
              Price above MA = uptrend, below MA = downtrend. Golden Cross (50 above 200) is bullish.
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} />
                <XAxis dataKey="date" tick={AXIS_TICK} stroke={AXIS_STROKE} />
                <YAxis tick={AXIS_TICK} stroke={AXIS_STROKE} />
                <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={{ color: '#e2e8f0' }} itemStyle={{ color: '#cbd5e1' }} />
                <Legend wrapperStyle={{ color: '#94a3b8' }} />
                <Line type="monotone" dataKey="sma_20" stroke="#ec4899" dot={false} isAnimationActive={false} name="SMA 20" />
                <Line type="monotone" dataKey="sma_50" stroke="#f59e0b" dot={false} isAnimationActive={false} name="SMA 50" />
                <Line type="monotone" dataKey="sma_200" stroke="#10b981" dot={false} isAnimationActive={false} name="SMA 200" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Tab>

        <Tab label="EMA">
          <div className="mt-2">
            <p className="text-sm text-slate-400 mb-4">
              EMA reacts faster to price changes than SMA. Good for short-term trends.
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} />
                <XAxis dataKey="date" tick={AXIS_TICK} stroke={AXIS_STROKE} />
                <YAxis tick={AXIS_TICK} stroke={AXIS_STROKE} />
                <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={{ color: '#e2e8f0' }} itemStyle={{ color: '#cbd5e1' }} />
                <Legend wrapperStyle={{ color: '#94a3b8' }} />
                <Line type="monotone" dataKey="ema_20" stroke="#818cf8" dot={false} isAnimationActive={false} name="EMA 20" />
                <Line type="monotone" dataKey="ema_50" stroke="#a78bfa" dot={false} isAnimationActive={false} name="EMA 50" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Tab>
      </Tabs>
    </div>
  );
}
