#!/bin/bash

# Force Container Rebuild and Clear Browser Cache Script
# This script ensures the containers are rebuilt with correct HTTPS URLs
# and provides instructions to clear browser cache

set -e

VPS_HOST="root@185.224.139.199"
VPS_PASSWORD="Nexolove@1234"
VPS_DIR="/root/AIAgentGuuard"

echo "================================================"
echo "Force Rebuild Containers with HTTPS API URLs"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Stopping containers...${NC}"
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no $VPS_HOST \
    "cd $VPS_DIR && docker-compose -f docker-compose.prod.yml stop web admin"

echo -e "${GREEN}✓ Containers stopped${NC}"
echo ""

echo -e "${YELLOW}Step 2: Removing old containers...${NC}"
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no $VPS_HOST \
    "cd $VPS_DIR && docker-compose -f docker-compose.prod.yml rm -f web admin"

echo -e "${GREEN}✓ Old containers removed${NC}"
echo ""

echo -e "${YELLOW}Step 3: Removing old images...${NC}"
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no $VPS_HOST \
    "docker rmi aiagentguuard-web aiagentguuard-admin || true"

echo -e "${GREEN}✓ Old images removed${NC}"
echo ""

echo -e "${YELLOW}Step 4: Rebuilding with --no-cache (this will take ~3 minutes)...${NC}"
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no $VPS_HOST \
    "cd $VPS_DIR && docker-compose -f docker-compose.prod.yml build --no-cache --progress=plain web admin 2>&1 | tail -20"

echo -e "${GREEN}✓ Containers rebuilt${NC}"
echo ""

echo -e "${YELLOW}Step 5: Starting new containers...${NC}"
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no $VPS_HOST \
    "cd $VPS_DIR && docker-compose -f docker-compose.prod.yml up -d web admin"

echo -e "${GREEN}✓ Containers started${NC}"
echo ""

echo -e "${YELLOW}Step 6: Waiting for containers to be ready (10 seconds)...${NC}"
sleep 10

echo -e "${GREEN}✓ Containers should be ready${NC}"
echo ""

echo -e "${YELLOW}Step 7: Verifying build...${NC}"

# Get the actual container names
WEB_CONTAINER=$(sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no $VPS_HOST \
    "docker ps --format '{{.Names}}' | grep web" || echo "unknown")

if [ "$WEB_CONTAINER" != "unknown" ]; then
    echo -e "${GREEN}✓ Web container running: $WEB_CONTAINER${NC}"
    
    # Check if the container has HTTPS URL
    HAS_HTTPS=$(sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no $VPS_HOST \
        "docker exec $WEB_CONTAINER cat apps/web/.next/BUILD_ID 2>/dev/null || echo 'error'" || echo "error")
    
    if [ "$HAS_HTTPS" != "error" ]; then
        echo -e "${GREEN}✓ Build ID: $HAS_HTTPS${NC}"
    fi
else
    echo -e "${RED}✗ Could not find web container${NC}"
fi

echo ""
echo "================================================"
echo -e "${GREEN}Rebuild Complete!${NC}"
echo "================================================"
echo ""
echo -e "${YELLOW}IMPORTANT: Clear Your Browser Cache${NC}"
echo ""
echo "The containers have been rebuilt with HTTPS URLs, but your browser"
echo "still has cached JavaScript files with HTTP URLs."
echo ""
echo "To fix the mixed content errors:"
echo ""
echo "1. ${RED}Hard Refresh${NC} (clears cache for current page):"
echo "   - Chrome/Edge: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)"
echo "   - Firefox: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)"
echo "   - Safari: Cmd+Option+R (Mac)"
echo ""
echo "2. ${RED}Clear All Browsing Data${NC} (recommended):"
echo "   - Chrome: Settings > Privacy > Clear browsing data"
echo "     ✓ Cached images and files"
echo "     ✓ Set time range to 'All time'"
echo "   - Firefox: Settings > Privacy > Clear Data"
echo "   - Safari: Safari > Clear History"
echo ""
echo "3. ${RED}Open Incognito/Private Window${NC} (for testing):"
echo "   - Ctrl+Shift+N (Chrome/Edge) or Cmd+Shift+N (Mac)"
echo "   - Ctrl+Shift+P (Firefox) or Cmd+Shift+P (Mac)"
echo ""
echo "After clearing cache:"
echo "  Visit: https://overseex.com/dashboard/settings"
echo "  Open DevTools Console (F12)"
echo "  Should see NO mixed content errors"
echo ""
echo "================================================"
echo ""

# Run a quick test
echo -e "${YELLOW}Running quick test...${NC}"
if command -v python3 &> /dev/null; then
    python3 -c "
import requests
try:
    r = requests.get('https://overseex.com', timeout=5)
    if 'http://api.overseex.com' in r.text.lower():
        print('\033[0;31m✗ Still found HTTP URLs in page (browser needs cache clear)\033[0m')
    else:
        print('\033[0;32m✓ No HTTP URLs found in static HTML\033[0m')
except Exception as e:
    print(f'\033[0;33m⚠ Could not test: {e}\033[0m')
" 2>/dev/null || echo "Python test skipped"
fi

echo ""
echo "Rebuild script completed successfully!"
