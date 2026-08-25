"""News Collection Agent — collects news articles via RSS feeds.

Fetches from 12+ Indonesian Tier-1 media RSS feeds, parses and sanitizes
the content, filters out consumer how-tos / entertainment noise, and returns
normalized article dicts ready for DB persistence and AI analysis.
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any


import feedparser
import requests
from dateutil import parser as dateutil_parser

from src.config import settings
from src.utils.validators import sanitize_text

logger = logging.getLogger(__name__)

FEEDS_JSON_PATH = Path(__file__).resolve().parents[2] / "kamus" / "feeds.json"

# Whitelist keywords that override noise detection (explicit legislative/policy entities)
LEGISLATIVE_WHITELIST_PATTERN = re.compile(
    r"\b(dpr|mpr|dpd|komisi [i|v|x]+|badan legislasi|baleg|badan anggaran|banggar|"
    r"bksap|mkd|bakn|burd|pansus|panja|puan maharani|ruu|undang-undang|apbn|rapbn|"
    r"rdp|sidang paripurna|interpelasi|hak angket|pemerintah pusat|kementerian|menteri)\b",
    re.IGNORECASE,
)

# Negative noise patterns (how-tos, tips, recipes, gossip, horoscopes, sports results, product discounts, lifestyle)
NOISE_PATTERNS = [
    # 1. Consumer How-Tos, Guides, Recipes, Answer Keys (handles "5 Tips...", "10 Cara...", etc.)
    re.compile(r"^(\d+\s+)?(cara|tips|trik|langkah|panduan|resep|kunci jawaban|tutorial|rekomendasi)\b", re.IGNORECASE),
    re.compile(r"\b(cara mudah|cara cepat|tips mudah|tips trik|resep masakan|resep kue|bumbu rujak|langkah mudah|resep ayam|resep praktis)\b", re.IGNORECASE),
    # 2. Entertainment, Horoscopes, Lyrics, Chords, Spoilers, K-Drama, Movies
    re.compile(r"\b(zodiak|ramalan zodiak|horoskop|sinopsis film|sinopsis drakor|lirik lagu|chord gitar|kunci gitar|spoiler manga|spoiler anime|link nonton|nonton streaming|drama korea|drakor|film bioskop)\b", re.IGNORECASE),
    # 3. Sports scores, Match results, Live stream links
    re.compile(r"\b(skor akhir|hasil liga|klasemen liga|link live streaming|siaran langsung sepak|motogp|formula 1|hasil f1|hasil motogp|piala fa|liga inggris|liga spanyol|liga italia|liga champions)\b", re.IGNORECASE),
    # 4. Commercial promos, discounts, phone/car price lists
    re.compile(r"\b(promo diskon|diskon gila|spesifikasi dan harga|harga hp|harga motor bekas|voucher cashback|kode promo|kode redeem|katalog promo)\b", re.IGNORECASE),
    # 5. Lifestyle, fashion, beauty, casual cafes
    re.compile(r"\b(ootd|skincare|gaya rambut|kafe kekinian|tempat nongkrong|menu diet|kuliner legendaris)\b", re.IGNORECASE),
    # 6. Explainer, FAQ, Trivia Q&A, Definition articles (e.g. 'Apa itu...', 'Kenapa...', 'Ini penyebab dan penjelasan...')
    re.compile(r"^(apa itu|kenapa|mengapa|bagaimana cara|kapan waktu|tahukah kamu|mengenal apa itu|benarkah|arti mimpi|fakta menarik|serba-serbi|alasan kenapa|inilah penyebab|deretan fakta)\b", re.IGNORECASE),
    re.compile(r"\b(dan cara buatnya|dan cara daftarnya|dan cara menggunakannya|ini penyebab dan penjelasan|penyebab dan cara mengatasi|kenapa sering|mengapa sering|mitos atau fakta|cek fungsi|cek syarat)\b", re.IGNORECASE),
    # 7. Gadget Leaks, Tech Product Rumors, Consumer Tech & Gaming (e.g. 'Bocoran Terbaru AirPods...', 'Rumor iPhone...')
    re.compile(r"^(bocoran|rumor|fitur baru|unboxing|review jujur|kelebihan dan kekurangan)\b", re.IGNORECASE),
    re.compile(r"\b(airpods|earbuds|smartwatch|iphone \d+|samsung galaxy|xiaomi|redmi|oppo|vivo|realme|infinix|playstation|ps5|nintendo switch|game android|game pc|mobile legends|pubg|free fire|gta|gameplay|update ios|update android)\b", re.IGNORECASE),
    re.compile(r"\b(bisa apa saja\??|apa saja fiturnya\??|kapan rilis\??|berapa harganya\??|bocoran terbaru|bocoran harga|bocoran spesifikasi|bocoran desain|rumor kencang)\b", re.IGNORECASE),
]




def is_consumer_or_entertainment_noise(title: str, content: str = "") -> tuple[bool, str]:
    """Check if an article is consumer how-to, entertainment gossip, or commercial noise.

    Returns:
        tuple (is_noise: bool, reason: str)
    """
    full_text = f"{title}. {content}".strip()
    if not full_text:
        return True, "empty_text"

    # Legislative whitelist override: Never drop articles mentioning parliamentary/policy entities
    if LEGISLATIVE_WHITELIST_PATTERN.search(full_text):
        return False, "legislative_whitelist_matched"

    # Check noise patterns against title and beginning of content
    for pattern in NOISE_PATTERNS:
        match = pattern.search(title) or pattern.search(content[:200])
        if match:
            return True, f"matched_noise_pattern: {match.group(0)}"

    return False, "clean_policy_news"


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
    """Collects, normalizes, and filters news articles from RSS feeds.

    Responsibilities:
    - Fetch RSS feeds with timeout protection
    - Monitor RSS feed health and auto-skip DEAD/unreachable sources
    - Parse XML entries via feedparser
    - Sanitize HTML content and normalize text
    - Filter consumer how-tos, entertainment, and sports noise
    - Deduplicate by URL and normalized title
    - Isolate errors per-feed
    """

    def __init__(self, feeds: list[FeedConfig] | None = None) -> None:
        self.feeds = feeds or list(load_feed_configs())
        self.timeout = settings.NEWS_FEED_TIMEOUT
        self._feed_health_cache: dict[str, dict] = {}

    def check_feed_health(self, feed: FeedConfig) -> dict:
        """Probe a single feed URL to check its availability, status code, latency, and validity."""
        import time

        start = time.time()
        try:
            resp = requests.get(
                feed.url,
                timeout=min(self.timeout, 5),
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36 DPR-Agentic-AI/1.0"
                    )
                },
            )
            duration_ms = round((time.time() - start) * 1000, 1)
            if resp.status_code == 200:
                parsed = feedparser.parse(resp.content)
                is_valid = bool(parsed.entries or (hasattr(parsed, "feed") and parsed.feed.get("title")))
                status = "HEALTHY" if is_valid else "EMPTY"
                health = {
                    "name": feed.name,
                    "url": feed.url,
                    "category": feed.category,
                    "status": status,
                    "status_code": resp.status_code,
                    "latency_ms": duration_ms,
                    "entry_count": len(parsed.entries),
                    "last_checked": datetime.now(UTC).isoformat(),
                    "error": None if is_valid else "Feed XML parsed with 0 entries",
                }
            elif resp.status_code in (404, 410):
                health = {
                    "name": feed.name,
                    "url": feed.url,
                    "category": feed.category,
                    "status": "DEAD",
                    "status_code": resp.status_code,
                    "latency_ms": duration_ms,
                    "entry_count": 0,
                    "last_checked": datetime.now(UTC).isoformat(),
                    "error": f"HTTP {resp.status_code} Not Found / Gone",
                }
            else:
                health = {
                    "name": feed.name,
                    "url": feed.url,
                    "category": feed.category,
                    "status": "DEGRADED",
                    "status_code": resp.status_code,
                    "latency_ms": duration_ms,
                    "entry_count": 0,
                    "last_checked": datetime.now(UTC).isoformat(),
                    "error": f"HTTP {resp.status_code} Error",
                }
        except requests.Timeout:
            health = {
                "name": feed.name,
                "url": feed.url,
                "category": feed.category,
                "status": "TIMEOUT",
                "status_code": 0,
                "latency_ms": round((time.time() - start) * 1000, 1),
                "entry_count": 0,
                "last_checked": datetime.now(UTC).isoformat(),
                "error": "Connection timed out",
            }
        except Exception as exc:
            health = {
                "name": feed.name,
                "url": feed.url,
                "category": feed.category,
                "status": "UNREACHABLE",
                "status_code": 0,
                "latency_ms": round((time.time() - start) * 1000, 1),
                "entry_count": 0,
                "last_checked": datetime.now(UTC).isoformat(),
                "error": str(exc),
            }

        self._feed_health_cache[feed.url] = health
        return health

    def check_all_feeds_health(self) -> list[dict]:
        """Probe all configured feeds and return comprehensive health status report."""
        return [self.check_feed_health(f) for f in self.feeds]

    async def collect(self) -> list[dict]:
        """Collect articles from all configured RSS feeds with noise and duplicate filtering.

        Returns:
            List of normalized article dicts with keys:
            title, content, url, published_at, source_type, source_name
        """
        all_articles: list[dict] = []

        for feed in self.feeds:
            # Auto-skip feeds flagged as DEAD in cache
            cached_health = self._feed_health_cache.get(feed.url)
            if cached_health and cached_health.get("status") == "DEAD":
                logger.warning(
                    "Skipping known DEAD feed",
                    extra={"feed_name": feed.name, "url": feed.url},
                )
                continue

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
                self._feed_health_cache[feed.url] = {
                    "name": feed.name,
                    "url": feed.url,
                    "category": feed.category,
                    "status": "TIMEOUT",
                    "status_code": 0,
                    "last_checked": datetime.now(UTC).isoformat(),
                    "error": "Timeout during collect()",
                }
            except requests.RequestException as exc:
                status_code = getattr(exc.response, "status_code", 0) if hasattr(exc, "response") else 0
                status_label = "DEAD" if status_code in (404, 410) else "DEGRADED"
                logger.error(
                    "Feed network error",
                    extra={"feed_name": feed.name, "error": str(exc)},
                )
                self._feed_health_cache[feed.url] = {
                    "name": feed.name,
                    "url": feed.url,
                    "category": feed.category,
                    "status": status_label,
                    "status_code": status_code,
                    "last_checked": datetime.now(UTC).isoformat(),
                    "error": str(exc),
                }
            except Exception as exc:
                logger.error(
                    "Feed processing failed",
                    extra={"feed_name": feed.name, "error": str(exc)},
                )


        logger.info(
            "News collection raw complete",
            extra={"total_articles": len(all_articles), "feeds_count": len(self.feeds)},
        )

        # 1. Noise Filter (Strip how-tos, zodiak, sports, promos)
        clean_articles: list[dict] = []
        noise_dropped = 0
        for article in all_articles:
            is_noise, reason = is_consumer_or_entertainment_noise(
                article.get("title", ""), article.get("content", "")
            )
            if is_noise:
                noise_dropped += 1
                logger.debug("Filtered noise article", extra={"title": article.get("title"), "reason": reason})
                continue
            clean_articles.append(article)

        if noise_dropped:
            logger.info(
                "Noise articles filtered during collection",
                extra={"noise_dropped": noise_dropped, "retained": len(clean_articles)},
            )

        # 2. Deduplicate by URL and normalized title across feeds
        seen_urls: set[str] = set()
        seen_titles: set[str] = set()
        unique_articles: list[dict] = []

        for article in clean_articles:
            url = article.get("url", "")
            title_key = (article.get("title") or "").strip().lower()

            if url and url in seen_urls:
                continue
            if title_key and title_key in seen_titles:
                continue

            if url:
                seen_urls.add(url)
            if title_key:
                seen_titles.add(title_key)
            unique_articles.append(article)

        duplicates_removed = len(clean_articles) - len(unique_articles)
        if duplicates_removed:
            logger.info(
                "Duplicates removed during collection",
                extra={"removed": duplicates_removed, "remaining": len(unique_articles)},
            )

        return unique_articles

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
                    "Chrome/124.0.0.0 Safari/537.36 DPR-Agentic-AI/1.0"
                )
            },
        )
        response.raise_for_status()

        parsed = feedparser.parse(response.content)
        articles: list[dict] = []

        for entry in parsed.entries:
            article = self._parse_entry(entry, feed.name)
            if article is not None:
                articles.append(article)

        return articles

    def _parse_entry(self, entry: feedparser.FeedParserDict | dict | Any, source_name: str) -> dict | None:
        """Parse a single feedparser entry into a normalized article dict.

        Returns None if required fields (title, url) are missing.
        """
        title = sanitize_text(entry.get("title", "") if hasattr(entry, "get") else getattr(entry, "title", ""))
        url = entry.get("link", "").strip() if hasattr(entry, "get") else getattr(entry, "link", "").strip()

        if not title or not url:
            return None

        # Content fallback chain: content -> summary -> description -> title
        content = ""
        raw_content = getattr(entry, "content", None)
        if raw_content and isinstance(raw_content, (list, tuple)) and len(raw_content) > 0:
            first = raw_content[0]
            content = first.get("value", "") if isinstance(first, dict) else getattr(first, "value", str(first))

        if not content and hasattr(entry, "get"):
            content = entry.get("summary", "") or entry.get("description", "")
        if not content and hasattr(entry, "summary"):
            content = getattr(entry, "summary", "")
        if not content:
            content = title

        content = sanitize_text(content)

        # Date parsing
        published_str = ""
        if hasattr(entry, "get"):
            val = entry.get("published", "") or entry.get("updated", "")
            if isinstance(val, str):
                published_str = val
        if not published_str and hasattr(entry, "published"):
            val = getattr(entry, "published", "")
            if isinstance(val, str):
                published_str = val
        if not published_str and hasattr(entry, "updated"):
            val = getattr(entry, "updated", "")
            if isinstance(val, str):
                published_str = val

        published_at = self._parse_date(published_str)


        return {
            "title": title,
            "content": content,
            "url": url,
            "published_at": published_at.isoformat() if published_at else None,
            "source_type": "news_online",
            "source_name": source_name,
        }

    def _parse_date(self, date_str: str) -> datetime | None:
        """Parse date string into UTC datetime.

        Handles RFC 822 (RSS), ISO 8601 (Atom), and standard formats.
        Returns None on parse failure.
        """
        if not date_str or not date_str.strip():
            return None

        try:
            dt = dateutil_parser.parse(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            else:
                dt = dt.astimezone(UTC)
            return dt
        except (ValueError, OverflowError):
            logger.warning(
                "Failed to parse article date",
                extra={"raw_date": date_str},
            )
            return None
