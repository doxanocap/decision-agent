# decision-agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)

**Make better decisions with AI-powered analysis, ML scoring, and historical context retrieval.**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Deployment](#-deployment) • [Documentation](#-documentation)

</div>

---

## 🎯 Overview

**Decisions** is an intelligent decision-making assistant that combines:
- **ML Scoring**: Cross-Encoder models to evaluate argument strength
- **RAG (Retrieval-Augmented Generation)**: Learn from your past decisions
- **LLM Analysis**: GPT-4o-mini provides reasoning and insights
- **Real-time Processing**: Asynchronous analysis with polling

Perfect for personal use when facing complex choices with multiple options and competing arguments.

---

## ✨ Features

### Core Capabilities
- 🧠 **AI-Powered Analysis**: GPT-4o-mini evaluates your decision context
- 📊 **ML Argument Scoring**: Cross-Encoder rates argument quality (0-100)
- 🔍 **Historical Context**: RAG retrieves similar past decisions
- ⚡ **Async Processing**: Background analysis with real-time status updates
- 📱 **Modern UI**: React + Tailwind CSS with smooth animations

### Technical Highlights
- 🐳 **Docker-Ready**: One-command deployment
- 🔐 **Browser-Based Auth**: UUID stored in localStorage (MVP)
- 🌐 **Network Isolation**: DB/Qdrant in internal network
- 📈 **Resource Optimized**: 1.5GB RAM limit for backend
- 🔄 **Auto-Retry**: Exponential backoff on network errors
- 🏥 **Health Checks**: Automatic service monitoring

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### 1. Clone Repository
```bash
git clone https://github.com/doxanocap/decisions.git
cd decisions
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Deploy
```bash
make deploy-prod
```

That's it! 🎉

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🏗️ Architecture

### System Overview
```
┌─────────────┐
│   Browser   │
│ (React App) │
└──────┬──────┘
       │ HTTP + X-User-ID
       ▼
┌─────────────┐      ┌──────────────┐
│   FastAPI   │◄────►│  PostgreSQL  │
│   Backend   │      └──────────────┘
└──────┬──────┘
       │
       ├─────► Qdrant (Vector DB)
       └─────► OpenAI API
```

### Tech Stack

**Backend:**
- FastAPI (Python 3.13)
- SQLAlchemy + Alembic
- Qdrant (vector database)
- OpenAI GPT-4o-mini
- BGE-M3 embeddings
- Cross-Encoder scoring

**Frontend:**
- React 18 + Vite
- Tailwind CSS v4
- Framer Motion
- Axios

**Infrastructure:**
- Docker + Docker Compose
- GitHub Actions CI/CD
- DockerHub registry

---

## 📖 How It Works

### 1. Create Decision
```json
{
  "context": "Should I switch to remote work?",
  "variants": ["Remote", "Office"],
  "arguments": [
    {"variant_name": "Remote", "type": "pro", "text": "Better work-life balance"},
    {"variant_name": "Office", "type": "pro", "text": "Face-to-face collaboration"}
  ]
}
```

### 2. AI Analysis Pipeline
```
1. ML Scoring      → Cross-Encoder rates each argument (0-100)
2. RAG Retrieval   → Find similar past decisions
3. LLM Analysis    → GPT-4o-mini provides reasoning
4. Index Decision  → Store in Qdrant for future retrieval
```

### 3. Get Results
```json
{
  "ml_scores": {"arg_1": 75.2, "arg_2": 68.4},
  "llm_analysis": {
    "argument_quality_comparison": "...",
    "key_weak_points_to_reconsider": ["..."],
    "final_note": "..."
  },
  "retrieved_context": [...]
}
```

---

## 🐳 Deployment

### Local Development
```bash
# Start dev servers
make dev

# Backend only
make back

# Frontend only
make front
```

### Production Deployment
```bash
# Build optimized images
make build-prod

# Push to DockerHub
docker login
make push-prod

# Deploy stack
make deploy-prod
```

### Docker Images
- `doxanocap/decisions-backend:prod` (~500MB)
- `doxanocap/decisions-frontend:prod` (~50MB)

**All deployment files are in `deploy/` directory:**
- `deploy/Dockerfile.backend` - Backend image
- `deploy/Dockerfile.frontend` - Frontend image
- `deploy/docker-compose.prod.yml` - Production orchestration
- `deploy/nginx.conf` - Nginx configuration
- `deploy/build.sh` - Build script
- `deploy/push.sh` - Push script

**Optimizations:**
- ✅ ML models baked into image
- ✅ CPU-only torch (saves 1.5GB)
- ✅ Multi-stage builds
- ✅ Non-root containers

---

## 📚 Documentation

- [**Architecture**](docs/ARCHITECTURE.md) - C4 diagrams, data flow, tech stack
- [**Deployment Guide**](docs/DEPLOYMENT.md) - Production setup, scaling, monitoring
- [**Use Cases**](docs/USE_CASES.md) - API endpoints and examples
- [**Auth Integration**](docs/AUTH_INTEGRATION.md) - Future JWT auth setup

---

## 🔧 Configuration

### Environment Variables

```env
# Required
OPENAI_API_KEY=sk-...

# Database (auto-configured in docker-compose)
DATABASE_URL=postgresql://postgres:postgres@postgresql:5432/decisions

# Qdrant (auto-configured)
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Optional
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=BAAI/bge-m3
JWT_SECRET_KEY=your-secret-key
```

---

## 🧪 Testing

```bash
# Run API tests
make test

# Health check
curl http://localhost:8000/health

# Detailed health (includes DB, ML services)
curl http://localhost:8000/health/detailed
```

---

## 🤝 Contributing

This is a personal project, but suggestions are welcome!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** - GPT-4o-mini API
- **FlagEmbedding** - BGE-M3 embeddings
- **Qdrant** - Vector database
- **FastAPI** - Backend framework
- **React** - Frontend framework

---

## 📧 Contact

**Author**: doxanocap  
**GitHub**: [@doxanocap](https://github.com/doxanocap)  
**DockerHub**: [doxanocap/decisions-backend](https://hub.docker.com/r/doxanocap/decisions-backend)

---

<div align="center">

**Made with ❤️ for better decision-making**

[⬆ Back to Top](#decisions---ai-powered-decision-analysis)

</div>
