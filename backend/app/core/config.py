from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CiteVault"
    database_url: str = "postgresql://privateai:privateai@localhost:5432/privateai"
    qdrant_url: str = "http://localhost:6333"
    default_llm_provider: str = "mock_llm"
    # mock_embedding: tiny hash vectors (tests / dev). fastembed: ONNX MiniLM (recommended).
    default_embedding_provider: str = "mock_embedding"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    # Must match the model output size (MiniLM is 384).
    embedding_vector_size: int = 384

    # Local LLM via Ollama (https://ollama.com) — used when default_llm_provider == "ollama".
    # On Docker Desktop, host Ollama is often http://host.docker.internal:11434
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout_seconds: float = 120.0

    jwt_secret: str = "dev-insecure-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    bootstrap_admin_email: str = "admin@example.com"
    bootstrap_admin_password: str | None = None

    upload_root: str = "./data/uploads"
    qdrant_collection: str = "privateai_chunks"
    max_upload_bytes: int = 50 * 1024 * 1024

    rag_top_k: int = 8
    # Points to pull from Qdrant / keyword search before reranking (>= rag_top_k).
    rag_vector_pool: int = 28
    rag_min_token_overlap: int = 1


@lru_cache
def get_settings() -> Settings:
    return Settings()
