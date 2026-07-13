"""Trends routes — GET /trends/{akd_name}."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/trends/{akd_name}")
async def get_trends(
    akd_name: str,
    db: Session = Depends(get_db),
) -> dict:
    """Get trend data and anomaly detection results for a specific AKD."""
    logger.info("Trends requested", extra={"akd_name": akd_name})
    # TODO: Query TrendWindow for the given AKD
    return {"akd_name": akd_name, "windows": [], "anomalies": []}
