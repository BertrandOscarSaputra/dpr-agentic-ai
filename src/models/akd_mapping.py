"""AKDMapping ORM model — maps content items to AKD (Alat Kelengkapan Dewan)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.content_item import ContentItem


class AKDMapping(Base):
    """Multi-label AKD classification for a ContentItem (max 3 per item)."""

    __tablename__ = "akd_mapping"
    __table_args__ = (
        UniqueConstraint("item_id", "akd_name", name="uq_akd_mapping_item_akd"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("content_items.id"), nullable=False)
    akd_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    akd_type: Mapped[str | None] = mapped_column(String(50))
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # Relationships
    content_item: Mapped[ContentItem] = relationship(back_populates="akd_mappings")

    def __repr__(self) -> str:
        return f"<AKDMapping(id={self.id}, akd={self.akd_name}, rank={self.rank})>"
