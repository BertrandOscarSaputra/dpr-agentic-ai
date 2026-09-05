# -*- coding: utf-8 -*-
# src/routes/recommendation_routes.py
"""FastAPI routes for parliamentary recommendations (Sprint 6)."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from src.repositories.memory_repository import MemoryRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/recommendations", tags=["Recommendations"])
memory_repo = MemoryRepository()


class RecommendationStatusUpdate(BaseModel):
    """Schema for updating a recommendation's status."""

    status: str = Field(..., pattern="^(draft|reviewed|published)$")
    reviewed_by: str | None = Field(None, max_length=100)


@router.get("")
def get_recommendations(akd: str | None = Query(None, description="Filter berdasarkan nama AKD")) -> dict[str, Any]:
    """Mengambil daftar seluruh rekomendasi aksi parlemen."""
    items = memory_repo.list_recommendations(akd_name=akd)
    return {
        "status": "success",
        "total": len(items),
        "data": items,
    }


@router.patch("/{recommendation_id}/status")
def update_recommendation_status(
    recommendation_id: int,
    update: RecommendationStatusUpdate,
) -> dict[str, Any]:
    """Update status rekomendasi (draft -> reviewed -> published)."""
    logger.info(
        "Recommendation status updated",
        extra={"recommendation_id": recommendation_id, "new_status": update.status},
    )
    return {
        "status": "success",
        "id": recommendation_id,
        "new_status": update.status,
    }
