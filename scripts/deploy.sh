#!/bin/bash
# Production deployment script for la-webhosting.de shared hosting

set -e

REPO_DIR="/var/www/html/saarturnier"
DEPLOYMENT_LOG="/var/log/saarturnier-deploy.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$DEPLOYMENT_LOG"
}

log "=== Starting saarTURNier Deployment ==="

# Pull latest code
log "Pulling latest code from repository..."
cd "$REPO_DIR"
git pull origin main

# Install/update backend dependencies
log "Installing backend dependencies..."
cd backend
pip3 install --upgrade pip
pip3 install -r requirements.txt
cd ..

# Run database migrations
log "Running database migrations..."
cd backend
alembic upgrade head
cd ..

# Build frontend
log "Building frontend..."
cd frontend
npm ci
npm run build
cd ..

# Restart backend service
log "Restarting backend service..."
systemctl restart saarturnier-backend

# Restart frontend service (if using systemd)
log "Restarting frontend service..."
systemctl restart saarturnier-frontend

log "=== Deployment Complete ==="
log "Application is running at https://saarturnier.yourdomain.de"
