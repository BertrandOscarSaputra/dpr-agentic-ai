"""Application configuration loaded from environment variables."""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation via Pydantic."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-me-in-production"

    # Database
    DATABASE_URL: str = "postgresql+psycopg://dpr_user:dpr_dev_password@localhost:5432/dpr_agentic_ai"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # APIs
    GEMINI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    TWITTER_BEARER_TOKEN: str = ""

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"

    # Authentication
    API_KEYS: list[str] = []  # Empty = no auth (dev mode)

    @property
    def database_url_resolved(self) -> str:
        """Normalize DATABASE_URL to use the psycopg driver for SQLAlchemy."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """Reject insecure defaults in production."""
        if self.ENV == "production" and self.SECRET_KEY == "change-me-in-production":
            raise ValueError("SECRET_KEY must be changed in production")
        return self


settings = Settings()
