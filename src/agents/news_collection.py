"""News Collection Agent — collects news articles via RSS feeds."""

import logging

import feedparser

logger = logging.getLogger(__name__)

# Default RSS feeds for DPR RI related news
DEFAULT_FEEDS: list[str] = [
    # TODO: Add actual RSS feed URLs for Indonesian news sources
]


class NewsCollectionAgent:
    """Collects and normalizes news articles from RSS feeds."""

    def __init__(self, feeds: list[str] | None = None) -> None:
        self.feeds = feeds or DEFAULT_FEEDS

    async def collect(self) -> list[dict]:
        """Collect articles from all configured RSS feeds."""
        articles: list[dict] = []
        for feed_url in self.feeds:
            logger.info("Fetching RSS feed", extra={"feed_url": feed_url})
            try:
                parsed = feedparser.parse(feed_url)
                for entry in parsed.entries:
                    articles.append({
                        "title": entry.get("title", ""),
                        "content": entry.get("summary", ""),
                        "url": entry.get("link", ""),
                        "published_at": entry.get("published", ""),
                        "source_type": "news_online",
                    })
            except Exception:
                logger.error("Failed to fetch RSS feed", extra={"feed_url": feed_url})
        logger.info("News collection complete", extra={"count": len(articles)})
        return articles
