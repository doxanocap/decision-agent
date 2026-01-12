# System Architecture

This document describes the architecture of the Decisions system using the C4 model with Mermaid diagrams.

## System Context (C4 Level 1)

```mermaid
graph TB
    User[👤 User<br/>Decision Maker]
    
    subgraph Decisions System
        Frontend[🔬 React Frontend<br/>Tailwind CSS + Framer Motion]
        Backend[⚡ FastAPI Backend<br/>Python 3.13]
    end
    
    PostgreSQL[(🗄️ PostgreSQL<br/>Decision Storage)]
    Qdrant[(🧠 Qdrant<br/>Vector Database)]
    OpenAI[🤖 OpenAI API<br/>GPT-4o-mini]
    
    User -->|Create & analyze<br/>decisions| Frontend
    Frontend -->|REST API| Backend
    Backend -->|Store decisions| PostgreSQL
    Backend -->|RAG retrieval| Qdrant
    Backend -->|LLM analysis| OpenAI
    
    style Frontend fill:#6366f1,color:#fff
    style Backend fill:#8b5cf6,color:#fff
    style PostgreSQL fill:#3b82f6,color:#fff
    style Qdrant fill:#10b981,color:#fff
    style OpenAI fill:#f59e0b,color:#fff
```

---

## Container Diagram (C4 Level 2)

```mermaid
graph TB
    subgraph Client
        Browser[🌐 Web Browser]
        React[⚛️ React App<br/>Vite + Tailwind v4]
    end
    
    subgraph Backend Services
        API[📡 FastAPI<br/>REST API]
        Orchestrator[🎯 Orchestrator<br/>Background Tasks]
        MLScoring[🔬 ML Scoring<br/>Cross-Encoder]
        LLMService[🤖 LLM Service<br/>GPT-4o-mini]
        RAGEngine[🧠 RAG Engine<br/>BGE-M3 Embeddings]
    end
    
    subgraph Data Layer
        DB[(PostgreSQL<br/>Decisions + Users)]
        VectorDB[(Qdrant<br/>Embeddings)]
    end
    
    Browser -->|HTTPS| React
    React -->|Polling<br/>3s interval| API
    API -->|Background task| Orchestrator
    
    Orchestrator -->|1. Score args| MLScoring
    Orchestrator -->|2. Retrieve| RAGEngine
    Orchestrator -->|3. Analyze| LLMService
    Orchestrator -->|4. Index| RAGEngine
    
    API -->|CRUD| DB
    RAGEngine -->|Vector search| VectorDB
    LLMService -->|API call| OpenAI[OpenAI API]
    
    style React fill:#6366f1,color:#fff
    style API fill:#8b5cf6,color:#fff
    style Orchestrator fill:#a855f7,color:#fff
    style MLScoring fill:#ec4899,color:#fff
    style LLMService fill:#f59e0b,color:#fff
    style RAGEngine fill:#10b981,color:#fff
```

---

## Analysis Flow (Sequence Diagram)

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant React as React Frontend
    participant API as FastAPI
    participant Orchestrator
    participant ML as ML Scoring
    participant RAG as RAG Engine
    participant LLM as LLM Service
    participant DB as PostgreSQL
    participant Qdrant

    User->>React: Submit decision
    React->>API: POST /analysis/analyze
    
    Note over API: Rate limit check<br/>Data validation
    
    API->>DB: INSERT decision<br/>(status="pending")
    DB-->>API: decision_id
    
    API->>Orchestrator: Start background task
    API-->>React: 202 Accepted<br/>{decision_id}
    
    React->>User: Show loading state
    
    Note over Orchestrator: Background processing starts
    
    Orchestrator->>DB: UPDATE status="analyzing"
    
    par Parallel Processing
        Orchestrator->>ML: Score arguments<br/>(Cross-Encoder)
        ML-->>Orchestrator: ML scores
    and
        Orchestrator->>RAG: Retrieve similar<br/>(BGE-M3 + Qdrant)
        RAG->>Qdrant: Vector search
        Qdrant-->>RAG: Top 3 contexts
        RAG-->>Orchestrator: Retrieved contexts
    end
    
    Orchestrator->>LLM: Analyze decision<br/>(context + scores + RAG)
    LLM-->>Orchestrator: Reasoning analysis
    
    Orchestrator->>RAG: Index decision
    RAG->>Qdrant: Upsert vector
    
    Orchestrator->>DB: UPDATE status="completed"<br/>Save results
    
    loop Polling (every 3s, max 60 attempts)
        React->>API: GET /analysis/{id}/status
        API->>DB: SELECT decision
        DB-->>API: Decision data
        
        alt Analysis complete
            API-->>React: {status: "completed", results}
            React->>User: Display results
        else Still analyzing
            API-->>React: {status: "analyzing"}
        end
    end
```

---

## State Transition Diagram

```mermaid
stateDiagram-v2
    [*] --> Pending: User submits decision
    
    Pending --> Analyzing: Background task starts
    
    Analyzing --> Completed: Analysis succeeds
    Analyzing --> Failed: Analysis fails<br/>(timeout, error)
    
    Completed --> [*]: User views results
    Failed --> [*]: User sees error
    
    note right of Analyzing
        ML Scoring (5-10s)
        RAG Retrieval (1-2s)
        LLM Analysis (10-15s)
        Total: 15-25s
    end note
    
    note right of Completed
        Results include:
        - ML scores
        - LLM analysis
        - Retrieved contexts
    end note
```

---

## Data Model (Entity Relationship)

```mermaid
erDiagram
    DECISION ||--o{ VARIANT : has
    DECISION ||--o{ ARGUMENT : has
    DECISION {
        uuid id PK
        uuid user_id FK
        text context
        string selected_variant
        timestamp timestamp
        text outcome
        string analysis_status
        json ml_scores
        json llm_analysis
        json retrieved_context
    }
    
    VARIANT {
        uuid id PK
        uuid decision_id FK
        string name
    }
    
    ARGUMENT {
        uuid id PK
        uuid decision_id FK
        string variant_name
        text text
        string type
    }
    
    QDRANT_POINT {
        string id
        vector dense_vector
        string decision_id
        text canonical_text
        string content_hash
    }
    
    DECISION ||--o| QDRANT_POINT : indexed_as
```

---

## Technology Stack

### Frontend
```mermaid
graph LR
    A[React 18] --> B[Vite]
    A --> C[Tailwind CSS v4]
    A --> D[Framer Motion]
    A --> E[Lucide Icons]
    A --> F[Axios]
    
    style A fill:#6366f1,color:#fff
    style B fill:#646cff,color:#fff
    style C fill:#06b6d4,color:#fff
```

### Backend
```mermaid
graph LR
    A[FastAPI] --> B[SQLAlchemy]
    A --> C[Pydantic v2]
    A --> D[Alembic]
    A --> E[slowapi<br/>Rate Limiting]
    
    style A fill:#009688,color:#fff
    style B fill:#d32f2f,color:#fff
    style C fill:#e91e63,color:#fff
```

### AI/ML Stack
```mermaid
graph TB
    subgraph ML Scoring
        A[sentence-transformers]
        B[Cross-Encoder<br/>ms-marco-MiniLM-L-12-v2]
    end
    
    subgraph RAG
        C[FlagEmbedding<br/>BGE-M3]
        D[Qdrant Client]
    end
    
    subgraph LLM
        E[OpenAI SDK]
        F[GPT-4o-mini]
    end
    
    A --> B
    C --> D
    E --> F
    
    style B fill:#ec4899,color:#fff
    style C fill:#10b981,color:#fff
    style F fill:#f59e0b,color:#fff
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph Production Environment
        LB[Load Balancer<br/>nginx/Caddy]
        
        subgraph Application Servers
            API1[FastAPI Instance 1]
            API2[FastAPI Instance 2]
        end
        
        subgraph Data Layer
            DB[(PostgreSQL<br/>Primary)]
            DBReplica[(PostgreSQL<br/>Replica)]
            Qdrant[(Qdrant<br/>Vector DB)]
        end
        
        subgraph External Services
            OpenAI[OpenAI API]
        end
    end
    
    Internet[🌐 Internet] --> LB
    LB --> API1
    LB --> API2
    
    API1 --> DB
    API2 --> DB
    DB --> DBReplica
    
    API1 --> Qdrant
    API2 --> Qdrant
    
    API1 --> OpenAI
    API2 --> OpenAI
    
    style LB fill:#6366f1,color:#fff
    style API1 fill:#8b5cf6,color:#fff
    style API2 fill:#8b5cf6,color:#fff
    style DB fill:#3b82f6,color:#fff
    style Qdrant fill:#10b981,color:#fff
    style OpenAI fill:#f59e0b,color:#fff
```

---

## Security Architecture

```mermaid
flowchart TD
    A[User Request] --> B{Rate Limiter}
    B -->|Exceeded| C[429 Response]
    B -->|OK| D{Input Validation}
    
    D -->|Invalid| E[422 Response]
    D -->|Valid| F{User ID Check}
    
    F -->|Missing| G[401 Response]
    F -->|Valid| H[Process Request]
    
    H --> I{Authorization}
    I -->|Forbidden| J[403 Response]
    I -->|Allowed| K[Execute Logic]
    
    K --> L[Structured Logging]
    L --> M[Response]
    
    style B fill:#f59e0b,color:#fff
    style D fill:#10b981,color:#fff
    style F fill:#3b82f6,color:#fff
    style L fill:#6366f1,color:#fff
```

**Security Layers:**
1. **Rate Limiting**: 5 requests/minute per IP for analysis
2. **Input Validation**: Pydantic schemas with custom validators
3. **User Identification**: X-User-ID header (MVP), JWT tokens (future)
4. **Structured Logging**: JSON logs for audit trail
5. **CORS**: Configured for specific origins in production

---

## Monitoring & Observability

```mermaid
graph TB
    subgraph Application
        API[FastAPI]
        Middleware[Logging Middleware]
    end
    
    subgraph Logging
        Stdout[stdout<br/>JSON logs]
    end
    
    subgraph Health Checks
        Basic[GET /health]
        Detailed[GET /health/detailed]
    end
    
    subgraph Metrics Future
        Prometheus[Prometheus]
        Grafana[Grafana]
    end
    
    API --> Middleware
    Middleware --> Stdout
    
    API --> Basic
    API --> Detailed
    
    Detailed --> DB[Check DB]
    Detailed --> ML[Check ML Services]
    
    Stdout -.Future.-> Prometheus
    Prometheus -.Future.-> Grafana
    
    style Middleware fill:#6366f1,color:#fff
    style Stdout fill:#10b981,color:#fff
    style Detailed fill:#f59e0b,color:#fff
```

**Current Monitoring:**
- Structured JSON logging (request/response)
- Basic health check: `/health`
- Detailed health check: `/health/detailed`
- Request duration tracking

**Future Enhancements:**
- Prometheus metrics
- Grafana dashboards
- Sentry error tracking
- APM (Application Performance Monitoring)
