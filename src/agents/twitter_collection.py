"""Twitter Collection Agent — collects tweets related to DPR RI topics.

Uses Scrapfly to render X.com search pages in a real browser and captures
the GraphQL SearchTimeline XHR responses. No cookies or credentials needed —
Scrapfly handles anti-bot protection and proxy rotation automatically.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from src.config import settings
from src.utils.validators import sanitize_text

logger = logging.getLogger(__name__)

AKD_MASTER_PATH = (
    Path(__file__).resolve().parents[2] / "kamus" / "akd_master.json"
)

# X.com search URL template (latest/live results)
SEARCH_URL = "https://x.com/search?q={query}&src=typed_query&f=live"


@dataclass(frozen=True)
class AKDQuery:
    """Represents a search query targeted at a specific AKD."""

    name: str
    full_name: str
    query_str: str


def load_akd_queries(
    file_path: Path = AKD_MASTER_PATH,
    since_days: int = 7,
) -> tuple[AKDQuery, ...]:
    """Load AKD keywords from JSON and construct search queries."""
    if not file_path.exists():
        logger.warning(
            "AKD master file not found",
            extra={"path": str(file_path)},
        )
        return ()

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(
            "Failed to parse AKD master JSON",
            extra={"error": str(e)},
        )
        return ()

    since_date = (datetime.now(UTC) - timedelta(days=since_days)).strftime("%Y-%m-%d")

    queries: list[AKDQuery] = []
    for item in data.get("akd", []):
        name = item.get("name", "")
        full_name = item.get("full_name") or item.get("scope") or name
        keywords = item.get("keywords", [])

        if not name or not keywords:
            continue

        # Build clean, targeted search query: e.g., "Komisi I DPR" OR "Komisi I DPR RI"
        if "DPR" in name:
            query_str = f'"{name}" lang:id'
        else:
            query_str = f'"{name} DPR" OR "{name} DPR RI" lang:id'

        queries.append(
            AKDQuery(
                name=name,
                full_name=full_name,
                query_str=query_str,
            )
        )

    return tuple(queries)


def _parse_tweet_from_result(tweet_result: dict[str, Any]) -> dict[str, Any] | None:
    """Parse a tweet from a GraphQL tweet_result entry."""
    try:
        # Handle tweet type
        typename = tweet_result.get("__typename", "")
        if typename == "TweetWithVisibilityResults":
            tweet_result = tweet_result.get("tweet", {})

        legacy = tweet_result.get("legacy", {})
        if not legacy:
            return None

        tweet_id = legacy.get("id_str") or tweet_result.get("rest_id")
        text = legacy.get("full_text") or legacy.get("text", "")

        if not tweet_id or not text:
            return None

        cleaned = sanitize_text(text)
        if not cleaned:
            return None

        # Username
        core = tweet_result.get("core", {})
        user_results = core.get("user_results", {}).get("result", {})
        user_legacy = user_results.get("legacy", {})
        screen_name = user_legacy.get("screen_name", "")
        source_name = f"@{screen_name}" if screen_name else "X / Twitter"

        # Title
        title = cleaned[:80] + "..." if len(cleaned) > 80 else cleaned

        # URL
        url = f"https://x.com/i/status/{tweet_id}"

        # Timestamp
        created_at_str = legacy.get("created_at", "")
        published_at: datetime | None = None
        if created_at_str:
            try:
                from dateutil import parser as dateutil_parser
                dt = dateutil_parser.parse(created_at_str)
                published_at = dt if dt.tzinfo else dt.replace(tzinfo=UTC)
            except Exception:
                published_at = datetime.now(UTC)
        else:
            published_at = datetime.now(UTC)

        return {
            "source_type": "twitter",
            "source_name": source_name,
            "content": cleaned,
            "title": title,
            "url": url,
            "published_at": published_at,
        }
    except Exception as e:
        logger.debug("Failed to parse tweet result", extra={"error": str(e)})
        return None


def parse_search_xhr_response(xhr_body: str) -> list[dict[str, Any]]:
    """Parse tweets from a SearchTimeline GraphQL XHR response body."""
    try:
        data = json.loads(xhr_body)
    except Exception:
        return []

    tweets: list[dict[str, Any]] = []

    try:
        # Navigate into the GraphQL response structure
        timeline = (
            data.get("data", {})
            .get("search_by_raw_query", {})
            .get("search_timeline", {})
            .get("timeline", {})
        )
        instructions = timeline.get("instructions", [])

        for instruction in instructions:
            entries = instruction.get("entries", [])
            for entry in entries:
                content = entry.get("content", {})

                # Single tweet entry
                item_content = content.get("itemContent", {})
                if item_content.get("__typename") == "TimelineTweet":
                    tweet_result = item_content.get("tweet_results", {}).get("result", {})
                    parsed = _parse_tweet_from_result(tweet_result)
                    if parsed:
                        tweets.append(parsed)

                # Module entries (multiple tweets in one)
                items = content.get("items", [])
                for item in items:
                    ic = item.get("item", {}).get("itemContent", {})
                    if ic.get("__typename") == "TimelineTweet":
                        tweet_result = ic.get("tweet_results", {}).get("result", {})
                        parsed = _parse_tweet_from_result(tweet_result)
                        if parsed:
                            tweets.append(parsed)
    except Exception as e:
        logger.debug("Error parsing search XHR response", extra={"error": str(e)})

    return tweets


async def _scrape_search_page(
    query_str: str,
    max_results: int = 20,
) -> list[dict[str, Any]]:
    """Scrape X.com search page using Scrapfly and extract tweets from XHR."""
    try:
        from scrapfly import ScrapeConfig, ScrapflyClient
    except ImportError:
        logger.error("scrapfly-sdk not installed — run: uv add scrapfly-sdk")
        return []

    if not settings.SCRAPFLY_KEY:
        logger.warning(
            "SCRAPFLY_KEY not set — Twitter collection disabled",
            extra={"status": "disabled"},
        )
        return []

    encoded_query = quote_plus(query_str)
    url = SEARCH_URL.format(query=encoded_query)

    client = ScrapflyClient(key=settings.SCRAPFLY_KEY)

    try:
        config_kwargs: dict[str, Any] = {
            "url": url,
            "asp": True,
            "render_js": True,
            "wait_for_selector": "xhr:*SearchTimeline*",
            "rendering_wait": 3000,
            "lang": "id-ID,id,en-US",
            "retry": True,
        }

        result = await client.async_scrape(ScrapeConfig(**config_kwargs))

        status_code = getattr(result, "status_code", 0)
        xhr_calls = result.scrape_result.get("browser_data", {}).get("xhr_call", [])
        search_xhrs = [x for x in xhr_calls if "SearchTimeline" in x.get("url", "")]

        if status_code != 200 or not search_xhrs:
            logger.warning(
                "Scrapfly search page fetch warning",
                extra={"query": query_str[:60], "status": status_code, "xhr_total": len(xhr_calls), "search_xhrs": len(search_xhrs)},
            )
            print(f"Scrapfly warning [{query_str[:30]}]: status={status_code}, xhr_total={len(xhr_calls)}, search_xhrs={len(search_xhrs)}")

        for xhr in search_xhrs:
            response = xhr.get("response")
            if not response:
                continue
            body = response.get("body", "")
            if not body:
                continue

            tweets = parse_search_xhr_response(body)
            if tweets:
                logger.info(
                    "Scraped tweets via Scrapfly SearchTimeline XHR",
                    extra={"query": query_str[:60], "count": len(tweets)},
                )
                print(f"✅ [{query_str[:30]}]: Scraped {len(tweets)} tweets")
                return tweets[:max_results]

    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "rate" in err_msg.lower():
            logger.warning(
                "Scrapfly rate limit or X rate limit reached",
                extra={"query": query_str[:60]},
            )
        else:
            logger.warning(
                "Search query returned error",
                extra={"query": query_str[:60], "error": err_msg},
            )

    return []


class TwitterCollectionAgent:
    """Collects tweets about DPR RI topics using Scrapfly browser scraping."""

    def __init__(
        self,
        queries: tuple[AKDQuery, ...] | None = None,
        max_results: int | None = None,
        delay_seconds: float = 2.0,
    ) -> None:
        self.queries = queries if queries is not None else load_akd_queries()
        self.max_results = max_results or settings.TWITTER_MAX_RESULTS_PER_QUERY
        self.delay_seconds = delay_seconds

    def parse_tweet(self, tweet: Any) -> dict[str, Any] | None:
        """Parse a twikit-style tweet object (kept for backwards compat with tests)."""
        return _parse_tweet_from_result(tweet) if isinstance(tweet, dict) else None

    async def collect(self) -> list[dict[str, Any]]:
        """Collect tweets across all AKD search queries via Scrapfly.

        Returns:
            Flat list of normalized ContentItem dictionaries.
        """
        if not settings.SCRAPFLY_KEY:
            logger.warning(
                "Skipping Twitter collection — SCRAPFLY_KEY not configured",
                extra={},
            )
            return []

        all_tweets: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        logger.info(
            "Starting Twitter collection via Scrapfly",
            extra={"queries_count": len(self.queries)},
        )

        for akd_q in self.queries:
            try:
                tweets = await _scrape_search_page(
                    akd_q.query_str,
                    max_results=self.max_results,
                )
                for tweet in tweets:
                    url = tweet.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_tweets.append(tweet)

                if tweets:
                    await asyncio.sleep(self.delay_seconds)

            except Exception as e:
                import traceback
                logger.error(
                    "Error querying tweets for AKD",
                    extra={"akd": akd_q.name, "error": str(e), "traceback": traceback.format_exc()},
                )
                print(f"Error querying {akd_q.name}: {e}\n{traceback.format_exc()}")
                continue

        logger.info(
            "Twitter collection complete",
            extra={"total_collected": len(all_tweets)},
        )
        return all_tweets
