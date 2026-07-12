#!/bin/bash

# Initial deployment and startup script for VPS
# Builds Docker images and starts services

set -e

echo "🐳 Starting AgentGuard deployment on VPS..."

cd /opt/agentguard

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Build all images (without cache for fresh build)
echo "🏗️  Building Docker images (this may take a while)..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start all services
echo "🚀 Starting all services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head || echo "Migration failed or not needed"

# Show status
echo "✅ Deployment complete! Checking container status:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🌐 Services should be available on:"
echo "   - Backend API: http://SERVER_IP:8000"
echo "   - Web App: http://SERVER_IP:3000"
echo "   - Admin Panel: http://SERVER_IP:3001"
echo "   - Documentation: http://SERVER_IP:3002"
echo ""
echo "📝 Next steps:"
echo "   1. Configure DNS for your domains to point to this server"
echo "   2. Obtain SSL certificates with: ./scripts/setup-ssl.sh"
echo "   3. Services will then be available on your domains with HTTPS"
