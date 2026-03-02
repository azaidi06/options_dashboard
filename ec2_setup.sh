#!/bin/bash
# EC2 Server Setup Script for Stock Analysis Dashboard
# Run this on a fresh Ubuntu 22.04 EC2 instance
# Usage: bash ec2_setup.sh

set -e

echo "=== Updating system ==="
sudo apt update && sudo apt upgrade -y

echo "=== Installing Python and tools ==="
sudo apt install python3-pip python3-venv git nginx -y

echo "=== Setting up application ==="
cd ~

# Clone repository (update with your GitHub URL)
if [ ! -d "options_dashboard" ]; then
    echo "Clone your repository manually:"
    echo "git clone https://github.com/YOUR_USERNAME/options_dashboard.git"
    exit 1
fi

cd options_dashboard

echo "=== Creating virtual environment ==="
python3 -m venv venv
source venv/bin/activate

echo "=== Installing dependencies ==="
pip install -r requirements.txt

echo "=== Creating systemd service ==="
sudo tee /etc/systemd/system/streamlit.service > /dev/null <<EOF
[Unit]
Description=Streamlit Stock Dashboard
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/options_dashboard
Environment="PATH=/home/ubuntu/options_dashboard/venv/bin"
ExecStart=/home/ubuntu/options_dashboard/venv/bin/streamlit run robust_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "=== Enabling and starting streamlit service ==="
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit

echo "=== Setting up Nginx reverse proxy ==="
sudo tee /etc/nginx/sites-available/streamlit > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo ""
echo "=== Setup Complete ==="
echo "Your app should be running at: http://$(curl -s ifconfig.me)"
echo ""
echo "To set up HTTPS with your domain, run:"
echo "  sudo apt install certbot python3-certbot-nginx -y"
echo "  sudo certbot --nginx -d yourdomain.duckdns.org"
echo ""
echo "Check status with: sudo systemctl status streamlit"
