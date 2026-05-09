/**
 * Custom hooks for options data fetching
 */

import useSWR from 'swr';
import {
  fetchOptionsTickers,
  fetchTickerDateRange,
  fetchOptionChain,
  fetchIVSmile,
  fetchPayoffDiagram,
  fetchTimeDecay,
  fetchPriceChangeImpact,
  fetchMoneyness,
  fetchPositionSize,
  fetchTickerCoverage,
  fetchStockData,
} from '../utils/api';

/**
 * Hook to fetch list of available option tickers
 */
export function useTickers() {
  const { data, error, isLoading } = useSWR(
    'options-tickers',
    fetchOptionsTickers,
    {
      revalidateOnFocus: true,
      dedupingInterval: 300000, // 5 minutes
    }
  );

  return {
    tickers: data?.tickers || [],
    loading: isLoading,
    error: error?.message,
  };
}

/**
 * Hook to fetch date range for a ticker
 */
export function useTickerDateRange(ticker) {
  const { data, error, isLoading } = useSWR(
    ticker ? `ticker-dates-${ticker}` : null,
    () => fetchTickerDateRange(ticker),
    {
      revalidateOnFocus: false,
      dedupingInterval: 300000,
    }
  );

  return {
    data,
    loading: isLoading,
    error: error?.message,
  };
}

/**
 * Hook to fetch option chain for a ticker
 */
export function useOptionChain(ticker, date, expiration, optionType = 'put') {
  const { data, error, isLoading, mutate } = useSWR(
    ticker && date ? [`option-chain-${ticker}`, date, optionType] : null,
    () => fetchOptionChain(ticker, date, expiration, optionType),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000, // 1 minute
    }
  );

  return {
    data,
    loading: isLoading,
    error: error?.message,
    refetch: mutate,
  };
}

/**
 * Hook to fetch IV smile data
 */
export function useIVSmile(ticker, date, expiration, optionType = 'put') {
  const { data, error, isLoading } = useSWR(
    ticker && date && expiration ? [`iv-smile-${ticker}`, date, expiration, optionType] : null,
    () => fetchIVSmile(ticker, date, expiration, optionType),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  return {
    data,
    loading: isLoading,
    error: error?.message,
  };
}

/**
 * Hook to calculate payoff diagram
 */
export function usePayoffDiagram(strike, premium, minPrice, maxPrice) {
  const { data, error, isLoading } = useSWR(
    strike && premium ? [`payoff-${strike}-${premium}`, minPrice, maxPrice] : null,
    () => fetchPayoffDiagram(strike, premium, minPrice, maxPrice),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  return {
    data,
    loading: isLoading,
    error: error?.message,
  };
}

/**
 * Hook to calculate time decay
 */
export function useTimeDecay(premium, theta, daysRemaining) {
  const { data, error, isLoading } = useSWR(
    premium && theta && daysRemaining ? [`time-decay-${premium}-${theta}-${daysRemaining}`] : null,
    () => fetchTimeDecay(premium, theta, daysRemaining),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  return {
    data,
    loading: isLoading,
    error: error?.message,
  };
}

/**
 * Hook to calculate price change impact
 */
export function usePriceChangeImpact(currentPremium, delta, gamma, priceChange) {
  const { data, error, isLoading } = useSWR(
    currentPremium && delta && gamma && priceChange !== undefined ? [`price-impact-${currentPremium}-${delta}-${gamma}-${priceChange}`] : null,
    () => fetchPriceChangeImpact(currentPremium, delta, gamma, priceChange),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  return {
    data,
    loading: isLoading,
    error: error?.message,
  };
}

/**
 * Hook to classify moneyness
 */
export function useMoneyness(strike, currentPrice, threshold = 0.02) {
  const { data, error, isLoading } = useSWR(
    strike && currentPrice ? [`moneyness-${strike}-${currentPrice}-${threshold}`] : null,
    () => fetchMoneyness(strike, currentPrice, threshold),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  return {
    data,
    loading: isLoading,
    error: error?.message,
  };
}

/**
 * Hook to fetch ticker coverage list (cached tickers and their date ranges).
 */
export function useTickerCoverage() {
  const { data, error, isLoading, mutate } = useSWR(
    'ticker-coverage',
    fetchTickerCoverage,
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  return {
    data: Array.isArray(data) ? data : [],
    loading: isLoading,
    error: error?.message,
    refetch: mutate,
  };
}

/**
 * Hook to fetch the underlying stock's OHLC for a single quote date.
 * Wraps /api/stock/{ticker} with start == end == date and pulls the row out.
 */
export function useUnderlyingOHLC(ticker, date) {
  const { data, error, isLoading } = useSWR(
    ticker && date ? ['underlying-ohlc', ticker, date] : null,
    async ([, t, d]) => {
      // yfinance has timezone-edge quirks where `start=d` sometimes drops
      // the row for d itself, and `end` is exclusive. Widen the window a
      // few days on both sides and pick the row that matches the
      // requested quote date exactly.
      const startDate = new Date(d);
      startDate.setUTCDate(startDate.getUTCDate() - 3);
      const endDate = new Date(d);
      endDate.setUTCDate(endDate.getUTCDate() + 4);
      const startStr = startDate.toISOString().slice(0, 10);
      const endStr = endDate.toISOString().slice(0, 10);
      const resp = await fetchStockData(t, startStr, endStr, 1);
      const rows = resp?.data || [];
      const row = rows.find((r) => r.date === d);
      if (!row) return null;
      return {
        date: row.date,
        open: row.open,
        high: row.high,
        low: row.low,
        close: row.close,
        volume: row.volume,
      };
    },
    {
      revalidateOnFocus: false,
      dedupingInterval: 300000,
    }
  );

  return {
    data,
    loading: isLoading,
    error: error?.message,
  };
}

/**
 * Hook to fetch the most recent available bar for a ticker (latest close).
 * Used to show "where is the stock now" alongside a historical chain so
 * users can eyeball whether a past option would have ended up profitable.
 */
export function useUnderlyingLatest(ticker) {
  const { data, error, isLoading } = useSWR(
    ticker ? ['underlying-latest', ticker] : null,
    async ([, t]) => {
      const today = new Date();
      const start = new Date(today);
      start.setUTCDate(start.getUTCDate() - 10);
      const startStr = start.toISOString().slice(0, 10);
      const end = new Date(today);
      end.setUTCDate(end.getUTCDate() + 1);
      const endStr = end.toISOString().slice(0, 10);
      const resp = await fetchStockData(t, startStr, endStr, 1);
      const rows = resp?.data || [];
      if (!rows.length) return null;
      const row = rows[rows.length - 1];
      return {
        date: row.date,
        close: row.close,
      };
    },
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  return {
    data,
    loading: isLoading,
    error: error?.message,
  };
}

/**
 * Hook to calculate position size
 */
export function usePositionSize(accountValue, riskPercent, premiumPerContract) {
  const { data, error, isLoading } = useSWR(
    accountValue && riskPercent && premiumPerContract ? [`position-size-${accountValue}-${riskPercent}-${premiumPerContract}`] : null,
    () => fetchPositionSize(accountValue, riskPercent, premiumPerContract),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  return {
    data,
    loading: isLoading,
    error: error?.message,
  };
}
