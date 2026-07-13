"""Recommendations routes — GET /recommendations, PATCH /recommendations/{id}/status."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.recommendation import RecommendationStatusUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/recommendations")
async def list_recommendations(
    akd_name: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """List recommendations, optionally filtered by AKD name or status."""
    logger.info("Recommendations listed", extra={"akd_name": akd_name, "status": status})
    # TODO: Query Recommendation model with filters
    return {"recommendations": [], "total": 0}


@router.patch("/recommendations/{recommendation_id}/status")
async def update_recommendation_status(
    recommendation_id: int,
    update: RecommendationStatusUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """Update the review status of a recommendation."""
    logger.info(
        "Recommendation status updated",
        extra={"recommendation_id": recommendation_id, "new_status": update.status},
    )
    # TODO: Update Recommendation.status
    return {"id": recommendation_id, "status": update.status}
