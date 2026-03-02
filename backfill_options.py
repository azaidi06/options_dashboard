#!/usr/bin/env python3
"""
Alpha Vantage US options backfill CLI.

Pulls historical option chains by trading day for specified tickers.
Saves one Parquet per day per symbol: data/options/<SYMBOL>/YYYY/MM/DD.parquet

Features:
- Resume support: existing files are skipped
- Daily limit enforcement: stops after N successful API requests
- Progress tracking: shows stats, days remaining, ETA
- IPO-aware: starts from actual IPO dates for newer stocks
- Ticker rename handling: META→FB before 2022-06-09

Requires: requests, pandas, python-dateutil
Optional: pandas-market-calendars (for accurate NYSE calendar)

Usage:
    python backfill_options.py [OPTIONS]

Options:
    --tickers       Comma-separated list (default: all 9)
    --start         Start date YYYY-MM-DD (default: 2008-01-23)
    --end           End date YYYY-MM-DD (default: today)
    --daily-limit   Max requests per run (default: 25)
    --output-dir    Output directory (default: data/options)
"""

import argparse
import io
import os
import sys
import time
from datetime import date, datetime

import pandas as pd
import requests
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "Q3EBFXC1GEUITND1")
BASE_URL = "https://www.alphavantage.co/query"

# All supported tickers
ALL_TICKERS = [
    "MSFT", "INTC", "META", "NVDA", "AMD", "PLTR", "ORCL", "AMZN", "GOOG",
    "AAPL", "GOOGL", "TSLA", "NFLX", "CRWV", "SMCI", "ARM", "SNOW", "TSM", "AVGO",
]

# IPO dates (or earliest Alpha Vantage data availability)
# Stocks with IPO before 2008-01-23 use 2008-01-23 as the effective start
IPO_DATES = {
    "MSFT": pd.Timestamp("2008-01-23"),  # IPO 1986, AV limit
    "INTC": pd.Timestamp("2008-01-23"),  # IPO 1971, AV limit
    "ORCL": pd.Timestamp("2008-01-23"),  # IPO 1986, AV limit
    "AMZN": pd.Timestamp("2008-01-23"),  # IPO 1997, AV limit
    "GOOG": pd.Timestamp("2008-01-23"),  # IPO 2004, AV limit
    "GOOGL": pd.Timestamp("2008-01-23"),
    "NVDA": pd.Timestamp("2008-01-23"),  # IPO 1999, AV limit
    "AMD": pd.Timestamp("2008-01-23"),   # IPO 1972, AV limit
    "AAPL": pd.Timestamp("2008-01-23"),
    "NFLX": pd.Timestamp("2008-01-23"),
    "SMCI": pd.Timestamp("2008-01-23"),
    "TSM": pd.Timestamp("2008-01-23"),
    "AVGO": pd.Timestamp("2009-08-06"),
    "TSLA": pd.Timestamp("2010-06-29"),
    "META": pd.Timestamp("2012-05-18"),  # IPO 2012-05-18
    "SNOW": pd.Timestamp("2020-09-16"),
    "PLTR": pd.Timestamp("2020-09-30"),  # IPO 2020-09-30
    "ARM": pd.Timestamp("2023-09-14"),
    "CRWV": pd.Timestamp("2025-03-28"),
}

# Rate limiting
PAUSE_S = 0.85  # seconds between requests (~70 req/min, premium tier)
MAX_RETRY = 3   # retries on rate limit

# ─────────────────────────────────────────────────────────────────────────────
# Core Functions (adapted from Untitled.ipynb)
# ─────────────────────────────────────────────────────────────────────────────


def trading_days(start: pd.Timestamp, end: pd.Timestamp) -> pd.DatetimeIndex:
    """
    Return actual NYSE trading sessions (preferred) or business days minus
    US federal holidays (fallback).
    """
    try:
        import pandas_market_calendars as mcal
        cal = mcal.get_calendar("XNYS")
        days = cal.valid_days(
            start_date=str(start.date()),
            end_date=str(end.date()),
            tz="America/New_York"
        )
        return days.tz_convert(None)
    except Exception:
        # Fallback: Mon–Fri minus US federal holidays
        usb = CustomBusinessDay(calendar=USFederalHolidayCalendar())
        return pd.date_range(start, end, freq=usb)


def symbol_for_date(symbol: str, day: pd.Timestamp) -> str:
    """
    Handle ticker renames. Alpha Vantage requires legacy symbol for historical data.
    META was FB before 2022-06-09.
    """
    if symbol.upper() == "META" and day < pd.Timestamp("2022-06-09"):
        return "FB"
    return symbol


def day_path(output_dir: str, symbol: str, d: pd.Timestamp) -> str:
    """Generate file path: output_dir/<SYMBOL>/YYYY/MM/DD.parquet"""
    return os.path.join(
        output_dir,
        symbol,
        f"{d.year:04d}",
        f"{d.month:02d}",
        f"{d.day:02d}.parquet"
    )


def ensure_dir(path: str) -> None:
    """Create parent directories if they don't exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)


def annotate_df(df: pd.DataFrame, day: pd.Timestamp, requested_symbol: str) -> pd.DataFrame:
    """
    Add metadata columns to the DataFrame.
    - as_of_date: the trading day
    - _requested_symbol: what the user asked for (e.g., META)
    - _api_symbol: what was queried (e.g., FB for dates before 2022-06-09)
    """
    api_sym = symbol_for_date(requested_symbol, day)
    if "as_of_date" not in df.columns:
        df.insert(0, "as_of_date", day.date())
    else:
        df["as_of_date"] = day.date()
    df["_requested_symbol"] = requested_symbol
    df["_api_symbol"] = api_sym
    return df


def fetch_chain(symbol: str, day: pd.Timestamp, datatype: str = "csv") -> str | None:
    """
    Fetch option chain from Alpha Vantage HISTORICAL_OPTIONS endpoint.

    Returns:
        CSV text on success, None if no data (holiday/pre-IPO), raises on error.
    """
    q_symbol = symbol_for_date(symbol, day)
    params = {
        "function": "HISTORICAL_OPTIONS",
        "symbol": q_symbol,
        "date": day.strftime("%Y-%m-%d"),
        "datatype": datatype,
        "apikey": API_KEY,
    }
    headers = {"Accept-Encoding": "gzip"}

    r = requests.get(BASE_URL, params=params, headers=headers, timeout=60)

    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} for {symbol} {day.date()}: {r.text[:200]}")

    ctype = r.headers.get("Content-Type", "").lower()
    text = r.text.strip()

    # JSON response indicates rate limit, no data, or error
    if "application/json" in ctype or text.startswith("{"):
        try:
            msg = r.json()
        except Exception:
            raise RuntimeError(f"Unexpected JSON/text for {symbol} {day.date()}: {text[:200]}")

        # Rate limit "Note" → tell caller to retry
        if "Note" in msg:
            raise RuntimeError("RATE_LIMIT: " + msg.get("Note", str(msg)))

        # No data → skip without retry
        if str(msg.get("message", "")).lower().startswith("no data for symbol"):
            return None

        # Other JSON → hard error
        raise RuntimeError(f"API_ERROR: {msg}")

    return text  # CSV


# ─────────────────────────────────────────────────────────────────────────────
# Backfill Logic
# ─────────────────────────────────────────────────────────────────────────────


def get_effective_start(symbol: str, user_start: pd.Timestamp) -> pd.Timestamp:
    """
    Return the effective start date for a symbol, respecting IPO dates.
    """
    ipo_date = IPO_DATES.get(symbol, pd.Timestamp("2008-01-23"))
    return max(user_start, ipo_date)


def collect_missing_days(
    tickers: list[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
    output_dir: str
) -> list[tuple[str, pd.Timestamp]]:
    """
    Build a list of (ticker, day) pairs that need to be fetched.
    Sorted by date descending (most recent first).
    """
    missing = []

    for ticker in tickers:
        effective_start = get_effective_start(ticker, start)
        days = trading_days(effective_start, end)

        for d in days:
            out_fp = day_path(output_dir, ticker, d)
            if not os.path.exists(out_fp):
                missing.append((ticker, d))

    # Sort by date descending (most recent first)
    missing.sort(key=lambda x: x[1], reverse=True)
    return missing


def fetch_and_save(
    ticker: str,
    day: pd.Timestamp,
    output_dir: str
) -> tuple[bool, str]:
    """
    Fetch data for a single ticker/day and save to CSV.

    Returns:
        (success, message) tuple
    """
    out_fp = day_path(output_dir, ticker, day)
    ensure_dir(out_fp)

    for attempt in range(1, MAX_RETRY + 1):
        try:
            csv_text = fetch_chain(ticker, day)

            if csv_text is None:
                # No data (holiday/pre-IPO) → write empty parquet placeholder
                pd.DataFrame().to_parquet(out_fp, compression="gzip", index=False)
                return True, "no data (holiday/pre-listing)"

            # Empty CSV edge case
            if len(csv_text.splitlines()) <= 1:
                pd.DataFrame().to_parquet(out_fp, compression="gzip", index=False)
                return True, "empty CSV"

            # Normal case: parse and save with annotations
            df = pd.read_csv(io.StringIO(csv_text))
            df = annotate_df(df, day, ticker)
            df.to_parquet(out_fp, compression="gzip", index=False)
            return True, f"saved {len(df)} contracts"

        except Exception as e:
            msg = str(e)

            if "RATE_LIMIT:" in msg and attempt < MAX_RETRY:
                sleep_s = PAUSE_S * attempt
                print(f"  Rate limit hit, retry {attempt}/{MAX_RETRY} in {sleep_s:.1f}s...")
                time.sleep(sleep_s)
                continue

            if "RATE_LIMIT:" in msg:
                return False, "rate limit exceeded after retries"

            return False, f"error: {msg[:100]}"

    return False, "unknown error"


def format_eta(seconds: float) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def run_backfill(
    tickers: list[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
    daily_limit: int,
    output_dir: str
) -> None:
    """
    Main backfill loop with progress tracking.
    """
    print(f"\n{'='*60}")
    print("Options Data Backfill")
    print(f"{'='*60}")
    print(f"Tickers:      {', '.join(tickers)}")
    print(f"Date range:   {start.date()} to {end.date()}")
    print(f"Daily limit:  {daily_limit} requests")
    print(f"Output dir:   {output_dir}")
    print(f"{'='*60}\n")

    # Collect all missing days
    print("Scanning for missing data...")
    missing = collect_missing_days(tickers, start, end, output_dir)
    total_missing = len(missing)

    if total_missing == 0:
        print("All data already downloaded!")
        return

    print(f"Found {total_missing} missing ticker-days")
    print(f"With {daily_limit} requests/day, full backfill needs ~{(total_missing + daily_limit - 1) // daily_limit} days\n")

    # Process up to daily_limit requests
    requests_made = 0
    successful = 0
    failed = 0

    for ticker, day in missing:
        if requests_made >= daily_limit:
            print(f"\nDaily limit of {daily_limit} requests reached.")
            break

        requests_made += 1
        remaining = total_missing - requests_made
        eta_seconds = remaining * PAUSE_S

        print(f"[{requests_made}/{daily_limit}] {ticker} {day.date()} ", end="", flush=True)

        success, message = fetch_and_save(ticker, day, output_dir)

        if success:
            successful += 1
            print(f"✓ {message}")
        else:
            failed += 1
            print(f"✗ {message}")

        # Rate limit pause (except for last request)
        if requests_made < daily_limit and requests_made < total_missing:
            time.sleep(PAUSE_S)

    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"Requests made:    {requests_made}")
    print(f"Successful:       {successful}")
    print(f"Failed:           {failed}")
    print(f"Remaining days:   {total_missing - requests_made}")

    if total_missing - requests_made > 0:
        days_needed = (total_missing - requests_made + daily_limit - 1) // daily_limit
        print(f"Days to complete: ~{days_needed} more runs")
    else:
        print("Backfill complete!")

    print(f"{'='*60}\n")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backfill historical options data from Alpha Vantage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backfill_options.py                           # All tickers, default settings
  python backfill_options.py --tickers MSFT,NVDA       # Specific tickers
  python backfill_options.py --daily-limit 5           # Test with 5 requests
  python backfill_options.py --start 2024-01-01        # From specific date
        """
    )

    parser.add_argument(
        "--tickers",
        type=str,
        default=",".join(ALL_TICKERS),
        help=f"Comma-separated list of tickers (default: {','.join(ALL_TICKERS)})"
    )

    parser.add_argument(
        "--start",
        type=str,
        default="2008-01-23",
        help="Start date YYYY-MM-DD (default: 2008-01-23, earliest AV data)"
    )

    parser.add_argument(
        "--end",
        type=str,
        default=str(date.today()),
        help=f"End date YYYY-MM-DD (default: today, {date.today()})"
    )

    parser.add_argument(
        "--daily-limit",
        type=int,
        default=25,
        help="Max API requests per run (default: 25, free tier limit)"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/options",
        help="Output directory (default: data/options)"
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Parse tickers
    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]

    # Validate tickers
    invalid = [t for t in tickers if t not in ALL_TICKERS]
    if invalid:
        print(f"Warning: Unknown tickers will use default IPO date of 2008-01-23: {invalid}")

    # Parse dates
    try:
        start = pd.Timestamp(args.start)
        end = pd.Timestamp(args.end)
    except Exception as e:
        print(f"Error parsing dates: {e}")
        sys.exit(1)

    if start > end:
        print(f"Error: Start date ({start.date()}) is after end date ({end.date()})")
        sys.exit(1)

    # Run backfill
    run_backfill(
        tickers=tickers,
        start=start,
        end=end,
        daily_limit=args.daily_limit,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
