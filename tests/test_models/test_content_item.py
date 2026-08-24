# -*- coding: utf-8 -*-
"""Tests for ContentItem ORM model."""

from src.models.content_item import ContentItem


class TestContentItemCreation:
    """Test ContentItem model instantiation and field defaults."""

    def test_basic_creation(self) -> None:
        item = ContentItem(
            source_type="news_online",
            content="Test content about DPR RI parliamentary activities",
            title="Test Title",
            url="https://example.com/test-article",
        )
        assert item.source_type == "news_online"
        assert item.content == "Test content about DPR RI parliamentary activities"
        assert item.title == "Test Title"
        assert item.url == "https://example.com/test-article"

    def test_news_rss_source_type(self) -> None:
        item = ContentItem(
            source_type="news_rss",
            content="Article about Komisi III and hukum",
        )
        assert item.source_type == "news_rss"

    def test_optional_fields_default_to_none(self) -> None:
        item = ContentItem(
            source_type="news_online",
            content="Minimal content item",
        )
        assert item.title is None
        assert item.url is None
        assert item.published_at is None

    def test_repr(self) -> None:
        item = ContentItem(id=42, source_type="news_online", content="test")
        assert "42" in repr(item)
        assert "news_online" in repr(item)
