# Decision Agent 🧠

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)

**AI-powered analysis engine for making better decisions.**

</div>

---


## 🚀 Features

- **Custom Fine-Tuned Cross Encoder**: fine-tuned model to detect logical coherence and argument strength.
- **Logical Analysis**: Deconstructs arguments into Claim → Evidence.
- **Bias Detection**: Identifies cognitive traps like Sunk Cost Fallacy.
- **RAG Context**: Checks new decisions against your personal archive.
- **Qdrant Vector DB**: Semantic search for similar past dilemmas.
- **Real-time Processing**: Asynchronous analysis with polling.

## 🛠️ Stack

**Backend**
- **FastAPI**: High-performance async API.
- **PyTorch (Last Mile)**: Custom Cross-Encoder for logic scoring.
- **LangChain**: Orchestration for RAG and LLM flows.

**Frontend**
- **React + Vite**: Fast, modern UI.
- **Tailwind CSS**: Sleek, responsive design.
- **Framer Motion**: Smooth animations.

**Infrastructure**
- **Docker Compose**: Full stack orchestration.
- **Qdrant**: High-performance vector search.
- **Nginx**: Production-grade reverse proxy.

## ⚡ Quick Start

### 1. Run Production (Docker)
```bash
make deploy-prod
```
Access at: `http://localhost`

### 2. Run Local Dev
```bash
make build
make run
```

## 📚 Documentation
- [**Use Cases**](docs/USE_CASES.md) - Examples and scenarios.
- [**Deployment**](docs/DEPLOYMENT.md) - Setup guide.
- [**Architecture**](docs/ARCHITECTURE.md) - System design.
