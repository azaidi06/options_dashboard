"""Daily options update — slim variant.

Replaces the cron path that called ``backfill_ticker_options.py --fetch --merge``.
The old script's ``print_status()`` step walked every per-day parquet
into memory, which OOMed the 1.9 GB box on mega-cap tickers with 4000+
files. This version:

1.  Reads the latest date already covered by the *consolidated* parquet
    via pyarrow column statistics — single seek, no row scan.
2.  Fetches each missing trading day via ``fetch_and_save`` directly.
    One AV call + one small per-day parquet per loop iteration.
3.  Streaming-appends the new days onto the consolidated parquet using
    ``pyarrow.parquet.ParquetWriter``: reads the existing file in
    20K-row batches, never holding more than a few MB at once.

Peak memory per ticker is roughly one batch (~5 MB) regardless of how
big the consolidated file is.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

# backfill_ticker_options.py lives next to this file; reuse its fetcher.
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from backfill_ticker_options import fetch_and_save, day_path, PAUSE_S  # noqa: E402

US_BDAY = CustomBusinessDay(calendar=USFederalHolidayCalendar())
DATA_DIR = ROOT / "data" / "options"
CONSOLIDATED_DIR = ROOT / "options_data"
APPEND_BATCH = 20_000  # rows per streaming batch
LIMIT_PER_TICKER = 30  # safety cap on trading days fetched per run


def consolidated_max_date(consolidated_path: Path) -> pd.Timestamp | None:
    """Return the max date in a consolidated parquet. Cheap path: read it from
    column statistics. Fallback path (when stats are absent from older writes):
    project just the date column and take its max — still way cheaper than
    loading the whole file."""
    if not consolidated_path.exists():
        return None
    pf = pq.ParquetFile(consolidated_path)
    date_idx = _col_index(pf.schema_arrow, "date")
    max_ts: pd.Timestamp | None = None
    needs_scan = False
    for rg in range(pf.num_row_groups):
        stats = pf.metadata.row_group(rg).column(date_idx).statistics
        if stats is None or stats.max is None:
            needs_scan = True
            break
        rg_ts = pd.Timestamp(stats.max)
        if max_ts is None or rg_ts > max_ts:
            max_ts = rg_ts
    if needs_scan:
        # Project just the date column; pyarrow streams it.
        t = pf.read(columns=["date"])
        scanned_max = pd.Timestamp(t.column("date").to_pandas().max())
        if max_ts is None or scanned_max > max_ts:
            max_ts = scanned_max
    return max_ts


def _col_index(schema: pa.Schema, name: str) -> int:
    for i, f in enumerate(schema):
        if f.name == name:
            return i
    raise KeyError(name)


def coerce_to_consolidated_schema(df: pd.DataFrame, schema: pa.Schema) -> pa.Table:
    """Per-day parquets store date/expiration as strings; consolidated wants
    timestamp[ns]. Coerce and project onto the consolidated schema."""
    for col in ("date", "expiration"):
        if col in df.columns and df[col].dtype == object:
            df[col] = pd.to_datetime(df[col])
    # Drop columns not in target schema, add missing as null
    target_cols = [f.name for f in schema]
    for c in target_cols:
        if c not in df.columns:
            df[c] = None
    df = df[target_cols]
    return pa.Table.from_pandas(df, schema=schema, preserve_index=False)


def streaming_append(consolidated_path: Path, new_day_paths: list[Path]) -> int:
    """Append new per-day parquets onto a consolidated parquet without
    loading the existing file into memory. Returns rows appended."""
    if not new_day_paths:
        return 0

    tmp_path = consolidated_path.with_suffix(consolidated_path.suffix + ".tmp")
    appended = 0

    if consolidated_path.exists():
        existing = pq.ParquetFile(consolidated_path)
        schema = existing.schema_arrow
        with pq.ParquetWriter(tmp_path, schema, compression="snappy", write_statistics=True) as writer:
            for batch in existing.iter_batches(batch_size=APPEND_BATCH):
                writer.write_table(pa.Table.from_batches([batch]))
            for day_path_ in new_day_paths:
                df = pd.read_parquet(day_path_)
                table = coerce_to_consolidated_schema(df, schema)
                writer.write_table(table)
                appended += table.num_rows
    else:
        # No consolidated file yet: derive schema from first per-day file,
        # promote date/expiration to timestamp[ns] so future appends match.
        first = pd.read_parquet(new_day_paths[0])
        for col in ("date", "expiration"):
            if col in first.columns and first[col].dtype == object:
                first[col] = pd.to_datetime(first[col])
        first_table = pa.Table.from_pandas(first, preserve_index=False)
        schema = first_table.schema
        with pq.ParquetWriter(tmp_path, schema, compression="snappy", write_statistics=True) as writer:
            writer.write_table(first_table)
            appended += first_table.num_rows
            for day_path_ in new_day_paths[1:]:
                df = pd.read_parquet(day_path_)
                table = coerce_to_consolidated_schema(df, schema)
                writer.write_table(table)
                appended += table.num_rows

    tmp_path.replace(consolidated_path)
    return appended


def update_ticker(ticker: str) -> dict:
    """Fetch missing days then streaming-append. Returns per-ticker stats."""
    cons = CONSOLIDATED_DIR / f"{ticker}_options.parquet"
    today = pd.Timestamp.utcnow().tz_localize(None).normalize()

    last = consolidated_max_date(cons)
    if last is None:
        # No consolidated yet — start from the earliest per-day file we have
        per_day = sorted((DATA_DIR / ticker).rglob("*.parquet"))
        if not per_day:
            return {"ticker": ticker, "status": "skip", "note": "no data at all"}
        # parse YYYY/MM/DD from path
        parts = per_day[0].relative_to(DATA_DIR / ticker).parts
        last = pd.Timestamp(f"{parts[0]}-{parts[1]}-{parts[2].replace('.parquet','')}") \
            - pd.Timedelta(days=1)

    start = last + pd.Timedelta(days=1)
    if start > today:
        return {"ticker": ticker, "status": "fresh", "last": str(last.date())}

    days = list(pd.bdate_range(start, today, freq=US_BDAY))[:LIMIT_PER_TICKER]
    if not days:
        return {"ticker": ticker, "status": "fresh", "last": str(last.date())}

    fetched_paths: list[Path] = []
    fetch_pass = fetch_fail = 0
    print(f"  fetching {len(days)} days: {days[0].date()}..{days[-1].date()}", flush=True)
    for d in days:
        ok, msg = fetch_and_save(ticker, d)
        if ok:
            fetch_pass += 1
            p = day_path(ticker, d)
            if p.exists():
                fetched_paths.append(p)
        else:
            fetch_fail += 1
            print(f"    {d.date()} FAIL {msg}", flush=True)
        time.sleep(PAUSE_S)

    appended = 0
    if fetched_paths:
        try:
            appended = streaming_append(cons, fetched_paths)
        except Exception as e:
            return {
                "ticker": ticker, "status": "merge_fail",
                "fetch_pass": fetch_pass, "fetch_fail": fetch_fail,
                "error": repr(e),
            }

    return {
        "ticker": ticker,
        "status": "ok" if fetch_fail == 0 else "partial",
        "fetch_pass": fetch_pass, "fetch_fail": fetch_fail,
        "appended_rows": appended,
    }


def main() -> int:
    if not DATA_DIR.exists():
        print(f"no data dir at {DATA_DIR}", file=sys.stderr)
        return 1
    tickers = sorted(p.name for p in DATA_DIR.iterdir() if p.is_dir())
    today = pd.Timestamp.utcnow().tz_localize(None).normalize()
    print(f"=== slim daily update for {len(tickers)} tickers ({today.date()}) ===", flush=True)
    print()

    results: list[dict] = []
    for t in tickers:
        print(f"--- {t} ---", flush=True)
        r = update_ticker(t)
        results.append(r)
        print(f"  -> {r}", flush=True)
        print(flush=True)

    print()
    ok = [r for r in results if r["status"] == "ok"]
    fresh = [r for r in results if r["status"] == "fresh"]
    partial = [r for r in results if r["status"] == "partial"]
    fail = [r for r in results if r["status"] in {"merge_fail", "skip"}]
    print(f"OK:      {len(ok)}/{len(results)}  ({' '.join(r['ticker'] for r in ok) or '-'})")
    print(f"FRESH:   {len(fresh)}/{len(results)}  ({' '.join(r['ticker'] for r in fresh) or '-'})")
    print(f"PARTIAL: {len(partial)}/{len(results)}  ({' '.join(r['ticker'] for r in partial) or '-'})")
    print(f"FAIL:    {len(fail)}/{len(results)}  ({' '.join(r['ticker'] for r in fail) or '-'})")
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
