"""
Options analysis endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..services.options import (
    get_available_tickers,
    get_date_range,
    load_option_chain,
    get_iv_smile,
    calculate_payoff,
    calculate_time_decay,
    estimate_price_change,
    classify_moneyness,
    calculate_position_sizing,
)

router = APIRouter()


@router.get("/tickers")
async def list_tickers():
    """Get list of available tickers with options data."""
    try:
        result = get_available_tickers()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tickers: {str(e)}")


@router.get("/{ticker}/dates")
async def get_ticker_dates(ticker: str):
    """Get available date range for a ticker's options data."""
    try:
        result = get_date_range(ticker)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting date range: {str(e)}")


@router.get("/{ticker}/chain")
async def get_option_chain(
    ticker: str,
    date: Optional[str] = Query(None, description="Quote date (YYYY-MM-DD)"),
    expiration: Optional[str] = Query(None, description="Expiration date (YYYY-MM-DD)"),
    start_date: Optional[str] = Query(None, description="Start date for range query (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for range query (YYYY-MM-DD)"),
):
    """
    Get option chain data for a specific date and/or expiration.

    Query params:
    - date: Quote date (YYYY-MM-DD)
    - expiration: Expiration date (YYYY-MM-DD)
    - start_date, end_date: Date range for loading multiple dates
    """
    try:
        result = load_option_chain(
            ticker=ticker,
            date=date,
            expiration=expiration,
            start_date=start_date,
            end_date=end_date,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading option chain: {str(e)}")


@router.get("/{ticker}/iv-smile")
async def get_smile(
    ticker: str,
    date: str = Query(..., description="Quote date (YYYY-MM-DD)"),
    expiration: str = Query(..., description="Expiration date (YYYY-MM-DD)"),
):
    """
    Get IV smile data (implied volatility vs strike) for visualization.

    Query params:
    - date: Quote date (required)
    - expiration: Expiration date (required)
    """
    try:
        result = get_iv_smile(ticker, date, expiration)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting IV smile: {str(e)}")


@router.get("/payoff")
async def payoff_diagram(
    strike: float = Query(..., description="Strike price"),
    premium: float = Query(..., description="Premium paid per share"),
    price_range_min: Optional[float] = Query(None, description="Min stock price for range"),
    price_range_max: Optional[float] = Query(None, description="Max stock price for range"),
    num_points: int = Query(11, description="Number of points in diagram"),
):
    """
    Calculate long put payoff diagram.

    Query params:
    - strike: Strike price (required)
    - premium: Premium paid per share (required)
    - price_range_min: Min stock price (default: 70% of strike)
    - price_range_max: Max stock price (default: 130% of strike)
    - num_points: Number of points (default: 11)
    """
    try:
        result = calculate_payoff(
            strike=strike,
            premium=premium,
            price_range_min=price_range_min,
            price_range_max=price_range_max,
            num_points=num_points,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating payoff: {str(e)}")


@router.get("/calculator/time-decay")
async def time_decay(
    premium: float = Query(..., description="Initial premium"),
    theta: float = Query(..., description="Daily theta"),
    days_remaining: int = Query(..., description="Days to expiration"),
):
    """
    Project premium decay over time.

    Query params:
    - premium: Initial premium (required)
    - theta: Daily theta decay (required)
    - days_remaining: Days to expiration (required)
    """
    try:
        result = calculate_time_decay(
            premium=premium,
            theta=theta,
            days_remaining=days_remaining,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating time decay: {str(e)}")


@router.get("/calculator/price-change")
async def price_change_impact(
    current_premium: float = Query(..., description="Current premium"),
    delta: float = Query(..., description="Option delta"),
    gamma: float = Query(..., description="Option gamma"),
    price_change: float = Query(..., description="Change in stock price"),
):
    """
    Estimate premium change from stock price move using delta-gamma approximation.

    Query params:
    - current_premium: Current premium (required)
    - delta: Option delta (required)
    - gamma: Option gamma (required)
    - price_change: Change in stock price (required)
    """
    try:
        result = estimate_price_change(
            current_premium=current_premium,
            delta=delta,
            gamma=gamma,
            price_change=price_change,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error estimating price change: {str(e)}")


@router.get("/calculator/moneyness")
async def moneyness(
    strike: float = Query(..., description="Strike price"),
    current_price: float = Query(..., description="Current stock price"),
    threshold: float = Query(0.02, description="ATM threshold (as decimal)"),
):
    """
    Classify option moneyness (ITM, ATM, OTM).

    Query params:
    - strike: Strike price (required)
    - current_price: Current stock price (required)
    - threshold: ATM threshold (default: 0.02 = 2%)
    """
    try:
        result = classify_moneyness(
            strike=strike,
            current_price=current_price,
            threshold=threshold,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error classifying moneyness: {str(e)}")


@router.get("/calculator/position-size")
async def position_size(
    account_value: float = Query(..., description="Account value in dollars"),
    risk_percent: float = Query(..., description="Risk percentage (0-100)"),
    premium_per_contract: float = Query(..., description="Premium per contract (premium * 100)"),
):
    """
    Calculate maximum position size based on risk tolerance.

    Query params:
    - account_value: Account value (required)
    - risk_percent: Risk percentage (required)
    - premium_per_contract: Premium per contract (required)
    """
    try:
        result = calculate_position_sizing(
            account_value=account_value,
            risk_percent=risk_percent,
            premium_per_contract=premium_per_contract,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating position size: {str(e)}")
