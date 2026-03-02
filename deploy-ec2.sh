#!/bin/bash
set -e

# EC2 Deployment Script for Options Dashboard
# Deploys both FastAPI backend and React frontend to EC2 instance

echo "🚀 Options Dashboard EC2 Deployment"
echo "===================================="

# Configuration
GITHUB_REPO="https://github.com/azaidi/options_dashboard.git"
EC2_USER="ubuntu"
EC2_HOST="options-dashboard.duckdns.org"
REMOTE_PATH="/home/ubuntu/options_dashboard"
FRONTEND_DIST="frontend/dist"

echo "📦 Building React frontend..."
cd frontend
npm run build
echo "✓ Frontend build complete"

echo ""
echo "🔐 SSH into EC2 and deploy..."
echo "Host: $EC2_HOST"
echo "Remote path: $REMOTE_PATH"
echo ""

# Deploy instructions (to be run on EC2)
cat << 'EOF'
📋 DEPLOYMENT CHECKLIST FOR EC2:

1. SSH into EC2:
   ssh -i ~/.ssh/options_dashboard.pem ubuntu@options-dashboard.duckdns.org

2. Clone/update repository:
   cd /home/ubuntu
   git clone https://github.com/azaidi/options_dashboard.git (or git pull if exists)
   cd options_dashboard

3. Set up Python environment:
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install fastapi uvicorn[standard]

4. Set up Node.js frontend (if not already built):
   cd frontend
   npm install
   npm run build
   cd ..

5. Copy systemd service files:
   sudo cp options-dashboard-api.service /etc/systemd/system/
   sudo cp options-dashboard-nginx.service /etc/systemd/system/
   sudo systemctl daemon-reload

6. Copy nginx config to /etc/nginx/sites-available/:
   sudo cp nginx.conf /etc/nginx/sites-available/options-dashboard
   sudo ln -sf /etc/nginx/sites-available/options-dashboard /etc/nginx/sites-enabled/options-dashboard
   sudo nginx -t

7. Set up SSL certificates (Let's Encrypt):
   sudo apt-get install -y certbot python3-certbot-nginx
   sudo certbot certonly --nginx -d options-dashboard.duckdns.org

8. Start services:
   sudo systemctl start options-dashboard-api
   sudo systemctl start nginx
   sudo systemctl enable options-dashboard-api
   sudo systemctl enable nginx

9. Verify deployment:
   curl http://127.0.0.1:8000/api/stock/tickers
   curl http://127.0.0.1:8000/health
   curl https://options-dashboard.duckdns.org/health

10. Monitor logs:
    sudo journalctl -u options-dashboard-api -f
    sudo tail -f /var/log/nginx/error.log
    sudo tail -f /var/log/nginx/access.log

EOF

echo ""
echo "✅ Local build complete. Follow the checklist above to deploy to EC2."
