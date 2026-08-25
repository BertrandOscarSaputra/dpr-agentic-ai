"""Tests for News Collection Agent."""

import asyncio
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from src.agents.news_collection import (
    FeedConfig,
    NewsCollectionAgent,
    is_consumer_or_entertainment_noise,
    load_feed_configs,
)


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

        result = agent._parse_entry(entry, "Test Feed")
        assert result is not None
        assert result["title"] == "Test Article Title"
        assert result["content"] == "This is the article summary text"
        assert result["url"] == "https://example.com/article-1"
        assert result["source_name"] == "Test Feed"
        assert result["source_type"] == "news_online"
        assert result["published_at"] is not None

    def test_parse_entry_skips_missing_title(self) -> None:
        agent = NewsCollectionAgent(feeds=[self._make_feed()])
        entry = MagicMock()
        entry.get = lambda key, default="": {
            "link": "https://example.com/article-1",
            "title": "",
            "summary": "Summary only",
        }.get(key, default)

        assert agent._parse_entry(entry, "Test Feed") is None

    def test_parse_entry_skips_missing_url(self) -> None:
        agent = NewsCollectionAgent(feeds=[self._make_feed()])
        entry = MagicMock()
        entry.get = lambda key, default="": {
            "link": "",
            "title": "Title Only",
            "summary": "Summary text",
        }.get(key, default)

        assert agent._parse_entry(entry, "Test Feed") is None

    def test_parse_entry_sanitizes_html(self) -> None:
        agent = NewsCollectionAgent(feeds=[self._make_feed()])
        entry = MagicMock()
        entry.get = lambda key, default="": {
            "link": "https://example.com/html",
            "title": "<b>Bold Title</b> &amp; More",
            "summary": "<p>Paragraph with <script>alert(1)</script> HTML</p>",
            "published": "",
        }.get(key, default)

        result = agent._parse_entry(entry, "Test Feed")
        assert result is not None
        assert "<script>" not in result["content"]
        assert "<p>" not in result["content"]

    def test_parse_entry_content_fallback_chain(self) -> None:
        agent = NewsCollectionAgent(feeds=[self._make_feed()])

        # Test: entry with "content" field takes precedence over "summary"
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

    def test_garbage_string_returns_none(self) -> None:
        assert self.agent._parse_date("not-a-real-date-string-xyz") is None


class TestCollectMethod:
    """Test the full collect() orchestration with mocked HTTP."""

    def _make_rss_xml(self, title: str = "Test Article", link: str = "https://example.com/1") -> bytes:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Test Feed</title>
                <item>
                    <title>{title}</title>
                    <link>{link}</link>
                    <description>Test description</description>
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


class TestNoiseFiltering:
    """Test suite for consumer how-tos, entertainment, and noise detection."""

    def test_filters_consumer_how_tos(self) -> None:
        title = "Cara Aktifkan Kartu Kredit Indonesia, Bisa Transaksi QRIS"
        is_noise, reason = is_consumer_or_entertainment_noise(title)
        assert is_noise is True
        assert "Cara" in reason

    def test_filters_recipes_and_tips(self) -> None:
        title = "5 Tips Hemat Listrik Selama Musim Kemarau"
        is_noise, _ = is_consumer_or_entertainment_noise(title)
        assert is_noise is True

        title_resep = "Resep Sambal Goreng Kentang Praktis untuk Pemula"
        is_noise_resep, _ = is_consumer_or_entertainment_noise(title_resep)
        assert is_noise_resep is True

    def test_filters_entertainment_and_horoscopes(self) -> None:
        title = "Ramalan Zodiak Scorpio Hari Ini: Keuangan Menanjak"
        is_noise, _ = is_consumer_or_entertainment_noise(title)
        assert is_noise is True

        title_drakor = "Sinopsis Drakor Queen of Tears Episode Terakhir"
        is_noise_drakor, _ = is_consumer_or_entertainment_noise(title_drakor)
        assert is_noise_drakor is True

    def test_filters_sports_match_results(self) -> None:
        title = "Hasil Liga Inggris: Arsenal Menang Telak 3-0 Lawan Chelsea"
        is_noise, _ = is_consumer_or_entertainment_noise(title)
        assert is_noise is True

    def test_retains_clean_policy_and_economic_news(self) -> None:
        title = "Investasi RI Tembus Rp 1.010 T, Pengusaha Ungkap Dampaknya ke Industri Lokal"
        is_noise, reason = is_consumer_or_entertainment_noise(title)
        assert is_noise is False
        assert reason == "clean_policy_news"

        title_spbu = "Seluruh SPBU di Flores Kembali Beroperasi Usai Gempa"
        is_noise_spbu, _ = is_consumer_or_entertainment_noise(title_spbu)
        assert is_noise_spbu is False

    def test_filters_explainer_and_faq_articles(self) -> None:
        title_ikd = "Apa itu IKD dan cara buatnya? Cek fungsi KTP digital resmi"
        is_noise, reason = is_consumer_or_entertainment_noise(title_ikd)
        assert is_noise is True
        assert "Apa itu" in reason or "dan cara buatnya" in reason

        title_gempa = "Kenapa Indonesia sering gempa? Ini penyebab dan penjelasan megathrust"
        is_noise_gempa, reason_gempa = is_consumer_or_entertainment_noise(title_gempa)
        assert is_noise_gempa is True
        assert "Kenapa" in reason_gempa or "penyebab" in reason_gempa

    def test_filters_gadget_leaks_and_rumors(self) -> None:
        title_airpods = "Bocoran Terbaru AirPods Berkamera, Bisa Apa Saja?"
        is_noise, reason = is_consumer_or_entertainment_noise(title_airpods)
        assert is_noise is True
        assert "Bocoran" in reason or "AirPods" in reason or "Bisa Apa Saja" in reason

        title_iphone = "Rumor iPhone 17 Pro Max: Bocoran Spesifikasi dan Jadwal Rilis"
        is_noise_iphone, _ = is_consumer_or_entertainment_noise(title_iphone)
        assert is_noise_iphone is True

    def test_legislative_whitelist_overrides_noise_words(self) -> None:
        # Title contains "tips" but is an official legislative statement
        title = "Ketua DPR Puan Maharani Bagikan Tips Ketahanan Pangan Nasional"
        is_noise, reason = is_consumer_or_entertainment_noise(title)
        assert is_noise is False
        assert reason == "legislative_whitelist_matched"


class TestFeedHealthMonitor:
    """Test suite for RSS feed health probing and dead feed auto-skip."""

    @patch("src.agents.news_collection.requests.get")
    def test_check_feed_health_healthy(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"""<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0"><channel><title>Antara</title><item><title>News 1</title><link>https://antara.com/1</link></item></channel></rss>"""
        mock_get.return_value = mock_resp

        agent = NewsCollectionAgent(feeds=[FeedConfig(name="Antara", url="https://antara.com/rss", category="nasional")])
        health = agent.check_feed_health(agent.feeds[0])

        assert health["status"] == "HEALTHY"
        assert health["status_code"] == 200
        assert health["entry_count"] == 1
        assert health["error"] is None

    @patch("src.agents.news_collection.requests.get")
    def test_check_feed_health_dead_404(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        agent = NewsCollectionAgent(feeds=[FeedConfig(name="Dead Feed", url="https://dead.com/rss", category="nasional")])
        health = agent.check_feed_health(agent.feeds[0])

        assert health["status"] == "DEAD"
        assert health["status_code"] == 404
        assert "Not Found" in health["error"]

    @patch("src.agents.news_collection.requests.get")
    def test_check_all_feeds_health(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>Feed</title></channel></rss>"""
        mock_get.return_value = mock_resp

        agent = NewsCollectionAgent(feeds=[
            FeedConfig(name="Feed A", url="https://a.com/rss", category="nasional"),
            FeedConfig(name="Feed B", url="https://b.com/rss", category="nasional"),
        ])
        results = agent.check_all_feeds_health()
        assert len(results) == 2
        assert all(r["status_code"] == 200 for r in results)



