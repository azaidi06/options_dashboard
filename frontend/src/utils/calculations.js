/**
 * Client-side calculator functions for options math.
 * These are trivial computations that don't need API calls.
 */

/**
 * Calculate long put payoff at expiration.
 * Returns array of { price, pl_per_share } objects.
 */
export function calculatePayoff(strike, premium, minPrice, maxPrice, numPoints = 50) {
  const step = (maxPrice - minPrice) / (numPoints - 1);
  const data = [];
  for (let i = 0; i < numPoints; i++) {
    const price = minPrice + step * i;
    const pl_per_share = Math.max(strike - price, 0) - premium;
    data.push({ price: Math.round(price * 100) / 100, pl_per_share: Math.round(pl_per_share * 100) / 100 });
  }
  const breakeven = strike - premium;
  return { data, breakeven, strike, premium };
}

/**
 * Project premium decay over time using linear theta approximation.
 * Returns array of { days_remaining, premium } objects.
 */
export function calculateTimeDecay(premium, theta, daysRemaining) {
  const data = [];
  for (let d = daysRemaining; d >= 0; d--) {
    const decayed = Math.max(premium + theta * (daysRemaining - d), 0);
    data.push({
      days_remaining: d,
      premium: Math.round(decayed * 1000) / 1000,
    });
  }
  return { data };
}

/**
 * Estimate premium change from stock price move using delta-gamma approximation.
 */
export function calculatePriceChangeImpact(currentPremium, delta, gamma, priceChange) {
  const deltaEffect = delta * priceChange;
  const gammaEffect = 0.5 * gamma * priceChange * priceChange;
  const estimatedPremium = Math.max(currentPremium + deltaEffect + gammaEffect, 0);
  return {
    current_premium: currentPremium,
    estimated_premium: Math.round(estimatedPremium * 1000) / 1000,
    delta_effect: Math.round(deltaEffect * 1000) / 1000,
    gamma_effect: Math.round(gammaEffect * 1000) / 1000,
  };
}

/**
 * Classify option moneyness (ITM, ATM, OTM) for a put option.
 */
export function classifyMoneyness(strike, currentPrice, threshold = 0.02) {
  const pctDiff = (strike - currentPrice) / currentPrice;
  let classification;
  if (Math.abs(pctDiff) <= threshold) {
    classification = 'ATM';
  } else if (strike > currentPrice) {
    classification = 'ITM';
  } else {
    classification = 'OTM';
  }
  return { strike, current_price: currentPrice, pct_diff: pctDiff, classification };
}

/**
 * Calculate maximum position size based on risk tolerance.
 */
export function calculatePositionSize(accountValue, riskPercent, premiumPerContract) {
  const maxRiskDollars = accountValue * (riskPercent / 100);
  const maxContractsTheoretical = premiumPerContract > 0 ? maxRiskDollars / premiumPerContract : 0;
  const maxContractsFloored = Math.floor(maxContractsTheoretical);
  return {
    max_risk_dollars: Math.round(maxRiskDollars * 100) / 100,
    max_contracts_theoretical: Math.round(maxContractsTheoretical * 100) / 100,
    max_contracts_floored: maxContractsFloored,
  };
}
