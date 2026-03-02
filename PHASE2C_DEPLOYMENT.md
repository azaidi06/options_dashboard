# Phase 2c: React + FastAPI Deployment to EC2

## Overview

Phase 2c completes the migration from Streamlit to a modern React + FastAPI stack. This document covers:
- Production build of React frontend
- EC2 infrastructure setup
- Nginx reverse proxy configuration
- SSL/HTTPS setup
- Systemd service management
- Monitoring and troubleshooting

## Completed Deliverables

### ✅ Production React Build
```bash
dist/index.html                   0.46 kB │ gzip:   0.29 kB
dist/assets/index-Cp7NqKkI.css   21.26 kB │ gzip:   4.43 kB
dist/assets/index-DRhefcr9.js   683.60 kB │ gzip: 204.42 kB
```

Build completed in 2.75s with all 705 modules compiled and optimized. Gzipped JS is 204.4 kB (excellent).

### ✅ Deployment Configuration Files Created

1. **nginx.conf** - Reverse proxy configuration
   - Routes `/api/*` to FastAPI backend on port 8000
   - Serves React static files from `/home/ubuntu/options_dashboard/frontend/dist`
   - SSL/TLS configuration for HTTPS
   - Security headers (HSTS, X-Frame-Options, etc.)
   - Caching rules for static assets (1-day cache with immutable flag)

2. **options-dashboard-api.service** - FastAPI systemd service
   - Runs uvicorn with 4 workers on 127.0.0.1:8000
   - Auto-restart on crash
   - Security sandbox (PrivateTmp, NoNewPrivileges, ProtectSystem)
   - Persistent data directory access

3. **options-dashboard-nginx.service** - Nginx systemd service
   - Auto-manages nginx configuration deployment
   - SSL certificate paths configured
   - Standard nginx restart/reload handling

4. **deploy-ec2.sh** - Automated deployment checklist script
   - Builds frontend locally
   - Provides step-by-step EC2 deployment instructions

## EC2 Deployment Instructions

### Prerequisites
- EC2 instance running Ubuntu 22.04 or later
- Domain: `options-dashboard.duckdns.org` (already configured)
- SSH key: `~/.ssh/options_dashboard.pem`
- Security group allows: port 22 (SSH), port 80 (HTTP), port 443 (HTTPS)

### Deployment Steps

#### 1. Connect to EC2
```bash
ssh -i ~/.ssh/options_dashboard.pem ubuntu@options-dashboard.duckdns.org
```

#### 2. Clone Repository
```bash
cd /home/ubuntu
git clone https://github.com/azaidi/options_dashboard.git
cd options_dashboard
```

#### 3. Set up Python Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install fastapi uvicorn[standard]
```

#### 4. Build/Deploy Frontend
```bash
cd frontend
npm install
npm run build
cd ..

# Verify build output
ls -lh frontend/dist/
```

#### 5. Set up Systemd Services
```bash
sudo cp options-dashboard-api.service /etc/systemd/system/
sudo cp options-dashboard-nginx.service /etc/systemd/system/
sudo systemctl daemon-reload
```

#### 6. Configure Nginx
```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/options-dashboard
sudo ln -sf /etc/nginx/sites-available/options-dashboard /etc/nginx/sites-enabled/options-dashboard

# Test nginx configuration
sudo nginx -t

# Remove default site if present
sudo rm -f /etc/nginx/sites-enabled/default
```

#### 7. Set up SSL with Let's Encrypt
```bash
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Generate certificates (will prompt for email)
sudo certbot certonly --nginx -d options-dashboard.duckdns.org

# Verify certificate paths
ls -la /etc/letsencrypt/live/options-dashboard.duckdns.org/
```

#### 8. Start Services
```bash
# Start FastAPI backend
sudo systemctl start options-dashboard-api
sudo systemctl status options-dashboard-api

# Reload and start Nginx
sudo systemctl restart nginx
sudo systemctl status nginx

# Enable auto-start on reboot
sudo systemctl enable options-dashboard-api
sudo systemctl enable nginx
```

#### 9. Verify Deployment
```bash
# Test API backend
curl http://127.0.0.1:8000/api/stock/tickers
curl http://127.0.0.1:8000/health

# Test frontend via https
curl -k https://options-dashboard.duckdns.org/health

# Full integration test
curl https://options-dashboard.duckdns.org/
```

## Architecture

```
Internet
   ↓
HTTPS (port 443)
   ↓
Nginx Reverse Proxy (systemd: options-dashboard-nginx.service)
   ├─ Static files (React build) → /frontend/dist/
   └─ API requests (/api/*) → http://127.0.0.1:8000
                              ↓
                       FastAPI Backend
                   (systemd: options-dashboard-api.service)
                              ↓
                    Python services + Data
                  (utils.py, options_utils.py, data/)
```

## Monitoring & Troubleshooting

### View Service Status
```bash
# FastAPI backend
sudo systemctl status options-dashboard-api
sudo journalctl -u options-dashboard-api -f

# Nginx
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Common Issues

**1. 502 Bad Gateway**
- FastAPI backend is not running
- Check: `sudo systemctl status options-dashboard-api`
- Logs: `sudo journalctl -u options-dashboard-api -f`

**2. 403 Forbidden on API**
- Nginx config issue
- Check: `sudo nginx -t`
- Reload: `sudo systemctl reload nginx`

**3. SSL Certificate Error**
- Certificate expired or path wrong
- Renew: `sudo certbot renew`
- Check paths in nginx.conf

**4. Static Files Not Loading**
- Frontend build missing
- Verify: `ls -la /home/ubuntu/options_dashboard/frontend/dist/`
- Rebuild: `cd frontend && npm run build`

**5. CORS Issues**
- FastAPI CORS middleware is configured in api/main.py
- Should allow localhost + options-dashboard.duckdns.org

### Restart Services
```bash
# Restart FastAPI
sudo systemctl restart options-dashboard-api

# Reload Nginx (without dropping connections)
sudo systemctl reload nginx

# Full restart
sudo systemctl restart options-dashboard-api nginx
```

## SSL Certificate Renewal

Let's Encrypt certificates expire after 90 days. Set up automatic renewal:

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# View renewal schedule
sudo systemctl status certbot.timer
```

Certbot automatically creates a timer that renews certificates 30 days before expiry.

## Post-Deployment Verification Checklist

- [ ] Access https://options-dashboard.duckdns.org in browser
- [ ] Homepage loads with correct styling
- [ ] Stock Analysis page loads and fetches data
- [ ] Put Options page loads and displays option chains
- [ ] API endpoints respond correctly: `/api/stock/tickers`, `/api/options/tickers`
- [ ] Static assets have cache headers
- [ ] SSL certificate is valid (green lock in browser)
- [ ] HTTPS redirect works (http:// redirects to https://)
- [ ] Service auto-restart works (kill FastAPI and verify it restarts)
- [ ] Logs are being written to journalctl

## Next Steps (Optional Optimizations)

1. **CDN Integration**: Serve static assets from CloudFront for better global performance
2. **Load Balancing**: Run multiple FastAPI workers behind Nginx for high traffic
3. **Database Caching**: Add Redis for caching option chain data (currently files are re-read per request)
4. **Analytics**: Add monitoring with Prometheus/Grafana
5. **CI/CD Pipeline**: Auto-deploy on git push (GitHub Actions → EC2)

## File Reference

- **Frontend Build**: `/home/ubuntu/options_dashboard/frontend/dist/`
- **FastAPI Backend**: `/home/ubuntu/options_dashboard/api/`
- **Configuration**:
  - Nginx: `/etc/nginx/sites-available/options-dashboard`
  - Systemd API: `/etc/systemd/system/options-dashboard-api.service`
  - Systemd Nginx: `/etc/systemd/system/options-dashboard-nginx.service`
- **Data**: `/home/ubuntu/options_dashboard/data/` and `options_data/`
- **Logs**:
  - FastAPI: `journalctl -u options-dashboard-api`
  - Nginx: `/var/log/nginx/`

## Rollback Plan

If deployment has issues:

```bash
# Stop services
sudo systemctl stop options-dashboard-api nginx

# Revert to previous Streamlit version
cd /home/ubuntu/options_dashboard
git checkout <previous-commit>
python3 -m streamlit run app.py

# Or restore from backup
# (backup previous state before deploying)
```

## Timeline

- **Phase 1**: FastAPI backend created (api/ directory, endpoints functional) ✅
- **Phase 2a**: Stock Analysis React UI (4 tabs, 4 components, data integration) ✅
- **Phase 2b**: Put Options React UI (5 tabs, 5 components, calculators, Greeks guide) ✅
- **Phase 2c**: Production deployment to EC2 (nginx, systemd, SSL) ✅

**Total effort**: ~6 focused development sessions (4-6 calendar days with testing)

---

**Deployment Status**: Ready for EC2 deployment
**React Build**: ✅ Complete (204 KB gzipped)
**Configuration**: ✅ Complete
**Next Action**: Execute deployment checklist on EC2 instance
