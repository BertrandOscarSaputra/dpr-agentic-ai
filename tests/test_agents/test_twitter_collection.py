"""Tests for TwitterCollectionAgent (Scrapfly-based).

Tests cover:
- AKD query loading and construction
- GraphQL XHR response parsing
- Tweet normalization from search timeline data
- Collection flow with mocked Scrapfly client
- Rate limit and error handling
- Graceful fallback when SCRAPFLY_KEY is absent
"""

import asyncio
import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.twitter_collection import (
    AKDQuery,
    TwitterCollectionAgent,
    load_akd_queries,
    parse_search_xhr_response,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_graphql_response(tweets: list[dict]) -> str:
    """Build a minimal SearchTimeline GraphQL JSON response body."""
    entries = []
    for i, tw in enumerate(tweets):
        entries.append({
            "entryId": f"tweet-{i}",
            "content": {
                "itemContent": {
                    "__typename": "TimelineTweet",
                    "tweet_results": {
                        "result": tw,
                    },
                }
            },
        })

    body = {
        "data": {
            "search_by_raw_query": {
                "search_timeline": {
                    "timeline": {
                        "instructions": [
                            {"entries": entries}
                        ]
                    }
                }
            }
        }
    }
    return json.dumps(body)


def _make_tweet_result(
    tweet_id: str = "12345",
    text: str = "Komisi III DPR membahas RUU Hukum Pidana",
    screen_name: str = "kabar_dpr",
    created_at: str = "Tue Jul 29 10:00:00 +0000 2026",
) -> dict:
    return {
        "__typename": "Tweet",
        "rest_id": tweet_id,
        "legacy": {
            "id_str": tweet_id,
            "full_text": text,
            "created_at": created_at,
        },
        "core": {
            "user_results": {
                "result": {
                    "legacy": {
                        "screen_name": screen_name,
                    }
                }
            }
        },
    }


# ---------------------------------------------------------------------------
# TestLoadAKDQueries
# ---------------------------------------------------------------------------

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

    def test_query_includes_dpr_or_dpr_ri(self) -> None:
        queries = load_akd_queries()
        for q in queries:
            assert "DPR" in q.query_str

    def test_query_targets_indonesian_language(self) -> None:
        queries = load_akd_queries()
        for q in queries:
            assert "lang:id" in q.query_str

    def test_queries_are_immutable(self) -> None:
        queries = load_akd_queries()
        assert isinstance(queries, tuple)

    def test_komisi_queries_contain_komisi_name(self) -> None:
        queries = load_akd_queries()
        komisi_i = next(
            (q for q in queries if q.name == "Komisi I"), None,
        )
        assert komisi_i is not None
        assert "Komisi I DPR" in komisi_i.query_str


# ---------------------------------------------------------------------------
# TestParseSearchXhrResponse
# ---------------------------------------------------------------------------

class TestParseSearchXhrResponse:
    """Test parsing GraphQL XHR responses from X.com SearchTimeline."""

    def test_parses_single_tweet(self) -> None:
        body = _make_graphql_response([_make_tweet_result()])
        results = parse_search_xhr_response(body)
        assert len(results) == 1
        assert results[0]["source_type"] == "twitter"
        assert results[0]["content"] == "Komisi III DPR membahas RUU Hukum Pidana"
        assert results[0]["url"] == "https://x.com/i/status/12345"
        assert results[0]["source_name"] == "@kabar_dpr"

    def test_parses_multiple_tweets(self) -> None:
        tweets = [_make_tweet_result(tweet_id=str(i), text=f"DPR tweet {i}") for i in range(5)]
        body = _make_graphql_response(tweets)
        results = parse_search_xhr_response(body)
        assert len(results) == 5

    def test_returns_empty_for_invalid_json(self) -> None:
        results = parse_search_xhr_response("not-json{{{")
        assert results == []

    def test_returns_empty_for_empty_body(self) -> None:
        results = parse_search_xhr_response("")
        assert results == []

    def test_returns_empty_for_empty_timeline(self) -> None:
        body = json.dumps({"data": {"search_by_raw_query": {"search_timeline": {"timeline": {"instructions": []}}}}})
        results = parse_search_xhr_response(body)
        assert results == []

    def test_title_truncated_at_80_chars(self) -> None:
        long_text = "A" * 120
        body = _make_graphql_response([_make_tweet_result(text=long_text)])
        results = parse_search_xhr_response(body)
        assert len(results) == 1
        assert len(results[0]["title"]) <= 84  # 80 + "..."

    def test_parses_twitter_date_format(self) -> None:
        body = _make_graphql_response([_make_tweet_result(created_at="Tue Jul 29 10:00:00 +0000 2026")])
        results = parse_search_xhr_response(body)
        assert results[0]["published_at"].year == 2026
        assert results[0]["published_at"].tzinfo is not None

    def test_source_name_fallback_when_no_user(self) -> None:
        tweet = {
            "__typename": "Tweet",
            "rest_id": "999",
            "legacy": {"id_str": "999", "full_text": "DPR tweet test", "created_at": "Tue Jul 29 10:00:00 +0000 2026"},
            "core": {"user_results": {"result": {"legacy": {}}}},
        }
        body = _make_graphql_response([tweet])
        results = parse_search_xhr_response(body)
        assert len(results) == 1
        assert results[0]["source_name"] == "X / Twitter"

    def test_skips_tweet_with_no_id(self) -> None:
        tweet = {
            "__typename": "Tweet",
            "legacy": {"full_text": "test", "created_at": "Tue Jul 29 10:00:00 +0000 2026"},
            "core": {"user_results": {"result": {"legacy": {"screen_name": "user"}}}},
        }
        body = _make_graphql_response([tweet])
        results = parse_search_xhr_response(body)
        assert results == []

    def test_skips_tweet_with_no_text(self) -> None:
        tweet = _make_tweet_result(text="")
        body = _make_graphql_response([tweet])
        results = parse_search_xhr_response(body)
        assert results == []

    def test_handles_tweet_with_visibility_wrapper(self) -> None:
        """TweetWithVisibilityResults wraps the tweet under 'tweet' key."""
        inner = _make_tweet_result(tweet_id="777", text="Rapat DPR hari ini")
        wrapped = {"__typename": "TweetWithVisibilityResults", "tweet": inner}
        entries = [{
            "entryId": "tweet-0",
            "content": {
                "itemContent": {
                    "__typename": "TimelineTweet",
                    "tweet_results": {"result": wrapped},
                }
            },
        }]
        body = json.dumps({
            "data": {"search_by_raw_query": {"search_timeline": {"timeline": {"instructions": [{"entries": entries}]}}}}
        })
        results = parse_search_xhr_response(body)
        assert len(results) == 1
        assert results[0]["url"] == "https://x.com/i/status/777"


# ---------------------------------------------------------------------------
# TestCollectWithMockedScrapfly
# ---------------------------------------------------------------------------

class TestCollectWithMockedScrapfly:
    """Test full collection flow with mocked Scrapfly client."""

    def test_collect_returns_empty_without_scrapfly_key(self) -> None:
        with patch("src.agents.twitter_collection.settings") as mock_settings:
            mock_settings.SCRAPFLY_KEY = ""
            agent = TwitterCollectionAgent(queries=())
            result = asyncio.run(agent.collect())
            assert result == []

    @patch("src.agents.twitter_collection.settings")
    @patch("src.agents.twitter_collection._scrape_search_page")
    def test_collect_returns_tweets(self, mock_scrape: MagicMock, mock_settings: MagicMock) -> None:
        mock_settings.SCRAPFLY_KEY = "scp-test-key"
        mock_settings.TWITTER_MAX_RESULTS_PER_QUERY = 20
        mock_scrape.return_value = [
            {
                "source_type": "twitter",
                "source_name": "@dpr_ri",
                "content": "DPR bahas RUU pertahanan nasional",
                "title": "DPR bahas RUU pertahanan nasional",
                "url": "https://x.com/i/status/111",
                "published_at": datetime(2026, 8, 8, 10, 0, 0, tzinfo=UTC),
            }
        ]

        query = AKDQuery(name="Komisi I", full_name="Pertahanan", query_str="test query")
        agent = TwitterCollectionAgent(queries=(query,), delay_seconds=0)
        result = asyncio.run(agent.collect())

        assert len(result) == 1
        assert result[0]["source_type"] == "twitter"
        assert result[0]["source_name"] == "@dpr_ri"

    @patch("src.agents.twitter_collection.settings")
    @patch("src.agents.twitter_collection._scrape_search_page")
    def test_collect_deduplicates_tweets(self, mock_scrape: MagicMock, mock_settings: MagicMock) -> None:
        """Same tweet URL from two queries should appear only once."""
        mock_settings.SCRAPFLY_KEY = "scp-test-key"
        mock_settings.TWITTER_MAX_RESULTS_PER_QUERY = 20
        duplicate = {
            "source_type": "twitter",
            "source_name": "@dpr_ri",
            "content": "DPR tweet",
            "title": "DPR tweet",
            "url": "https://x.com/i/status/111",
            "published_at": datetime(2026, 8, 8, 10, 0, 0, tzinfo=UTC),
        }
        mock_scrape.return_value = [duplicate]

        queries = (
            AKDQuery(name="Komisi I", full_name="Pertahanan", query_str="q1"),
            AKDQuery(name="Komisi II", full_name="Dalam Negeri", query_str="q2"),
        )
        agent = TwitterCollectionAgent(queries=queries, delay_seconds=0)
        result = asyncio.run(agent.collect())

        assert len(result) == 1  # deduplicated

    @patch("src.agents.twitter_collection._scrape_search_page")
    def test_collect_handles_empty_response(self, mock_scrape: MagicMock) -> None:
        mock_scrape.return_value = []
        query = AKDQuery(name="Komisi II", full_name="Dalam Negeri", query_str="test")
        agent = TwitterCollectionAgent(queries=(query,), delay_seconds=0)
        result = asyncio.run(agent.collect())
        assert result == []

    @patch("src.agents.twitter_collection.settings")
    @patch("src.agents.twitter_collection._scrape_search_page")
    def test_collect_isolates_per_query_errors(self, mock_scrape: MagicMock, mock_settings: MagicMock) -> None:
        """One failing query should not prevent others from collecting."""
        mock_settings.SCRAPFLY_KEY = "scp-test-key"
        mock_settings.TWITTER_MAX_RESULTS_PER_QUERY = 20
        good_tweet = {
            "source_type": "twitter",
            "source_name": "@berita",
            "content": "Diskusi hukum di Komisi III DPR",
            "title": "Diskusi hukum",
            "url": "https://x.com/i/status/222",
            "published_at": datetime(2026, 8, 8, 10, 0, 0, tzinfo=UTC),
        }

        call_count = 0

        async def side_effect(query_str, max_results=20):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("Scrapfly error")
            return [good_tweet]

        mock_scrape.side_effect = side_effect

        queries = (
            AKDQuery(name="Bad", full_name="Bad", query_str="fail"),
            AKDQuery(name="Good", full_name="Good", query_str="ok"),
        )
        agent = TwitterCollectionAgent(queries=queries, delay_seconds=0)
        result = asyncio.run(agent.collect())

        assert len(result) == 1
        assert result[0]["source_type"] == "twitter"

    @patch("src.agents.twitter_collection._scrape_search_page")
    def test_collect_handles_rate_limit(self, mock_scrape: MagicMock) -> None:
        mock_scrape.return_value = []  # rate limit → empty list
        query = AKDQuery(name="Komisi XI", full_name="Keuangan", query_str="test")
        agent = TwitterCollectionAgent(queries=(query,), delay_seconds=0)
        result = asyncio.run(agent.collect())
        assert result == []
