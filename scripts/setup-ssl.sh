#!/bin/bash

# SSL Certificate Setup Script
# Obtains Let's Encrypt SSL certificates for all domains

set -e

VPS_HOST="${VPS_HOST:-185.224.139.199}"
VPS_USER="${VPS_USER:-root}"
VPS_PASSWORD="${VPS_PASSWORD:-Nexolve@1234}"

DOMAINS=(
    "overseex.com"
    "www.overseex.com"
    "api.overseex.com"
    "admin.overseex.com"
    "docs.overseex.com"
)

EMAIL="${SSL_EMAIL:-admin@overseex.com}"

echo "🔒 Setting up SSL certificates..."

sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no \
    $VPS_USER@$VPS_HOST << ENDSSH
set -e

# Stop nginx temporarily
docker-compose -f /opt/agentguard/docker-compose.prod.yml stop nginx || true

# Obtain certificates for each domain
for domain in ${DOMAINS[@]}; do
    echo "📜 Obtaining certificate for \$domain..."
    
    certbot certonly --standalone \
        --non-interactive \
        --agree-tos \
        --email $EMAIL \
        -d \$domain \
        --cert-path /opt/agentguard/nginx/ssl || true
done

# Create symbolic links for Nginx
mkdir -p /opt/agentguard/nginx/ssl/live

for domain in overseex.com api.overseex.com admin.overseex.com docs.overseex.com; do
    if [ -d "/etc/letsencrypt/live/\$domain" ]; then
        ln -sf /etc/letsencrypt/live/\$domain /opt/agentguard/nginx/ssl/live/\$domain
    fi
done

# Restart nginx
docker-compose -f /opt/agentguard/docker-compose.prod.yml start nginx

echo "✅ SSL certificates installed!"

ENDSSH

echo "✅ SSL setup complete!"
