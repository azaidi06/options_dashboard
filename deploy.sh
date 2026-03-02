#!/bin/bash
# Deploy script for Stock Analysis Dashboard
# Usage: ./deploy.sh

set -e

# Configuration - UPDATE THIS with your EC2 details
EC2_HOST="ubuntu@98.94.234.0"

echo "Pushing changes to GitHub..."
git push origin main

echo "Deploying to EC2..."
ssh $EC2_HOST "cd ~/options_dashboard && git pull && sudo systemctl restart streamlit"

echo "Deployed successfully!"
echo "Access your app at: https://stockdashboard.duckdns.org"
