"""Twitter Collection Agent — collects tweets related to DPR RI topics.

Uses twikit library to scrape X/Twitter without official API access.
Authentication is handled via session cookies (cookies.json) or X account
credentials (username/email/password) with cookie persistence.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from src.config import settings
from src.utils.validators import sanitize_text

logger = logging.getLogger(__name__)

AKD_MASTER_PATH = (
    Path(__file__).resolve().parents[2] / "kamus" / "akd_master.json"
)
COOKIES_PATH = Path(settings.X_COOKIES_PATH)


@dataclass(frozen=True)
class AKDQuery:
    """Represents a search query targeted at a specific AKD."""

    name: str
    full_name: str
    query_str: str


def load_akd_queries(
    file_path: Path = AKD_MASTER_PATH,
    since_days: int = 90,
) -> tuple[AKDQuery, ...]:
    """Load AKD keywords from JSON and construct search queries with date filter for recent tweets."""
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

        # Build keyword clause: e.g., (pertahanan OR "luar negeri" OR TNI)
        formatted_kw = []
        for kw in keywords:
            if " " in kw:
                formatted_kw.append(f'"{kw}"')
            else:
                formatted_kw.append(kw)

        kw_clause = " OR ".join(formatted_kw)

        # Query: (DPR OR "DPR RI") (<keywords>) lang:id since:YYYY-MM-DD
        query_str = f'(DPR OR "DPR RI") ({kw_clause}) lang:id since:{since_date}'
        queries.append(
            AKDQuery(
                name=name,
                full_name=full_name,
                query_str=query_str,
            )
        )

    return tuple(queries)


async def _create_twikit_client() -> Any | None:
    """Create and authenticate a twikit Client.

    Tries to load existing cookies first. If cookies are expired or
    missing, falls back to full login with username/email/password.
    Returns None if credentials are not configured.
    """
    try:
        from twikit import Client

        client = Client("id-ID")

        # 1. Try loading existing cookies first (bypasses Cloudflare block)
        if COOKIES_PATH.exists():
            try:
                with open(COOKIES_PATH, encoding="utf-8") as f:
                    cookie_data = json.load(f)

                if isinstance(cookie_data, list):
                    cookie_dict = {}
                    for item in cookie_data:
                        c_name = item.get("name") or item.get("key")
                        val = item.get("value")
                        if c_name and val:
                            cookie_dict[c_name] = val
                    cookie_data = cookie_dict

                if isinstance(cookie_data, dict) and cookie_data:
                    client.set_cookies(cookie_data)
                    logger.info(
                        "Loaded existing X session cookies from file",
                        extra={"path": str(COOKIES_PATH), "cookies_count": len(cookie_data)},
                    )
                    return client
            except Exception as e:
                logger.warning(
                    "Stored cookies.json invalid or corrupt",
                    extra={"error": str(e)},
                )

        if not settings.X_USERNAME or not settings.X_PASSWORD:
            logger.warning(
                "X credentials not set and cookies.json missing — Twitter collection disabled.",
                extra={"status": "disabled"},
            )
            return None

        # 2. Full programmatic login fallback
        await client.login(
            auth_info_1=settings.X_USERNAME,
            auth_info_2=settings.X_EMAIL,
            password=settings.X_PASSWORD,
        )

        # Save cookies for next runs
        client.save_cookies(str(COOKIES_PATH))
        logger.info(
            "Authenticated to X and saved cookies",
            extra={"user": settings.X_USERNAME},
        )
        return client

    except ImportError:
        logger.error(
            "twikit not installed — run: uv add twikit",
            extra={},
        )
    except Exception as e:
        logger.error(
            "X authentication failed",
            extra={"error": str(e)},
        )
    return None


class TwitterCollectionAgent:
    """Collects tweets for AKD topics and normalizes them for analysis."""

    def __init__(
        self,
        queries: tuple[AKDQuery, ...] | None = None,
        max_results: int | None = None,
    ) -> None:
        self.queries = queries if queries is not None else load_akd_queries()
        self.max_results = max_results or settings.TWITTER_MAX_RESULTS_PER_QUERY

    def parse_tweet(self, tweet: Any) -> dict[str, Any] | None:
        """Extract and normalize fields from a twikit Tweet object.

        Args:
            tweet: twikit Tweet object with .id, .text, .user,
                   .created_at attributes.

        Returns:
            Normalized dict matching ContentItem schema, or None.
        """
        try:
            tweet_id = getattr(tweet, "id", None)
            text = getattr(tweet, "text", None)
            created_at_str = getattr(tweet, "created_at", None)
            user = getattr(tweet, "user", None)
        except AttributeError:
            return None

        if not tweet_id or not text:
            return None

        cleaned = sanitize_text(text)
        if not cleaned:
            return None

        # Build source name
        username = ""
        if user:
            username = getattr(user, "screen_name", "") or getattr(
                user, "name", ""
            )
        source_name = f"@{username}" if username else "X / Twitter"

        # Title (first 80 chars)
        title = (
            cleaned[:80] + "..." if len(cleaned) > 80 else cleaned
        )

        # Parse published_at
        pub_date = self._parse_created_at(created_at_str)

        tweet_url = f"https://x.com/i/status/{tweet_id}"

        return {
            "source_type": "twitter",
            "source_name": source_name,
            "content": cleaned,
            "title": title,
            "url": tweet_url,
            "published_at": pub_date,
        }

    @staticmethod
    def _parse_created_at(value: Any) -> datetime | None:
        """Parse tweet created_at to a timezone-aware datetime."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=UTC)
        try:
            from dateutil import parser as dateutil_parser

            dt = dateutil_parser.parse(str(value))
            return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
        except Exception:
            return None

    async def collect(self) -> list[dict[str, Any]]:
        """Collect tweets across all AKD search queries.

        Returns:
            Flat list of normalized ContentItem dictionaries.
        """
        client = await _create_twikit_client()
        if client is None:
            logger.warning(
                "Skipping Twitter collection (client unavailable)",
                extra={},
            )
            return []

        all_tweets: list[dict[str, Any]] = []

        logger.info(
            "Starting Twitter collection via twikit",
            extra={"queries_count": len(self.queries)},
        )

        for akd_q in self.queries:
            try:
                tweets = await self._search_for_query(
                    client, akd_q
                )
                all_tweets.extend(tweets)
            except Exception as e:
                logger.error(
                    "Error querying tweets for AKD",
                    extra={"akd": akd_q.name, "error": str(e)},
                )
                continue

        logger.info(
            "Twitter collection complete",
            extra={"total_collected": len(all_tweets)},
        )
        return all_tweets

    async def _search_for_query(
        self, client: Any, akd_q: AKDQuery,
    ) -> list[dict[str, Any]]:
        """Search tweets for a single AKD query via twikit."""
        try:
            await asyncio.sleep(0.5)
            result = await client.search_tweet(
                akd_q.query_str, "Latest"
            )
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "Rate limit" in err_msg:
                logger.warning(
                    "X rate limit reached for query",
                    extra={"query": akd_q.name},
                )
            else:
                logger.warning(
                    "Search query returned error",
                    extra={"query": akd_q.name, "error": err_msg},
                )
            return []

        if not result:
            return []

        parsed_items: list[dict[str, Any]] = []
        for tweet in result:
            if len(parsed_items) >= self.max_results:
                break
            parsed = self.parse_tweet(tweet)
            if parsed:
                parsed_items.append(parsed)

        return parsed_items
