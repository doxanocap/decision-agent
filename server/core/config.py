from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Decisions Architect"
    VERSION: str = "0.1.0"
    
    # Database Config
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/decisions"
    
    # Qdrant Config
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "decisions"
    
    # Model Configs
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"
    CROSS_ENCODER_MODEL: str = "./models/aqm/best_model_v2"
    
    # LLM Configs
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    
    # Auth Config (for future auth-api integration)
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"  # TODO: Use same key as auth-api
    
    # Client Config (used by client, but can be in .env)
    API_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        extra = "ignore"

config = Settings()
