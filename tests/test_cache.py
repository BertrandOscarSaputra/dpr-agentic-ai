"""Tests for cache module — verifies lazy initialization."""


def test_cache_import_does_not_crash_without_redis() -> None:
    """Importing cache.py should not crash when Redis is unavailable.

    This verifies Issue #4 fix: the Redis client is now lazy-initialized
    on first use, not at import time.
    """
    from src.cache import _redis_client
    # The module-level client should be None (lazy, not yet created)
    assert _redis_client is None


def test_get_cache_returns_none_on_connection_error() -> None:
    """get_cache should return None gracefully when Redis is down."""
    from src.cache import get_cache
    # Without a running Redis, this should not raise, just return None
    result = get_cache("nonexistent_key")
    assert result is None


def test_set_cache_returns_false_on_connection_error() -> None:
    """set_cache should return False gracefully when Redis is down."""
    from src.cache import set_cache
    result = set_cache("test_key", "test_value")
    assert result is False


def test_delete_cache_returns_false_on_connection_error() -> None:
    """delete_cache should return False gracefully when Redis is down."""
    from src.cache import delete_cache
    result = delete_cache("test_key")
    assert result is False
