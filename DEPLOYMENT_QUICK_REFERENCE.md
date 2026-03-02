# Quick Deployment Reference

## One-Liner Deployment (After SSH)

```bash
# On EC2, from /home/ubuntu/options_dashboard:
git pull && \
source .venv/bin/activate && \
pip install -r requirements.txt && \
cd frontend && npm install && npm run build && cd .. && \
sudo cp nginx.conf /etc/nginx/sites-available/options-dashboard && \
sudo systemctl restart options-dashboard-api nginx && \
echo "✅ Deployed successfully. Check status:"
```

## Status Checks

```bash
# All services
systemctl status options-dashboard-api nginx

# API Health
curl http://127.0.0.1:8000/health

# Frontend
curl https://options-dashboard.duckdns.org/health

# View logs in real-time
sudo journalctl -u options-dashboard-api -f
```

## File Structure (EC2)

```
/home/ubuntu/options_dashboard/
├── frontend/
│   ├── dist/                 ← React static files served by Nginx
│   ├── src/
│   └── package.json
├── api/
│   ├── main.py              ← FastAPI entry point (runs on :8000)
│   ├── routes/              ← Stock & options endpoints
│   └── services/            ← Analytics logic
├── data/                    ← Stock data
├── options_data/            ← Options data
├── nginx.conf               ← Nginx reverse proxy config
├── options-dashboard-api.service       ← FastAPI systemd
├── options-dashboard-nginx.service     ← Nginx systemd
└── requirements.txt         ← Python dependencies
```

## Common Tasks

**Update frontend only**:
```bash
cd /home/ubuntu/options_dashboard/frontend
git pull
npm run build
sudo systemctl reload nginx
```

**View API errors**:
```bash
sudo journalctl -u options-dashboard-api -f | grep -i error
```

**Check disk space**:
```bash
df -h /home/ubuntu/options_dashboard
du -sh /home/ubuntu/options_dashboard/frontend/dist
```

**Restart everything**:
```bash
sudo systemctl restart options-dashboard-api nginx
```

**Test API**:
```bash
# Get available tickers
curl https://options-dashboard.duckdns.org/api/stock/tickers

# Get option tickers
curl https://options-dashboard.duckdns.org/api/options/tickers

# Health check
curl https://options-dashboard.duckdns.org/health
```

## SSL Certificate Expiry

```bash
# Check expiry
sudo certbot certificates

# Renew manually
sudo certbot renew

# Auto-renewal status
sudo systemctl list-timers certbot.timer
```

## Logs Location

- FastAPI: `journalctl -u options-dashboard-api`
- Nginx: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`
- Systemd: `/var/log/syslog`

---

**Last Updated**: 2026-03-01
**Deployment Status**: Ready for EC2
**Build Version**: React 19 + FastAPI (uvicorn)
