"""Celery tasks for data collection from Twitter and news sources."""

import asyncio
import logging

from src.agents.news_collection import NewsCollectionAgent
from src.database import get_session_factory
from src.repositories.content_repository import ContentRepository
from src.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.collect_twitter", bind=True, max_retries=3)
def collect_twitter(self) -> dict:
    """Collect tweets from X API v2 across all AKD queries and persist to database.

    Retries up to 3 times on failure with exponential backoff.
    """
    from src.config import settings

    if not settings.ENABLE_TWITTER_COLLECTION:
        logger.info("Twitter collection is currently disabled in settings", extra={})
        return {"status": "disabled", "collected": 0, "saved": 0, "skipped": 0}

    logger.info("Twitter collection task started", extra={})

    try:
        from src.agents.twitter_collection import TwitterCollectionAgent

        agent = TwitterCollectionAgent()
        tweets = asyncio.run(agent.collect())

        if not tweets:
            logger.info("No tweets collected", extra={})
            return {"status": "completed", "collected": 0, "saved": 0, "skipped": 0}

        # Persist to database
        session_factory = get_session_factory()
        with session_factory() as session:
            repo = ContentRepository(session)
            saved, skipped = repo.save_articles(tweets)

        logger.info(
            "Twitter collection task completed",
            extra={"collected": len(tweets), "saved": saved, "skipped": skipped},
        )
        return {
            "status": "completed",
            "collected": len(tweets),
            "saved": saved,
            "skipped": skipped,
        }

    except Exception as exc:
        logger.error("Twitter collection task failed", extra={"error": str(exc)})
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(name="tasks.collect_news", bind=True, max_retries=3)
def collect_news(self) -> dict:
    """Collect news articles from RSS feeds and persist to database.

    Retries up to 3 times on failure with exponential backoff.
    """
    logger.info("News collection task started", extra={})

    try:
        # Collect articles from RSS feeds
        agent = NewsCollectionAgent()
        articles = asyncio.run(agent.collect())

        if not articles:
            logger.info("No articles collected", extra={})
            return {"status": "completed", "collected": 0, "saved": 0, "skipped": 0}

        # Persist to database
        session_factory = get_session_factory()
        with session_factory() as session:
            repo = ContentRepository(session)
            saved, skipped = repo.save_articles(articles)

        logger.info(
            "News collection task completed",
            extra={"collected": len(articles), "saved": saved, "skipped": skipped},
        )
        return {
            "status": "completed",
            "collected": len(articles),
            "saved": saved,
            "skipped": skipped,
        }

    except Exception as exc:
        logger.error("News collection task failed", extra={"error": str(exc)})
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
