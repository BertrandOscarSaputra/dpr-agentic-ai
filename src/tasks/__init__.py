"""Celery task definitions and Beat schedule configuration."""

from celery import Celery
from celery.schedules import crontab

from src.config import settings

celery_app = Celery(
    "dpr_agentic_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jakarta",
    enable_utc=True,
    beat_schedule={
        "collect-news-every-4-hours": {
            "task": "tasks.collect_news",
            "schedule": crontab(minute=0, hour="*/4"),  # Every 4 hours at :00
        },
    },
)
