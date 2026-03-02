#!/usr/bin/env python3
"""
AMD Options Data Backfill Script

Downloads historical AMD options data from Alpha Vantage, checking for existing
data to avoid re-downloading.

Features:
- Checks multiple data sources (CSV files, parquet files) for existing data
- Only downloads missing dates
- Saves to data/options/AMD/YYYY/MM/DD.parquet format
- Can merge all data into a single combined parquet file
- Progress tracking with ETA

Usage:
    python backfill_amd_options.py                    # Check status only
    python backfill_amd_options.py --fetch            # Fetch missing data
    python backfill_amd_options.py --fetch --limit 50 # Fetch with daily limit
    python backfill_amd_options.py --merge            # Merge all data to single parquet
    python backfill_amd_options.py --start 2010-01-01 # Custom start date
"""

import argparse
import io
import os
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import requests
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

# Configuration
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"
PAUSE_S = 0.85  # Rate limit delay
MAX_RETRY = 3

# Data directories
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "data" / "options" / "AMD"
LEGACY_DIR = BASE_DIR / "options_data" / "amd_test"
COMBINED_OUTPUT = BASE_DIR / "options_data" / "amd_test" / "AMD_options.parquet"

# AMD-specific settings
# Alpha Vantage historical options data starts around 2008, but AMD options
# liquidity was limited before ~2010
AMD_START_DATE = pd.Timestamp("2010-01-01")
AMD_END_DATE = pd.Timestamp(date.today())


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


def get_existing_dates_from_parquet(output_dir: Path) -> set:
    """
    Get set of dates that already have parquet files.
    Looks in data/options/AMD/YYYY/MM/DD.parquet structure.
    """
    existing = set()

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


def get_existing_dates_from_legacy(legacy_dir: Path) -> set:
    """
    Get set of dates from legacy CSV/JSON files.
    Looks for AMD_YYYY-MM-DD.csv or AMD_YYYY-MM-DD.json files.
    """
    existing = set()

    if not legacy_dir.exists():
        return existing

    date_pattern = re.compile(r"AMD_(\d{4}-\d{2}-\d{2})\.(csv|json)")

    for f in legacy_dir.iterdir():
        match = date_pattern.match(f.name)
        if match:
            try:
                date_str = match.group(1)
                existing.add(pd.Timestamp(date_str))
            except ValueError:
                continue

    return existing


def get_all_existing_dates() -> set:
    """Get all dates that have data from any source."""
    parquet_dates = get_existing_dates_from_parquet(OUTPUT_DIR)
    legacy_dates = get_existing_dates_from_legacy(LEGACY_DIR)
    return parquet_dates | legacy_dates


def get_missing_dates(start: pd.Timestamp, end: pd.Timestamp) -> list:
    """
    Get list of trading dates that are missing data.
    Returns sorted list (oldest first for backfill).
    """
    all_trading_days = set(get_trading_days(start, end))
    existing_dates = get_all_existing_dates()
    missing = all_trading_days - existing_dates
    return sorted(missing)


def day_path(d: pd.Timestamp) -> Path:
    """Generate file path: data/options/AMD/YYYY/MM/DD.parquet"""
    return OUTPUT_DIR / f"{d.year:04d}" / f"{d.month:02d}" / f"{d.day:02d}.parquet"


def fetch_options_chain(day: pd.Timestamp) -> str | None:
    """
    Fetch AMD option chain from Alpha Vantage.

    Returns:
        CSV text on success, None if no data, raises on error.
    """
    if not API_KEY:
        raise RuntimeError("ALPHAVANTAGE_API_KEY environment variable not set")

    params = {
        "function": "HISTORICAL_OPTIONS",
        "symbol": "AMD",
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


def save_options_data(csv_text: str | None, day: pd.Timestamp) -> tuple[bool, str]:
    """
    Save options data to parquet file.

    Returns:
        (success, message) tuple
    """
    out_path = day_path(day)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if csv_text is None or len(csv_text.splitlines()) <= 1:
        # No data - save empty placeholder
        pd.DataFrame().to_parquet(out_path, compression="gzip", index=False)
        return True, "no data (holiday/no trading)"

    # Parse and save
    df = pd.read_csv(io.StringIO(csv_text))

    # API already includes 'date' column, no need to add it

    df.to_parquet(out_path, compression="gzip", index=False)
    return True, f"saved {len(df)} contracts"


def fetch_and_save(day: pd.Timestamp) -> tuple[bool, str]:
    """
    Fetch and save data for a single day with retry logic.
    """
    for attempt in range(1, MAX_RETRY + 1):
        try:
            csv_text = fetch_options_chain(day)
            return save_options_data(csv_text, day)

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


def print_status(start: pd.Timestamp, end: pd.Timestamp):
    """Print current data status."""
    print(f"\n{'='*60}")
    print("AMD Options Data Status")
    print(f"{'='*60}")

    all_days = get_trading_days(start, end)
    parquet_dates = get_existing_dates_from_parquet(OUTPUT_DIR)
    legacy_dates = get_existing_dates_from_legacy(LEGACY_DIR)
    all_existing = parquet_dates | legacy_dates
    missing = get_missing_dates(start, end)

    print(f"Date range:        {start.date()} to {end.date()}")
    print(f"Total trading days: {len(all_days)}")
    print(f"")
    print(f"Existing data:")
    print(f"  Parquet files:   {len(parquet_dates)}")
    print(f"  Legacy CSV/JSON: {len(legacy_dates)}")
    print(f"  Total unique:    {len(all_existing)}")
    print(f"")
    print(f"Missing dates:     {len(missing)}")

    if missing:
        print(f"  Oldest missing:  {missing[0].date()}")
        print(f"  Newest missing:  {missing[-1].date()}")

        # Estimate time to complete
        est_time = len(missing) * PAUSE_S
        print(f"  Est. fetch time: {format_duration(est_time)}")

    print(f"{'='*60}\n")

    return missing


def run_backfill(start: pd.Timestamp, end: pd.Timestamp, limit: int):
    """Run the backfill process."""
    missing = print_status(start, end)

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
        remaining = len(missing) - fetched

        print(f"[{fetched}/{min(limit, len(missing))}] {day.date()} ", end="", flush=True)

        ok, msg = fetch_and_save(day)

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


def merge_all_data(start: pd.Timestamp, end: pd.Timestamp, output_path: Path):
    """
    Merge all AMD options data into a single parquet file.
    Combines both legacy CSV files and new parquet files.
    """
    print(f"\n{'='*60}")
    print("Merging AMD Options Data")
    print(f"{'='*60}")

    all_dfs = []

    # Load legacy CSV files
    if LEGACY_DIR.exists():
        csv_files = sorted(LEGACY_DIR.glob("AMD_*.csv"))
        print(f"Found {len(csv_files)} legacy CSV files")

        for f in csv_files:
            try:
                # Extract date from filename
                match = re.search(r"AMD_(\d{4}-\d{2}-\d{2})\.csv", f.name)
                if match:
                    date_str = match.group(1)
                    df = pd.read_csv(f)
                    if not df.empty:
                        df["date"] = date_str
                        all_dfs.append(df)
            except Exception as e:
                print(f"  Warning: Could not read {f.name}: {e}")

    # Load parquet files
    parquet_count = 0
    if OUTPUT_DIR.exists():
        for pq_file in OUTPUT_DIR.rglob("*.parquet"):
            try:
                df = pd.read_parquet(pq_file)
                if not df.empty:
                    all_dfs.append(df)
                    parquet_count += 1
            except Exception as e:
                print(f"  Warning: Could not read {pq_file}: {e}")

    print(f"Found {parquet_count} parquet files")

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

    # Remove duplicates (same contract on same date)
    if "contractID" in combined.columns and "date" in combined.columns:
        before = len(combined)
        combined = combined.drop_duplicates(subset=["contractID", "date"], keep="last")
        print(f"Removed {before - len(combined)} duplicates")

    # Sort by date
    if "date" in combined.columns:
        combined = combined.sort_values("date")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(output_path, compression="gzip", index=False)

    print(f"\nSaved combined data:")
    print(f"  Path: {output_path}")
    print(f"  Rows: {len(combined):,}")
    print(f"  Date range: {combined['date'].min()} to {combined['date'].max()}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="AMD Options Data Backfill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--start",
        type=str,
        default=str(AMD_START_DATE.date()),
        help=f"Start date YYYY-MM-DD (default: {AMD_START_DATE.date()})"
    )

    parser.add_argument(
        "--end",
        type=str,
        default=str(date.today()),
        help=f"End date YYYY-MM-DD (default: today)"
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
        help="Max requests per run (default: 25)"
    )

    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge all data into single parquet file"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=str(COMBINED_OUTPUT),
        help=f"Output path for merged file (default: {COMBINED_OUTPUT})"
    )

    args = parser.parse_args()

    start = pd.Timestamp(args.start)
    end = pd.Timestamp(args.end)

    if args.merge:
        merge_all_data(start, end, Path(args.output))
    elif args.fetch:
        run_backfill(start, end, args.limit)
    else:
        # Status check only
        print_status(start, end)
        print("Use --fetch to download missing data")
        print("Use --merge to combine all data into single parquet")


if __name__ == "__main__":
    main()
