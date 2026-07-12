#!/bin/bash

# Deployment Script for AgentGuard
# Deploys the application to the VPS using SCP and Docker

set -e

# Configuration
VPS_HOST="${VPS_HOST:-185.224.139.199}"
VPS_USER="${VPS_USER:-root}"
VPS_PASSWORD="${VPS_PASSWORD:-Nexolve@1234}"
VPS_DIR="/opt/agentguard"

echo "🚀 Deploying AgentGuard to VPS..."

# Create deployment archive (exclude node_modules, .git, etc.)
echo "📦 Creating deployment archive..."
tar -czf /tmp/agentguard-deploy.tar.gz \
    --exclude='node_modules' \
    --exclude='.next' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.env.local' \
    --exclude='.env.development' \
    -C /Users/developer/Desktop/AgentGaurd .

# Upload to VPS using sshpass
echo "📤 Uploading to VPS..."
sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no \
    /tmp/agentguard-deploy.tar.gz \
    $VPS_USER@$VPS_HOST:/tmp/

# Execute deployment on VPS
echo "🔧 Executing deployment on VPS..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no \
    $VPS_USER@$VPS_HOST << 'ENDSSH'
set -e

# Extract archive
cd /opt/agentguard
tar -xzf /tmp/agentguard-deploy.tar.gz
rm /tmp/agentguard-deploy.tar.gz

# Stop existing containers
if [ -f docker-compose.prod.yml ]; then
    docker-compose -f docker-compose.prod.yml down || true
fi

# Build and start containers
echo "🐳 Building and starting containers..."
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head || true

# Show running containers
echo "✅ Deployment complete! Running containers:"
docker-compose -f docker-compose.prod.yml ps

ENDSSH

# Cleanup local archive
rm /tmp/agentguard-deploy.tar.gz

echo "✅ Deployment successful!"
echo ""
echo "🌐 Your applications should be available at:"
echo "   - https://overseex.com (Web App)"
echo "   - https://admin.overseex.com (Admin Panel)"
echo "   - https://api.overseex.com (API)"
echo "   - https://docs.overseex.com (Documentation)"
