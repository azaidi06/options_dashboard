/**
 * Custom hooks for stock data fetching
 */

import useSWR from 'swr';
import {
  fetchStockData,
  fetchIndicators,
  fetchDrawdown,
  fetchOpportunities,
  fetchOptionsTickers,
} from '../utils/api';

/**
 * Hook to fetch stock OHLCV data with metrics
 */
export function useStockData(ticker, start, end, lookbackDays = 30) {
  const { data, error, isLoading, mutate } = useSWR(
    ticker ? [`stock-${ticker}`, start, end, lookbackDays] : null,
    () => fetchStockData(ticker, start, end, lookbackDays),
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
 * Hook to fetch technical indicators
 */
export function useIndicators(ticker, start, end) {
  const { data, error, isLoading } = useSWR(
    ticker ? [`indicators-${ticker}`, start, end] : null,
    () => fetchIndicators(ticker, start, end),
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
 * Hook to fetch drawdown analysis
 */
export function useDrawdown(ticker, start, end, minDrawdownPct = 0.05) {
  const { data, error, isLoading } = useSWR(
    ticker ? [`drawdown-${ticker}`, start, end, minDrawdownPct] : null,
    () => fetchDrawdown(ticker, start, end, minDrawdownPct),
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
 * Hook to fetch opportunity windows
 */
export function useOpportunities(ticker, start, end, entryThreshold = 0.10, exitThreshold = 0.05) {
  const { data, error, isLoading } = useSWR(
    ticker ? [`opportunities-${ticker}`, start, end, entryThreshold, exitThreshold] : null,
    () => fetchOpportunities(ticker, start, end, entryThreshold, exitThreshold),
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
 * Hook to fetch available option tickers
 */
export function useTickers() {
  const { data, error, isLoading } = useSWR(
    'tickers',
    fetchOptionsTickers,
    {
      revalidateOnFocus: false,
      dedupingInterval: 300000, // 5 minutes
    }
  );

  return {
    tickers: data?.tickers || [],
    loading: isLoading,
    error: error?.message,
  };
}
