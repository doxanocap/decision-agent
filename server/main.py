from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import json
import time
from datetime import datetime

from server.db.database import engine
from server.db import models
from server.api.routes import decisions, analysis

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create Tables
models.Base.metadata.create_all(bind=engine)

# Initialize ML services at startup (eager loading)
logger.info("Initializing ML services...")
from server.services.orchestrator import get_orchestrator
orchestrator = get_orchestrator()
logger.info("✅ All ML services initialized successfully")

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Decisions API",
    version="0.1.0",
    description="AI-powered decision analysis assistant"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(decisions.router, prefix="/decisions", tags=["decisions"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])


@app.get("/")
def read_root():
    return {
        "message": "Decisions Architect API",
        "status": "active",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Basic health check."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/health/detailed")
def detailed_health_check():
    """Detailed health check with service status."""
    from server.services.orchestrator import get_orchestrator
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check database
    try:
        from server.db.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check ML/LLM services
    try:
        orchestrator = get_orchestrator()
        health_status["services"]["ml_scoring"] = "ready"
        health_status["services"]["llm_service"] = "ready"
        health_status["services"]["rag_engine"] = "ready"
    except Exception as e:
        health_status["services"]["ai_services"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with structured logging."""
    start_time = time.time()
    
    # Log request
    log_data = {
        "event": "request_started",
        "method": request.method,
        "path": request.url.path,
        "client_ip": get_remote_address(request),
        "timestamp": datetime.utcnow().isoformat()
    }
    logger.info(json.dumps(log_data))
    
    # Process request
    response = await call_next(request)
    
    # Log response
    duration = time.time() - start_time
    log_data = {
        "event": "request_completed",
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(duration * 1000, 2),
        "timestamp": datetime.utcnow().isoformat()
    }
    logger.info(json.dumps(log_data))
    
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)
