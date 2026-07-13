"""Celery task for content analysis."""

import logging

from src.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.analyze_content")
def analyze_content(item_id: int) -> dict:
    """Run sentiment analysis and AKD classification for a content item."""
    logger.info("Analysis task started", extra={"item_id": item_id})
    # TODO: Instantiate AnalysisAgent, run analysis, persist results
    return {"status": "completed", "item_id": item_id}
