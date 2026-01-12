# Architecture Overview

## High-Level Design
The system consists of three main layers:

1.  **Frontend (React + Vite)**:
    - User Interface for decision input and analysis visualization.
    - Communicates with Backend via REST API.

2.  **Backend (FastAPI)**:
    - **API Layer**: Handles requests.
    - **Orchestrator**: Manages the analysis pipeline (Validation -> ML Scoring -> RAG -> LLM).
    - **ML Engine**: Custom PyTorch model for scoring arguments.
    - **LLM Service**: OpenAI integration for deep reasoning.

3.  **Data & Infrastructure**:
    - **PostgreSQL**: Stores decisions.
    - **Qdrant**: Vector database for semantic search (RAG).
    - **Docker**: Containerization.

## Data Flow
User Input -> API -> Orchestrator -> ML Model -> RAG Retrieval -> LLM Contextualization -> JSON Output -> Frontend
