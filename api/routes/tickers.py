"""
Ticker management endpoints.

Provides coverage info for cached tickers, upstream availability probes,
and asynchronous fetch jobs that backfill missing days from Alpha Vantage.
"""

from __future__ import annotations

import io
import os
import re
import sys
import time
import threading
import uuid
from datetime import date as _date
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

# Repo root so we can import options_utils + reuse backfill helpers
_DASHBOARD_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_DASHBOARD_ROOT) not in sys.path:
    sys.path.insert(0, str(_DASHBOARD_ROOT))

import options_utils  # noqa: E402
from backfill_ticker_options import (  # noqa: E402
    BASE_URL as AV_BASE_URL,
    fetch_options_chain,
    save_options_data,
    get_trading_days,
    get_all_existing_dates,
    get_combined_output_path,
    merge_all_data,
    get_default_start_date,
    PAUSE_S as _BACKFILL_PAUSE_S,
)

router = APIRouter()

OPTIONS_DATA_DIR = _DASHBOARD_ROOT / "options_data"

# Alpha Vantage HISTORICAL_OPTIONS data starts here (per repo IPO_DATES floor)
_AV_HISTORICAL_FLOOR = "2008-01-01"

# Free-tier rate limit: 5 calls/min => 12s; we use 15s for safety.
_AV_RATE_LIMIT_SLEEP = 15.0

# Cap synchronous fetches to keep request times reasonable. With BackgroundTasks
# we avoid blocking, but this still bounds memory + API spend per job.
_MAX_FETCH_DAYS = 250

_TICKER_RE = re.compile(r"^[A-Z0-9]{1,6}$")

# In-memory job registry. Acceptable to lose on restart (v1 contract).
_JOBS: Dict[str, Dict[str, Any]] = {}
_JOBS_LOCK = threading.Lock()


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def _parquet_path(ticker: str) -> Path:
    return OPTIONS_DATA_DIR / f"{ticker.upper()}_options.parquet"


def _coverage_for_parquet(path: Path) -> Optional[Dict[str, Any]]:
    """Return coverage dict or None if the parquet has no usable date column."""
    try:
        import pyarrow.parquet as pq
        import pyarrow.compute as pc

        table = pq.read_table(path, columns=["date"])
        col = table.column("date")
        if col.length() == 0:
            return None
        mn = pd.Timestamp(pc.min(col).as_py())
        mx = pd.Timestamp(pc.max(col).as_py())
        # count_distinct returns a scalar
        try:
            distinct = pc.count_distinct(col).as_py()
        except Exception:
            distinct = len(set(col.to_pylist()))
        ticker = path.stem.replace("_options", "")
        return {
            "ticker": ticker,
            "firstDate": mn.strftime("%Y-%m-%d") if not pd.isna(mn) else None,
            "lastDate": mx.strftime("%Y-%m-%d") if not pd.isna(mx) else None,
            "tradingDays": int(distinct) if distinct is not None else None,
        }
    except Exception:
        return None


def _coverage_for_ticker(ticker: str) -> Optional[Dict[str, Any]]:
    path = _parquet_path(ticker)
    if not path.exists():
        return None
    return _coverage_for_parquet(path)


def _validate_ticker(ticker: str) -> str:
    t = (ticker or "").strip().upper()
    if not _TICKER_RE.match(t):
        raise HTTPException(
            status_code=400,
            detail="ticker must be 1-6 alphanumeric characters",
        )
    return t


def _today() -> pd.Timestamp:
    return pd.Timestamp(_date.today())


def _previous_trading_day(reference: Optional[pd.Timestamp] = None) -> pd.Timestamp:
    """Return the most recent NYSE trading day strictly before ``reference`` (default: today)."""
    if reference is None:
        reference = _today()
    # Look back up to ~10 days to find a trading day
    lookback_start = reference - pd.Timedelta(days=10)
    days = get_trading_days(lookback_start, reference)
    days = [d for d in days if d < reference]
    if not days:
        # Pathological fallback: yesterday
        return reference - pd.Timedelta(days=1)
    return pd.Timestamp(days[-1])


def _next_trading_day(reference: pd.Timestamp) -> pd.Timestamp:
    """Return the next NYSE trading day strictly after ``reference``."""
    horizon = reference + pd.Timedelta(days=10)
    days = get_trading_days(reference, horizon)
    days = [d for d in days if d > reference]
    if not days:
        return reference + pd.Timedelta(days=1)
    return pd.Timestamp(days[0])


def _probe_upstream(ticker: str) -> tuple[Optional[bool], Optional[str]]:
    """
    Hit Alpha Vantage HISTORICAL_OPTIONS for one recent trading day.

    Returns:
        (exists_upstream, warning) where exists_upstream is True/False/None.
        None means we couldn't determine (e.g. missing API key).
    """
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        return None, "ALPHAVANTAGE_API_KEY not set; upstream probe skipped"

    probe_day = _previous_trading_day()
    params = {
        "function": "HISTORICAL_OPTIONS",
        "symbol": ticker,
        "date": probe_day.strftime("%Y-%m-%d"),
        "datatype": "csv",
        "apikey": api_key,
    }
    try:
        r = requests.get(AV_BASE_URL, params=params, timeout=30)
    except Exception as e:
        return None, f"upstream probe failed: {e}"

    if r.status_code != 200:
        return None, f"upstream probe HTTP {r.status_code}"

    ctype = r.headers.get("Content-Type", "").lower()
    text = (r.text or "").strip()

    if "application/json" in ctype or text.startswith("{"):
        try:
            msg = r.json()
        except Exception:
            return None, f"upstream probe returned non-JSON error: {text[:120]}"
        # Rate limit / info messages
        if "Note" in msg or "Information" in msg:
            return None, f"upstream rate-limited: {msg.get('Note') or msg.get('Information')}"
        # No data => ticker probably has no options chain (false), but the
        # endpoint also returns the same shape for unknown symbols. Treat both as False.
        if str(msg.get("message", "")).lower().startswith("no data"):
            return False, None
        return False, f"upstream error: {str(msg)[:160]}"

    # CSV response with at least one data row beyond the header => exists
    lines = text.splitlines()
    if len(lines) <= 1:
        return False, None
    return True, None


# ----------------------------------------------------------------------------
# Coverage endpoints
# ----------------------------------------------------------------------------

@router.get("/coverage")
async def coverage_all() -> List[Dict[str, Any]]:
    """List date-range coverage for every cached ticker parquet."""
    if not OPTIONS_DATA_DIR.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for path in sorted(OPTIONS_DATA_DIR.glob("*_options.parquet")):
        cov = _coverage_for_parquet(path)
        if cov is not None:
            rows.append(cov)
    rows.sort(key=lambda r: r.get("ticker") or "")
    return rows


@router.get("/coverage/{ticker}")
async def coverage_one(ticker: str) -> Dict[str, Any]:
    t = _validate_ticker(ticker)
    cov = _coverage_for_ticker(t)
    if cov is None:
        raise HTTPException(status_code=404, detail=f"No cached options data for {t}")
    return cov


# ----------------------------------------------------------------------------
# Probe endpoint
# ----------------------------------------------------------------------------

@router.get("/probe/{ticker}")
async def probe_ticker(ticker: str) -> Dict[str, Any]:
    """
    Probe what's available upstream and what's already cached for a ticker.
    """
    t = _validate_ticker(ticker)
    cached = _coverage_for_ticker(t)

    today = _today()
    available = {
        "firstDate": _AV_HISTORICAL_FLOOR,
        "lastDate": today.strftime("%Y-%m-%d"),
    }

    exists_upstream, warning = _probe_upstream(t)

    # Compute simple missingRanges: only the tail gap (since last cached date).
    missing_ranges: List[Dict[str, str]] = []
    if cached and cached.get("lastDate"):
        last_cached = pd.Timestamp(cached["lastDate"])
        nxt = _next_trading_day(last_cached)
        if nxt <= today:
            missing_ranges.append({
                "from": nxt.strftime("%Y-%m-%d"),
                "to": today.strftime("%Y-%m-%d"),
            })
    else:
        # No cached data: full range from AV floor (clamped to ticker IPO if known) -> today
        try:
            ipo_floor = get_default_start_date(t)
        except Exception:
            ipo_floor = pd.Timestamp(_AV_HISTORICAL_FLOOR)
        start = max(ipo_floor, pd.Timestamp(_AV_HISTORICAL_FLOOR))
        missing_ranges.append({
            "from": start.strftime("%Y-%m-%d"),
            "to": today.strftime("%Y-%m-%d"),
        })

    response: Dict[str, Any] = {
        "ticker": t,
        "existsUpstream": exists_upstream,
        "cached": cached,
        "available": available,
        "missingRanges": missing_ranges,
    }
    if warning:
        response["warning"] = warning
    return response


# ----------------------------------------------------------------------------
# Fetch endpoint (async via BackgroundTasks)
# ----------------------------------------------------------------------------

class FetchRequest(BaseModel):
    ticker: str = Field(..., description="Ticker symbol (1-6 alphanumeric)")
    fromDate: str = Field(..., description="Start date (YYYY-MM-DD), inclusive")
    toDate: str = Field(..., description="End date (YYYY-MM-DD), inclusive")

    @field_validator("ticker")
    @classmethod
    def _v_ticker(cls, v: str) -> str:
        v = (v or "").strip().upper()
        if not _TICKER_RE.match(v):
            raise ValueError("ticker must be 1-6 alphanumeric characters")
        return v

    @field_validator("fromDate", "toDate")
    @classmethod
    def _v_date(cls, v: str) -> str:
        try:
            pd.Timestamp(v)
        except Exception:
            raise ValueError(f"invalid date: {v!r}")
        return v


def _set_job(job_id: str, **patch: Any) -> None:
    with _JOBS_LOCK:
        job = _JOBS.get(job_id, {})
        job.update(patch)
        _JOBS[job_id] = job


def _run_fetch_job(
    job_id: str,
    ticker: str,
    days: List[pd.Timestamp],
    rebuild_after: bool,
) -> None:
    """Background worker: fetch each missing day, then rebuild combined parquet."""
    try:
        for i, day in enumerate(days):
            try:
                csv_text = fetch_options_chain(ticker, day)
                save_options_data(ticker, csv_text, day)
            except Exception as exc:
                _set_job(
                    job_id,
                    status="failed",
                    error=f"{day.date()}: {exc}",
                    progress={"done": i, "total": len(days)},
                )
                return

            _set_job(job_id, progress={"done": i + 1, "total": len(days)})

            # Honor free-tier rate limit (skip the sleep on the last item)
            if i < len(days) - 1:
                time.sleep(_AV_RATE_LIMIT_SLEEP)

        if rebuild_after and days:
            try:
                start = min(days)
                end = max(days)
                merge_all_data(
                    ticker,
                    start=start,
                    end=end,
                    output_path=get_combined_output_path(ticker),
                )
            except Exception as exc:
                _set_job(
                    job_id,
                    status="failed",
                    error=f"merge failed: {exc}",
                )
                return

        _set_job(job_id, status="complete", error=None)
    except Exception as exc:  # pragma: no cover - defensive catch-all
        _set_job(job_id, status="failed", error=str(exc))


@router.post("/fetch")
async def fetch_ticker(req: FetchRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Kick off a background job to backfill any missing trading days for ``ticker``
    between ``fromDate`` and ``toDate``.

    Returns immediately with a job ID. Poll ``/api/tickers/fetch/status/{job_id}``
    for progress.
    """
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="ALPHAVANTAGE_API_KEY not set on the server",
        )

    ticker = req.ticker
    start = pd.Timestamp(req.fromDate)
    end = pd.Timestamp(req.toDate)
    if end < start:
        raise HTTPException(status_code=400, detail="toDate must be >= fromDate")

    # Compute trading days in range, then subtract anything already cached.
    trading_days = list(get_trading_days(start, end))
    existing = get_all_existing_dates(ticker)
    missing = [d for d in trading_days if pd.Timestamp(d) not in existing]
    missing = [pd.Timestamp(d) for d in missing]
    missing.sort()

    if len(missing) > _MAX_FETCH_DAYS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"requested range has {len(missing)} missing trading days; "
                f"max per job is {_MAX_FETCH_DAYS}. Narrow the range."
            ),
        )

    job_id = uuid.uuid4().hex[:12]
    initial = {
        "jobId": job_id,
        "ticker": ticker,
        "status": "running" if missing else "complete",
        "progress": {"done": 0, "total": len(missing)},
        "error": None,
        "fromDate": req.fromDate,
        "toDate": req.toDate,
    }
    with _JOBS_LOCK:
        _JOBS[job_id] = initial

    if missing:
        background_tasks.add_task(
            _run_fetch_job,
            job_id=job_id,
            ticker=ticker,
            days=missing,
            rebuild_after=True,
        )

    return {
        "jobId": job_id,
        "ticker": ticker,
        "status": initial["status"],
        "progress": initial["progress"],
        "missingDays": len(missing),
        "rateLimitSleepSeconds": _AV_RATE_LIMIT_SLEEP,
    }


@router.get("/fetch/status/{job_id}")
async def fetch_status(job_id: str) -> Dict[str, Any]:
    with _JOBS_LOCK:
        job = _JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"unknown job_id {job_id}")
    # Return a shallow copy with only the contracted fields
    return {
        "jobId": job.get("jobId", job_id),
        "ticker": job.get("ticker"),
        "status": job.get("status"),
        "progress": job.get("progress", {"done": 0, "total": 0}),
        "error": job.get("error"),
    }
