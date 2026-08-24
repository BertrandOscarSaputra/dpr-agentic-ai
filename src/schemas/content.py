"""Pydantic schemas for content items."""

from datetime import datetime

from pydantic import BaseModel, Field


class ContentItemBase(BaseModel):
    """Base fields shared by create and read schemas."""

    source_type: str = Field(..., max_length=50, description="news_online | news_rss")
    content: str = Field(..., min_length=1, description="The text content")
    title: str | None = Field(None, max_length=500)
    url: str | None = Field(None, max_length=1000)
    published_at: datetime | None = None


class ContentItemCreate(ContentItemBase):
    """Schema for creating a new content item."""


class ContentItemRead(ContentItemBase):
    """Schema for reading a content item from the database."""

    id: int
    collected_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
