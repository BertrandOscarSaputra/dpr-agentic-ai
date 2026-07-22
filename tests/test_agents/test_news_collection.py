"""Tests for News Collection Agent."""

import asyncio
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from src.agents.news_collection import FeedConfig, NewsCollectionAgent, load_feed_configs


class TestLoadFeedConfigs:
    """Test feed configuration loading from JSON."""

    def test_loads_feeds_from_json(self) -> None:
        # Clear lru_cache to ensure fresh load
        load_feed_configs.cache_clear()
        feeds = load_feed_configs()
        assert len(feeds) >= 10
        assert all(isinstance(f, FeedConfig) for f in feeds)

    def test_feed_has_required_fields(self) -> None:
        load_feed_configs.cache_clear()
        feeds = load_feed_configs()
        for feed in feeds:
            assert feed.name
            assert feed.url.startswith("http")
            assert feed.category

    def test_feeds_are_immutable_tuple(self) -> None:
        load_feed_configs.cache_clear()
        feeds = load_feed_configs()
        assert isinstance(feeds, tuple)


class TestNewsCollectionAgent:
    """Test the NewsCollectionAgent parsing and collection logic."""

    def _make_feed(
        self, name: str = "Test Feed", url: str = "https://example.com/rss",
    ) -> FeedConfig:
        return FeedConfig(name=name, url=url, category="nasional")

    def test_agent_initializes_with_custom_feeds(self) -> None:
        feeds = [self._make_feed()]
        agent = NewsCollectionAgent(feeds=feeds)
        assert len(agent.feeds) == 1
        assert agent.feeds[0].name == "Test Feed"

    def test_agent_initializes_with_default_feeds(self) -> None:
        agent = NewsCollectionAgent()
        assert len(agent.feeds) >= 10

    def test_parse_entry_extracts_fields(self) -> None:
        agent = NewsCollectionAgent(feeds=[self._make_feed()])
        entry = MagicMock()
        entry.get = lambda key, default="": {
            "link": "https://example.com/article-1",
            "title": "Test Article Title",
            "summary": "This is the article summary text",
            "published": "Mon, 21 Jul 2025 10:00:00 +0700",
        }.get(key, default)
        entry.content = []

        result = agent._parse_entry(entry, "Test Feed")
        assert result is not None
        assert result["url"] == "https://example.com/article-1"
        assert result["title"] == "Test Article Title"
        assert result["content"] == "This is the article summary text"
        assert result["source_type"] == "news_online"
        assert result["source_name"] == "Test Feed"
        assert isinstance(result["published_at"], datetime)

    def test_parse_entry_strips_html(self) -> None:
        agent = NewsCollectionAgent(feeds=[self._make_feed()])
        entry = MagicMock()
        entry.get = lambda key, default="": {
            "link": "https://example.com/article-2",
            "title": "<b>Bold Title</b>",
            "summary": "<p>Paragraph with <a href='#'>link</a></p>",
            "published": "",
        }.get(key, default)
        entry.content = []

        result = agent._parse_entry(entry, "Test Feed")
        assert result is not None
        assert result["title"] == "Bold Title"
        assert "<" not in result["content"]
        assert ">" not in result["content"]

    def test_parse_entry_returns_none_for_no_url(self) -> None:
        agent = NewsCollectionAgent(feeds=[self._make_feed()])
        entry = MagicMock()
        entry.get = lambda key, default="": {
            "link": "",
            "title": "No URL Article",
            "summary": "Content here",
        }.get(key, default)
        entry.content = []

        result = agent._parse_entry(entry, "Test Feed")
        assert result is None

    def test_parse_entry_returns_none_for_no_content(self) -> None:
        agent = NewsCollectionAgent(feeds=[self._make_feed()])
        entry = MagicMock()
        entry.get = lambda key, default="": {
            "link": "https://example.com/empty",
            "title": "Empty Content",
            "summary": "",
            "published": "",
            "description": "",
        }.get(key, default)
        entry.content = []

        result = agent._parse_entry(entry, "Test Feed")
        assert result is None

    def test_parse_entry_prefers_content_over_summary(self) -> None:
        agent = NewsCollectionAgent(feeds=[self._make_feed()])
        entry = MagicMock()
        entry.get = lambda key, default="": {
            "link": "https://example.com/full",
            "title": "Full Content Article",
            "summary": "Short summary",
            "published": "",
        }.get(key, default)
        entry.content = [{"value": "This is the full article content which is longer"}]

        result = agent._parse_entry(entry, "Test Feed")
        assert result is not None
        assert result["content"] == "This is the full article content which is longer"


class TestParseDateMethod:
    """Test the date parsing across multiple formats."""

    def setup_method(self) -> None:
        self.agent = NewsCollectionAgent(
            feeds=[FeedConfig(name="Test", url="https://x.com", category="test")]
        )

    def test_rfc822_date(self) -> None:
        result = self.agent._parse_date("Mon, 21 Jul 2025 10:30:00 +0700")
        assert result is not None
        assert result.year == 2025
        assert result.month == 7
        assert result.day == 21

    def test_iso8601_date(self) -> None:
        result = self.agent._parse_date("2025-07-21T10:30:00+07:00")
        assert result is not None
        assert result.year == 2025

    def test_naive_date_gets_utc(self) -> None:
        result = self.agent._parse_date("2025-07-21 10:30:00")
        assert result is not None
        assert result.tzinfo == UTC

    def test_empty_string_returns_none(self) -> None:
        assert self.agent._parse_date("") is None

    def test_invalid_date_returns_none(self) -> None:
        assert self.agent._parse_date("not-a-date") is None

    def test_timezone_aware_preserved(self) -> None:
        result = self.agent._parse_date("Mon, 21 Jul 2025 10:30:00 +0700")
        assert result is not None
        assert result.tzinfo is not None


class TestCollectWithMockedHTTP:
    """Test the full collection flow with mocked HTTP responses."""

    def _make_rss_xml(
        self, title: str = "Test Article", url: str = "https://example.com/1",
    ) -> bytes:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
          <channel>
            <title>Test Feed</title>
            <item>
              <title>{title}</title>
              <link>{url}</link>
              <description>Test content for the article</description>
              <pubDate>Mon, 21 Jul 2025 10:00:00 +0700</pubDate>
            </item>
          </channel>
        </rss>""".encode()

    @patch("src.agents.news_collection.requests.get")
    def test_collect_parses_rss_response(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.content = self._make_rss_xml()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        feed = FeedConfig(name="Test", url="https://example.com/rss", category="test")
        agent = NewsCollectionAgent(feeds=[feed])
        articles = asyncio.run(agent.collect())

        assert len(articles) == 1
        assert articles[0]["title"] == "Test Article"
        assert articles[0]["source_type"] == "news_online"

    @patch("src.agents.news_collection.requests.get")
    def test_collect_isolates_feed_errors(
        self, mock_get: MagicMock,
    ) -> None:
        """One broken feed should not prevent others from being collected."""
        import requests as req

        good_response = MagicMock()
        good_response.content = self._make_rss_xml("Good Article", "https://good.com/1")
        good_response.raise_for_status = MagicMock()

        bad_response = MagicMock()
        bad_response.raise_for_status.side_effect = req.HTTPError("500")

        mock_get.side_effect = [bad_response, good_response]

        feeds = [
            FeedConfig(name="Bad Feed", url="https://bad.com/rss", category="test"),
            FeedConfig(name="Good Feed", url="https://good.com/rss", category="test"),
        ]
        agent = NewsCollectionAgent(feeds=feeds)
        articles = asyncio.run(agent.collect())

        assert len(articles) == 1
        assert articles[0]["title"] == "Good Article"

    @patch("src.agents.news_collection.requests.get")
    def test_collect_handles_timeout(self, mock_get: MagicMock) -> None:
        import requests as req

        mock_get.side_effect = req.Timeout("Connection timed out")

        feed = FeedConfig(name="Slow Feed", url="https://slow.com/rss", category="test")
        agent = NewsCollectionAgent(feeds=[feed])
        articles = asyncio.run(agent.collect())

        assert articles == []

    @patch("src.agents.news_collection.requests.get")
    def test_collect_handles_empty_feed(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.content = b"""<?xml version="1.0"?>
        <rss version="2.0"><channel><title>Empty</title></channel></rss>"""
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        feed = FeedConfig(name="Empty Feed", url="https://empty.com/rss", category="test")
        agent = NewsCollectionAgent(feeds=[feed])
        articles = asyncio.run(agent.collect())

        assert articles == []
