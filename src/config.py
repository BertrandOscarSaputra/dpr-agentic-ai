"""Application configuration loaded from environment variables."""

from typing import Any

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation via Pydantic."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
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
    TWITTER_BEARER_TOKEN: str = ""  # Optional: for tweepy API v2

    # X/Twitter Scraping (twikit — no API key required)
    X_USERNAME: str = ""
    X_EMAIL: str = ""
    X_PASSWORD: str = ""
    X_COOKIES_PATH: str = "cookies.json"  # Persisted session cookies

    # X/Twitter Scraping (twikit)
    X_USERNAME: str = ""
    X_EMAIL: str = ""
    X_PASSWORD: str = ""
    X_COOKIES_PATH: str = "cookies.json"
    ENABLE_TWITTER_COLLECTION: bool = False
    TWITTER_MAX_RESULTS_PER_QUERY: int = 10

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"

    # Authentication
    API_KEYS: list[str] = []  # Empty = no auth (dev mode)

    # News Collection
    NEWS_FEED_TIMEOUT: int = 15  # seconds per RSS feed HTTP request
    NEWS_COLLECTION_BATCH_SIZE: int = 100  # DB insert batch size

    # Twitter Collection
    ENABLE_TWITTER_COLLECTION: bool = False  # Set to True to enable automated Twitter scraping
    TWITTER_MAX_RESULTS_PER_QUERY: int = 10  # Max tweets per AKD query (10-100 for API v2)
    TWITTER_COLLECTION_BATCH_SIZE: int = 100  # DB insert batch size

    @model_validator(mode="before")
    @classmethod
    def parse_api_keys_from_env(cls, data: Any) -> Any:
        """Handle API_KEYS string parsing from .env gracefully."""
        if isinstance(data, dict):
            api_keys = data.get("API_KEYS")
            if isinstance(api_keys, str):
                if not api_keys.strip():
                    data["API_KEYS"] = []
                elif api_keys.startswith("["):
                    import json

                    try:
                        data["API_KEYS"] = json.loads(api_keys)
                    except Exception:
                        data["API_KEYS"] = []
                else:
                    data["API_KEYS"] = [k.strip() for k in api_keys.split(",") if k.strip()]
        return data

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
