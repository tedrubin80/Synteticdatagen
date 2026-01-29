#!/bin/bash
# SynthGen Production Setup Script
# Run with: sudo bash setup-production.sh

set -e

echo "=========================================="
echo "SynthGen Production Setup for synthgenapp.dev"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo bash setup-production.sh)"
    exit 1
fi

echo -e "${YELLOW}Step 1: Setting up directories${NC}"
mkdir -p /var/www/Synteticdatagen/logs
chown -R www-data:www-data /var/www/Synteticdatagen
chmod -R 755 /var/www/Synteticdatagen

echo -e "${GREEN}[OK]${NC} Directories set up"

echo -e "${YELLOW}Step 2: Installing systemd services${NC}"
cp /var/www/Synteticdatagen/systemd/synthgen-web.service /etc/systemd/system/
cp /var/www/Synteticdatagen/systemd/synthgen-api.service /etc/systemd/system/
systemctl daemon-reload

echo -e "${GREEN}[OK]${NC} Systemd services installed"

echo -e "${YELLOW}Step 3: Setting up NGINX (HTTP only for SSL setup)${NC}"
cp /var/www/Synteticdatagen/nginx/synthgenapp.dev-http.conf /etc/nginx/sites-available/synthgenapp.dev
ln -sf /etc/nginx/sites-available/synthgenapp.dev /etc/nginx/sites-enabled/

# Test nginx config
nginx -t
systemctl reload nginx

echo -e "${GREEN}[OK]${NC} NGINX configured"

echo -e "${YELLOW}Step 4: Starting application services${NC}"
systemctl enable synthgen-web
systemctl enable synthgen-api
systemctl start synthgen-web
systemctl start synthgen-api

echo -e "${GREEN}[OK]${NC} Services started"

echo ""
echo "=========================================="
echo -e "${GREEN}Basic setup complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps to complete SSL setup:"
echo ""
echo "1. Ensure DNS is pointing to this server:"
echo "   synthgenapp.dev -> YOUR_SERVER_IP"
echo "   www.synthgenapp.dev -> YOUR_SERVER_IP"
echo ""
echo "2. Run Certbot to obtain SSL certificates:"
echo "   sudo certbot --nginx -d synthgenapp.dev -d www.synthgenapp.dev"
echo ""
echo "3. After certbot completes, copy the full HTTPS config:"
echo "   sudo cp /var/www/Synteticdatagen/nginx/synthgenapp.dev.conf /etc/nginx/sites-available/synthgenapp.dev"
echo "   sudo nginx -t && sudo systemctl reload nginx"
echo ""
echo "4. Verify services are running:"
echo "   sudo systemctl status synthgen-web"
echo "   sudo systemctl status synthgen-api"
echo ""
echo "5. Test your site:"
echo "   curl -I https://synthgenapp.dev"
echo ""
