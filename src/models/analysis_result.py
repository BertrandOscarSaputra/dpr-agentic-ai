"""AnalysisResult ORM model — sentiment analysis result for a content item."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.content_item import ContentItem


class AnalysisResult(Base):
    """Sentiment analysis result linked to a ContentItem."""

    __tablename__ = "item_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("content_items.id"), nullable=False)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # Relationships
    content_item: Mapped[ContentItem] = relationship(back_populates="analyses")

    def __repr__(self) -> str:
        return f"<AnalysisResult(id={self.id}, sentiment={self.sentiment})>"
