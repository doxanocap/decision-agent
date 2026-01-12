# Production Deployment Guide

## 🚀 Quick Start

### One-Command Deployment
```bash
make deploy-prod
```

This will:
- Start PostgreSQL (with data persistence)
- Start Qdrant (vector database)
- Start Backend API (with ML models baked in)
- Start Frontend (nginx-served React app)

Access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📦 Building Images

### Local Build
```bash
make build-prod
```

This creates:
- `doxanocap/decisions-backend:prod` (~500MB)
- `doxanocap/decisions-frontend:prod` (~50MB)

### Push to DockerHub
```bash
# Login first
docker login

# Push images
make push-prod
```

---

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Required variables:**
```env
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=sk-...

# Database (auto-configured in docker-compose)
DATABASE_URL=postgresql://postgres:postgres@postgresql:5432/decisions

# Qdrant (auto-configured)
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

**Optional variables:**
```env
# Change models if needed
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=BAAI/bge-m3

# JWT secret for future auth
JWT_SECRET_KEY=your-secret-key-here
```

---

## 🏗️ Architecture

### Network Isolation
```
┌─────────────────────────────────────┐
│         frontend_net (public)       │
│  ┌──────────┐      ┌──────────┐    │
│  │ Frontend │◄────►│ Backend  │    │
│  └──────────┘      └────┬─────┘    │
└─────────────────────────┼───────────┘
                          │
┌─────────────────────────┼───────────┐
│      backend_net (internal)         │
│                         │            │
│  ┌──────────────┐  ┌───▼────┐       │
│  │  PostgreSQL  │  │ Qdrant │       │
│  └──────────────┘  └────────┘       │
└─────────────────────────────────────┘
```

- **frontend_net**: Public network (internet access)
- **backend_net**: Internal network (no internet)
- DB and Qdrant are isolated from external access

### Resource Limits
- **Backend**: 1.5GB RAM, 1.5 CPU cores
- **Frontend**: 128MB RAM, 0.5 CPU cores
- **PostgreSQL**: No limits (adjust if needed)
- **Qdrant**: No limits (adjust if needed)

---

## 🔐 Security

### Secrets Management

**GitHub Secrets** (for CI/CD):
1. Go to repo Settings → Secrets → Actions
2. Add secrets:
   - `DOCKERHUB_USERNAME`: Your DockerHub username
   - `DOCKERHUB_TOKEN`: DockerHub access token

**Production Secrets**:
- Never commit `.env` file
- Use environment variables or secret management service
- Rotate `JWT_SECRET_KEY` regularly

### Image Security
- ✅ Non-root users in all containers
- ✅ Minimal base images (alpine/slim)
- ✅ No secrets baked into images
- ✅ Read-only filesystems where possible

---

## 📊 Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Detailed health (includes DB, ML services)
curl http://localhost:8000/health/detailed

# Frontend health
curl http://localhost:3000
```

### Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### Log Rotation
Logs are automatically rotated:
- Max size: 10MB per file
- Max files: 3
- Total: ~30MB per service

---

## 🔄 CI/CD Pipeline

### Automatic Deployment

Push to `main` branch triggers:
1. **Test**: Run backend tests
2. **Build**: Build Docker images with layer caching
3. **Push**: Push to DockerHub
4. **Verify**: Health check deployment

### Manual Deployment

```bash
# Trigger workflow manually
gh workflow run deploy.yml
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker logs decisions_backend

# Common issues:
# 1. Missing OPENAI_API_KEY
# 2. Database not ready (wait 30s)
# 3. Model download failed (check internet)
```

### Frontend 404 errors
```bash
# Check nginx logs
docker logs decisions_frontend

# Rebuild if needed
docker-compose -f docker-compose.prod.yml up -d --build frontend
```

### Database connection failed
```bash
# Check PostgreSQL
docker logs decisions_postgres

# Reset database
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

### Out of memory
```bash
# Check resource usage
docker stats

# Increase backend memory limit in docker-compose.prod.yml:
deploy:
  resources:
    limits:
      memory: 2G  # Increase from 1.5G
```

---

## 📈 Scaling

### Horizontal Scaling
```yaml
# In docker-compose.prod.yml
backend:
  deploy:
    replicas: 3  # Run 3 backend instances
```

### Load Balancer
Add nginx reverse proxy:
```yaml
nginx-lb:
  image: nginx:alpine
  ports:
    - "80:80"
  depends_on:
    - backend
```

---

## 🔄 Updates

### Update Backend
```bash
# Pull latest image
docker pull doxanocap/decisions-backend:prod

# Restart
docker-compose -f docker-compose.prod.yml up -d backend
```

### Update Frontend
```bash
# Pull latest image
docker pull doxanocap/decisions-frontend:prod

# Restart
docker-compose -f docker-compose.prod.yml up -d frontend
```

### Update All
```bash
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📝 Maintenance

### Backup Database
```bash
docker exec decisions_postgres pg_dump -U postgres decisions > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker exec -i decisions_postgres psql -U postgres decisions
```

### Clean Up
```bash
# Remove stopped containers
docker-compose -f docker-compose.prod.yml down

# Remove volumes (⚠️ deletes data)
docker-compose -f docker-compose.prod.yml down -v

# Remove images
docker rmi doxanocap/decisions-backend:prod
docker rmi doxanocap/decisions-frontend:prod
```

---

## 🎯 Production Checklist

Before deploying to production:

- [ ] Set strong `JWT_SECRET_KEY`
- [ ] Configure real `OPENAI_API_KEY`
- [ ] Set `DATABASE_URL` to production DB
- [ ] Configure CORS origins (not `*`)
- [ ] Enable HTTPS (use Caddy/nginx)
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure backups
- [ ] Test disaster recovery
- [ ] Document runbooks
- [ ] Set up alerts

---

## 📞 Support

Issues? Check:
1. Logs: `make logs`
2. Health: `curl http://localhost:8000/health`
3. GitHub Issues: Report bugs
