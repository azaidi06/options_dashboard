#!/usr/bin/env bash
# Slim daily updater wrapper. See daily_options_update_slim.py for design notes.
# Replaces daily_options_update.sh in the cron.
set -uo pipefail
cd /home/ubuntu/options_dashboard
set -a; source .env; set +a
LOG=/home/ubuntu/options_dashboard/logs/daily-slim-$(date -u +%F).log
SNS=arn:aws:sns:us-east-1:108181825111:ec2-health-alerts
PY=/home/ubuntu/options_dashboard/venv/bin/python

mkdir -p logs

{
echo "=== slim daily update started $(date -u) ==="
echo "memory before:"; free -m | head -2
echo
$PY /home/ubuntu/options_dashboard/daily_options_update_slim.py
RC=$?
echo
echo "memory after:"; free -m | head -2
echo "=== slim daily update done $(date -u) (rc=$RC) ==="
} 2>&1 | tee -a "$LOG"
RC=${PIPESTATUS[0]:-0}

# Only ping SNS on failure so we don't spam a daily success
if [ "$RC" -ne 0 ]; then
    BODY=$(tail -50 "$LOG")
    aws sns publish --region us-east-1 \
        --topic-arn "$SNS" \
        --subject "[options-dashboard] daily update had failures" \
        --message "$BODY" >/dev/null 2>&1 || true
fi

exit "$RC"
