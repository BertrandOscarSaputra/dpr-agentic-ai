"""Pydantic schemas for analysis results."""

from datetime import datetime

from pydantic import BaseModel, Field


class AnalysisResultBase(BaseModel):
    """Base fields for an analysis result."""

    sentiment: str = Field(..., description="Positif | Negatif | Netral")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)


class AnalysisResultCreate(AnalysisResultBase):
    """Schema for creating an analysis result."""

    item_id: int


class AnalysisResultRead(AnalysisResultBase):
    """Schema for reading an analysis result."""

    id: int
    item_id: int
    analyzed_at: datetime

    model_config = {"from_attributes": True}


class AKDMappingRead(BaseModel):
    """Schema for reading an AKD mapping."""

    id: int
    item_id: int
    akd_name: str
    akd_type: str | None
    confidence_score: float
    rank: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalyzeRequest(BaseModel):
    """Request body for the POST /analyze endpoint."""

    content: str = Field(..., min_length=10, description="Text content to analyze")
    source_type: str = Field(default="manual", max_length=50)
    source_name: str | None = Field(default=None, max_length=200)
    title: str | None = Field(default=None, max_length=500)
    url: str | None = Field(default=None, max_length=1000)
    published_at: datetime | None = Field(default=None)
