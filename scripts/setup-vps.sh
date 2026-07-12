#!/bin/bash

# VPS Setup Script for AgentGuard on Hostinger
# This script sets up Docker, Docker Compose, and Nginx on a fresh VPS

set -e

echo "🚀 Setting up VPS for AgentGuard..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "📦 Installing required packages..."
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    sshpass

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed successfully"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed successfully"
else
    echo "✅ Docker Compose already installed"
fi

# Install Certbot for SSL
echo "🔒 Installing Certbot..."
sudo apt install -y certbot

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/agentguard
sudo chown -R $USER:$USER /opt/agentguard

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Enable Docker service
echo "⚙️  Enabling Docker service..."
sudo systemctl enable docker
sudo systemctl start docker

# Create directories for SSL and Nginx
mkdir -p /opt/agentguard/nginx/ssl
mkdir -p /opt/agentguard/nginx/conf.d

echo "✅ VPS setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone your repository to /opt/agentguard"
echo "2. Set up environment variables in .env.production"
echo "3. Obtain SSL certificates using certbot"
echo "4. Run docker-compose up -d"
echo ""
echo "⚠️  Note: You may need to log out and back in for Docker group changes to take effect"
