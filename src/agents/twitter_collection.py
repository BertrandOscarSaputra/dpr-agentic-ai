"""Twitter Collection Agent — collects tweets related to DPR RI topics.

Uses the tweepy library with the X API v2 (Bearer Token auth).
"""

import logging

from src.config import settings

logger = logging.getLogger(__name__)

_client = None


def _get_twitter_client():
    """Lazy-initialize the tweepy client."""
    global _client  # noqa: PLW0603
    if _client is not None:
        return _client
    if not settings.TWITTER_BEARER_TOKEN:
        logger.warning("TWITTER_BEARER_TOKEN not set — Twitter collection disabled", extra={})
        return None
    try:
        import tweepy
        _client = tweepy.Client(bearer_token=settings.TWITTER_BEARER_TOKEN)
        logger.info("Twitter client initialized", extra={})
    except ImportError:
        logger.error("tweepy not installed — run: uv add tweepy", extra={})
    return _client


class TwitterCollectionAgent:
    """Collects and normalizes tweets for analysis."""

    async def collect(self, query: str, max_results: int = 100) -> list[dict]:
        """Collect tweets matching the query."""
        logger.info("Collecting tweets", extra={"query": query, "max_results": max_results})
        client = _get_twitter_client()
        if client is None:
            return []
        # TODO: Implement search_recent_tweets with pagination
        # response = client.search_recent_tweets(
        #     query=query,
        #     max_results=min(max_results, 100),
        #     tweet_fields=["created_at", "text", "author_id"],
        # )
        return []
