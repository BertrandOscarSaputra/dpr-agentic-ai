"""Recommendation ORM model — AI-generated recommendations per AKD."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.trend_window import TrendWindow


class Recommendation(Base):
    """AI-generated recommendation for a specific AKD."""

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    akd_name: Mapped[str] = mapped_column(String(50), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(100))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    trend_window_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("trend_windows.id"), nullable=True
    )

    # Relationships
    trend_window: Mapped[TrendWindow | None] = relationship()

    def __repr__(self) -> str:
        return f"<Recommendation(id={self.id}, akd={self.akd_name}, status={self.status})>"
