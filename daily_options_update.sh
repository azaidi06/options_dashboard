#!/usr/bin/env bash
# daily_options_update.sh — Per-ticker smart-fill of missing options data.
#
# For each ticker discovered under data/options/, reads the consolidated
# parquet's max date and fetches from there forward to today (capped at
# 90 days/run for safety). Steady-state cost: 1 AV call/ticker/night.
# Recovers from longer outages over multiple nights.
#
# Designed to run via cron at 6 UTC on weekdays.
#
# Usage:
#   bash daily_options_update.sh            # normal run
#   bash daily_options_update.sh --dry-run  # print what would run, skip execution

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
DATE_STAMP=$(date +%Y-%m-%d)

# Load API key from .env if not already in environment
if [[ -z "${ALPHAVANTAGE_API_KEY:-}" ]] && [[ -f "${SCRIPT_DIR}/.env" ]]; then
    # shellcheck disable=SC1091
    set -a; source "${SCRIPT_DIR}/.env"; set +a
fi
if [[ -z "${ALPHAVANTAGE_API_KEY:-}" ]]; then
    echo "ERROR: ALPHAVANTAGE_API_KEY not set (no environment, no .env)" >&2
    exit 1
fi

LOG_FILE="${LOG_DIR}/daily_options_${DATE_STAMP}.log"

# Pick Python: prefer EC2 venv if present, fall back to local conda env
if [[ -x "/home/ubuntu/options_dashboard/venv/bin/python" ]]; then
    PYTHON="/home/ubuntu/options_dashboard/venv/bin/python"
elif [[ -x "/home/azaidi/anaconda3/envs/options_dashboard/bin/python" ]]; then
    PYTHON="/home/azaidi/anaconda3/envs/options_dashboard/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
else
    echo "ERROR: no Python interpreter found" >&2
    exit 1
fi

DATA_DIR="${SCRIPT_DIR}/data/options"
OPTIONS_DATA_DIR="${SCRIPT_DIR}/options_data"

if [[ ! -d "$DATA_DIR" ]] || [[ -z "$(ls -A "$DATA_DIR" 2>/dev/null || true)" ]]; then
    echo "WARNING: No ticker directories in ${DATA_DIR}; nothing to refresh" >&2
    exit 0
fi

# Discover tickers from data/options/<TKR>/ subdirectories
TICKERS=()
for d in "${DATA_DIR}"/*/; do
    [[ -d "$d" ]] && TICKERS+=("$(basename "$d")")
done

LIMIT_PER_TICKER=90  # Cap per-run trading days/ticker so a stale ticker recovers gradually
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

mkdir -p "$LOG_DIR"

# Helper: read max(date) from a ticker's consolidated parquet, return YYYY-MM-DD.
# Prints empty string if no parquet or error.
ticker_last_date() {
    local tkr="$1"
    local parquet="${OPTIONS_DATA_DIR}/${tkr}_options.parquet"
    [[ ! -f "$parquet" ]] && { echo ""; return; }
    "$PYTHON" -c "
import sys, pyarrow.parquet as pq, pyarrow.compute as pc
try:
    t = pq.read_table('$parquet', columns=['date'])
    m = pc.max(t['date']).as_py()
    print(m if isinstance(m, str) else m.strftime('%Y-%m-%d'))
except Exception as e:
    sys.stderr.write(f'  warn: could not read $parquet: {e}\n')
" 2>>"$LOG_FILE" || echo ""
}

{
    echo "========================================"
    echo "  Daily Options Update — ${DATE_STAMP}"
    echo "  Python: ${PYTHON}"
    echo "  Tickers: ${#TICKERS[@]}"
    echo "  Per-ticker cap: ${LIMIT_PER_TICKER} trading days"
    echo "========================================"
    echo ""

    TOTAL=0; PASS=0; FAIL=0; SKIP=0; FRESH=0
    START_TIME=$(date +%s)
    TODAY=$(date +%Y-%m-%d)

    for TICKER in "${TICKERS[@]}"; do
        echo "--- ${TICKER} ---"

        LAST=$(ticker_last_date "$TICKER")
        if [[ -n "$LAST" ]]; then
            # Start from one day after last cached date so we don't refetch
            START_DATE=$(date -d "${LAST} +1 day" +%Y-%m-%d 2>/dev/null \
                      || date -j -v+1d -f "%Y-%m-%d" "$LAST" +%Y-%m-%d)
            echo "  Cached through: ${LAST}; fetching from ${START_DATE}"
            if [[ "$START_DATE" > "$TODAY" ]]; then
                echo "  Already current — skipping fetch"
                FRESH=$((FRESH + 1))
                continue
            fi
        else
            # No parquet yet — start from 90 days ago (initial seed)
            START_DATE=$(date -d "90 days ago" +%Y-%m-%d 2>/dev/null || date -v-90d +%Y-%m-%d)
            echo "  No cached parquet; seeding from ${START_DATE}"
        fi

        if $DRY_RUN; then
            echo "  [dry-run] would run: $PYTHON backfill_ticker_options.py $TICKER --start $START_DATE --end $TODAY --fetch --merge --limit $LIMIT_PER_TICKER"
            SKIP=$((SKIP + 1))
        else
            TOTAL=$((TOTAL + 1))
            if "$PYTHON" "${SCRIPT_DIR}/backfill_ticker_options.py" "$TICKER" \
                    --start "$START_DATE" --end "$TODAY" \
                    --fetch --merge --limit "$LIMIT_PER_TICKER"; then
                PASS=$((PASS + 1))
            else
                echo "  WARNING: ${TICKER} failed (exit $?)"
                FAIL=$((FAIL + 1))
            fi
        fi
        echo ""
    done

    END_TIME=$(date +%s)
    ELAPSED=$(( END_TIME - START_TIME ))

    echo "========================================"
    echo "  Summary"
    echo "  Elapsed: ${ELAPSED}s"
    if $DRY_RUN; then
        echo "  Mode: dry-run (${SKIP} tickers)"
    else
        echo "  Passed: ${PASS}/${TOTAL}  Failed: ${FAIL}/${TOTAL}  Already-fresh: ${FRESH}"
    fi
    echo "========================================"

} 2>&1 | tee -a "$LOG_FILE"
