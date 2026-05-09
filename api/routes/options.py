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
    get_contract_history,
    calculate_payoff,
    calculate_time_decay,
    estimate_price_change,
    classify_moneyness,
    calculate_position_sizing,
)

router = APIRouter()


_VALID_OPTION_TYPES = {"put", "call", "both"}
_VALID_SINGLE_OPTION_TYPES = {"put", "call"}


def _validate_option_type(option_type: str, allow_both: bool = True) -> str:
    """Normalise + validate option_type query param. Raises HTTPException(400) on bad input."""
    ot = str(option_type or "put").strip().lower()
    valid = _VALID_OPTION_TYPES if allow_both else _VALID_SINGLE_OPTION_TYPES
    if ot not in valid:
        raise HTTPException(
            status_code=400,
            detail=f"option_type must be one of {sorted(valid)} (got {option_type!r})",
        )
    return ot


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
    option_type: str = Query("put", description="Option type: put|call|both"),
):
    """
    Get option chain data for a specific date and/or expiration.

    Query params:
    - date: Quote date (YYYY-MM-DD)
    - expiration: Expiration date (YYYY-MM-DD)
    - start_date, end_date: Date range for loading multiple dates
    - option_type: 'put' (default), 'call', or 'both'
    """
    ot = _validate_option_type(option_type, allow_both=True)
    try:
        result = load_option_chain(
            ticker=ticker,
            date=date,
            expiration=expiration,
            start_date=start_date,
            end_date=end_date,
            option_type=ot,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading option chain: {str(e)}")


@router.get("/{ticker}/iv-smile")
async def get_smile(
    ticker: str,
    date: str = Query(..., description="Quote date (YYYY-MM-DD)"),
    expiration: str = Query(..., description="Expiration date (YYYY-MM-DD)"),
    option_type: str = Query("put", description="Option type: put|call|both"),
):
    """
    Get IV smile data (implied volatility vs strike) for visualization.

    Query params:
    - date: Quote date (required)
    - expiration: Expiration date (required)
    - option_type: 'put' (default), 'call', or 'both'
    """
    ot = _validate_option_type(option_type, allow_both=True)
    try:
        result = get_iv_smile(ticker, date, expiration, option_type=ot)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting IV smile: {str(e)}")


@router.get("/{ticker}/contract-history")
async def contract_history(
    ticker: str,
    strike: float = Query(..., description="Strike price"),
    expiration: str = Query(..., description="Expiration date (YYYY-MM-DD)"),
    option_type: str = Query("put", description="Option type: put|call"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
):
    """
    Per-day premium series for one specific (strike, expiration, type)
    contract. Powers the chain row's expandable P/L sparkline.
    """
    ot = _validate_option_type(option_type, allow_both=False)
    try:
        result = get_contract_history(
            ticker=ticker,
            strike=strike,
            expiration=expiration,
            option_type=ot,
            start_date=start_date,
            end_date=end_date,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading contract history: {str(e)}")


@router.get("/payoff")
async def payoff_diagram(
    strike: float = Query(..., description="Strike price"),
    premium: float = Query(..., description="Premium paid per share"),
    price_range_min: Optional[float] = Query(None, description="Min stock price for range"),
    price_range_max: Optional[float] = Query(None, description="Max stock price for range"),
    num_points: int = Query(11, description="Number of points in diagram"),
    option_type: str = Query("put", description="Option type: put|call"),
):
    """
    Calculate long single-leg option payoff diagram.

    Query params:
    - strike: Strike price (required)
    - premium: Premium paid per share (required)
    - price_range_min: Min stock price (default: 70% of strike)
    - price_range_max: Max stock price (default: 130% of strike)
    - num_points: Number of points (default: 11)
    - option_type: 'put' (default) or 'call'
    """
    ot = _validate_option_type(option_type, allow_both=False)
    try:
        result = calculate_payoff(
            strike=strike,
            premium=premium,
            price_range_min=price_range_min,
            price_range_max=price_range_max,
            num_points=num_points,
            option_type=ot,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating payoff: {str(e)}")


@router.get("/calculator/time-decay")
async def time_decay(
    premium: float = Query(..., description="Initial premium"),
    theta: float = Query(..., description="Daily theta"),
    days_remaining: int = Query(..., description="Days to expiration"),
    option_type: str = Query("put", description="Option type: put|call (informational)"),
):
    """
    Project premium decay over time.

    Query params:
    - premium: Initial premium (required)
    - theta: Daily theta decay (required)
    - days_remaining: Days to expiration (required)
    - option_type: 'put' (default) or 'call' (theta decay model is the same;
      flag is preserved for traceability).
    """
    ot = _validate_option_type(option_type, allow_both=False)
    try:
        result = calculate_time_decay(
            premium=premium,
            theta=theta,
            days_remaining=days_remaining,
        )
        result["option_type"] = ot
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating time decay: {str(e)}")


@router.get("/calculator/price-change")
async def price_change_impact(
    current_premium: float = Query(..., description="Current premium"),
    delta: float = Query(..., description="Option delta"),
    gamma: float = Query(..., description="Option gamma"),
    price_change: float = Query(..., description="Change in stock price"),
    option_type: str = Query("put", description="Option type: put|call"),
):
    """
    Estimate premium change from stock price move using delta-gamma approximation.

    Query params:
    - current_premium: Current premium (required)
    - delta: Option delta (required). Sign is corrected per option_type.
    - gamma: Option gamma (required)
    - price_change: Change in stock price (required)
    - option_type: 'put' (default) or 'call'
    """
    ot = _validate_option_type(option_type, allow_both=False)
    try:
        result = estimate_price_change(
            current_premium=current_premium,
            delta=delta,
            gamma=gamma,
            price_change=price_change,
            option_type=ot,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error estimating price change: {str(e)}")


@router.get("/calculator/moneyness")
async def moneyness(
    strike: float = Query(..., description="Strike price"),
    current_price: float = Query(..., description="Current stock price"),
    threshold: float = Query(0.02, description="ATM threshold (as decimal)"),
    option_type: str = Query("put", description="Option type: put|call"),
):
    """
    Classify option moneyness (ITM, ATM, OTM).

    Query params:
    - strike: Strike price (required)
    - current_price: Current stock price (required)
    - threshold: ATM threshold (default: 0.02 = 2%)
    - option_type: 'put' (default) or 'call' (calls invert ITM rule)
    """
    ot = _validate_option_type(option_type, allow_both=False)
    try:
        result = classify_moneyness(
            strike=strike,
            current_price=current_price,
            threshold=threshold,
            option_type=ot,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error classifying moneyness: {str(e)}")


@router.get("/calculator/position-size")
async def position_size(
    account_value: float = Query(..., description="Account value in dollars"),
    risk_percent: float = Query(..., description="Risk percentage (0-100)"),
    premium_per_contract: float = Query(..., description="Premium per contract (premium * 100)"),
    option_type: str = Query("put", description="Option type: put|call (informational)"),
):
    """
    Calculate maximum position size based on risk tolerance.

    Query params:
    - account_value: Account value (required)
    - risk_percent: Risk percentage (required)
    - premium_per_contract: Premium per contract (required)
    - option_type: 'put' (default) or 'call' (sizing math is identical;
      flag is preserved for traceability).
    """
    ot = _validate_option_type(option_type, allow_both=False)
    try:
        result = calculate_position_sizing(
            account_value=account_value,
            risk_percent=risk_percent,
            premium_per_contract=premium_per_contract,
        )
        result["option_type"] = ot
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating position size: {str(e)}")
