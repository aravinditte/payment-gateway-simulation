from functools import lru_cache
from typing import List

from pydantic import AnyUrl, BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    This class defines ALL runtime configuration for the service.
    """

    # -------------------------------------------------
    # Application
    # -------------------------------------------------
    APP_NAME: str = "payment-gateway-simulator"
    APP_ENV: str = Field(
        default="development",
        description="Environment name: development | staging | production",
    )
    DEBUG: bool = False

    # -------------------------------------------------
    # Server
    # -------------------------------------------------
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # -------------------------------------------------
    # Security
    # -------------------------------------------------
    SECRET_KEY: str = Field(..., description="Internal signing secret")
    API_KEY_HEADER: str = "X-API-Key"

    WEBHOOK_SIGNATURE_HEADER: str = "X-Signature"
    WEBHOOK_TOLERANCE_SECONDS: int = 300

    # -------------------------------------------------
    # Database
    # -------------------------------------------------
    DATABASE_URL: AnyUrl = Field(
        ...,
        description="PostgreSQL DSN, e.g. postgresql+asyncpg://user:pass@host/db",
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # -------------------------------------------------
    # Redis (Optional)
    # -------------------------------------------------
    REDIS_URL: AnyUrl | None = None

    # -------------------------------------------------
    # Rate Limiting
    # -------------------------------------------------
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # -------------------------------------------------
    # CORS
    # -------------------------------------------------
    CORS_ALLOW_ORIGINS: List[str] = ["*"]

    # -------------------------------------------------
    # Webhooks
    # -------------------------------------------------
    WEBHOOK_MAX_RETRIES: int = 5
    WEBHOOK_RETRY_BACKOFF_SECONDS: int = 2

    # -------------------------------------------------
    # Pydantic Settings Config
    # -------------------------------------------------
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    Ensures settings are loaded once and reused across the app.
    """
    return Settings()
