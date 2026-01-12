# Deployment Guide

## Production
Deploy the full stack with Nginx, Qdrant, and the App:
```bash
make deploy-prod
```
The app will be available at `http://localhost`.

## Development
Run locally with hot-reload:
```bash
make build
make run
```

## Troubleshooting
- **Logs**: `docker-compose logs -f`
- **Rebuild**: `docker-compose up --build -d`
