"""Content repository — database access for content_items table."""

import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.models.content_item import ContentItem

logger = logging.getLogger(__name__)


class ContentRepository:
    """Handles persistence and querying of ContentItem records.

    Separates database access from agent logic (Single Responsibility).
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def save_articles(self, articles: list[dict], batch_size: int = 100) -> tuple[int, int]:
        """Save articles to the content_items table, skipping duplicates.

        Uses PostgreSQL INSERT ... ON CONFLICT (url) DO NOTHING for
        efficient deduplication without pre-querying.

        Args:
            articles: List of normalized article dicts from the collection agent.
            batch_size: Number of articles to insert per batch.

        Returns:
            Tuple of (saved_count, skipped_count).
        """
        if not articles:
            return 0, 0

        # Filter out articles without URLs (can't deduplicate without URL)
        valid_articles = [a for a in articles if a.get("url")]
        skipped_no_url = len(articles) - len(valid_articles)
        if skipped_no_url > 0:
            logger.warning(
                "Articles skipped due to missing URL",
                extra={"count": skipped_no_url},
            )

        total_saved = 0
        total_skipped = 0

        for i in range(0, len(valid_articles), batch_size):
            batch = valid_articles[i : i + batch_size]
            saved, skipped = self._insert_batch(batch)
            total_saved += saved
            total_skipped += skipped

        logger.info(
            "Articles persisted",
            extra={"saved": total_saved, "skipped": total_skipped + skipped_no_url},
        )
        return total_saved, total_skipped + skipped_no_url

    def _insert_batch(self, batch: list[dict]) -> tuple[int, int]:
        """Insert a batch of articles using ON CONFLICT DO NOTHING.

        Returns:
            Tuple of (inserted_count, skipped_count).
        """
        now = datetime.now(UTC)
        values = [
            {
                "source_type": article["source_type"],
                "content": article["content"],
                "title": article.get("title"),
                "url": article["url"],
                "published_at": article.get("published_at"),
                "collected_at": now,
                "created_at": now,
            }
            for article in batch
        ]

        stmt = (
            insert(ContentItem)
            .values(values)
            .on_conflict_do_nothing(constraint="uq_content_items_url")
        )

        result = self.session.execute(stmt)
        self.session.commit()

        inserted = result.rowcount  # type: ignore[union-attr]
        skipped = len(batch) - inserted
        return inserted, skipped

    def get_existing_urls(self, urls: list[str]) -> set[str]:
        """Check which URLs already exist in the database.

        Useful for pre-filtering before collection if needed.
        """
        if not urls:
            return set()

        stmt = select(ContentItem.url).where(ContentItem.url.in_(urls))
        result = self.session.execute(stmt)
        return {row[0] for row in result}

    def count_by_source_type(self, source_type: str) -> int:
        """Count content items by source type."""
        stmt = (
            select(ContentItem.id)
            .where(ContentItem.source_type == source_type)
        )
        result = self.session.execute(stmt)
        return len(result.all())
