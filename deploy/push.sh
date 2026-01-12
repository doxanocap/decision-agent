#!/bin/bash
set -e

echo "🚀 Pushing images to DockerHub..."

# Check if logged in
if ! docker info | grep -q "Username"; then
    echo "❌ Not logged in to DockerHub"
    echo "Run: docker login"
    exit 1
fi

# Push backend
echo "📤 Pushing backend..."
docker push doxanocap/decisions-backend:prod

# Push frontend
echo "📤 Pushing frontend..."
docker push doxanocap/decisions-frontend:prod

echo "✅ Push complete!"
echo ""
echo "Images available at:"
echo "  - https://hub.docker.com/r/doxanocap/decisions-backend"
echo "  - https://hub.docker.com/r/doxanocap/decisions-frontend"
