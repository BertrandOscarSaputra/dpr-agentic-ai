"""ContentItem ORM model — represents collected content from Twitter/news."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class ContentItem(Base):
    """A piece of content collected from Twitter or news sources."""

    __tablename__ = "content_items"
    __table_args__ = (
        UniqueConstraint("url", name="uq_content_items_url"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(String(500))
    url: Mapped[str | None] = mapped_column(String(1000))
    published_at: Mapped[datetime | None] = mapped_column(DateTime)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    analyses: Mapped[list["AnalysisResult"]] = relationship(back_populates="content_item")
    akd_mappings: Mapped[list["AKDMapping"]] = relationship(back_populates="content_item")

    def __repr__(self) -> str:
        return f"<ContentItem(id={self.id}, source={self.source_type})>"


# Avoid circular imports — these are resolved at runtime by SQLAlchemy
from src.models.akd_mapping import AKDMapping  # noqa: E402, F811
from src.models.analysis_result import AnalysisResult  # noqa: E402, F811
