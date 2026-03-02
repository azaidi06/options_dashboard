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
export function useOptionChain(ticker, date, expiration) {
  const { data, error, isLoading, mutate } = useSWR(
    ticker && date ? [`option-chain-${ticker}`, date] : null,
    () => fetchOptionChain(ticker, date, expiration),
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
export function useIVSmile(ticker, date, expiration) {
  const { data, error, isLoading } = useSWR(
    ticker && date && expiration ? [`iv-smile-${ticker}`, date, expiration] : null,
    () => fetchIVSmile(ticker, date, expiration),
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
