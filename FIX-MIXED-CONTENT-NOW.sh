#!/bin/bash

# MANUAL FIX FOR MIXED CONTENT ERROR
# Run this script to rebuild containers with HTTPS URLs

echo "=========================================="
echo "   FIXING MIXED CONTENT ERROR"
echo "=========================================="
echo ""
echo "This will:"
echo "1. Upload updated docker-compose.prod.yml to VPS"
echo "2. Stop web and admin containers"
echo "3. Remove old images"
echo "4. Rebuild with --no-cache (takes 3-5 minutes)"
echo "5. Start new containers with HTTPS URLs"
echo ""
echo "Press Enter to continue or Ctrl+C to cancel..."
read

echo ""
echo "Step 1: Uploading docker-compose.prod.yml..."
scp -o StrictHostKeyChecking=no docker-compose.prod.yml root@185.224.139.199:/root/AIAgentGuuard/docker-compose.prod.yml

if [ $? -ne 0 ]; then
    echo "ERROR: Could not upload file. Check your SSH connection."
    exit 1
fi

echo "✓ File uploaded"
echo ""

echo "Step 2: Connecting to VPS and rebuilding..."
echo "(This will take 3-5 minutes, please wait...)"
echo ""

ssh -o StrictHostKeyChecking=no root@185.224.139.199 << 'ENDSSH'
cd /root/AIAgentGuuard

echo "=== Stopping web and admin containers ==="
docker-compose -f docker-compose.prod.yml stop web admin

echo ""
echo "=== Removing old containers ==="
docker-compose -f docker-compose.prod.yml rm -f web admin

echo ""
echo "=== Removing old images (force clean) ==="
docker rmi -f aiagentguuard-web aiagentguuard-admin 2>/dev/null || true

echo ""
echo "=== Building with --no-cache (please wait 3-5 minutes) ==="
docker-compose -f docker-compose.prod.yml build --no-cache web admin

echo ""
echo "=== Starting new containers ==="
docker-compose -f docker-compose.prod.yml up -d web admin

echo ""
echo "=== Waiting 10 seconds for containers to start ==="
sleep 10

echo ""
echo "=== Container Status ==="
docker ps | grep -E "agentguard-web|agentguard-admin|NAMES"

echo ""
echo "✓ REBUILD COMPLETE"
ENDSSH

echo ""
echo "=========================================="
echo "          REBUILD COMPLETE!"
echo "=========================================="
echo ""
echo "Now do this in your browser:"
echo ""
echo "1. HARD REFRESH the page:"
echo "   - Windows/Linux: Ctrl + Shift + R"
echo "   - Mac: Cmd + Shift + R"
echo ""
echo "2. Or CLEAR ALL CACHE:"
echo "   - Chrome: Settings > Privacy > Clear browsing data"
echo "   - Select 'Cached images and files'"
echo "   - Time range: 'All time'"
echo "   - Click 'Clear data'"
echo ""
echo "3. Or open INCOGNITO/PRIVATE window to test"
echo ""
echo "After that, the API key creation should work!"
echo ""
