from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Always resolve .env relative to this file (backend/app/core/config.py -> backend/.env)
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    app_name: str = "Enterprise Knowledge Intelligence Platform"
    environment: str = "development"
    backend_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    database_url: str = "postgresql+psycopg://eki:eki_password@localhost:5432/eki"
    vector_db_provider: str = "chroma"
    chroma_persist_dir: str = "./chroma_store"
    pinecone_api_key: str = ""
    pinecone_index_name: str = "enterprise-knowledge"
    pinecone_namespace: str = "enterprise-documents"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    pinecone_dimension: int = 384
    pinecone_create_index: bool = False

    embedding_model: str = "local-hash"
    # When VECTOR_DB_PROVIDER=pinecone and embedding_model is still "local-hash",
    # the backend auto-selects this model for real semantic embeddings.
    pinecone_embedding_model: str = "all-MiniLM-L6-v2"
    llm_provider: str = "local"
    llm_model: str = "qwen3-8b"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_timeout_seconds: float = 60.0
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    jwt_secret_key: str = "change-this-demo-secret"
    jwt_expiration_minutes: int = 480

    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), env_file_encoding="utf-8", extra="ignore")


def get_settings() -> Settings:
    return Settings()


settings = Settings()
