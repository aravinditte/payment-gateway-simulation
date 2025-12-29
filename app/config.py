"""Application configuration management."""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    database_url: str
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    api_secret_key: str
    webhook_signing_secret: str

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Webhook
    webhook_timeout: int = 30
    webhook_max_retries: int = 5
    webhook_retry_delay: int = 5

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60

    # Simulation
    simulation_enabled: bool = True
    simulation_latency_ms: int = 100

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


settings = Settings()  # type: ignore
