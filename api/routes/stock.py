"""
Stock analysis endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
from ..services.analytics import (
    get_stock_with_metrics,
    compute_indicators,
    compute_drawdown,
    compute_opportunities,
)

router = APIRouter()


@router.get("/{ticker}")
async def get_stock(
    ticker: str,
    start: str = Query("2020-01-01", description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD), defaults to today"),
    lookback_days: int = Query(30, description="Lookback period for rolling high"),
):
    """
    Get stock OHLCV data with metrics (rolling high, pct change).

    Query params:
    - start: Start date (default: 2020-01-01)
    - end: End date (default: today)
    - lookback_days: Lookback period for rolling high (default: 30)
    """
    try:
        result = get_stock_with_metrics(
            ticker=ticker,
            start=start,
            end=end,
            lookback_days=lookback_days,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")


@router.get("/{ticker}/indicators")
async def get_indicators(
    ticker: str,
    start: str = Query("2020-01-01", description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    rsi_period: int = Query(14, description="RSI period"),
    macd_fast: int = Query(12, description="MACD fast period"),
    macd_slow: int = Query(26, description="MACD slow period"),
    macd_signal: int = Query(9, description="MACD signal period"),
    bb_period: int = Query(20, description="Bollinger Bands period"),
    bb_std: float = Query(2.0, description="Bollinger Bands std dev multiplier"),
    sma_periods: Optional[str] = Query("20,50,200", description="SMA periods (comma-separated)"),
    ema_periods: Optional[str] = Query("20,50", description="EMA periods (comma-separated)"),
):
    """
    Get technical indicators for a stock.

    Query params:
    - rsi_period: RSI period (default: 14)
    - macd_fast: MACD fast EMA (default: 12)
    - macd_slow: MACD slow EMA (default: 26)
    - macd_signal: MACD signal (default: 9)
    - bb_period: Bollinger Bands period (default: 20)
    - bb_std: Bollinger Bands std dev (default: 2.0)
    - sma_periods: SMA periods (comma-separated, default: "20,50,200")
    - ema_periods: EMA periods (comma-separated, default: "20,50")
    """
    try:
        # Parse periods from comma-separated strings
        sma_list = [int(x.strip()) for x in sma_periods.split(",")] if sma_periods else [20, 50, 200]
        ema_list = [int(x.strip()) for x in ema_periods.split(",")] if ema_periods else [20, 50]

        result = compute_indicators(
            ticker=ticker,
            start=start,
            end=end,
            rsi_period=rsi_period,
            macd_fast=macd_fast,
            macd_slow=macd_slow,
            macd_signal=macd_signal,
            bb_period=bb_period,
            bb_std=bb_std,
            sma_periods=sma_list,
            ema_periods=ema_list,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing indicators: {str(e)}")


@router.get("/{ticker}/drawdown")
async def get_drawdown(
    ticker: str,
    start: str = Query("2020-01-01", description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    min_drawdown_pct: float = Query(0.05, description="Minimum drawdown threshold (as decimal, e.g., 0.05 = 5%)"),
):
    """
    Get drawdown analysis including underwater periods and drawdown events.

    Query params:
    - min_drawdown_pct: Minimum drawdown to qualify as event (default: 0.05 = 5%)
    """
    try:
        result = compute_drawdown(
            ticker=ticker,
            start=start,
            end=end,
            min_drawdown_pct=min_drawdown_pct,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing drawdown: {str(e)}")


@router.get("/{ticker}/opportunities")
async def get_opportunities(
    ticker: str,
    start: str = Query("2020-01-01", description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    entry_threshold: float = Query(0.10, description="Entry threshold (e.g., 0.10 = 10% drawdown)"),
    exit_threshold: float = Query(0.05, description="Exit threshold (e.g., 0.05 = 5% drawdown)"),
):
    """
    Get opportunity windows (periods below entry threshold).

    Query params:
    - entry_threshold: Drawdown level to enter (default: 0.10 = 10%)
    - exit_threshold: Drawdown level to exit (default: 0.05 = 5%)
    """
    try:
        result = compute_opportunities(
            ticker=ticker,
            start=start,
            end=end,
            entry_threshold=entry_threshold,
            exit_threshold=exit_threshold,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing opportunities: {str(e)}")
