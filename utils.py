"""
Stock data utilities with robust error handling and caching.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


def get_stock_data(
    ticker: str = "AAPL",
    start: str = "2020-01-01",
    end: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance.

    Args:
        ticker: Stock ticker symbol
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD), defaults to today

    Returns:
        DataFrame with Date, Open, High, Low, Close, Volume columns

    Raises:
        ValueError: If no data is returned for the ticker
    """
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")

    try:
        data = yf.download(ticker, start=start, end=end, progress=False)
    except Exception as e:
        raise ValueError(f"Failed to fetch data for {ticker}: {e}")

    if data.empty:
        raise ValueError(f"No data returned for ticker '{ticker}' in date range {start} to {end}")

    # Reset index to get Date as a column
    df = data.reset_index()

    # Handle MultiIndex columns from newer yfinance versions
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if col[1] == "" or col[1] == ticker.upper() else col[0] for col in df.columns]

    # Ensure we have the expected columns
    expected_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
    for col in expected_cols:
        if col not in df.columns:
            # Try case-insensitive match
            for c in df.columns:
                if c.lower() == col.lower():
                    df = df.rename(columns={c: col})
                    break

    # Parse date components
    df["Date"] = pd.to_datetime(df["Date"])
    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month
    df["day"] = df["Date"].dt.day

    return df


def compute_prev_xday_high(
    df: pd.DataFrame,
    num_days: int = 30,
    price_col: str = "Close",
) -> pd.DataFrame:
    """
    Compute the previous X-day rolling high and percentage change from it.

    Args:
        df: DataFrame with price data
        num_days: Lookback period for computing the rolling high
        price_col: Column name to use for price (default: Close)

    Returns:
        DataFrame with added columns:
        - prev_{num_days}_high: Rolling high over previous num_days
        - pct_change: Percentage change from rolling high (as decimal, not %)
    """
    if len(df) <= num_days:
        raise ValueError(f"DataFrame has {len(df)} rows, need more than {num_days} for lookback")

    df = df.copy()

    # Ensure price column is 1D
    close = df[price_col]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.values.flatten()

    # Compute rolling max using vectorized approach
    rolling_high = pd.Series(close).rolling(window=num_days, min_periods=num_days).max().values

    # Shift by 1 to get "previous" X-day high (not including current day)
    prev_xday_high = np.roll(rolling_high, 1)
    prev_xday_high[:num_days] = np.nan

    df[f"prev_{num_days}_high"] = prev_xday_high

    # Compute percentage change from the rolling high (as decimal)
    with np.errstate(divide="ignore", invalid="ignore"):
        pct_change = (close - prev_xday_high) / prev_xday_high

    df["pct_change"] = pct_change

    # Remove rows where we don't have enough history
    df = df.iloc[num_days:].reset_index(drop=True)

    return df


def get_stock_with_metrics(
    ticker: str = "AAPL",
    start: str = "2020-01-01",
    end: Optional[str] = None,
    lookback_days: int = 30,
) -> pd.DataFrame:
    """
    Convenience function to fetch stock data and compute metrics in one call.

    Args:
        ticker: Stock ticker symbol
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD), defaults to today
        lookback_days: Lookback period for rolling high calculation

    Returns:
        DataFrame with stock data and computed metrics
    """
    df = get_stock_data(ticker, start, end)
    df = compute_prev_xday_high(df, num_days=lookback_days)
    return df


# Common stock tickers for quick selection
_CATEGORY_TICKERS = {
    # Mega-cap Tech
    "Mega-Cap Tech": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "NFLX"],

    # AI & Cloud Infrastructure (CoreWeave, etc.)
    "AI Infrastructure": ["CRWV", "SMCI", "ARM", "PLTR", "SNOW", "AI", "PATH", "IONQ"],

    # Semiconductors (expanded)
    "Semiconductors": ["NVDA", "AMD", "INTC", "TSM", "AVGO", "QCOM", "MU", "MRVL", "ASML", "AMAT", "LRCX", "KLAC", "ON"],

    # Cybersecurity
    "Cybersecurity": ["CRWD", "ZS", "PANW", "FTNT", "S", "OKTA"],

    # Cloud & SaaS
    "Cloud & SaaS": ["CRM", "ADBE", "ORCL", "NOW", "DDOG", "NET", "MDB", "SHOP", "TEAM", "ZM"],

    # Internet & Consumer
    "Internet & Consumer": ["UBER", "ABNB", "PYPL", "SQ", "COIN", "HOOD", "RBLX", "SNAP", "PINS"],

    # Finance
    "Finance": ["JPM", "BAC", "GS", "MS", "V", "MA", "AXP", "BLK"],

    # ETFs
    "ETFs": ["SPY", "QQQ", "IWM", "DIA", "ARKK", "SMH", "XLK", "SOXX"],
}

# Build "All" category with unique tickers sorted alphabetically
_all_tickers = sorted(set(t for tickers in _CATEGORY_TICKERS.values() for t in tickers))

POPULAR_TICKERS = {
    "All": _all_tickers,
    **_CATEGORY_TICKERS,
}


def get_realtime_quote(ticker: str) -> dict:
    """
    Fetch real-time quote for a ticker using fast_info (avoids slow .info scrape).

    Returns:
        dict with keys: price, change, change_pct, volume, timestamp, market_state
    """
    try:
        stock = yf.Ticker(ticker)
        fi = stock.fast_info

        price = fi.get("lastPrice")
        prev_close = fi.get("previousClose") or fi.get("regularMarketPreviousClose")

        if price and prev_close:
            change = price - prev_close
            change_pct = (change / prev_close) * 100
        else:
            change = None
            change_pct = None

        day_high = fi.get("dayHigh")
        day_low = fi.get("dayLow")
        volume = fi.get("lastVolume")
        # fast_info doesn't include marketState; fall back to UNKNOWN
        market_state = "UNKNOWN"

        return {
            "ticker": ticker,
            "price": price,
            "prev_close": prev_close,
            "change": change,
            "change_pct": change_pct,
            "volume": volume,
            "day_high": day_high,
            "day_low": day_low,
            "market_state": market_state,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "price": None,
            "error": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


# Technical Indicator Functions (computed locally using ta library)


def compute_rsi(df: pd.DataFrame, period: int = 14, price_col: str = "Close") -> pd.DataFrame:
    """
    Compute RSI (Relative Strength Index) from price data.

    Args:
        df: DataFrame with price data (must have Date and price_col columns)
        period: RSI lookback period (default: 14)
        price_col: Column name for price (default: "Close")

    Returns:
        DataFrame with Date and RSI columns
    """
    from ta.momentum import RSIIndicator

    # Handle MultiIndex or squeezed columns
    close = df[price_col]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = pd.Series(close.values.flatten(), index=df.index)

    rsi_indicator = RSIIndicator(close=close, window=period)

    result = pd.DataFrame()
    result["Date"] = df["Date"].values
    result["RSI"] = rsi_indicator.rsi().values
    return result


def compute_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    price_col: str = "Close",
) -> pd.DataFrame:
    """
    Compute MACD (Moving Average Convergence Divergence) from price data.

    Args:
        df: DataFrame with price data
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)
        price_col: Column name for price (default: "Close")

    Returns:
        DataFrame with Date, MACD, MACD_Signal, MACD_Hist columns
    """
    from ta.trend import MACD

    close = df[price_col]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = pd.Series(close.values.flatten(), index=df.index)

    macd_indicator = MACD(close=close, window_fast=fast, window_slow=slow, window_sign=signal)

    result = pd.DataFrame()
    result["Date"] = df["Date"].values
    result["MACD"] = macd_indicator.macd().values
    result["MACD_Signal"] = macd_indicator.macd_signal().values
    result["MACD_Hist"] = macd_indicator.macd_diff().values
    return result


def compute_bollinger_bands(
    df: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0,
    price_col: str = "Close",
) -> pd.DataFrame:
    """
    Compute Bollinger Bands from price data.

    Args:
        df: DataFrame with price data
        period: Lookback period (default: 20)
        std_dev: Standard deviation multiplier (default: 2.0)
        price_col: Column name for price (default: "Close")

    Returns:
        DataFrame with Date, BB_Lower, BB_Middle, BB_Upper columns
    """
    from ta.volatility import BollingerBands

    close = df[price_col]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = pd.Series(close.values.flatten(), index=df.index)

    bb_indicator = BollingerBands(close=close, window=period, window_dev=std_dev)

    result = pd.DataFrame()
    result["Date"] = df["Date"].values
    result["BB_Lower"] = bb_indicator.bollinger_lband().values
    result["BB_Middle"] = bb_indicator.bollinger_mavg().values
    result["BB_Upper"] = bb_indicator.bollinger_hband().values
    return result


def compute_sma(df: pd.DataFrame, period: int = 20, price_col: str = "Close") -> pd.DataFrame:
    """
    Compute Simple Moving Average from price data.

    Args:
        df: DataFrame with price data
        period: SMA period (default: 20)
        price_col: Column name for price (default: "Close")

    Returns:
        DataFrame with Date and SMA_{period} columns
    """
    from ta.trend import SMAIndicator

    close = df[price_col]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = pd.Series(close.values.flatten(), index=df.index)

    sma_indicator = SMAIndicator(close=close, window=period)

    result = pd.DataFrame()
    result["Date"] = df["Date"].values
    result[f"SMA_{period}"] = sma_indicator.sma_indicator().values
    return result


def compute_ema(df: pd.DataFrame, period: int = 20, price_col: str = "Close") -> pd.DataFrame:
    """
    Compute Exponential Moving Average from price data.

    Args:
        df: DataFrame with price data
        period: EMA period (default: 20)
        price_col: Column name for price (default: "Close")

    Returns:
        DataFrame with Date and EMA_{period} columns
    """
    from ta.trend import EMAIndicator

    close = df[price_col]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = pd.Series(close.values.flatten(), index=df.index)

    ema_indicator = EMAIndicator(close=close, window=period)

    result = pd.DataFrame()
    result["Date"] = df["Date"].values
    result[f"EMA_{period}"] = ema_indicator.ema_indicator().values
    return result


# ============================================================================
# Drawdown & Recovery Analysis Functions
# ============================================================================


def compute_underwater_periods(
    df: pd.DataFrame,
    price_col: str = "Close",
) -> pd.DataFrame:
    """
    Calculate drawdown metrics from all-time high.

    Adds columns:
    - cummax: Running all-time high
    - drawdown_from_ath: (price - ATH) / ATH (negative when underwater)
    - days_underwater: Consecutive days below ATH
    - underwater_period_id: Unique ID for each underwater period

    Args:
        df: DataFrame with price data (must have 'Date' column)
        price_col: Column name for price

    Returns:
        DataFrame with added drawdown columns
    """
    df = df.copy()

    # Ensure price is 1D array
    close = df[price_col]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.values.flatten()

    # Calculate cumulative max (all-time high up to each point)
    cummax = pd.Series(close).cummax().values
    df["cummax"] = cummax

    # Calculate drawdown from ATH (negative when below ATH)
    with np.errstate(divide="ignore", invalid="ignore"):
        drawdown = (close - cummax) / cummax
    df["drawdown_from_ath"] = drawdown

    # Track consecutive days underwater
    is_underwater = drawdown < 0
    days_underwater = np.zeros(len(df), dtype=int)
    current_streak = 0
    for i in range(len(df)):
        if is_underwater[i]:
            current_streak += 1
            days_underwater[i] = current_streak
        else:
            current_streak = 0
            days_underwater[i] = 0
    df["days_underwater"] = days_underwater

    # Assign underwater period IDs
    period_ids = np.zeros(len(df), dtype=int)
    current_id = 0
    in_period = False
    for i in range(len(df)):
        if is_underwater[i]:
            if not in_period:
                current_id += 1
                in_period = True
            period_ids[i] = current_id
        else:
            in_period = False
            period_ids[i] = 0
    df["underwater_period_id"] = period_ids

    return df


def identify_drawdown_events(
    df: pd.DataFrame,
    min_drawdown_pct: float = 0.05,
    price_col: str = "Close",
) -> list[dict]:
    """
    Detect peak-to-trough-to-recovery cycles.

    Args:
        df: DataFrame with price data (must have 'Date' column)
        min_drawdown_pct: Minimum drawdown to qualify as an event (e.g., 0.05 = 5%)
        price_col: Column name for price

    Returns:
        List of event dictionaries with keys:
        - peak_date: Date of the peak before drawdown
        - peak_price: Price at peak
        - trough_date: Date of maximum drawdown
        - trough_price: Price at trough
        - recovery_date: Date when price recovered to peak (None if not recovered)
        - drawdown_pct: Maximum drawdown percentage (as positive decimal, e.g., 0.15 = 15%)
        - days_to_trough: Trading days from peak to trough
        - days_to_recovery: Trading days from peak to recovery (None if not recovered)
    """
    if "cummax" not in df.columns or "drawdown_from_ath" not in df.columns:
        df = compute_underwater_periods(df, price_col)

    events = []
    close = df[price_col].values.flatten() if hasattr(df[price_col], "values") else df[price_col].to_numpy()
    dates = pd.to_datetime(df["Date"]).values
    cummax = df["cummax"].values
    drawdown = df["drawdown_from_ath"].values

    i = 0
    while i < len(df):
        # Look for start of a drawdown (price drops below cummax)
        if drawdown[i] < -min_drawdown_pct:
            # Found a significant drawdown - find the peak before it
            peak_idx = i
            while peak_idx > 0 and drawdown[peak_idx] < 0:
                peak_idx -= 1

            # Find the trough (maximum drawdown in this period)
            trough_idx = i
            j = i
            while j < len(df) and drawdown[j] < 0:
                if drawdown[j] < drawdown[trough_idx]:
                    trough_idx = j
                j += 1

            # Only record if drawdown exceeds threshold
            max_drawdown = abs(drawdown[trough_idx])
            if max_drawdown >= min_drawdown_pct:
                # Find recovery point (when price returns to peak level)
                recovery_idx = None
                peak_price = cummax[peak_idx]
                for k in range(trough_idx + 1, len(df)):
                    if close[k] >= peak_price:
                        recovery_idx = k
                        break

                event = {
                    "peak_date": pd.Timestamp(dates[peak_idx]),
                    "peak_price": float(cummax[peak_idx]),
                    "trough_date": pd.Timestamp(dates[trough_idx]),
                    "trough_price": float(close[trough_idx]),
                    "drawdown_pct": float(max_drawdown),
                    "days_to_trough": int(trough_idx - peak_idx),
                }

                if recovery_idx is not None:
                    event["recovery_date"] = pd.Timestamp(dates[recovery_idx])
                    event["days_to_recovery"] = int(recovery_idx - peak_idx)
                else:
                    event["recovery_date"] = None
                    event["days_to_recovery"] = None

                events.append(event)

            # Move past this drawdown period
            i = j if j < len(df) else len(df)
        else:
            i += 1

    return events


def compute_drawdown_time_distribution(
    df: pd.DataFrame,
    bins: Optional[list[float]] = None,
) -> pd.DataFrame:
    """
    Calculate percentage of time spent at each drawdown level.

    Args:
        df: DataFrame with drawdown_from_ath column
        bins: List of bin edges (as positive percentages).
              Default: [0, 0.05, 0.10, 0.15, 0.20, 1.0] for 0-5%, 5-10%, etc.

    Returns:
        DataFrame with columns: bin_label, days, pct_of_time
    """
    if "drawdown_from_ath" not in df.columns:
        df = compute_underwater_periods(df)

    if bins is None:
        bins = [0, 0.05, 0.10, 0.15, 0.20, 1.0]

    # Convert drawdown to positive values for binning
    drawdown_abs = df["drawdown_from_ath"].abs().values

    # Count days in each bin
    results = []
    total_days = len(df)

    for i in range(len(bins) - 1):
        low, high = bins[i], bins[i + 1]

        if i == 0:
            # First bin includes 0 (at ATH)
            mask = (drawdown_abs >= low) & (drawdown_abs < high)
            label = f"0-{int(high*100)}%"
        elif i == len(bins) - 2:
            # Last bin includes everything above
            mask = drawdown_abs >= low
            label = f"{int(low*100)}%+"
        else:
            mask = (drawdown_abs >= low) & (drawdown_abs < high)
            label = f"{int(low*100)}-{int(high*100)}%"

        days = mask.sum()
        pct = days / total_days if total_days > 0 else 0

        results.append({
            "bin_label": label,
            "bin_low": low,
            "bin_high": high,
            "days": int(days),
            "pct_of_time": float(pct),
        })

    return pd.DataFrame(results)


def compute_recovery_stats(
    events: list[dict],
    depth_thresholds: Optional[list[float]] = None,
) -> pd.DataFrame:
    """
    Compute recovery statistics for different drawdown depths.

    Args:
        events: List of drawdown events from identify_drawdown_events
        depth_thresholds: List of depth thresholds to analyze
                         Default: [0.05, 0.10, 0.15, 0.20, 0.25]

    Returns:
        DataFrame with columns: threshold, count, avg_recovery_days,
        median_recovery_days, pct_recovered
    """
    if depth_thresholds is None:
        depth_thresholds = [0.05, 0.10, 0.15, 0.20, 0.25]

    results = []

    for threshold in depth_thresholds:
        # Filter events that reached at least this depth
        qualified = [e for e in events if e["drawdown_pct"] >= threshold]
        count = len(qualified)

        if count == 0:
            results.append({
                "threshold": f"{int(threshold*100)}%+",
                "threshold_value": threshold,
                "count": 0,
                "avg_recovery_days": None,
                "median_recovery_days": None,
                "pct_recovered": None,
            })
            continue

        # Get recovery days for events that recovered
        recovery_days = [
            e["days_to_recovery"] for e in qualified
            if e["days_to_recovery"] is not None
        ]
        recovered_count = len(recovery_days)
        pct_recovered = recovered_count / count if count > 0 else 0

        avg_days = np.mean(recovery_days) if recovery_days else None
        median_days = np.median(recovery_days) if recovery_days else None

        results.append({
            "threshold": f"{int(threshold*100)}%+",
            "threshold_value": threshold,
            "count": count,
            "avg_recovery_days": float(avg_days) if avg_days is not None else None,
            "median_recovery_days": float(median_days) if median_days is not None else None,
            "pct_recovered": float(pct_recovered),
        })

    return pd.DataFrame(results)


def compute_opportunity_windows(
    df: pd.DataFrame,
    entry_threshold: float = 0.10,
    exit_threshold: float = 0.05,
) -> list[dict]:
    """
    Identify periods where stock was below entry threshold (opportunity windows).

    An opportunity window starts when drawdown exceeds entry_threshold and
    ends when drawdown recovers above exit_threshold.

    Args:
        df: DataFrame with drawdown_from_ath column
        entry_threshold: Drawdown level to enter (e.g., 0.10 = 10% down)
        exit_threshold: Drawdown level to exit (e.g., 0.05 = 5% down)

    Returns:
        List of opportunity windows with keys:
        - start_date: When drawdown exceeded entry threshold
        - end_date: When drawdown recovered above exit threshold
        - duration_days: Trading days in the window
        - max_drawdown: Maximum drawdown during the window
        - entry_drawdown: Drawdown at entry
        - exit_drawdown: Drawdown at exit (None if still in window)
    """
    if "drawdown_from_ath" not in df.columns:
        df = compute_underwater_periods(df)

    windows = []
    dates = pd.to_datetime(df["Date"]).values
    drawdown = df["drawdown_from_ath"].values

    in_window = False
    window_start = None
    window_max_dd = 0
    entry_dd = 0

    for i in range(len(df)):
        dd = abs(drawdown[i])  # Work with positive values

        if not in_window and dd >= entry_threshold:
            # Enter window
            in_window = True
            window_start = i
            window_max_dd = dd
            entry_dd = dd

        elif in_window:
            # Update max drawdown
            window_max_dd = max(window_max_dd, dd)

            # Check for exit
            if dd < exit_threshold:
                # Exit window
                windows.append({
                    "start_date": pd.Timestamp(dates[window_start]),
                    "end_date": pd.Timestamp(dates[i]),
                    "duration_days": int(i - window_start),
                    "max_drawdown": float(window_max_dd),
                    "entry_drawdown": float(entry_dd),
                    "exit_drawdown": float(dd),
                })
                in_window = False

    # Handle window that's still open
    if in_window:
        windows.append({
            "start_date": pd.Timestamp(dates[window_start]),
            "end_date": None,
            "duration_days": int(len(df) - 1 - window_start),
            "max_drawdown": float(window_max_dd),
            "entry_drawdown": float(entry_dd),
            "exit_drawdown": None,
        })

    return windows


def compute_opportunity_stats(
    windows: list[dict],
    total_trading_days: int,
    years: float,
) -> dict:
    """
    Compute aggregate statistics for opportunity windows.

    Args:
        windows: List of opportunity windows from compute_opportunity_windows
        total_trading_days: Total trading days in the period
        years: Number of years in the analysis period

    Returns:
        Dictionary with:
        - total_windows: Number of opportunity windows
        - windows_per_year: Average windows per year
        - avg_duration: Average duration in days
        - median_duration: Median duration in days
        - max_duration: Maximum duration in days
        - avg_max_drawdown: Average max drawdown during windows
        - pct_time_in_window: Percentage of time in opportunity windows
    """
    if not windows:
        return {
            "total_windows": 0,
            "windows_per_year": 0,
            "avg_duration": None,
            "median_duration": None,
            "max_duration": None,
            "avg_max_drawdown": None,
            "pct_time_in_window": 0,
        }

    durations = [w["duration_days"] for w in windows]
    max_drawdowns = [w["max_drawdown"] for w in windows]

    total_days_in_windows = sum(durations)

    return {
        "total_windows": len(windows),
        "windows_per_year": len(windows) / years if years > 0 else 0,
        "avg_duration": float(np.mean(durations)),
        "median_duration": float(np.median(durations)),
        "max_duration": int(max(durations)),
        "avg_max_drawdown": float(np.mean(max_drawdowns)),
        "pct_time_in_window": total_days_in_windows / total_trading_days if total_trading_days > 0 else 0,
    }
