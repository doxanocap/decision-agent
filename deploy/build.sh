#!/bin/bash
set -e

echo "🔨 Building production images..."

# Build backend
echo "📦 Building backend..."
docker build -f deploy/Dockerfile.backend -t doxanocap/decisions-backend:prod .

# Build frontend
echo "🎨 Building frontend..."
docker build -f deploy/Dockerfile.frontend -t doxanocap/decisions-frontend:prod .

echo "✅ Build complete!"
echo ""
echo "Images created:"
echo "  - doxanocap/decisions-backend:prod"
echo "  - doxanocap/decisions-frontend:prod"
echo ""
echo "To push to DockerHub, run: ./deploy/push.sh"
