#!/usr/bin/env python3
"""
Single-Ticker Options Data Backfill Script

Downloads historical options data from Alpha Vantage for any ticker,
checking for existing data to avoid re-downloading.

Features:
- Checks multiple data sources (CSV files, parquet files) for existing data
- Only downloads missing dates
- Saves to data/options/<TICKER>/YYYY/MM/DD.parquet format
- Can merge all data into a single combined parquet file
- Progress tracking with ETA
- IPO-aware start dates for common tickers

Usage:
    python backfill_ticker_options.py NVDA                    # Check status only
    python backfill_ticker_options.py NVDA --fetch            # Fetch missing data
    python backfill_ticker_options.py NVDA --fetch --limit 50 # Fetch with daily limit
    python backfill_ticker_options.py NVDA --merge            # Merge all data to single parquet
    python backfill_ticker_options.py NVDA --start 2015-01-01 # Custom start date
"""

import argparse
import io
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

# Configuration
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"
PAUSE_S = 0.85  # Rate limit delay (~70 req/min for premium)
MAX_RETRY = 3

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "options"
OPTIONS_DATA_DIR = BASE_DIR / "options_data"

# IPO dates / earliest Alpha Vantage data availability
# Stocks with IPO before 2008-01-23 use 2008-01-23 as the effective start
IPO_DATES = {
    "MSFT": pd.Timestamp("2008-01-23"),
    "INTC": pd.Timestamp("2008-01-23"),
    "ORCL": pd.Timestamp("2008-01-23"),
    "AMZN": pd.Timestamp("2008-01-23"),
    "GOOG": pd.Timestamp("2008-01-23"),
    "GOOGL": pd.Timestamp("2008-01-23"),
    "NVDA": pd.Timestamp("2008-01-23"),
    "AMD": pd.Timestamp("2008-01-23"),
    "AAPL": pd.Timestamp("2008-01-23"),
    "NFLX": pd.Timestamp("2008-01-23"),
    "SMCI": pd.Timestamp("2008-01-23"),
    "TSM": pd.Timestamp("2008-01-23"),
    "AVGO": pd.Timestamp("2009-08-06"),
    "TSLA": pd.Timestamp("2010-06-29"),
    "META": pd.Timestamp("2012-05-18"),
    "SNOW": pd.Timestamp("2020-09-16"),
    "PLTR": pd.Timestamp("2020-09-30"),
    "ARM": pd.Timestamp("2023-09-14"),
    "CRWV": pd.Timestamp("2025-03-28"),
    "ADBE": pd.Timestamp("2008-01-23"),
    "CRM": pd.Timestamp("2008-01-23"),
    "NOW": pd.Timestamp("2012-06-29"),
}

# Ticker renames (for historical API queries)
TICKER_RENAMES = {
    "META": ("FB", pd.Timestamp("2022-06-09")),  # META was FB before this date
    "GOOGL": ("GOOG", pd.Timestamp("2014-04-03")),  # GOOGL split from GOOG
}


def get_api_symbol(ticker: str, day: pd.Timestamp) -> str:
    """Get the API symbol for a ticker on a given date (handles renames)."""
    if ticker in TICKER_RENAMES:
        old_symbol, rename_date = TICKER_RENAMES[ticker]
        if day < rename_date:
            return old_symbol
    return ticker


def get_trading_days(start: pd.Timestamp, end: pd.Timestamp) -> pd.DatetimeIndex:
    """Return NYSE trading days between start and end dates."""
    try:
        import pandas_market_calendars as mcal
        cal = mcal.get_calendar("XNYS")
        days = cal.valid_days(
            start_date=str(start.date()),
            end_date=str(end.date()),
            tz="America/New_York"
        )
        return days.tz_convert(None)
    except ImportError:
        # Fallback: weekdays minus federal holidays
        usb = CustomBusinessDay(calendar=USFederalHolidayCalendar())
        return pd.date_range(start, end, freq=usb)


def get_default_start_date(ticker: str) -> pd.Timestamp:
    """Get the default start date for a ticker based on IPO/data availability."""
    return IPO_DATES.get(ticker.upper(), pd.Timestamp("2008-01-23"))


def get_output_dir(ticker: str) -> Path:
    """Get the daily parquet output directory for a ticker."""
    return DATA_DIR / ticker.upper()


def get_combined_output_path(ticker: str) -> Path:
    """Get the combined parquet output path for a ticker."""
    return OPTIONS_DATA_DIR / f"{ticker.upper()}_options.parquet"


def get_legacy_dir(ticker: str) -> Path:
    """Get legacy data directory (for backwards compatibility with AMD)."""
    if ticker.upper() == "AMD":
        return OPTIONS_DATA_DIR / "amd_test"
    return OPTIONS_DATA_DIR / ticker.lower()


def get_existing_dates_from_parquet(ticker: str) -> set:
    """Get set of dates that already have parquet files."""
    existing = set()
    output_dir = get_output_dir(ticker)

    if not output_dir.exists():
        return existing

    for year_dir in output_dir.iterdir():
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue
        year = int(year_dir.name)

        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir() or not month_dir.name.isdigit():
                continue
            month = int(month_dir.name)

            for day_file in month_dir.glob("*.parquet"):
                day = int(day_file.stem)
                try:
                    existing.add(pd.Timestamp(year=year, month=month, day=day))
                except ValueError:
                    continue

    return existing


def get_existing_dates_from_legacy(ticker: str) -> set:
    """Get set of dates from legacy CSV/JSON files."""
    existing = set()
    legacy_dir = get_legacy_dir(ticker)

    if not legacy_dir.exists():
        return existing

    # Pattern matches TICKER_YYYY-MM-DD.csv or TICKER_YYYY-MM-DD.json
    date_pattern = re.compile(rf"{ticker.upper()}_(\d{{4}}-\d{{2}}-\d{{2}})\.(csv|json)", re.IGNORECASE)

    for f in legacy_dir.iterdir():
        match = date_pattern.match(f.name)
        if match:
            try:
                date_str = match.group(1)
                existing.add(pd.Timestamp(date_str))
            except ValueError:
                continue

    return existing


def get_existing_dates_from_combined(ticker: str) -> set:
    """Get set of dates from an existing combined parquet file."""
    existing = set()
    combined_path = get_combined_output_path(ticker)

    # Also check legacy AMD path
    if ticker.upper() == "AMD":
        legacy_combined = get_legacy_dir(ticker) / "AMD_options.parquet"
        if legacy_combined.exists():
            combined_path = legacy_combined

    if not combined_path.exists():
        return existing

    try:
        df = pd.read_parquet(combined_path)
        if "date" in df.columns:
            dates = pd.to_datetime(df["date"].unique())
            existing = set(dates)
    except Exception:
        pass

    return existing


def get_all_existing_dates(ticker: str) -> set:
    """Get all dates that have data from any source."""
    parquet_dates = get_existing_dates_from_parquet(ticker)
    legacy_dates = get_existing_dates_from_legacy(ticker)
    combined_dates = get_existing_dates_from_combined(ticker)
    return parquet_dates | legacy_dates | combined_dates


def get_missing_dates(ticker: str, start: pd.Timestamp, end: pd.Timestamp) -> list:
    """Get list of trading dates that are missing data."""
    all_trading_days = set(get_trading_days(start, end))
    existing_dates = get_all_existing_dates(ticker)
    missing = all_trading_days - existing_dates
    return sorted(missing)


def day_path(ticker: str, d: pd.Timestamp) -> Path:
    """Generate file path: data/options/<TICKER>/YYYY/MM/DD.parquet"""
    return get_output_dir(ticker) / f"{d.year:04d}" / f"{d.month:02d}" / f"{d.day:02d}.parquet"


def fetch_options_chain(ticker: str, day: pd.Timestamp) -> str | None:
    """
    Fetch option chain from Alpha Vantage.

    Returns:
        CSV text on success, None if no data, raises on error.
    """
    if not API_KEY:
        raise RuntimeError("ALPHAVANTAGE_API_KEY environment variable not set")

    api_symbol = get_api_symbol(ticker, day)

    params = {
        "function": "HISTORICAL_OPTIONS",
        "symbol": api_symbol,
        "date": day.strftime("%Y-%m-%d"),
        "datatype": "csv",
        "apikey": API_KEY,
    }

    r = requests.get(BASE_URL, params=params, timeout=60)

    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")

    ctype = r.headers.get("Content-Type", "").lower()
    text = r.text.strip()

    # JSON response = error or no data
    if "application/json" in ctype or text.startswith("{"):
        try:
            msg = r.json()
        except Exception:
            raise RuntimeError(f"Unexpected response: {text[:200]}")

        if "Note" in msg:
            raise RuntimeError("RATE_LIMIT: " + msg.get("Note", ""))

        if str(msg.get("message", "")).lower().startswith("no data"):
            return None

        raise RuntimeError(f"API error: {msg}")

    return text


def save_options_data(ticker: str, csv_text: str | None, day: pd.Timestamp) -> tuple[bool, str]:
    """Save options data to parquet file."""
    out_path = day_path(ticker, day)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if csv_text is None or len(csv_text.splitlines()) <= 1:
        # No data - save empty placeholder
        pd.DataFrame().to_parquet(out_path, compression="gzip", index=False)
        return True, "no data (holiday/no trading)"

    # Parse and save
    df = pd.read_csv(io.StringIO(csv_text))
    df.to_parquet(out_path, compression="gzip", index=False)
    return True, f"saved {len(df)} contracts"


def fetch_and_save(ticker: str, day: pd.Timestamp) -> tuple[bool, str]:
    """Fetch and save data for a single day with retry logic."""
    for attempt in range(1, MAX_RETRY + 1):
        try:
            csv_text = fetch_options_chain(ticker, day)
            return save_options_data(ticker, csv_text, day)

        except Exception as e:
            msg = str(e)

            if "RATE_LIMIT:" in msg and attempt < MAX_RETRY:
                sleep_s = PAUSE_S * (attempt + 1)
                print(f"  Rate limit, retry {attempt}/{MAX_RETRY} in {sleep_s:.1f}s...")
                time.sleep(sleep_s)
                continue

            if "RATE_LIMIT:" in msg:
                return False, "rate limit exceeded"

            return False, f"error: {msg[:80]}"

    return False, "max retries exceeded"


def format_duration(seconds: float) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"


def print_status(ticker: str, start: pd.Timestamp, end: pd.Timestamp) -> list:
    """Print current data status."""
    print(f"\n{'='*60}")
    print(f"{ticker} Options Data Status")
    print(f"{'='*60}")

    all_days = get_trading_days(start, end)
    parquet_dates = get_existing_dates_from_parquet(ticker)
    legacy_dates = get_existing_dates_from_legacy(ticker)
    combined_dates = get_existing_dates_from_combined(ticker)
    all_existing = parquet_dates | legacy_dates | combined_dates
    missing = get_missing_dates(ticker, start, end)

    print(f"Date range:         {start.date()} to {end.date()}")
    print(f"Total trading days: {len(all_days)}")
    print(f"")
    print(f"Existing data:")
    print(f"  Daily parquet:    {len(parquet_dates)}")
    print(f"  Legacy CSV/JSON:  {len(legacy_dates)}")
    print(f"  Combined parquet: {len(combined_dates)}")
    print(f"  Total unique:     {len(all_existing)}")
    print(f"")
    print(f"Missing dates:      {len(missing)}")

    if missing:
        print(f"  Oldest missing:   {missing[0].date()}")
        print(f"  Newest missing:   {missing[-1].date()}")

        # Estimate time to complete
        est_time = len(missing) * PAUSE_S
        print(f"  Est. fetch time:  {format_duration(est_time)}")

    print(f"{'='*60}\n")

    return missing


def run_backfill(ticker: str, start: pd.Timestamp, end: pd.Timestamp, limit: int):
    """Run the backfill process."""
    missing = print_status(ticker, start, end)

    if not missing:
        print("All data already downloaded!")
        return

    if not API_KEY:
        print("ERROR: Set ALPHAVANTAGE_API_KEY environment variable to fetch data")
        sys.exit(1)

    print(f"Fetching up to {limit} missing dates...\n")

    fetched = 0
    success = 0
    failed = 0

    # Fetch oldest first for chronological backfill
    for day in missing[:limit]:
        fetched += 1

        print(f"[{fetched}/{min(limit, len(missing))}] {day.date()} ", end="", flush=True)

        ok, msg = fetch_and_save(ticker, day)

        if ok:
            success += 1
            print(f"OK - {msg}")
        else:
            failed += 1
            print(f"FAIL - {msg}")

        # Rate limit (except last)
        if fetched < limit and fetched < len(missing):
            time.sleep(PAUSE_S)

    # Summary
    print(f"\n{'='*60}")
    print("Fetch Summary")
    print(f"{'='*60}")
    print(f"Attempted: {fetched}")
    print(f"Success:   {success}")
    print(f"Failed:    {failed}")
    print(f"Remaining: {len(missing) - fetched}")
    print(f"{'='*60}\n")


def merge_all_data(ticker: str, start: pd.Timestamp, end: pd.Timestamp, output_path: Path):
    """Merge all options data into a single parquet file."""
    print(f"\n{'='*60}")
    print(f"Merging {ticker} Options Data")
    print(f"{'='*60}")

    all_dfs = []

    # Load existing combined parquet first (as the base dataset)
    existing_combined = output_path
    if not existing_combined.exists() and ticker.upper() == "AMD":
        existing_combined = get_legacy_dir(ticker) / "AMD_options.parquet"
    if existing_combined.exists():
        try:
            df_existing = pd.read_parquet(existing_combined)
            if not df_existing.empty:
                df_existing["date"] = pd.to_datetime(df_existing["date"])
                all_dfs.append(df_existing)
                print(f"Loaded existing combined: {len(df_existing):,} rows ({df_existing['date'].min().date()} to {df_existing['date'].max().date()})")
        except Exception as e:
            print(f"  Warning: Could not read existing combined parquet: {e}")

    # Load legacy CSV files
    legacy_dir = get_legacy_dir(ticker)
    if legacy_dir.exists():
        csv_pattern = re.compile(rf"{ticker.upper()}_(\d{{4}}-\d{{2}}-\d{{2}})\.csv", re.IGNORECASE)
        csv_files = sorted(f for f in legacy_dir.iterdir() if csv_pattern.match(f.name))
        print(f"Found {len(csv_files)} legacy CSV files")

        for f in csv_files:
            try:
                match = csv_pattern.match(f.name)
                if match:
                    date_str = match.group(1)
                    df = pd.read_csv(f)
                    if not df.empty:
                        df["date"] = date_str
                        all_dfs.append(df)
            except Exception as e:
                print(f"  Warning: Could not read {f.name}: {e}")

    # Load daily parquet files
    output_dir = get_output_dir(ticker)
    parquet_count = 0
    if output_dir.exists():
        for pq_file in output_dir.rglob("*.parquet"):
            try:
                df = pd.read_parquet(pq_file)
                if not df.empty:
                    # Extract date from path if not in data
                    if "date" not in df.columns:
                        # Path: .../YYYY/MM/DD.parquet
                        parts = pq_file.parts
                        year, month, day = parts[-3], parts[-2], pq_file.stem
                        df["date"] = f"{year}-{month}-{day}"
                    all_dfs.append(df)
                    parquet_count += 1
            except Exception as e:
                print(f"  Warning: Could not read {pq_file}: {e}")

    print(f"Found {parquet_count} daily parquet files")

    if not all_dfs:
        print("No data found to merge!")
        return

    # Combine all data
    print("Combining data...")
    combined = pd.concat(all_dfs, ignore_index=True)

    # Standardize column names
    col_renames = {
        "contractID": "contractID",
        "contract_id": "contractID",
        "implied_volatility": "implied_volatility",
        "impliedVolatility": "implied_volatility",
        "open_interest": "open_interest",
        "openInterest": "open_interest",
    }
    combined = combined.rename(columns=col_renames)

    # Clean numeric columns - replace '-' and other non-numeric values with NaN
    numeric_columns = [
        "strike", "last", "mark", "bid", "bid_size", "ask", "ask_size",
        "volume", "open_interest", "implied_volatility", "delta", "gamma",
        "theta", "vega", "rho"
    ]
    for col in numeric_columns:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce")

    # Remove duplicates (same contract on same date)
    if "contractID" in combined.columns and "date" in combined.columns:
        before = len(combined)
        combined = combined.drop_duplicates(subset=["contractID", "date"], keep="last")
        removed = before - len(combined)
        if removed > 0:
            print(f"Removed {removed} duplicates")

    # Sort by date
    if "date" in combined.columns:
        combined = combined.sort_values("date")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(output_path, compression="gzip", index=False)

    print(f"\nSaved combined data:")
    print(f"  Path: {output_path}")
    print(f"  Rows: {len(combined):,}")
    if "date" in combined.columns:
        print(f"  Date range: {combined['date'].min()} to {combined['date'].max()}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Single-Ticker Options Data Backfill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backfill_ticker_options.py NVDA                     # Check status
  python backfill_ticker_options.py NVDA --fetch             # Fetch missing data
  python backfill_ticker_options.py NVDA --fetch --limit 100 # Fetch with limit
  python backfill_ticker_options.py NVDA --merge             # Merge to single file
  python backfill_ticker_options.py NVDA --start 2015-01-01  # Custom start date
  python backfill_ticker_options.py AMD --fetch --merge      # Fetch then merge
        """
    )

    parser.add_argument(
        "ticker",
        type=str,
        help="Stock ticker symbol (e.g., NVDA, AMD, MSFT)"
    )

    parser.add_argument(
        "--start",
        type=str,
        default=None,
        help="Start date YYYY-MM-DD (default: based on ticker IPO/data availability)"
    )

    parser.add_argument(
        "--end",
        type=str,
        default=str(date.today()),
        help="End date YYYY-MM-DD (default: today)"
    )

    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch missing data (default: status check only)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Max requests per run (default: 25, increase for premium API)"
    )

    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge all data into single parquet file"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for merged file (default: options_data/<TICKER>_options.parquet)"
    )

    args = parser.parse_args()

    ticker = args.ticker.upper()

    # Determine start date
    if args.start:
        start = pd.Timestamp(args.start)
    else:
        start = get_default_start_date(ticker)

    end = pd.Timestamp(args.end)

    # Determine output path for merge
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = get_combined_output_path(ticker)

    # Run requested operations
    if args.fetch:
        run_backfill(ticker, start, end, args.limit)

    if args.merge:
        merge_all_data(ticker, start, end, output_path)

    if not args.fetch and not args.merge:
        # Status check only
        print_status(ticker, start, end)
        print("Use --fetch to download missing data")
        print("Use --merge to combine all data into single parquet")


if __name__ == "__main__":
    main()
