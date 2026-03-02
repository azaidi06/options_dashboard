# Phase 2: React Frontend - Detailed Plan

## Overview

Build a modern React UI to replace the Streamlit app. The React app will call the FastAPI backend created in Phase 1.

**Key Principle**: One API endpoint = one React component or hook.

---

## Architecture

```
options_dashboard/
├── api/                          ← Phase 1 (complete)
├── frontend/                     ← Phase 2 (new Vite + React app)
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   └── Layout.jsx
│   │   │   ├── pages/
│   │   │   │   ├── HomePage.jsx
│   │   │   │   ├── StockAnalysisPage.jsx
│   │   │   │   └── PutOptionsPage.jsx
│   │   │   ├── stock/
│   │   │   │   ├── PriceChart.jsx
│   │   │   │   ├── IndicatorsPanel.jsx
│   │   │   │   ├── DrawdownChart.jsx
│   │   │   │   ├── OpportunitiesTable.jsx
│   │   │   │   └── TechnicalIndicatorTabs.jsx
│   │   │   ├── options/
│   │   │   │   ├── OptionChain.jsx
│   │   │   │   ├── IVSmileChart.jsx
│   │   │   │   ├── PayoffDiagram.jsx
│   │   │   │   ├── CalculatorPanel.jsx
│   │   │   │   ├── GreeksExplainer.jsx
│   │   │   │   └── RiskCalculator.jsx
│   │   │   └── common/
│   │   │       ├── Card.jsx
│   │   │       ├── Button.jsx
│   │   │       ├── Input.jsx
│   │   │       └── Select.jsx
│   │   ├── hooks/
│   │   │   ├── useStockData.js
│   │   │   ├── useIndicators.js
│   │   │   ├── useDrawdown.js
│   │   │   ├── useOpportunities.js
│   │   │   ├── useOptionChain.js
│   │   │   └── useTickers.js
│   │   ├── utils/
│   │   │   └── api.js         ← API client wrapper
│   │   ├── App.jsx
│   │   ├── index.css          ← Tailwind + custom styles
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── robust_app.py               ← Streamlit (still running)
└── requirements.txt
```

---

## Phase 2a: Stock Analysis UI (Days 1-2)

### Goal
Build the stock analysis page with price charts, indicators, drawdown analysis, and opportunities.

### Components to Build

#### 1. **StockAnalysisPage.jsx**
Main page layout. Features:
- Ticker input + date range picker
- Load button
- Tabs: Price Chart | Indicators | Drawdown | Opportunities

```jsx
export default function StockAnalysisPage() {
  const [ticker, setTicker] = useState("AAPL");
  const [startDate, setStartDate] = useState("2023-01-01");
  const [endDate, setEndDate] = useState(today);
  const [lookbackDays, setLookbackDays] = useState(30);

  // Load data when user clicks Load
  const { data, loading, error } = useStockData(ticker, startDate, endDate, lookbackDays);

  return (
    <Layout>
      <Card>
        <Input placeholder="Ticker" value={ticker} onChange={setTicker} />
        <Input type="date" value={startDate} onChange={setStartDate} />
        <Input type="date" value={endDate} onChange={setEndDate} />
        <Select label="Lookback Days" options={[5, 10, 20, 30, 60, 200]} value={lookbackDays} onChange={setLookbackDays} />
        <Button onClick={() => /* refetch */}>Load Data</Button>
      </Card>

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {data && (
        <Tabs defaultTab="chart">
          <Tab label="Price Chart">
            <PriceChart data={data.data} />
          </Tab>
          <Tab label="Indicators">
            <IndicatorsPanel ticker={ticker} startDate={startDate} endDate={endDate} />
          </Tab>
          <Tab label="Drawdown">
            <DrawdownChart ticker={ticker} startDate={startDate} endDate={endDate} />
          </Tab>
          <Tab label="Opportunities">
            <OpportunitiesTable ticker={ticker} startDate={startDate} endDate={endDate} />
          </Tab>
        </Tabs>
      )}
    </Layout>
  );
}
```

#### 2. **PriceChart.jsx**
Recharts ComposedChart with:
- Line chart for Close price
- Column chart for Volume
- Gradient coloring based on distance from rolling high
- Hover tooltips with OHLCV

```jsx
export default function PriceChart({ data }) {
  // Compute color based on pct_change
  const getColor = (pctChange) => {
    if (pctChange >= 0) return "#22c55e"; // green
    if (pctChange > -0.05) return "#fbbf24"; // yellow
    if (pctChange > -0.10) return "#fb923c"; // orange
    return "#ef4444"; // red
  };

  return (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="close" stroke="#1f2937" isAnimationActive={false} />
        <Bar dataKey="volume" fill="#9ca3af" />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
```

#### 3. **IndicatorsPanel.jsx**
Tabs for RSI, MACD, Bollinger Bands, Moving Averages.

```jsx
export default function IndicatorsPanel({ ticker, startDate, endDate }) {
  const { data, loading } = useIndicators(ticker, startDate, endDate);

  return (
    <Tabs defaultTab="rsi">
      <Tab label="RSI">
        <RSIChart data={data?.rsi} />
      </Tab>
      <Tab label="MACD">
        <MACDChart data={data?.macd} />
      </Tab>
      <Tab label="Bollinger Bands">
        <BollingerChart data={data?.bollinger} />
      </Tab>
      <Tab label="Moving Averages">
        <MovingAveragesChart data={data?.moving_averages} />
      </Tab>
    </Tabs>
  );
}
```

#### 4. **DrawdownChart.jsx**
Stacked area chart showing underwater periods + line chart for cumulative drawdown.

```jsx
export default function DrawdownChart({ ticker, startDate, endDate }) {
  const { data } = useDrawdown(ticker, startDate, endDate);

  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data?.underwater_data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Area type="monotone" dataKey="drawdown_pct" fill="#ef4444" stroke="#dc2626" />
        </AreaChart>
      </ResponsiveContainer>

      <Card className="mt-4">
        <h3>Drawdown Events</h3>
        <table>
          <thead>
            <tr>
              <th>Peak Date</th>
              <th>Peak Price</th>
              <th>Trough Date</th>
              <th>Drawdown %</th>
              <th>Recovery Days</th>
            </tr>
          </thead>
          <tbody>
            {data?.events.map((event) => (
              <tr key={event.peak_date}>
                <td>{event.peak_date}</td>
                <td>${event.peak_price.toFixed(2)}</td>
                <td>{event.trough_date}</td>
                <td>{(event.drawdown_pct * 100).toFixed(1)}%</td>
                <td>{event.days_to_recovery || "Not recovered"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
```

#### 5. **OpportunitiesTable.jsx**
Table showing opportunity windows with filters.

```jsx
export default function OpportunitiesTable({ ticker, startDate, endDate }) {
  const [entryThreshold, setEntryThreshold] = useState(0.10);
  const [exitThreshold, setExitThreshold] = useState(0.05);

  const { data } = useOpportunities(ticker, startDate, endDate, entryThreshold, exitThreshold);

  return (
    <Card>
      <div className="flex gap-4 mb-4">
        <div>
          <label>Entry Threshold</label>
          <Input type="number" value={entryThreshold} onChange={(v) => setEntryThreshold(v / 100)} step="0.01" />
        </div>
        <div>
          <label>Exit Threshold</label>
          <Input type="number" value={exitThreshold} onChange={(v) => setExitThreshold(v / 100)} step="0.01" />
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Start Date</th>
            <th>End Date</th>
            <th>Duration (Days)</th>
            <th>Max Drawdown</th>
          </tr>
        </thead>
        <tbody>
          {data?.windows.map((window) => (
            <tr key={window.start_date}>
              <td>{window.start_date}</td>
              <td>{window.end_date || "Open"}</td>
              <td>{window.duration_days}</td>
              <td>{(window.max_drawdown * 100).toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>

      <Card className="mt-4">
        <h3>Statistics</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-gray-500">Total Windows</p>
            <p className="text-2xl font-bold">{data?.stats.total_windows}</p>
          </div>
          <div>
            <p className="text-gray-500">Avg Duration</p>
            <p className="text-2xl font-bold">{data?.stats.avg_duration?.toFixed(0)} days</p>
          </div>
          <div>
            <p className="text-gray-500">Avg Max Drawdown</p>
            <p className="text-2xl font-bold">{(data?.stats.avg_max_drawdown * 100).toFixed(1)}%</p>
          </div>
          <div>
            <p className="text-gray-500">% Time in Window</p>
            <p className="text-2xl font-bold">{(data?.stats.pct_time_in_window * 100).toFixed(1)}%</p>
          </div>
        </div>
      </Card>
    </Card>
  );
}
```

### Custom Hooks

#### **useStockData.js**
```javascript
import useSWR from "swr";
import { fetchStockData } from "../utils/api";

export function useStockData(ticker, start, end, lookbackDays) {
  const { data, error, isLoading, mutate } = useSWR(
    ticker ? `/api/stock/${ticker}?start=${start}&end=${end}&lookback_days=${lookbackDays}` : null,
    fetchStockData,
    { revalidateOnFocus: false }
  );

  return {
    data,
    loading: isLoading,
    error: error?.message,
    refetch: mutate,
  };
}
```

#### **useIndicators.js**, **useDrawdown.js**, **useOpportunities.js**
Similar pattern, wrapping API calls with SWR.

---

## Phase 2b: Options UI (Days 3-4)

### Goal
Build the put options page with option chains, calculators, and Greeks.

### Components to Build

#### 1. **PutOptionsPage.jsx**
Main options page. Features:
- Ticker selector (dropdown from available tickers)
- Date picker (quote date)
- Expiration selector
- Tabs: Option Chain | IV Smile | Calculators | Greeks

#### 2. **OptionChain.jsx**
Interactive table with sortable columns: Strike, Bid, Ask, IV, Delta, Gamma, etc.

#### 3. **IVSmileChart.jsx**
Recharts LineChart: X = Strike, Y = Implied Volatility

#### 4. **PayoffDiagram.jsx**
Recharts showing long put payoff profile with strike/premium inputs.

#### 5. **CalculatorPanel.jsx**
Forms for:
- Time Decay: premium + theta + days → decay projection
- Price Change: premium + delta + gamma + price_change → new premium
- Moneyness: strike + current_price → ITM/ATM/OTM
- Position Size: account + risk% + premium → max contracts

#### 6. **GreeksExplainer.jsx**
Educational cards explaining Delta, Theta, Gamma, Vega with examples.

### Estimated Effort
- Option Chain UI: 3-4 hours
- IV Smile Chart: 1-2 hours
- Payoff Diagram: 2-3 hours
- Calculators: 3-4 hours
- Greeks Explainer: 1-2 hours
- **Total: ~6-8 hours of development**

---

## Phase 2c: Deployment (Day 5)

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/options-dashboard.conf

upstream fastapi {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name options-dashboard.duckdns.org;

    # API proxy
    location /api/ {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # React static files
    location / {
        root /home/ubuntu/options_dashboard/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

### Build & Deploy Steps
```bash
# 1. Build React app
cd frontend
npm run build
# Generates: dist/ folder with optimized static files

# 2. Verify nginx config
sudo nginx -t

# 3. Reload nginx
sudo systemctl reload nginx

# 4. Verify backend is running
curl http://localhost:8000/health

# 5. Test full app
# Visit: http://options-dashboard.duckdns.org
```

---

## Tech Stack Details

### Dependencies to Add
```json
{
  "react": "^19.0.0",
  "react-dom": "^19.0.0",
  "vite": "^5.0.0",
  "recharts": "^2.10.0",
  "swr": "^2.2.0",
  "tailwindcss": "^3.3.0",
  "postcss": "^8.4.0",
  "autoprefixer": "^10.4.0"
}
```

### Build Command
```bash
npm run build  # Builds to frontend/dist/
```

### Dev Server
```bash
npm run dev    # Runs on http://localhost:5173
```

---

## Component Structure

### Data Flow
```
Page Component (StockAnalysisPage, PutOptionsPage)
    ↓
Custom Hook (useStockData, useIndicators)
    ↓
SWR + Fetcher (api.js)
    ↓
FastAPI Endpoint (/api/stock/*, /api/options/*)
    ↓
Service Layer (analytics.py, options.py)
    ↓
Existing Functions (utils.py, options_utils.py)
```

### Styling Approach
- **Tailwind CSS** for utility classes (same as war-markets-react)
- **Custom component library** for common UI (Card, Button, Input, Select)
- **Recharts** for all charts (consistent with war-markets)

---

## Testing Strategy

### Unit Tests (Optional, Phase 2 end)
- Test custom hooks with MSW (Mock Service Worker)
- Test component rendering with React Testing Library

### E2E Tests (Optional, Phase 2 end)
- Playwright or Cypress for full page flows
- Test loading data, switching tabs, chart rendering

### Manual Testing Checklist
- [ ] Stock page loads AAPL data correctly
- [ ] Indicators tab shows RSI, MACD, Bollinger Bands
- [ ] Drawdown tab shows underwater periods and events
- [ ] Opportunities tab filters work
- [ ] Options page loads available tickers
- [ ] Option chain filters by date/expiration
- [ ] Payoff diagram updates with strike/premium
- [ ] All calculators work correctly
- [ ] Mobile responsive on phone/tablet
- [ ] Dark mode (if added)

---

## Performance Optimizations

1. **SWR Caching**: Automatic client-side cache prevents duplicate API calls
2. **React.memo()**: Memoize chart components to prevent unnecessary rerenders
3. **Lazy Loading**: Dynamic imports for less-used routes
4. **Debouncing**: Debounce input changes before API calls
5. **Code Splitting**: Vite automatically chunks code for lazy loading

---

## Migration Roadmap

### Timeline
- **Phase 1**: FastAPI Backend ✅ (complete)
- **Phase 2a**: Stock UI (Days 1-2)
- **Phase 2b**: Options UI (Days 3-4)
- **Phase 2c**: Deployment (Day 5)
- **Total: ~4-5 days of focused development**

### Concurrent Running
During Phase 2 development:
- React app runs on localhost:5173 (dev server)
- FastAPI backend runs on localhost:8000
- Streamlit still running on localhost:8501
- All three can coexist without conflicts

### Cutover Strategy
1. **Week 1-2**: Develop and test React app
2. **Week 3**: Feature parity testing (compare React vs Streamlit outputs)
3. **Week 4**: Deploy React to production, keep Streamlit as backup
4. **Week 5+**: Monitor React usage, deprecate Streamlit once stable

---

## Estimated Complete Timeline

| Phase | Component | Duration | Status |
|-------|-----------|----------|--------|
| 1 | FastAPI Backend | 1 day | ✅ Complete |
| 2a | Stock UI | 2 days | 🔄 TODO |
| 2b | Options UI | 2 days | 🔄 TODO |
| 2c | Deployment | 1 day | 🔄 TODO |
| | **Total** | **6 days** | |

---

## Success Criteria: Phase 2

- ✅ React app displays stock data (OHLCV chart with gradient coloring)
- ✅ All tabs (Indicators, Drawdown, Opportunities) functional
- ✅ Option chain loads and filters correctly
- ✅ All calculator endpoints work and display results
- ✅ Mobile responsive on phone/tablet
- ✅ Feature parity with Streamlit app achieved
- ✅ Deployed and running on options-dashboard.duckdns.org

---

## First Steps to Start Phase 2

```bash
# 1. Create new React app with Vite
cd options_dashboard
npm create vite@latest frontend -- --template react

# 2. Install dependencies
cd frontend
npm install
npm install recharts swr tailwindcss postcss autoprefixer

# 3. Setup Tailwind
npx tailwindcss init -p

# 4. Start dev server
npm run dev

# 5. Open browser
# http://localhost:5173
```

Then start building components!

---

**Phase 2 Planning: Complete**

Ready to begin React frontend development on your signal.
