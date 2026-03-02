#!/usr/bin/env python3
"""
Fetch historical options data from Alpha Vantage for all tickers.

Usage:
    python fetch_historical_options.py                    # Previous trading day, all tickers
    python fetch_historical_options.py --date 2024-01-15  # Specific date
    python fetch_historical_options.py --ticker AAPL      # Single ticker
    python fetch_historical_options.py --start 2024-01-01 --end 2024-01-31  # Date range
"""

import os
import sys
import time
import argparse
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Import tickers from utils
sys.path.insert(0, str(Path(__file__).parent))
from utils import POPULAR_TICKERS

# Configuration
ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"
OUTPUT_DIR = Path(__file__).parent / "options_data"
RATE_LIMIT_DELAY = 0.85  # ~70 requests/min (staying under 75/min premium limit)


def get_api_key():
    """Get Alpha Vantage API key from environment."""
    key = os.environ.get("ALPHAVANTAGE_API_KEY")
    if not key:
        print("ERROR: ALPHAVANTAGE_API_KEY environment variable not set")
        sys.exit(1)
    return key


def fetch_options_chain(ticker: str, date: str = None, api_key: str = None) -> dict:
    """
    Fetch historical options chain for a ticker on a specific date.

    Args:
        ticker: Stock symbol
        date: Date in YYYY-MM-DD format (None = previous trading day)
        api_key: Alpha Vantage API key

    Returns:
        dict with options data or error info
    """
    params = {
        "function": "HISTORICAL_OPTIONS",
        "symbol": ticker,
        "apikey": api_key,
    }
    if date:
        params["date"] = date

    try:
        response = requests.get(ALPHAVANTAGE_BASE_URL, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Check for API errors
        if "Error Message" in data:
            return {"error": data["Error Message"], "ticker": ticker, "date": date}
        if "Note" in data:
            return {"error": f"Rate limit: {data['Note']}", "ticker": ticker, "date": date}
        if "Information" in data:
            return {"error": data["Information"], "ticker": ticker, "date": date}

        return data

    except requests.RequestException as e:
        return {"error": str(e), "ticker": ticker, "date": date}


def save_options_data(data: dict, ticker: str, date: str, output_dir: Path):
    """Save options data to Parquet file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    date_str = date or "latest"

    if "data" in data and data["data"]:
        df = pd.DataFrame(data["data"])
        parquet_path = output_dir / f"{ticker}_{date_str}.parquet"
        df.to_parquet(parquet_path, compression="gzip", index=False)
        return parquet_path
    return None


def get_trading_days(start_date: str, end_date: str) -> list:
    """Generate list of potential trading days (weekdays) between dates."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    days = []
    current = start
    while current <= end:
        # Skip weekends
        if current.weekday() < 5:
            days.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return days


def main():
    parser = argparse.ArgumentParser(description="Fetch historical options data from Alpha Vantage")
    parser.add_argument("--ticker", "-t", help="Single ticker (default: all tickers)")
    parser.add_argument("--date", "-d", help="Specific date YYYY-MM-DD (default: previous trading day)")
    parser.add_argument("--start", "-s", help="Start date for range YYYY-MM-DD")
    parser.add_argument("--end", "-e", help="End date for range YYYY-MM-DD")
    parser.add_argument("--category", "-c", help="Ticker category from POPULAR_TICKERS")
    parser.add_argument("--output", "-o", default=str(OUTPUT_DIR), help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fetched without fetching")

    args = parser.parse_args()

    api_key = get_api_key()
    output_dir = Path(args.output)

    # Determine tickers to fetch
    if args.ticker:
        tickers = [args.ticker.upper()]
    elif args.category:
        if args.category not in POPULAR_TICKERS:
            print(f"ERROR: Unknown category '{args.category}'")
            print(f"Available: {list(POPULAR_TICKERS.keys())}")
            sys.exit(1)
        tickers = POPULAR_TICKERS[args.category]
    else:
        tickers = POPULAR_TICKERS["All"]

    # Determine dates to fetch
    if args.start and args.end:
        dates = get_trading_days(args.start, args.end)
    elif args.date:
        dates = [args.date]
    else:
        dates = [None]  # None = previous trading day

    # Calculate total requests
    total_requests = len(tickers) * len(dates)
    est_time_min = (total_requests * RATE_LIMIT_DELAY) / 60

    print(f"=" * 60)
    print(f"Historical Options Data Fetcher")
    print(f"=" * 60)
    print(f"Tickers: {len(tickers)}")
    print(f"Dates: {len(dates)} {'(previous trading day)' if dates == [None] else ''}")
    print(f"Total requests: {total_requests}")
    print(f"Estimated time: {est_time_min:.1f} minutes")
    print(f"Output directory: {output_dir}")
    print(f"=" * 60)

    if args.dry_run:
        print("\nDRY RUN - Tickers to fetch:")
        for t in tickers:
            print(f"  {t}")
        if dates != [None]:
            print(f"\nDates: {dates[0]} to {dates[-1]}")
        return

    # Fetch data
    success_count = 0
    error_count = 0
    errors = []

    for date in dates:
        date_str = date or "latest"
        print(f"\n--- Fetching for date: {date_str} ---")

        for i, ticker in enumerate(tickers, 1):
            print(f"[{i}/{len(tickers)}] {ticker}...", end=" ", flush=True)

            data = fetch_options_chain(ticker, date, api_key)

            if "error" in data:
                print(f"ERROR: {data['error'][:50]}")
                error_count += 1
                errors.append((ticker, date_str, data["error"]))
            else:
                parquet_path = save_options_data(data, ticker, date, output_dir)
                num_contracts = len(data.get("data", []))
                if parquet_path:
                    print(f"OK ({num_contracts} contracts) -> {parquet_path.name}")
                else:
                    print(f"OK (no contracts)")
                success_count += 1

            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)

    # Summary
    print(f"\n" + "=" * 60)
    print(f"COMPLETE")
    print(f"=" * 60)
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Output: {output_dir}")

    if errors:
        print(f"\nErrors encountered:")
        for ticker, date, err in errors[:10]:
            print(f"  {ticker} ({date}): {err[:60]}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")


if __name__ == "__main__":
    main()
