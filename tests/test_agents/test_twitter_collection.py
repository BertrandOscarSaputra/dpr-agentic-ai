"""Tests for TwitterCollectionAgent (twikit-based).

Tests cover:
- AKD query loading and construction
- Tweet parsing and normalization
- Collection flow with mocked twikit client
- Rate limit and error handling
- Graceful fallback when credentials are absent
"""

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.twitter_collection import (
    AKDQuery,
    TwitterCollectionAgent,
    load_akd_queries,
)


class TestLoadAKDQueries:
    """Test query loading from kamus/akd_master.json."""

    def test_loads_queries_from_json(self) -> None:
        queries = load_akd_queries()
        assert isinstance(queries, tuple)
        assert len(queries) > 0

    def test_query_has_required_fields(self) -> None:
        queries = load_akd_queries()
        for q in queries:
            assert q.name, "Query must have a name"
            assert q.full_name, "Query must have a full_name"
            assert q.query_str, "Query must have a query_str"

    def test_query_contains_dpr_keyword(self) -> None:
        queries = load_akd_queries()
        for q in queries:
            assert "DPR" in q.query_str

    def test_query_includes_recency_filter(self) -> None:
        queries = load_akd_queries()
        for q in queries:
            assert "since:" in q.query_str

    def test_query_targets_indonesian_language(self) -> None:
        queries = load_akd_queries()
        for q in queries:
            assert "lang:id" in q.query_str

    def test_queries_are_immutable(self) -> None:
        queries = load_akd_queries()
        assert isinstance(queries, tuple)

    def test_multi_word_keywords_are_quoted(self) -> None:
        """Keywords like 'luar negeri' should be wrapped in quotes."""
        queries = load_akd_queries()
        komisi_i = next(
            (q for q in queries if q.name == "Komisi I"), None,
        )
        assert komisi_i is not None
        assert '"luar negeri"' in komisi_i.query_str


class TestTweetParsing:
    """Test parsing and normalization of twikit tweet objects."""

    def _make_agent(self) -> TwitterCollectionAgent:
        return TwitterCollectionAgent(queries=())

    def _make_tweet(
        self,
        tweet_id: str = "12345",
        text: str = "Komisi III DPR membahas RUU Hukum Pidana",
        created_at: str | None = None,
        username: str = "kabar_dpr",
    ) -> SimpleNamespace:
        user = SimpleNamespace(
            screen_name=username,
            name=f"User {username}",
        )
        return SimpleNamespace(
            id=tweet_id,
            text=text,
            created_at=created_at or "Tue Jul 29 10:00:00 +0000 2026",
            user=user,
        )

    def test_parses_valid_tweet(self) -> None:
        agent = self._make_agent()
        tweet = self._make_tweet()
        result = agent.parse_tweet(tweet)
        assert result is not None
        assert result["source_type"] == "twitter"
        assert result["content"] == "Komisi III DPR membahas RUU Hukum Pidana"
        assert result["url"] == "https://x.com/i/status/12345"

    def test_maps_username_from_tweet_user(self) -> None:
        agent = self._make_agent()
        tweet = self._make_tweet(username="dpr_ri")
        result = agent.parse_tweet(tweet)
        assert result is not None
        assert result["source_name"] == "@dpr_ri"

    def test_fallback_source_name_without_user(self) -> None:
        agent = self._make_agent()
        tweet = SimpleNamespace(
            id="999",
            text="Some tweet",
            created_at="Tue Jul 29 10:00:00 +0000 2026",
            user=None,
        )
        result = agent.parse_tweet(tweet)
        assert result is not None
        assert result["source_name"] == "X / Twitter"

    def test_returns_none_for_no_id(self) -> None:
        agent = self._make_agent()
        tweet = SimpleNamespace(
            id=None, text="Some text", created_at=None, user=None,
        )
        assert agent.parse_tweet(tweet) is None

    def test_returns_none_for_no_text(self) -> None:
        agent = self._make_agent()
        tweet = SimpleNamespace(
            id="123", text="", created_at=None, user=None,
        )
        assert agent.parse_tweet(tweet) is None

    def test_strips_html_from_tweet_text(self) -> None:
        agent = self._make_agent()
        tweet = self._make_tweet(text="<b>Bold</b> statement by DPR")
        result = agent.parse_tweet(tweet)
        assert result is not None
        assert "<b>" not in result["content"]
        assert "Bold" in result["content"]

    def test_title_truncated_at_80_chars(self) -> None:
        agent = self._make_agent()
        long_text = "A" * 120
        tweet = self._make_tweet(text=long_text)
        result = agent.parse_tweet(tweet)
        assert result is not None
        assert len(result["title"]) <= 84  # 80 + "..."

    def test_parses_twitter_date_format(self) -> None:
        agent = self._make_agent()
        tweet = self._make_tweet(
            created_at="Tue Jul 29 10:00:00 +0000 2026",
        )
        result = agent.parse_tweet(tweet)
        assert result is not None
        assert result["published_at"] is not None
        assert result["published_at"].year == 2026
        assert result["published_at"].tzinfo is not None

    def test_parses_iso_string_date(self) -> None:
        agent = self._make_agent()
        tweet = self._make_tweet(
            created_at="2026-07-29T10:00:00Z",
        )
        result = agent.parse_tweet(tweet)
        assert result is not None
        assert result["published_at"] is not None
        assert result["published_at"].year == 2026

    def test_parses_datetime_object(self) -> None:
        agent = self._make_agent()
        dt = datetime(2026, 7, 29, 10, 0, 0, tzinfo=UTC)
        tweet = self._make_tweet()
        tweet.created_at = dt
        result = agent.parse_tweet(tweet)
        assert result is not None
        assert result["published_at"] == dt

    def test_handles_invalid_date_gracefully(self) -> None:
        agent = self._make_agent()
        tweet = self._make_tweet(created_at="not-a-date")
        result = agent.parse_tweet(tweet)
        assert result is not None
        assert result["published_at"] is None


class TestCollectWithMockedClient:
    """Test full collection flow with mocked twikit client."""

    @patch("src.agents.twitter_collection._create_twikit_client")
    def test_collect_returns_empty_when_no_client(
        self, mock_create: MagicMock,
    ) -> None:
        mock_create.return_value = None
        agent = TwitterCollectionAgent(queries=())
        result = asyncio.run(agent.collect())
        assert result == []

    @patch("src.agents.twitter_collection._create_twikit_client")
    def test_collect_parses_twikit_response(
        self, mock_create: MagicMock,
    ) -> None:
        mock_client = AsyncMock()
        mock_create.return_value = mock_client

        user = SimpleNamespace(screen_name="kabar_dpr", name="Kabar")
        tweet = SimpleNamespace(
            id="111",
            text="DPR bahas RUU pertahanan nasional",
            created_at="Tue Jul 29 12:00:00 +0000 2026",
            user=user,
        )
        mock_client.search_tweet = AsyncMock(return_value=[tweet])

        query = AKDQuery(
            name="Komisi I",
            full_name="Pertahanan",
            query_str="test query",
        )
        agent = TwitterCollectionAgent(queries=(query,))
        result = asyncio.run(agent.collect())

        assert len(result) == 1
        assert result[0]["source_type"] == "twitter"
        assert result[0]["source_name"] == "@kabar_dpr"
        assert "pertahanan" in result[0]["content"].lower()

    @patch("src.agents.twitter_collection._create_twikit_client")
    def test_collect_handles_empty_response(
        self, mock_create: MagicMock,
    ) -> None:
        mock_client = AsyncMock()
        mock_create.return_value = mock_client
        mock_client.search_tweet = AsyncMock(return_value=[])

        query = AKDQuery(
            name="Komisi II",
            full_name="Dalam Negeri",
            query_str="test",
        )
        agent = TwitterCollectionAgent(queries=(query,))
        result = asyncio.run(agent.collect())
        assert result == []

    @patch("src.agents.twitter_collection._create_twikit_client")
    def test_collect_isolates_per_query_errors(
        self, mock_create: MagicMock,
    ) -> None:
        """One failing query should not prevent others."""
        mock_client = AsyncMock()
        mock_create.return_value = mock_client

        good_tweet = SimpleNamespace(
            id="222",
            text="Diskusi hukum di Komisi III DPR",
            created_at="Tue Jul 29 12:00:00 +0000 2026",
            user=SimpleNamespace(screen_name="berita", name="B"),
        )

        async def side_effect(query, *args, **kwargs):
            if "FAIL" in query:
                raise RuntimeError("API error")
            return [good_tweet]

        mock_client.search_tweet = AsyncMock(
            side_effect=side_effect,
        )

        queries = (
            AKDQuery(
                name="Bad", full_name="Bad", query_str="FAIL query",
            ),
            AKDQuery(
                name="Good", full_name="Good", query_str="ok query",
            ),
        )
        agent = TwitterCollectionAgent(queries=queries)
        result = asyncio.run(agent.collect())

        # "Bad" fails, "Good" returns 1 tweet
        assert len(result) == 1
        assert result[0]["source_type"] == "twitter"

    @patch("src.agents.twitter_collection._create_twikit_client")
    def test_collect_handles_rate_limit(
        self, mock_create: MagicMock,
    ) -> None:
        mock_client = AsyncMock()
        mock_create.return_value = mock_client

        class TooManyRequests(Exception):  # noqa: N818
            pass

        mock_client.search_tweet = AsyncMock(
            side_effect=TooManyRequests("Rate limit"),
        )

        query = AKDQuery(
            name="Komisi XI",
            full_name="Keuangan",
            query_str="test",
        )
        agent = TwitterCollectionAgent(queries=(query,))
        result = asyncio.run(agent.collect())
        assert result == []

    @patch("src.agents.twitter_collection._create_twikit_client")
    def test_collect_respects_max_results(
        self, mock_create: MagicMock,
    ) -> None:
        """Agent should stop collecting after max_results per query."""
        mock_client = AsyncMock()
        mock_create.return_value = mock_client

        # Return 50 tweets but max_results is 10
        tweets = [
            SimpleNamespace(
                id=str(i),
                text=f"Tweet {i} about DPR",
                created_at="Tue Jul 29 12:00:00 +0000 2026",
                user=SimpleNamespace(screen_name="u", name="U"),
            )
            for i in range(50)
        ]
        mock_client.search_tweet = AsyncMock(return_value=tweets)

        query = AKDQuery(
            name="Test", full_name="Test", query_str="test",
        )
        agent = TwitterCollectionAgent(queries=(query,))
        agent.max_results = 10
        result = asyncio.run(agent.collect())

        assert len(result) == 10
