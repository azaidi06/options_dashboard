#!/usr/bin/env python3
"""
Test script: Fetch AMD historical options data from 2018-01-01 to present.
Outputs diagnostics on data volume and storage.
Stores data in Parquet format with gzip compression for efficient storage.
"""

import os
import sys
import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("Note: Install tqdm for better progress bars: pip install tqdm")

# Configuration
ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"
OUTPUT_DIR = Path(__file__).parent / "options_data" / "amd_test"
RATE_LIMIT_DELAY = 0.85
TICKER = "AMD"
START_DATE = "2018-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")


def get_api_key():
    key = os.environ.get("ALPHAVANTAGE_API_KEY")
    if not key:
        print("ERROR: ALPHAVANTAGE_API_KEY environment variable not set")
        sys.exit(1)
    return key


def get_trading_days(start_date: str, end_date: str) -> list:
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            days.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return days


def fetch_options_chain(ticker: str, date: str, api_key: str) -> dict:
    params = {
        "function": "HISTORICAL_OPTIONS",
        "symbol": ticker,
        "date": date,
        "apikey": api_key,
    }
    try:
        response = requests.get(ALPHAVANTAGE_BASE_URL, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data:
            return {"error": data["Error Message"]}
        if "Note" in data:
            return {"error": f"Rate limit: {data['Note']}"}
        if "Information" in data:
            return {"error": data["Information"]}
        return data
    except requests.RequestException as e:
        return {"error": str(e)}


def format_bytes(b):
    """Format bytes to human readable."""
    if b < 1024:
        return f"{b}B"
    elif b < 1024 * 1024:
        return f"{b/1024:.1f}KB"
    elif b < 1024 * 1024 * 1024:
        return f"{b/1024/1024:.2f}MB"
    else:
        return f"{b/1024/1024/1024:.2f}GB"


def format_time(seconds):
    """Format seconds to human readable."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}min"
    else:
        return f"{seconds/3600:.1f}hr"


def main():
    api_key = get_api_key()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    trading_days = get_trading_days(START_DATE, END_DATE)
    total_days = len(trading_days)
    est_time_min = (total_days * RATE_LIMIT_DELAY) / 60

    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " AMD OPTIONS DATA TEST ".center(58) + "║")
    print("╠" + "═" * 58 + "╣")
    print(f"║  Ticker: {TICKER:<47} ║")
    print(f"║  Date range: {START_DATE} to {END_DATE:<24} ║")
    print(f"║  Trading days: {total_days:<42} ║")
    print(f"║  Estimated time: {est_time_min:.0f} minutes{' ' * 34}║")
    print(f"║  Output: {str(OUTPUT_DIR):<47} ║")
    print("╚" + "═" * 58 + "╝")
    print()

    # Running stats
    stats = {
        "ticker": TICKER,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "total_trading_days": total_days,
        "successful_fetches": 0,
        "failed_fetches": 0,
        "total_contracts": 0,
        "total_parquet_bytes": 0,
        "dates_with_data": [],
        "dates_without_data": [],
        "errors": [],
        "contracts_per_day": [],
    }

    # Collect all data for single Parquet file
    all_data = []

    start_time = time.time()

    # Progress bar setup
    if HAS_TQDM:
        pbar = tqdm(
            trading_days,
            desc="Fetching",
            unit="day",
            ncols=100,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
        )
    else:
        pbar = trading_days

    for i, date in enumerate(pbar):
        # Fetch data
        data = fetch_options_chain(TICKER, date, api_key)

        if "error" in data:
            stats["failed_fetches"] += 1
            stats["errors"].append({"date": date, "error": data["error"]})
            stats["dates_without_data"].append(date)
            status = "ERR"
            contracts = 0
        else:
            num_contracts = len(data.get("data", []))

            # Collect data for Parquet (add date column)
            if num_contracts > 0:
                for record in data["data"]:
                    record["date"] = date
                all_data.extend(data["data"])

            stats["successful_fetches"] += 1
            stats["total_contracts"] += num_contracts
            stats["dates_with_data"].append(date)
            stats["contracts_per_day"].append({
                "date": date,
                "contracts": num_contracts,
            })
            status = "OK"
            contracts = num_contracts

        # Update progress bar description with running stats
        if HAS_TQDM:
            pbar.set_postfix_str(
                f"✓{stats['successful_fetches']} ✗{stats['failed_fetches']} | "
                f"{stats['total_contracts']:,} contracts"
            )
        else:
            # Fallback without tqdm
            elapsed = time.time() - start_time
            if i > 0:
                eta = (elapsed / (i + 1)) * (total_days - i - 1)
            else:
                eta = 0
            print(
                f"[{i+1:4}/{total_days}] {date} {status:3} | "
                f"Contracts: {stats['total_contracts']:>7,} | "
                f"ETA: {format_time(eta)}"
            )

        time.sleep(RATE_LIMIT_DELAY)

    if HAS_TQDM:
        pbar.close()

    elapsed_total = time.time() - start_time

    # Write all data to single Parquet file with gzip compression
    parquet_path = OUTPUT_DIR / f"{TICKER}_options.parquet"
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_parquet(parquet_path, compression="gzip", index=False)
        stats["total_parquet_bytes"] = parquet_path.stat().st_size
        print(f"\nWrote {len(df):,} records to {parquet_path}")
    else:
        stats["total_parquet_bytes"] = 0
        print("\nNo data to write.")

    # Final stats
    stats["elapsed_seconds"] = elapsed_total
    stats["elapsed_minutes"] = elapsed_total / 60
    stats["total_bytes"] = stats["total_parquet_bytes"]
    stats["total_mb"] = stats["total_bytes"] / (1024 * 1024)
    stats["avg_contracts_per_day"] = stats["total_contracts"] / max(stats["successful_fetches"], 1)
    stats["avg_parquet_kb_per_day"] = (stats["total_parquet_bytes"] / 1024) / max(stats["successful_fetches"], 1)

    # Save diagnostics
    diag_path = OUTPUT_DIR / "diagnostics.json"
    with open(diag_path, "w") as f:
        json.dump(stats, f, indent=2)

    # Print summary
    print()
    total_contracts_str = f"{stats['total_contracts']:,}"
    avg_contracts_str = f"{stats['avg_contracts_per_day']:.0f}"

    print("╔" + "═" * 58 + "╗")
    print("║" + " DIAGNOSTICS SUMMARY ".center(58) + "║")
    print("╠" + "═" * 58 + "╣")
    print(f"║  Time elapsed: {format_time(elapsed_total):<42} ║")
    print(f"║  Successful: {stats['successful_fetches']:<44} ║")
    print(f"║  Failed: {stats['failed_fetches']:<48} ║")
    print("╠" + "═" * 58 + "╣")
    print(f"║  Total contracts: {total_contracts_str:<38} ║")
    print(f"║  Avg contracts/day: {avg_contracts_str:<36} ║")
    print("╠" + "═" * 58 + "╣")
    print(f"║  Parquet size (gzip): {format_bytes(stats['total_parquet_bytes']):<35} ║")
    avg_day_bytes = int(stats['avg_parquet_kb_per_day'] * 1024)
    print(f"║  Avg/day: {format_bytes(avg_day_bytes):<47} ║")
    print("╚" + "═" * 58 + "╝")

    # Extrapolation
    print()
    print("┌" + "─" * 58 + "┐")
    print("│" + " EXTRAPOLATION ".center(58) + "│")
    print("├" + "─" * 58 + "┤")
    full_days = len(get_trading_days("2010-01-01", END_DATE))
    ratio = full_days / max(total_days, 1)
    est_full_time = stats["elapsed_minutes"] * ratio
    est_full_size = stats["total_mb"] * ratio

    print(f"│  Full AMD (2010-now): ~{full_days} days{' ' * 28} │")
    print(f"│    Time: {format_time(est_full_time * 60):>10}{' ' * 37} │")
    print(f"│    Storage: {format_bytes(int(est_full_size * 1024 * 1024)):>10}{' ' * 34} │")
    print("├" + "─" * 58 + "┤")
    print(f"│  All 69 tickers (2010-now):{' ' * 30} │")
    print(f"│    Time: {format_time(est_full_time * 69 * 60):>10}{' ' * 37} │")
    print(f"│    Storage: {format_bytes(int(est_full_size * 69 * 1024 * 1024)):>10}{' ' * 34} │")
    print("└" + "─" * 58 + "┘")
    print()
    print(f"Diagnostics saved to: {diag_path}")
    print()


if __name__ == "__main__":
    main()
