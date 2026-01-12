# API Use Cases

This document describes the main use cases for the Decisions API with visual sequence diagrams.

## Use Case 1: Create and Analyze Decision

**Actor:** User  
**Goal:** Get AI analysis of decision reasoning quality

### Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant Frontend as React Frontend
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant ML as ML Scoring
    participant RAG as RAG Engine
    participant LLM as GPT-4o-mini
    participant Qdrant as Qdrant Vector DB

    User->>Frontend: Fill decision form<br/>(context + variants + arguments)
    Frontend->>API: POST /analysis/analyze
    
    Note over API: Rate limit: 5/min
    Note over API: Validate input<br/>(20-5000 chars context,<br/>1-5 variants, 1-20 args)
    
    API->>DB: Create decision<br/>(status="pending")
    DB-->>API: decision_id
    API-->>Frontend: 202 Accepted<br/>{decision_id, status: "pending"}
    
    Note over API: Start background task
    
    API->>DB: Update status="analyzing"
    
    par ML Scoring (5-10s)
        API->>ML: Score arguments<br/>(pairwise comparison)
        ML-->>API: {arg_0: 75.5, arg_1: 58.2}
    and RAG Retrieval (1-2s)
        API->>Qdrant: Search similar decisions
        Qdrant-->>API: Top 3 similar contexts
    end
    
    API->>LLM: Analyze decision<br/>(context + ML scores + RAG)
    LLM-->>API: Reasoning analysis<br/>(quality, weak points, biases)
    
    API->>Qdrant: Index decision<br/>(for future RAG)
    
    API->>DB: Update status="completed"<br/>Save results
    
    loop Poll every 3s (max 60 attempts)
        Frontend->>API: GET /analysis/{id}/status
        alt Analysis in progress
            API-->>Frontend: {status: "analyzing"}
        else Analysis complete
            API-->>Frontend: {status: "completed", results: {...}}
            Frontend->>User: Display analysis results
        end
    end
```

### Success Criteria
- Decision created in DB
- Analysis completes in 15-25 seconds
- LLM provides actionable insights
- Results saved and retrievable

### Error Scenarios

```mermaid
flowchart TD
    A[POST /analysis/analyze] --> B{Validation}
    B -->|Invalid input| C[422 Unprocessable Entity]
    B -->|Valid| D{Rate Limit}
    D -->|Exceeded| E[429 Too Many Requests]
    D -->|OK| F[Start Analysis]
    F --> G{Analysis}
    G -->|Success| H[Status: completed]
    G -->|Failure| I[Status: failed]
    I --> J[Show error to user]
```

---

## Use Case 2: View Decision History

**Actor:** User  
**Goal:** Review past decisions and their analyses

### Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant Frontend as React Frontend
    participant API as FastAPI Backend
    participant DB as PostgreSQL

    User->>Frontend: Click "History" tab
    Frontend->>API: GET /decisions?skip=0&limit=100
    
    Note over API: Filter by user_id<br/>(from X-User-ID header)
    
    API->>DB: SELECT * FROM decisions<br/>WHERE user_id = ?<br/>ORDER BY timestamp DESC
    DB-->>API: List of decisions
    API-->>Frontend: [{id, context, variants,<br/>analysis_status, results, ...}]
    
    Frontend->>User: Display decision cards<br/>(sorted by date)
    
    User->>Frontend: Click decision to expand
    Frontend->>User: Show full details<br/>(context, arguments,<br/>ML scores, LLM analysis)
```

### Success Criteria
- All user's decisions returned
- Sorted by timestamp (newest first)
- Pagination works correctly
- Analysis results displayed properly

---

## Use Case 3: Record Decision Outcome

**Actor:** User  
**Goal:** Log which path was chosen and what happened

### Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant Frontend as React Frontend
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant Qdrant as Qdrant Vector DB

    User->>Frontend: Open decision from history
    User->>Frontend: Fill outcome form<br/>(selected path + reasoning)
    Frontend->>API: PATCH /decisions/{id}/outcome<br/>{outcome, selected_variant}
    
    Note over API: Validate outcome text
    
    API->>DB: UPDATE decisions<br/>SET outcome = ?,<br/>selected_variant = ?
    DB-->>API: Updated decision
    
    Note over API,Qdrant: Future: Re-index with outcome<br/>for better RAG learning
    
    API-->>Frontend: {id, outcome, selected_variant, ...}
    Frontend->>User: Show success message<br/>"Outcome logged"
```

### Success Criteria
- Outcome saved to DB
- `selected_variant` captured for RAG learning
- Visible in history view
- Can be used for future recommendations

---

## Use Case 4: Health Check

**Actor:** Monitoring System  
**Goal:** Verify all services are operational

### Sequence Diagram

```mermaid
sequenceDiagram
    participant Monitor as Monitoring
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant ML as ML Services
    participant Qdrant as Qdrant

    Monitor->>API: GET /health/detailed
    
    par Check Database
        API->>DB: SELECT 1
        DB-->>API: OK / Error
    and Check ML Services
        API->>ML: Check orchestrator
        ML-->>API: Ready / Error
    and Check Vector DB
        Note over API,Qdrant: Implicit check<br/>via orchestrator
    end
    
    API-->>Monitor: {<br/>  status: "healthy/degraded",<br/>  services: {<br/>    database: "healthy",<br/>    ml_scoring: "ready",<br/>    llm_service: "ready",<br/>    rag_engine: "ready"<br/>  }<br/>}
```

---

## Performance Characteristics

| Endpoint | Response Time | Notes |
|----------|--------------|-------|
| POST /analysis/analyze | <100ms | Returns 202 immediately |
| GET /analysis/{id}/status | <50ms | Fast DB query |
| GET /decisions | <200ms | Depends on pagination |
| PATCH /decisions/{id}/outcome | <100ms | Simple update |

**Background Analysis Breakdown:**
- ML Scoring: 5-10s (depends on # of arguments)
- RAG Retrieval: 1-2s
- LLM Analysis: 10-15s
- **Total: 15-25s**

---

## Rate Limiting

```mermaid
flowchart LR
    A[User Request] --> B{Rate Limiter}
    B -->|Within limit| C[Process Request]
    B -->|Exceeded| D[429 Too Many Requests]
    
    C --> E[Response]
    D --> F[Retry-After: 60s]
```

**Limits:**
- `/analysis/analyze`: 5 requests/minute per IP
- Other endpoints: No limit (for MVP)

---

## Data Validation Rules

```mermaid
flowchart TD
    A[Decision Input] --> B{Context}
    B -->|20-5000 chars| C{Variants}
    B -->|Invalid| E[422 Error]
    
    C -->|1-5 unique| D{Arguments}
    C -->|Invalid| E
    
    D -->|1-20 total| F{Argument Quality}
    D -->|Invalid| E
    
    F -->|5+ words each| G[Valid ✓]
    F -->|Invalid| E
    
    G --> H[Start Analysis]
```

**Validation Rules:**
- **Context**: 20-5000 characters, min 10 words
- **Variants**: 1-5 unique names, max 100 chars each
- **Arguments**: 1-20 total, min 5 words each, max 2000 chars
- **Argument-Variant Matching**: All arguments must reference valid variants
