"""
Options service layer - wraps options_utils.py functions for API use.
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd

# Add parent directory to path so we can import options_utils from the dashboard root
dashboard_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(dashboard_root))

# Import options functions from options_utils.py
import options_utils


def get_available_tickers() -> Dict[str, List[str]]:
    """
    Get list of available tickers with options data.

    Returns:
        {"tickers": ["AMD", "AAPL", ...]}
    """
    tickers = options_utils.available_tickers()
    return {"tickers": tickers}


def get_date_range(ticker: str) -> Dict[str, Any]:
    """
    Get available date range for a ticker's options data.

    Returns:
        {
            "ticker": str,
            "min_date": "2018-01-01",
            "max_date": "2024-03-01",
            "range_days": 2280
        }
    """
    try:
        min_date, max_date = options_utils.ticker_date_range(ticker)
        days = (max_date - min_date).days
        return {
            "ticker": ticker,
            "min_date": min_date.strftime("%Y-%m-%d"),
            "max_date": max_date.strftime("%Y-%m-%d"),
            "range_days": days,
        }
    except FileNotFoundError as e:
        return {"error": str(e), "ticker": ticker}


def load_option_chain(
    ticker: str,
    date: Optional[str] = None,
    expiration: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Load option chain data (filtered to puts if specify expiration).

    Returns:
        {
            "ticker": str,
            "filters": {"date": "2024-02-01", "expiration": "2024-03-15"},
            "data": [{"strike": 100, "mark": 2.5, "delta": -0.45, "implied_volatility": 0.25, ...}],
            "metadata": {"total_contracts": 500, "date_range": "2024-01-01 to 2024-02-01"}
        }
    """
    # Load puts
    if start_date and end_date:
        df = options_utils.load_puts(ticker, start_date=start_date, end_date=end_date)
    else:
        df = options_utils.load_puts(ticker, start_date=date, end_date=date)

    # Filter by date and expiration if specified
    if date:
        df = df[df["date"] == pd.to_datetime(date)]
    if expiration:
        df = df[df["expiration"] == pd.to_datetime(expiration)]

    # Convert to JSON-serializable format
    data = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            value = row[col]
            if pd.isna(value):
                record[col] = None
            elif isinstance(value, (pd.Timestamp, pd.Timedelta)):
                record[col] = str(value)
            elif isinstance(value, (int, float)):
                record[col] = float(value)
            else:
                record[col] = str(value)
        data.append(record)

    # Get date range
    if not df.empty:
        min_date = df["date"].min().strftime("%Y-%m-%d")
        max_date = df["date"].max().strftime("%Y-%m-%d")
    else:
        min_date = None
        max_date = None

    return {
        "ticker": ticker,
        "filters": {
            "date": date,
            "expiration": expiration,
            "start_date": start_date,
            "end_date": end_date,
        },
        "data": data,
        "metadata": {
            "total_contracts": len(data),
            "min_date": min_date,
            "max_date": max_date,
            "columns": list(df.columns),
        }
    }


def get_iv_smile(
    ticker: str,
    date: str,
    expiration: str,
) -> Dict[str, Any]:
    """
    Get IV smile data (implied volatility vs strike) for visualization.

    Returns:
        {
            "ticker": str,
            "date": "2024-02-01",
            "expiration": "2024-03-15",
            "data": [{"strike": 95, "implied_volatility": 0.25}, ...]
        }
    """
    df = options_utils.load_puts(ticker, start_date=date, end_date=date)
    smile_df = options_utils.get_iv_smile_data(df, date, expiration)

    data = []
    for _, row in smile_df.iterrows():
        data.append({
            "strike": float(row["strike"]),
            "implied_volatility": float(row["implied_volatility"]),
        })

    return {
        "ticker": ticker,
        "date": date,
        "expiration": expiration,
        "data": data,
    }


def calculate_payoff(
    strike: float,
    premium: float,
    price_range_min: Optional[float] = None,
    price_range_max: Optional[float] = None,
    num_points: int = 11,
) -> Dict[str, Any]:
    """
    Calculate long put payoff diagram data.

    Returns:
        {
            "strike": 100,
            "premium": 2.5,
            "data": [{"price": 70, "pl_per_share": 27.5, "pl_per_contract": 2750}, ...],
            "breakeven": 97.5
        }
    """
    if price_range_min is None:
        price_range_min = strike * 0.7
    if price_range_max is None:
        price_range_max = strike * 1.3

    pl_df = options_utils.calculate_pl_scenarios(
        strike=strike,
        premium=premium,
        price_range=[price_range_min, price_range_max],
        num_points=num_points,
    )

    data = []
    for _, row in pl_df.iterrows():
        data.append({
            "price": float(row["stock_price"]),
            "pl_per_share": float(row["pl_per_share"]),
            "pl_per_contract": float(row["pl_per_contract"]),
        })

    breakeven = options_utils.calculate_break_even(strike, premium)

    return {
        "strike": strike,
        "premium": premium,
        "breakeven": float(breakeven),
        "data": data,
    }


def calculate_time_decay(
    premium: float,
    theta: float,
    days_remaining: int,
) -> Dict[str, Any]:
    """
    Project option premium decay over time.

    Returns:
        {
            "initial_premium": 2.5,
            "theta": -0.05,
            "days_remaining": 30,
            "data": [{"days_remaining": 30, "premium": 2.5}, ...]
        }
    """
    decay_df = options_utils.calculate_time_decay(
        days_remaining=days_remaining,
        theta=theta,
        current_premium=premium,
    )

    data = []
    for _, row in decay_df.iterrows():
        data.append({
            "days_remaining": int(row["days_remaining"]),
            "premium": float(row["premium"]),
        })

    return {
        "initial_premium": premium,
        "theta": theta,
        "days_remaining": days_remaining,
        "data": data,
    }


def estimate_price_change(
    current_premium: float,
    delta: float,
    gamma: float,
    price_change: float,
) -> Dict[str, Any]:
    """
    Estimate premium change from stock price move using delta-gamma approximation.

    Returns:
        {
            "current_premium": 2.5,
            "delta": -0.45,
            "gamma": 0.02,
            "price_change": -5.0,
            "estimated_premium": 4.75,
            "delta_effect": 2.25,
            "gamma_effect": 0.25
        }
    """
    new_premium = options_utils.estimate_put_value_change(
        price_change=price_change,
        delta=delta,
        gamma=gamma,
        current_premium=current_premium,
    )

    delta_effect = delta * price_change
    gamma_effect = 0.5 * gamma * (price_change ** 2)

    return {
        "current_premium": float(current_premium),
        "delta": float(delta),
        "gamma": float(gamma),
        "price_change": float(price_change),
        "estimated_premium": float(new_premium),
        "delta_effect": float(delta_effect),
        "gamma_effect": float(gamma_effect),
    }


def classify_moneyness(
    strike: float,
    current_price: float,
    threshold: float = 0.02,
) -> Dict[str, Any]:
    """
    Classify option moneyness (ITM, ATM, OTM).

    Returns:
        {
            "strike": 100,
            "current_price": 102,
            "classification": "OTM",
            "pct_diff": 0.0196
        }
    """
    classification = options_utils.classify_moneyness(
        strike=strike,
        current_price=current_price,
        threshold=threshold,
    )

    pct_diff = (strike - current_price) / current_price

    return {
        "strike": float(strike),
        "current_price": float(current_price),
        "classification": classification,
        "pct_diff": float(pct_diff),
    }


def calculate_position_sizing(
    account_value: float,
    risk_percent: float,
    premium_per_contract: float,
) -> Dict[str, Any]:
    """
    Calculate maximum position size based on risk tolerance.

    Returns:
        {
            "account_value": 10000,
            "risk_percent": 2.0,
            "premium_per_contract": 250,
            "max_risk_dollars": 200,
            "max_contracts": 0.8,
            "max_contracts_floored": 0
        }
    """
    max_contracts = options_utils.calculate_position_size(
        account_value=account_value,
        risk_percent=risk_percent,
        premium_per_contract=premium_per_contract,
    )

    max_risk = account_value * (risk_percent / 100)
    theoretical_contracts = max_risk / premium_per_contract if premium_per_contract > 0 else 0

    return {
        "account_value": float(account_value),
        "risk_percent": float(risk_percent),
        "premium_per_contract": float(premium_per_contract),
        "max_risk_dollars": float(max_risk),
        "max_contracts_theoretical": float(theoretical_contracts),
        "max_contracts_floored": int(max_contracts),
    }
