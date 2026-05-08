#!/usr/bin/env bash
# sync_data_to_ec2.sh — One-shot rsync of local options + per-day shards to EC2.
#
# Use this when local parquets are fresher than EC2 (e.g., the daily cron has
# fallen behind). Avoids burning Alpha Vantage quota by copying data we
# already have.
#
# Required:
#   EC2_HOST       — public DNS / IP of the EC2 host
#   EC2_KEY_PATH   — path to the SSH private key (~/.ssh/options_dashboard.pem etc.)
#
# Optional:
#   DRY_RUN=1      — show what would transfer without copying
#
# Usage:
#   EC2_HOST=ec2-x-x-x-x.compute.amazonaws.com EC2_KEY_PATH=~/.ssh/key.pem ./scripts/sync_data_to_ec2.sh
#   DRY_RUN=1 ./scripts/sync_data_to_ec2.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

: "${EC2_HOST:?EC2_HOST not set. Run: EC2_HOST=... EC2_KEY_PATH=... $0}"
: "${EC2_KEY_PATH:?EC2_KEY_PATH not set. Run: EC2_HOST=... EC2_KEY_PATH=... $0}"

SSH_OPTS="-i ${EC2_KEY_PATH} -o StrictHostKeyChecking=no"
RSYNC_FLAGS=(-avz --progress)
[[ "${DRY_RUN:-0}" == "1" ]] && RSYNC_FLAGS+=(--dry-run)

REMOTE="ubuntu@${EC2_HOST}:/home/ubuntu/options_dashboard"

echo "==> Syncing options_data/ (consolidated per-ticker parquets)"
rsync "${RSYNC_FLAGS[@]}" -e "ssh ${SSH_OPTS}" \
    "${ROOT}/options_data/" \
    "${REMOTE}/options_data/"

echo ""
echo "==> Syncing data/options/ (per-day shards used by backfill_ticker_options.py --merge)"
rsync "${RSYNC_FLAGS[@]}" -e "ssh ${SSH_OPTS}" \
    "${ROOT}/data/options/" \
    "${REMOTE}/data/options/"

echo ""
echo "==> Restarting FastAPI backend so any cached parquets are reloaded"
ssh ${SSH_OPTS} "ubuntu@${EC2_HOST}" "sudo systemctl restart options-dashboard-api"

echo ""
echo "Done. Verify with:"
echo "  curl -s https://options-dashboard.duckdns.org/api/tickers/coverage | python3 -m json.tool | head -30"
