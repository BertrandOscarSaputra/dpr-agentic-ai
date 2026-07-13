"""Celery task for PDF report generation."""

import logging

from src.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.generate_report")
def generate_report(akd_name: str | None = None) -> dict:
    """Generate a PDF report for the given AKD (or all AKDs)."""
    logger.info("Report generation task started", extra={"akd_name": akd_name or "all"})
    # TODO: Instantiate ReportAgent, generate PDF, return file path
    return {"status": "completed", "akd_name": akd_name or "all", "file_path": ""}
