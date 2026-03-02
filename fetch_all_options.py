#!/usr/bin/env python3
"""
Batch Options Data Fetcher

Downloads historical options data for multiple tickers using backfill_ticker_options.py.
Runs each ticker sequentially: fetch all missing days, then merge.

Usage:
    python fetch_all_options.py                     # Fetch all tickers (full run)
    python fetch_all_options.py --status-only       # Show estimates without fetching
    python fetch_all_options.py --limit 100         # Cap requests per ticker
    python fetch_all_options.py --tickers AAPL,MSFT # Specific tickers only
"""

import argparse
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data" / "options"
TICKERS = sorted(d.name for d in DATA_DIR.iterdir() if d.is_dir()) if DATA_DIR.is_dir() else []

START_DATE = "2010-01-01"

# Import IPO dates from the backfill script to clamp start dates
IPO_DATES = {
    "MSFT": "2008-01-23",
    "INTC": "2008-01-23",
    "ORCL": "2008-01-23",
    "AMZN": "2008-01-23",
    "GOOG": "2008-01-23",
    "GOOGL": "2008-01-23",
    "NVDA": "2008-01-23",
    "AMD": "2008-01-23",
    "AAPL": "2008-01-23",
    "NFLX": "2008-01-23",
    "SMCI": "2008-01-23",
    "TSM": "2008-01-23",
    "AVGO": "2009-08-06",
    "TSLA": "2010-06-29",
    "META": "2012-05-18",
    "SNOW": "2020-09-16",
    "PLTR": "2020-09-30",
    "ARM": "2023-09-14",
    "CRWV": "2025-03-28",
    "ADBE": "2008-01-23",
    "CRM": "2008-01-23",
    "NOW": "2012-06-29",
}


def effective_start(ticker: str, user_start: str) -> str:
    """Return the later of user_start and the ticker's IPO/data-availability date."""
    ipo = IPO_DATES.get(ticker, "2008-01-23")
    return max(user_start, ipo)


def run_ticker(ticker: str, start: str, end: str, limit: int | None, merge: bool) -> float:
    """Run backfill for a single ticker. Returns elapsed seconds."""
    t0 = time.time()

    actual_start = effective_start(ticker, start)

    cmd = [
        sys.executable, "backfill_ticker_options.py",
        ticker,
        "--start", actual_start,
        "--end", end,
        "--fetch",
    ]
    if limit is not None:
        cmd.extend(["--limit", str(limit)])
    else:
        cmd.extend(["--limit", "999999"])

    print(f"\n{'='*70}")
    print(f"  FETCHING: {ticker}  (start={actual_start})")
    print(f"{'='*70}")

    subprocess.run(cmd, cwd="/home/azaidi/Desktop/nonsense/fin")

    if merge:
        print(f"\n  Merging {ticker}...")
        merge_cmd = [
            sys.executable, "backfill_ticker_options.py",
            ticker,
            "--start", actual_start,
            "--end", end,
            "--merge",
        ]
        subprocess.run(merge_cmd, cwd="/home/azaidi/Desktop/nonsense/fin")

    elapsed = time.time() - t0
    return elapsed


def run_status(ticker: str, start: str, end: str) -> None:
    """Run status check for a single ticker."""
    actual_start = effective_start(ticker, start)
    cmd = [
        sys.executable, "backfill_ticker_options.py",
        ticker,
        "--start", actual_start,
        "--end", end,
    ]
    subprocess.run(cmd, cwd="/home/azaidi/Desktop/nonsense/fin")


def main():
    parser = argparse.ArgumentParser(description="Batch options data fetcher")
    parser.add_argument(
        "--tickers", type=str, default=",".join(TICKERS),
        help=f"Comma-separated tickers (default: {','.join(TICKERS)})"
    )
    parser.add_argument(
        "--start", type=str, default=START_DATE,
        help=f"Start date (default: {START_DATE})"
    )
    parser.add_argument(
        "--end", type=str, default=str(date.today()),
        help="End date (default: today)"
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Max requests per ticker (default: unlimited)"
    )
    parser.add_argument(
        "--status-only", action="store_true",
        help="Show status and time estimates without fetching"
    )
    parser.add_argument(
        "--no-merge", action="store_true",
        help="Skip merge step after fetching"
    )
    args = parser.parse_args()

    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]

    if args.status_only:
        print(f"\n{'#'*70}")
        print(f"  OPTIONS DATA STATUS FOR {len(tickers)} TICKERS")
        print(f"{'#'*70}")
        for ticker in tickers:
            run_status(ticker, args.start, args.end)
        return

    print(f"\n{'#'*70}")
    print(f"  BATCH OPTIONS FETCH: {len(tickers)} tickers")
    print(f"  Start date: {args.start} (clamped to IPO dates per ticker)")
    print(f"  Limit per ticker: {'unlimited' if args.limit is None else args.limit}")
    print(f"{'#'*70}")

    total_start = time.time()
    results = {}

    for i, ticker in enumerate(tickers, 1):
        print(f"\n{'*'*70}")
        print(f"  TICKER {i}/{len(tickers)}: {ticker}")
        print(f"{'*'*70}")

        elapsed = run_ticker(
            ticker, args.start, args.end,
            limit=args.limit,
            merge=not args.no_merge,
        )
        results[ticker] = elapsed

        mins = elapsed / 60
        print(f"\n  {ticker} completed in {mins:.1f} min")

    total_elapsed = time.time() - total_start

    print(f"\n{'#'*70}")
    print(f"  BATCH COMPLETE")
    print(f"{'#'*70}")
    print(f"  Total time: {total_elapsed/3600:.1f} hours ({total_elapsed/60:.0f} min)")
    print(f"\n  Per-ticker times:")
    for ticker, elapsed in results.items():
        print(f"    {ticker:6s}: {elapsed/60:.1f} min")
    print(f"{'#'*70}\n")


if __name__ == "__main__":
    main()
