#!/usr/bin/env bash
# Weekly consolidated-parquet compaction. See weekly_compact_consolidated.py
# for design notes. Pings SNS only on failure.
set -uo pipefail
cd /home/ubuntu/options_dashboard
LOG=/home/ubuntu/options_dashboard/logs/weekly-compact-$(date -u +%F).log
SNS=arn:aws:sns:us-east-1:108181825111:ec2-health-alerts
PY=/home/ubuntu/options_dashboard/venv/bin/python

mkdir -p logs

{
echo "=== weekly compact started $(date -u) ==="
echo "memory before:"; free -m | head -2
echo "disk before:";   df -h / | tail -1
echo
$PY /home/ubuntu/options_dashboard/weekly_compact_consolidated.py
RC=$?
echo
echo "memory after:";  free -m | head -2
echo "disk after:";    df -h / | tail -1
echo "=== weekly compact done $(date -u) (rc=$RC) ==="
} 2>&1 | tee -a "$LOG"
RC=${PIPESTATUS[0]:-0}

if [ "$RC" -ne 0 ]; then
    BODY=$(tail -50 "$LOG")
    aws sns publish --region us-east-1 \
        --topic-arn "$SNS" \
        --subject "[options-dashboard] weekly compact had failures" \
        --message "$BODY" >/dev/null 2>&1 || true
fi

exit "$RC"
