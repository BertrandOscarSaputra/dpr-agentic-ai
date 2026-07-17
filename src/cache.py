"""Redis connection & caching utilities."""

import logging

import redis

from src.config import settings

logger = logging.getLogger(__name__)

_redis_client: redis.Redis | None = None


def _get_redis() -> redis.Redis:
    """Lazy singleton for the Redis client with connection pooling."""
    global _redis_client  # noqa: PLW0603
    if _redis_client is None:
        pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20,
        )
        _redis_client = redis.Redis(connection_pool=pool)
    return _redis_client


def get_cache(key: str) -> str | None:
    """Retrieve a cached value by key."""
    try:
        return _get_redis().get(key)
    except redis.ConnectionError:
        logger.error("Redis connection failed", extra={"key": key})
        return None


def set_cache(key: str, value: str, ttl_seconds: int = 3600) -> bool:
    """Set a cached value with a TTL."""
    try:
        _get_redis().setex(key, ttl_seconds, value)
        return True
    except redis.ConnectionError:
        logger.error("Redis connection failed", extra={"key": key})
        return False


def delete_cache(key: str) -> bool:
    """Delete a cached value by key."""
    try:
        _get_redis().delete(key)
        return True
    except redis.ConnectionError:
        logger.error("Redis connection failed", extra={"key": key})
        return False
