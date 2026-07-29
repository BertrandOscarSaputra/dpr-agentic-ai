"""ContentItem ORM model — represents collected content from Twitter/news."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.akd_mapping import AKDMapping
    from src.models.analysis_result import AnalysisResult


class ContentItem(Base):
    """A piece of content collected from Twitter or news sources."""

    __tablename__ = "content_items"
    __table_args__ = (
        UniqueConstraint("url", name="uq_content_items_url"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_name: Mapped[str | None] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(String(500))
    url: Mapped[str | None] = mapped_column(String(1000))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # Relationships
    analyses: Mapped[list[AnalysisResult]] = relationship(back_populates="content_item")
    akd_mappings: Mapped[list[AKDMapping]] = relationship(back_populates="content_item")

    def __repr__(self) -> str:
        return f"<ContentItem(id={self.id}, source={self.source_type})>"
