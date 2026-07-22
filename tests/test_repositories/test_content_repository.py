"""Tests for ContentRepository.

These tests use mock Sessions since they test the repository's logic
(batch handling, empty lists, URL filtering) without requiring a live DB.
For full integration tests, use a test database.
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock

from src.repositories.content_repository import ContentRepository


class TestSaveArticles:
    """Test article persistence logic."""

    def test_empty_list_returns_zero_counts(self) -> None:
        session = MagicMock()
        repo = ContentRepository(session)
        saved, skipped = repo.save_articles([])
        assert saved == 0
        assert skipped == 0
        session.execute.assert_not_called()

    def test_articles_without_url_are_skipped(self) -> None:
        session = MagicMock()
        repo = ContentRepository(session)

        articles = [
            {"content": "No URL article", "source_type": "news_online"},
            {"content": "Also no URL", "source_type": "news_online", "url": None},
            {"content": "Empty URL", "source_type": "news_online", "url": ""},
        ]

        saved, skipped = repo.save_articles(articles)
        assert saved == 0
        assert skipped == 3

    def test_calls_execute_for_valid_articles(self) -> None:
        session = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 2
        session.execute.return_value = mock_result

        repo = ContentRepository(session)

        articles = [
            {
                "content": "Article 1 content",
                "title": "Title 1",
                "url": "https://example.com/1",
                "source_type": "news_online",
                "published_at": datetime.now(UTC),
            },
            {
                "content": "Article 2 content",
                "title": "Title 2",
                "url": "https://example.com/2",
                "source_type": "news_online",
                "published_at": None,
            },
        ]

        saved, skipped = repo.save_articles(articles)
        assert saved == 2
        assert skipped == 0
        session.execute.assert_called_once()
        session.commit.assert_called_once()

    def test_batch_processing_with_large_list(self) -> None:
        session = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 50
        session.execute.return_value = mock_result

        repo = ContentRepository(session)

        # Create 150 articles to trigger 2 batches (batch_size=100)
        articles = [
            {
                "content": f"Article {i} content",
                "title": f"Title {i}",
                "url": f"https://example.com/{i}",
                "source_type": "news_online",
                "published_at": None,
            }
            for i in range(150)
        ]

        saved, skipped = repo.save_articles(articles, batch_size=100)
        # 2 batches: first 100 → 50 inserted, next 50 → 50 inserted
        assert session.execute.call_count == 2

    def test_mixed_valid_and_invalid_articles(self) -> None:
        session = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 1
        session.execute.return_value = mock_result

        repo = ContentRepository(session)

        articles = [
            {"content": "No URL", "source_type": "news_online"},  # Skipped
            {
                "content": "Valid article",
                "title": "Title",
                "url": "https://example.com/valid",
                "source_type": "news_online",
                "published_at": None,
            },
        ]

        saved, skipped = repo.save_articles(articles)
        assert saved == 1
        assert skipped == 1  # 1 skipped for no URL


class TestGetExistingUrls:
    """Test URL existence checking."""

    def test_empty_list_returns_empty_set(self) -> None:
        session = MagicMock()
        repo = ContentRepository(session)
        result = repo.get_existing_urls([])
        assert result == set()
        session.execute.assert_not_called()

    def test_returns_matching_urls(self) -> None:
        session = MagicMock()
        session.execute.return_value = [
            ("https://example.com/1",),
            ("https://example.com/3",),
        ]

        repo = ContentRepository(session)
        result = repo.get_existing_urls([
            "https://example.com/1",
            "https://example.com/2",
            "https://example.com/3",
        ])

        assert result == {"https://example.com/1", "https://example.com/3"}
