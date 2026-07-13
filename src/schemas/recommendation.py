"""Pydantic schemas for recommendations."""

from datetime import datetime

from pydantic import BaseModel, Field


class RecommendationBase(BaseModel):
    """Base fields for a recommendation."""

    akd_name: str = Field(..., max_length=50)
    summary: str = Field(..., min_length=1)
    recommendation: str = Field(..., min_length=1)


class RecommendationCreate(RecommendationBase):
    """Schema for creating a recommendation."""


class RecommendationRead(RecommendationBase):
    """Schema for reading a recommendation."""

    id: int
    status: str
    reviewed_by: str | None
    reviewed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationStatusUpdate(BaseModel):
    """Schema for updating a recommendation's status."""

    status: str = Field(..., pattern="^(draft|reviewed|published)$")
    reviewed_by: str | None = Field(None, max_length=100)
