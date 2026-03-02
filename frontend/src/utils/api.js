/**
 * API client for FastAPI backend
 * Handles all HTTP requests to the backend API
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
  } catch (err) {
    const networkError = new Error(
      'Backend not running. Start with: python -m uvicorn api.main:app --port 8000 --reload'
    );
    networkError.isNetworkError = true;
    throw networkError;
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: response.statusText,
    }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return await response.json();
}

// ============================================================================
// Stock Endpoints
// ============================================================================

export async function fetchStockData(ticker, start, end, lookbackDays = 30) {
  const params = new URLSearchParams({
    start,
    end,
    lookback_days: lookbackDays,
  });
  return fetchAPI(`/stock/${ticker}?${params}`);
}

export async function fetchIndicators(
  ticker,
  start,
  end,
  rsiPeriod = 14,
  macdFast = 12,
  macdSlow = 26,
  macdSignal = 9,
  bbPeriod = 20,
  bbStd = 2.0,
  smaPeriods = '20,50,200',
  emaPeriods = '20,50'
) {
  const params = new URLSearchParams({
    start,
    end,
    rsi_period: rsiPeriod,
    macd_fast: macdFast,
    macd_slow: macdSlow,
    macd_signal: macdSignal,
    bb_period: bbPeriod,
    bb_std: bbStd,
    sma_periods: smaPeriods,
    ema_periods: emaPeriods,
  });
  return fetchAPI(`/stock/${ticker}/indicators?${params}`);
}

export async function fetchDrawdown(ticker, start, end, minDrawdownPct = 0.05) {
  const params = new URLSearchParams({
    start,
    end,
    min_drawdown_pct: minDrawdownPct,
  });
  return fetchAPI(`/stock/${ticker}/drawdown?${params}`);
}

export async function fetchOpportunities(
  ticker,
  start,
  end,
  entryThreshold = 0.10,
  exitThreshold = 0.05
) {
  const params = new URLSearchParams({
    start,
    end,
    entry_threshold: entryThreshold,
    exit_threshold: exitThreshold,
  });
  return fetchAPI(`/stock/${ticker}/opportunities?${params}`);
}

// ============================================================================
// Options Endpoints
// ============================================================================

export async function fetchOptionsTickers() {
  return fetchAPI('/options/tickers');
}

export async function fetchTickerDateRange(ticker) {
  return fetchAPI(`/options/${ticker}/dates`);
}

export async function fetchOptionChain(ticker, date, expiration) {
  const params = new URLSearchParams({
    ...(date && { date }),
    ...(expiration && { expiration }),
  });
  return fetchAPI(`/options/${ticker}/chain?${params}`);
}

export async function fetchIVSmile(ticker, date, expiration) {
  const params = new URLSearchParams({
    date,
    expiration,
  });
  return fetchAPI(`/options/${ticker}/iv-smile?${params}`);
}

export async function fetchPayoffDiagram(strike, premium, minPrice, maxPrice, numPoints = 11) {
  const params = new URLSearchParams({
    strike,
    premium,
    ...(minPrice && { price_range_min: minPrice }),
    ...(maxPrice && { price_range_max: maxPrice }),
    num_points: numPoints,
  });
  return fetchAPI(`/options/payoff?${params}`);
}

export async function fetchTimeDecay(premium, theta, daysRemaining) {
  const params = new URLSearchParams({
    premium,
    theta,
    days_remaining: daysRemaining,
  });
  return fetchAPI(`/options/calculator/time-decay?${params}`);
}

export async function fetchPriceChangeImpact(currentPremium, delta, gamma, priceChange) {
  const params = new URLSearchParams({
    current_premium: currentPremium,
    delta,
    gamma,
    price_change: priceChange,
  });
  return fetchAPI(`/options/calculator/price-change?${params}`);
}

export async function fetchMoneyness(strike, currentPrice, threshold = 0.02) {
  const params = new URLSearchParams({
    strike,
    current_price: currentPrice,
    threshold,
  });
  return fetchAPI(`/options/calculator/moneyness?${params}`);
}

export async function fetchPositionSize(accountValue, riskPercent, premiumPerContract) {
  const params = new URLSearchParams({
    account_value: accountValue,
    risk_percent: riskPercent,
    premium_per_contract: premiumPerContract,
  });
  return fetchAPI(`/options/calculator/position-size?${params}`);
}
