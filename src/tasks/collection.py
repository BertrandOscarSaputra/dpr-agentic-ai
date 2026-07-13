"""Celery task for data collection from Twitter and news sources."""

import logging

from src.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.collect_twitter")
def collect_twitter(query: str, max_results: int = 100) -> dict:
    """Collect tweets matching the query."""
    logger.info("Twitter collection task started", extra={"query": query, "max_results": max_results})
    # TODO: Instantiate TwitterCollectionAgent and run
    return {"status": "completed", "collected": 0}


@celery_app.task(name="tasks.collect_news")
def collect_news() -> dict:
    """Collect news articles from RSS feeds."""
    logger.info("News collection task started", extra={})
    # TODO: Instantiate NewsCollectionAgent and run
    return {"status": "completed", "collected": 0}
