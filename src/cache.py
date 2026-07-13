"""Redis connection & caching utilities."""

import logging

import redis

from src.config import settings

logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_cache(key: str) -> str | None:
    """Retrieve a cached value by key."""
    try:
        return redis_client.get(key)
    except redis.ConnectionError:
        logger.error("Redis connection failed", extra={"key": key})
        return None


def set_cache(key: str, value: str, ttl_seconds: int = 3600) -> bool:
    """Set a cached value with a TTL."""
    try:
        redis_client.setex(key, ttl_seconds, value)
        return True
    except redis.ConnectionError:
        logger.error("Redis connection failed", extra={"key": key})
        return False


def delete_cache(key: str) -> bool:
    """Delete a cached value by key."""
    try:
        redis_client.delete(key)
        return True
    except redis.ConnectionError:
        logger.error("Redis connection failed", extra={"key": key})
        return False
