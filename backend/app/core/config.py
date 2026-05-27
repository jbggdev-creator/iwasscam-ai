from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "IwasScam AI"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Database
    database_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    secret_key: str
    access_token_expire_minutes: int = 30

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Rate limiting
    rate_limit_per_minute: int = 30

    # AI
    langsmith_api_key: str = ""
    langsmith_tracing: bool = False

    # LLM (Ollama)
    use_llm: bool = False
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"
    vision_model: str = "qwen2.5vl:7b"

    # RAG / Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    rag_retrieval_limit: int = 3

    # Security
    sentry_dsn: str = ""
    max_request_body_bytes: int = 1024 * 1024       # 1 MB JSON limit
    max_upload_bytes: int = 10 * 1024 * 1024        # 10 MB file upload limit
    clamav_enabled: bool = False
    clamav_socket: str = "/var/run/clamav/clamd.ctl"
    clamav_host: str = "localhost"
    clamav_port: int = 3310

    # Threat intelligence
    urlhaus_enabled: bool = True
    google_safe_browsing_api_key: str = ""

    # Observability
    otel_enabled: bool = False
    otel_endpoint: str = ""
    log_format: str = "json"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

