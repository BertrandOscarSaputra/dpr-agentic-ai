"""News Collection Agent — collects news articles via RSS feeds.

Fetches from 12+ Indonesian Tier-1 media RSS feeds, parses and sanitizes
the content, and returns normalized article dicts ready for DB persistence.
"""

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

import feedparser
import requests
from dateutil import parser as dateutil_parser

from src.config import settings
from src.utils.validators import sanitize_text

logger = logging.getLogger(__name__)

FEEDS_JSON_PATH = Path(__file__).resolve().parents[2] / "kamus" / "feeds.json"


@dataclass(frozen=True)
class FeedConfig:
    """Configuration for a single RSS feed source."""

    name: str
    url: str
    category: str


@lru_cache(maxsize=1)
def load_feed_configs() -> tuple[FeedConfig, ...]:
    """Load RSS feed configurations from kamus/feeds.json."""
    with open(FEEDS_JSON_PATH) as f:
        data = json.load(f)
    return tuple(
        FeedConfig(name=feed["name"], url=feed["url"], category=feed["category"])
        for feed in data["feeds"]
    )


class NewsCollectionAgent:
    """Collects and normalizes news articles from RSS feeds.

    Responsibilities:
    - Fetch RSS feeds with timeout protection
    - Parse XML entries via feedparser
    - Sanitize HTML content and normalize text
    - Parse dates robustly across multiple formats
    - Isolate errors per-feed (one broken feed doesn't kill the run)
    """

    def __init__(self, feeds: list[FeedConfig] | None = None) -> None:
        self.feeds = feeds or list(load_feed_configs())
        self.timeout = settings.NEWS_FEED_TIMEOUT

    async def collect(self) -> list[dict]:
        """Collect articles from all configured RSS feeds.

        Returns:
            List of normalized article dicts with keys:
            title, content, url, published_at, source_type, source_name
        """
        all_articles: list[dict] = []

        for feed in self.feeds:
            try:
                articles = self._fetch_feed(feed)
                all_articles.extend(articles)
                logger.info(
                    "Feed fetched successfully",
                    extra={"feed_name": feed.name, "article_count": len(articles)},
                )
            except requests.Timeout:
                logger.warning(
                    "Feed timed out",
                    extra={"feed_name": feed.name, "timeout": self.timeout},
                )
            except requests.RequestException as exc:
                logger.error(
                    "Feed network error",
                    extra={"feed_name": feed.name, "error": str(exc)},
                )
            except Exception as exc:
                logger.error(
                    "Feed processing failed",
                    extra={"feed_name": feed.name, "error": str(exc)},
                )

        logger.info(
            "News collection complete",
            extra={"total_articles": len(all_articles), "feeds_count": len(self.feeds)},
        )
        return all_articles

    def _fetch_feed(self, feed: FeedConfig) -> list[dict]:
        """Fetch and parse a single RSS feed.

        Uses requests for HTTP (with timeout), then feedparser for XML parsing.
        This gives us control over timeouts that feedparser.parse(url) lacks.
        """
        response = requests.get(
            feed.url,
            timeout=self.timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            },
        )
        response.raise_for_status()

        parsed = feedparser.parse(response.content)

        if parsed.bozo and not parsed.entries:
            logger.warning(
                "Feed XML malformed and empty",
                extra={"feed_name": feed.name, "bozo_exception": str(parsed.bozo_exception)},
            )
            return []

        articles: list[dict] = []
        for entry in parsed.entries:
            article = self._parse_entry(entry, feed.name)
            if article is not None:
                articles.append(article)

        return articles

    def _parse_entry(self, entry: feedparser.FeedParserDict, feed_name: str) -> dict | None:
        """Parse a single RSS feed entry into a normalized dict.

        Returns None if the entry has no usable content or URL.
        """
        url = entry.get("link", "").strip()
        if not url:
            return None

        # Extract content: prefer full content, fall back to summary
        content = ""
        if hasattr(entry, "content") and entry.content:
            content = entry.content[0].get("value", "")
        if not content:
            content = entry.get("summary", "")
        if not content:
            content = entry.get("description", "")

        # Sanitize HTML and normalize whitespace
        content = sanitize_text(content)
        if not content:
            return None

        title = sanitize_text(entry.get("title", ""))
        published_at = self._parse_date(entry.get("published", ""))

        return {
            "title": title or None,
            "content": content,
            "url": url,
            "published_at": published_at,
            "source_type": "news_online",
            "source_name": feed_name,
        }

    def _parse_date(self, date_str: str) -> datetime | None:
        """Parse various RSS date formats into a timezone-aware datetime.

        Handles RFC 822, ISO 8601, and other common formats.
        Returns None if parsing fails.
        """
        if not date_str:
            return None
        try:
            dt = dateutil_parser.parse(date_str)
            # Ensure timezone-aware (default to UTC if naive)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return dt
        except (ValueError, OverflowError):
            logger.debug(
                "Date parse failed",
                extra={"date_str": date_str},
            )
            return None
