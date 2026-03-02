"""
Analytics service layer - wraps utils.py functions for API use.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# Add parent directory to path so we can import utils from the dashboard root
dashboard_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(dashboard_root))

# Import analytics functions from utils.py
import utils


def get_stock_with_metrics(
    ticker: str = "AAPL",
    start: str = "2020-01-01",
    end: Optional[str] = None,
    lookback_days: int = 30,
) -> Dict[str, Any]:
    """
    Fetch stock data and metrics. Returns JSON-serializable dict with OHLCV data.

    Returns:
        {
            "ticker": str,
            "data": [{"date": "2020-01-02", "open": 75.0, "high": 76.0, ...}],
            "metadata": {"lookback_days": 30, "start": "2020-01-01", "end": "2024-03-01"}
        }
    """
    df = utils.get_stock_with_metrics(ticker, start, end, lookback_days)

    # Convert datetime to string for JSON serialization
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    # Create data records
    data = []
    for _, row in df.iterrows():
        record = {
            "date": row["Date"],
            "open": float(row.get("Open", 0)),
            "high": float(row.get("High", 0)),
            "low": float(row.get("Low", 0)),
            "close": float(row.get("Close", 0)),
            "volume": int(row.get("Volume", 0)),
            "pct_change": float(row.get("pct_change", 0)) if "pct_change" in row else None,
            f"prev_{lookback_days}_high": float(row.get(f"prev_{lookback_days}_high", 0)) if f"prev_{lookback_days}_high" in row else None,
        }
        data.append(record)

    end_date = end or datetime.now().strftime("%Y-%m-%d")

    return {
        "ticker": ticker,
        "data": data,
        "metadata": {
            "lookback_days": lookback_days,
            "start": start,
            "end": end_date,
            "total_rows": len(data),
        }
    }


def compute_indicators(
    ticker: str,
    start: str = "2020-01-01",
    end: Optional[str] = None,
    rsi_period: int = 14,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    bb_period: int = 20,
    bb_std: float = 2.0,
    sma_periods: Optional[List[int]] = None,
    ema_periods: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """
    Compute technical indicators for a stock.

    Returns:
        {
            "ticker": str,
            "data": [{"date": "2020-01-02", "rsi": 45.5, "macd": 0.2, ...}],
            "available_indicators": ["rsi", "macd", "bollinger_bands", "sma_20", "ema_20"]
        }
    """
    if sma_periods is None:
        sma_periods = [20, 50, 200]
    if ema_periods is None:
        ema_periods = [20, 50]

    # Get base data
    df = utils.get_stock_data(ticker, start, end)

    # Initialize result dict with dates
    result_data = []
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    # Compute RSI
    try:
        rsi_df = utils.compute_rsi(df, period=rsi_period)
        rsi_dict = dict(zip(rsi_df["Date"], rsi_df["RSI"]))
    except Exception as e:
        print(f"Error computing RSI: {e}")
        rsi_dict = {}

    # Compute MACD
    try:
        macd_df = utils.compute_macd(df, fast=macd_fast, slow=macd_slow, signal=macd_signal)
        macd_dict = dict(zip(macd_df["Date"], macd_df[["MACD", "MACD_Signal", "MACD_Hist"]].values.tolist()))
    except Exception as e:
        print(f"Error computing MACD: {e}")
        macd_dict = {}

    # Compute Bollinger Bands
    try:
        bb_df = utils.compute_bollinger_bands(df, period=bb_period, std_dev=bb_std)
        bb_dict = dict(zip(bb_df["Date"], bb_df[["BB_Lower", "BB_Middle", "BB_Upper"]].values.tolist()))
    except Exception as e:
        print(f"Error computing Bollinger Bands: {e}")
        bb_dict = {}

    # Compute SMAs
    sma_dicts = {}
    for period in sma_periods:
        try:
            sma_df = utils.compute_sma(df, period=period)
            sma_dicts[period] = dict(zip(sma_df["Date"], sma_df[f"SMA_{period}"]))
        except Exception as e:
            print(f"Error computing SMA{period}: {e}")
            sma_dicts[period] = {}

    # Compute EMAs
    ema_dicts = {}
    for period in ema_periods:
        try:
            ema_df = utils.compute_ema(df, period=period)
            ema_dicts[period] = dict(zip(ema_df["Date"], ema_df[f"EMA_{period}"]))
        except Exception as e:
            print(f"Error computing EMA{period}: {e}")
            ema_dicts[period] = {}

    # Merge all indicators by date
    for date in df["Date"]:
        record = {"date": date}

        if date in rsi_dict:
            record["rsi"] = float(rsi_dict[date]) if pd.notna(rsi_dict[date]) else None

        if date in macd_dict:
            record["macd"] = float(macd_dict[date][0]) if pd.notna(macd_dict[date][0]) else None
            record["macd_signal"] = float(macd_dict[date][1]) if pd.notna(macd_dict[date][1]) else None
            record["macd_hist"] = float(macd_dict[date][2]) if pd.notna(macd_dict[date][2]) else None

        if date in bb_dict:
            record["bb_lower"] = float(bb_dict[date][0]) if pd.notna(bb_dict[date][0]) else None
            record["bb_middle"] = float(bb_dict[date][1]) if pd.notna(bb_dict[date][1]) else None
            record["bb_upper"] = float(bb_dict[date][2]) if pd.notna(bb_dict[date][2]) else None

        for period in sma_periods:
            if date in sma_dicts[period]:
                record[f"sma_{period}"] = float(sma_dicts[period][date]) if pd.notna(sma_dicts[period][date]) else None

        for period in ema_periods:
            if date in ema_dicts[period]:
                record[f"ema_{period}"] = float(ema_dicts[period][date]) if pd.notna(ema_dicts[period][date]) else None

        result_data.append(record)

    return {
        "ticker": ticker,
        "data": result_data,
        "indicators_computed": {
            "rsi": rsi_period,
            "macd": {"fast": macd_fast, "slow": macd_slow, "signal": macd_signal},
            "bollinger_bands": {"period": bb_period, "std_dev": bb_std},
            "sma_periods": sma_periods,
            "ema_periods": ema_periods,
        }
    }


def compute_drawdown(
    ticker: str,
    start: str = "2020-01-01",
    end: Optional[str] = None,
    min_drawdown_pct: float = 0.05,
) -> Dict[str, Any]:
    """
    Compute drawdown analysis for a stock.

    Returns:
        {
            "ticker": str,
            "underwater_data": [{"date": "2020-01-02", "drawdown_pct": -0.05, "days_underwater": 5}],
            "events": [{"peak_date": "2020-01-01", "peak_price": 100, "trough_date": "2020-02-01", ...}],
            "summary": {"max_drawdown": 0.15, "avg_recovery_days": 30, ...}
        }
    """
    df = utils.get_stock_data(ticker, start, end)
    df = utils.compute_underwater_periods(df)

    # Convert datetime to string
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    # Underwater data
    underwater_data = []
    for _, row in df.iterrows():
        underwater_data.append({
            "date": row["Date"],
            "drawdown_pct": float(row["drawdown_from_ath"]) if pd.notna(row["drawdown_from_ath"]) else None,
            "days_underwater": int(row["days_underwater"]) if pd.notna(row["days_underwater"]) else None,
            "cummax": float(row["cummax"]) if pd.notna(row["cummax"]) else None,
        })

    # Get drawdown events
    events = utils.identify_drawdown_events(df, min_drawdown_pct=min_drawdown_pct)

    # Convert timestamps to strings in events
    for event in events:
        event["peak_date"] = event["peak_date"].strftime("%Y-%m-%d") if event["peak_date"] else None
        event["trough_date"] = event["trough_date"].strftime("%Y-%m-%d") if event["trough_date"] else None
        event["recovery_date"] = event["recovery_date"].strftime("%Y-%m-%d") if event["recovery_date"] else None

    # Summary stats
    if events:
        recovery_days = [e["days_to_recovery"] for e in events if e["days_to_recovery"] is not None]
        avg_recovery = sum(recovery_days) / len(recovery_days) if recovery_days else None
    else:
        avg_recovery = None

    max_drawdown = min([e["drawdown_pct"] for e in events]) if events else 0

    summary = {
        "total_events": len(events),
        "max_drawdown_pct": float(abs(max_drawdown)),
        "avg_recovery_days": float(avg_recovery) if avg_recovery else None,
        "min_event_threshold": min_drawdown_pct,
    }

    return {
        "ticker": ticker,
        "underwater_data": underwater_data,
        "events": events,
        "summary": summary,
    }


def compute_opportunities(
    ticker: str,
    start: str = "2020-01-01",
    end: Optional[str] = None,
    entry_threshold: float = 0.10,
    exit_threshold: float = 0.05,
) -> Dict[str, Any]:
    """
    Compute opportunity windows (drawdown-based entry/exit points).

    Returns:
        {
            "ticker": str,
            "windows": [{"start_date": "2020-01-01", "end_date": "2020-02-01", "duration_days": 20, ...}],
            "stats": {"total_windows": 5, "avg_duration": 25, "windows_per_year": 1.2, ...}
        }
    """
    df = utils.get_stock_data(ticker, start, end)
    df = utils.compute_underwater_periods(df)

    windows = utils.compute_opportunity_windows(df, entry_threshold=entry_threshold, exit_threshold=exit_threshold)

    # Convert timestamps to strings
    for window in windows:
        window["start_date"] = window["start_date"].strftime("%Y-%m-%d") if window["start_date"] else None
        window["end_date"] = window["end_date"].strftime("%Y-%m-%d") if window["end_date"] else None

    # Compute stats
    total_trading_days = len(df)
    years = (pd.to_datetime(end or datetime.now()) - pd.to_datetime(start)).days / 365.25
    stats = utils.compute_opportunity_stats(windows, total_trading_days, years)

    # Convert numpy types to native Python types
    stats = {
        k: float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
        for k, v in stats.items()
    }

    return {
        "ticker": ticker,
        "windows": windows,
        "stats": stats,
        "thresholds": {
            "entry_threshold": entry_threshold,
            "exit_threshold": exit_threshold,
        }
    }
