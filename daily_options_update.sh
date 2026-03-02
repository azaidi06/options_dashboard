#!/usr/bin/env bash
# daily_options_update.sh — Fetch yesterday's options data for all tickers
#
# Designed to run via cron at 8 PM ET on weekdays. Reuses
# backfill_ticker_options.py (--limit 5 covers a few missed days).
#
# Usage:
#   bash daily_options_update.sh            # normal run
#   bash daily_options_update.sh --dry-run  # print what would run, skip execution

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
DATE_STAMP=$(date +%Y-%m-%d)

# Load API key from .env if not already set
if [[ -z "${ALPHAVANTAGE_API_KEY:-}" ]] && [[ -f "${SCRIPT_DIR}/.env" ]]; then
    export ALPHAVANTAGE_API_KEY="$(grep -m1 '^ALPHAVANTAGE_API_KEY=' "${SCRIPT_DIR}/.env" | cut -d= -f2-)"
fi
LOG_FILE="${LOG_DIR}/daily_options_${DATE_STAMP}.log"

PYTHON="${SCRIPT_DIR}/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
    PYTHON=$(command -v python3)
fi

DATA_DIR="${SCRIPT_DIR}/data/options"
if [[ ! -d "$DATA_DIR" ]] || [[ -z "$(ls -A "$DATA_DIR")" ]]; then
    echo "ERROR: No ticker directories found in ${DATA_DIR}" >&2
    exit 1
fi
TICKERS=()
for d in "${DATA_DIR}"/*/; do
    [[ -d "$d" ]] && TICKERS+=("$(basename "$d")")
done

LIMIT=5
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

mkdir -p "$LOG_DIR"

{
    echo "========================================"
    echo "  Daily Options Update — ${DATE_STAMP}"
    echo "  Python: ${PYTHON}"
    echo "  Tickers: ${#TICKERS[@]}"
    echo "  Limit per ticker: ${LIMIT}"
    echo "========================================"
    echo ""

    TOTAL=0
    PASS=0
    FAIL=0
    SKIP=0
    START_TIME=$(date +%s)

    for TICKER in "${TICKERS[@]}"; do
        echo "--- ${TICKER} ---"

        # Use 14-day start window so we catch any missed days without going back to IPO
        START_DATE=$(date -d "14 days ago" +%Y-%m-%d 2>/dev/null || date -v-14d +%Y-%m-%d)

        if $DRY_RUN; then
            echo "  [dry-run] would run: ${PYTHON} backfill_ticker_options.py ${TICKER} --start ${START_DATE} --fetch --merge --limit ${LIMIT}"
            SKIP=$((SKIP + 1))
        else
            TOTAL=$((TOTAL + 1))
            if "$PYTHON" "${SCRIPT_DIR}/backfill_ticker_options.py" "$TICKER" --start "$START_DATE" --fetch --merge --limit "$LIMIT"; then
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
        echo "  Mode: dry-run (${SKIP} tickers skipped)"
    else
        echo "  Passed: ${PASS}/${TOTAL}  Failed: ${FAIL}/${TOTAL}"
    fi
    echo "========================================"

} 2>&1 | tee -a "$LOG_FILE"
