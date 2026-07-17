"""Reports routes — POST /reports/generate, GET /reports/{id}."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth import require_api_key
from src.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/reports/generate")
async def generate_report(
    akd_name: str | None = None,
    db: Session = Depends(get_db),
    _api_key: str = Depends(require_api_key),
) -> dict:
    """Trigger PDF report generation for an AKD or all AKDs."""
    logger.info("Report generation requested", extra={"akd_name": akd_name})
    # TODO: Queue Celery task for PDF generation
    return {"status": "queued", "akd_name": akd_name or "all"}


@router.get("/reports/{report_id}")
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Retrieve a generated report by ID."""
    logger.info("Report requested", extra={"report_id": report_id})
    # TODO: Return report metadata + download link
    return {"id": report_id, "status": "not_implemented"}
