"""Weekly compact pass for consolidated option parquets.

The slim daily updater streaming-appends a few-day chunk onto each
``options_data/<TICKER>_options.parquet`` per run. Each append produces
a new tiny row group, so over time the file accumulates many small row
groups and compression becomes less efficient (smaller dictionaries,
more metadata overhead). After ~1 week of appends, file size drift is
typically 15-30% above what a single rewrite would produce.

This script rewrites each file end-to-end via streaming row-group
consolidation: read in 20K-row batches, flush a fresh row group every
200K rows. Peak memory per ticker is roughly one target row group
(~40-80 MB), regardless of file size. Snappy compression and statistics
are explicitly enabled so the file stays compatible with the slim
daily updater (which uses column statistics for cheap max-date reads).

Runs Sunday at 07:00 UTC via cron — no daily run conflict, and quotes
data isn't updated on Sundays so the read-side has nothing to disrupt.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent
CONSOLIDATED_DIR = ROOT / "options_data"
TARGET_ROWS_PER_RG = 200_000
READ_BATCH = 20_000


def compact_one(path: Path) -> dict:
    """Stream-rewrite a single consolidated parquet. Returns size delta + timing."""
    if not path.is_file():
        return {"path": str(path), "status": "skip", "note": "not a regular file"}

    size_before = path.stat().st_size
    tmp = path.with_suffix(path.suffix + ".tmp")
    t0 = time.time()

    src = pq.ParquetFile(path)
    schema = src.schema_arrow
    rg_before = src.num_row_groups

    rows = 0
    rg_after = 0
    buffer: list[pa.RecordBatch] = []
    buffer_rows = 0

    with pq.ParquetWriter(tmp, schema, compression="snappy", write_statistics=True) as writer:
        for batch in src.iter_batches(batch_size=READ_BATCH):
            buffer.append(batch)
            buffer_rows += batch.num_rows
            rows += batch.num_rows
            if buffer_rows >= TARGET_ROWS_PER_RG:
                writer.write_table(pa.Table.from_batches(buffer))
                rg_after += 1
                buffer = []
                buffer_rows = 0
        if buffer:
            writer.write_table(pa.Table.from_batches(buffer))
            rg_after += 1

    tmp.replace(path)
    size_after = path.stat().st_size
    elapsed = time.time() - t0
    return {
        "path": str(path.name),
        "status": "ok",
        "rows": rows,
        "rg_before": rg_before,
        "rg_after": rg_after,
        "size_before_mb": round(size_before / 1024 / 1024, 1),
        "size_after_mb": round(size_after / 1024 / 1024, 1),
        "reclaimed_mb": round((size_before - size_after) / 1024 / 1024, 1),
        "elapsed_s": round(elapsed, 1),
    }


def main() -> int:
    if not CONSOLIDATED_DIR.is_dir():
        print(f"no consolidated dir at {CONSOLIDATED_DIR}", file=sys.stderr)
        return 1
    targets = sorted(CONSOLIDATED_DIR.glob("*_options.parquet"))
    print(f"=== weekly compact for {len(targets)} files ===", flush=True)
    print()

    total_before = total_after = 0
    fails: list[str] = []
    for p in targets:
        print(f"--- {p.name} ---", flush=True)
        try:
            r = compact_one(p)
            print(f"  {r}", flush=True)
            total_before += r.get("size_before_mb", 0) or 0
            total_after += r.get("size_after_mb", 0) or 0
        except Exception as e:
            print(f"  FAIL: {e!r}", flush=True)
            fails.append(p.name)
        print(flush=True)

    print()
    print(f"TOTAL: before {total_before:.1f} MB → after {total_after:.1f} MB "
          f"(reclaimed {total_before - total_after:.1f} MB)")
    print(f"failed: {fails or 'none'}")
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
