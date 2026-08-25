# -*- coding: utf-8 -*-
"""Collect and analyze news for 20, 21, 22, and 23 August 2026."""
import sys
import io
import json
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import Counter

import feedparser
import requests
from dateutil import parser as dateutil_parser

from src.agents.news_collection import FeedConfig, sanitize_text
from src.agents.analysis import AnalysisAgent

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(r"c:\Users\Lenovo\Documents\DPR\dpr-agentic-ai")
WIB = timezone(timedelta(hours=7))

ALL_FEEDS = [
    # Detik
    FeedConfig("Detik.com", "https://news.detik.com/berita/rss", "nasional"),
    FeedConfig("Detik.com", "https://news.detik.com/hukum-dan-kriminal/rss", "hukum"),
    FeedConfig("Detik.com", "https://finance.detik.com/rss", "ekonomi"),
    FeedConfig("Detik.com", "https://www.detik.com/edu/rss", "edukasi"),
    FeedConfig("Detik.com", "https://health.detik.com/rss", "kesehatan"),
    # Antara
    FeedConfig("Antaranews.com", "https://www.antaranews.com/rss/terkini", "terkini"),
    FeedConfig("Antaranews.com", "https://www.antaranews.com/rss/politik", "politik"),
    FeedConfig("Antaranews.com", "https://www.antaranews.com/rss/hukum", "hukum"),
    FeedConfig("Antaranews.com", "https://www.antaranews.com/rss/ekonomi", "ekonomi"),
    FeedConfig("Antaranews.com", "https://www.antaranews.com/rss/humaniora", "sosial"),
    FeedConfig("Antaranews.com", "https://www.antaranews.com/rss/metro", "metro"),
    FeedConfig("Antaranews.com", "https://www.antaranews.com/rss/warta-bumi", "lingkungan"),
    # CNN Indonesia
    FeedConfig("CNN Indonesia", "https://www.cnnindonesia.com/nasional/rss", "nasional"),
    FeedConfig("CNN Indonesia", "https://www.cnnindonesia.com/ekonomi/rss", "ekonomi"),
    FeedConfig("CNN Indonesia", "https://www.cnnindonesia.com/teknologi/rss", "teknologi"),
    # Republika
    FeedConfig("Republika.co.id", "https://www.republika.co.id/rss/nasional", "nasional"),
    FeedConfig("Republika.co.id", "https://www.republika.co.id/rss/khazanah", "agama"),
    FeedConfig("Republika.co.id", "https://www.republika.co.id/rss/ekonomi", "ekonomi"),
    FeedConfig("Republika.co.id", "https://www.republika.co.id/rss/pendidikan", "pendidikan"),
    FeedConfig("Republika.co.id", "https://www.republika.co.id/rss/hukum", "hukum"),
    # Tempo
    FeedConfig("Tempo.co", "https://rss.tempo.co/nasional", "nasional"),
    FeedConfig("Tempo.co", "https://rss.tempo.co/bisnis", "ekonomi"),
    FeedConfig("Tempo.co", "https://rss.tempo.co/hukum", "hukum"),
    FeedConfig("Tempo.co", "https://rss.tempo.co/metro", "metro"),
    # Liputan6
    FeedConfig("Liputan6.com", "https://feed.liputan6.com/rss/news", "nasional"),
    FeedConfig("Liputan6.com", "https://feed.liputan6.com/rss/bisnis", "ekonomi"),
    FeedConfig("Liputan6.com", "https://feed.liputan6.com/rss/hot", "sosial"),
    # Tribunnews
    FeedConfig("Tribunnews.com", "https://www.tribunnews.com/rss", "nasional"),
    FeedConfig("Tribunnews.com", "https://www.tribunnews.com/rss/nasional", "nasional"),
    FeedConfig("Tribunnews.com", "https://www.tribunnews.com/rss/bisnis", "ekonomi"),
    FeedConfig("Tribunnews.com", "https://www.tribunnews.com/rss/superskor", "olahraga"),
    # Viva
    FeedConfig("Viva.co.id", "https://www.viva.co.id/get/all", "nasional"),
    FeedConfig("Viva.co.id", "https://www.viva.co.id/get/berita", "berita"),
    FeedConfig("Viva.co.id", "https://www.viva.co.id/get/bisnis", "bisnis"),
    # RMOL
    FeedConfig("RMOL.id", "https://rmol.id/rss/latest-posts", "nasional"),
    FeedConfig("RMOL.id", "https://rmol.id/rss/kategori/politik", "politik"),
    FeedConfig("RMOL.id", "https://rmol.id/rss/kategori/nusantara", "nusantara"),
    # Suara
    FeedConfig("Suara.com", "https://www.suara.com/rss/news", "nasional"),
    FeedConfig("Suara.com", "https://www.suara.com/rss/bisnis", "ekonomi"),
    # Media Indonesia
    FeedConfig("Mediaindonesia.com", "https://mediaindonesia.com/feed", "nasional"),
    FeedConfig("RM.id", "https://rm.id/rss", "nasional"),
    # Sindonews
    FeedConfig("Sindonews.com", "https://sindonews.com/feed", "nasional"),
    FeedConfig("Sindonews.com", "https://nasional.sindonews.com/rss", "nasional"),
    FeedConfig("Sindonews.com", "https://ekbis.sindonews.com/rss", "ekonomi"),
    FeedConfig("Sindonews.com", "https://edukasi.sindonews.com/rss", "edukasi"),
]

def parse_date_wib(date_str: str) -> tuple[datetime | None, str]:
    if not date_str:
        return None, ""
    try:
        dt = dateutil_parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt_wib = dt.astimezone(WIB)
        return dt_wib, dt_wib.strftime("%Y-%m-%d")
    except Exception:
        return None, ""

def fetch_all_feeds() -> list[dict]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36 DPR-Agentic-AI/1.0"
        )
    }
    raw_articles = []
    seen_urls = set()

    logger.info("Fetching %d RSS feeds...", len(ALL_FEEDS))
    for feed in ALL_FEEDS:
        try:
            resp = requests.get(feed.url, headers=headers, timeout=8)
            if resp.status_code != 200:
                continue
            parsed = feedparser.parse(resp.content)
            for entry in parsed.entries:
                title = sanitize_text(getattr(entry, "title", ""))
                if not title:
                    continue
                content = sanitize_text(
                    getattr(entry, "summary", "") or getattr(entry, "description", "") or title
                )
                url = getattr(entry, "link", "").strip()
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                d_str = getattr(entry, "published", "") or getattr(entry, "updated", "")
                dt_wib, date_key = parse_date_wib(d_str)
                if not dt_wib:
                    continue

                raw_articles.append({
                    "title": title,
                    "content": content,
                    "url": url,
                    "published_at": dt_wib.isoformat(),
                    "source_type": "news_online",
                    "source_name": feed.name,
                    "date_key": date_key,
                })
        except Exception as e:
            continue

    logger.info("Total unique articles collected: %d", len(raw_articles))
    return raw_articles

async def analyze_and_partition(articles: list[dict]):
    target_dates = {"2026-08-20", "2026-08-21", "2026-08-22", "2026-08-23", "2026-08-24"}
    filtered_articles = [a for a in articles if a["date_key"] in target_dates]

    logger.info("Articles in target range (20-24 August): %d", len(filtered_articles))
    date_counts = Counter(a["date_key"] for a in filtered_articles)
    for d, c in sorted(date_counts.items()):
        logger.info("  %s: %d articles", d, c)

    analysis_agent = AnalysisAgent()
    analyzed_by_date = {d: [] for d in target_dates}
    news_by_date = {d: [] for d in target_dates}

    for idx, art in enumerate(filtered_articles, 1):
        text_for_analysis = f"{art['title']}. {art['content']}"
        sentiment, sentiment_score = analysis_agent.analyze_sentiment(text_for_analysis)
        akd_mappings = await analysis_agent.classify_akd(text_for_analysis)

        analyzed_item = {
            "title": art["title"],
            "content": art["content"],
            "url": art["url"],
            "published_at": art["published_at"],
            "source_type": art["source_type"],
            "source_name": art["source_name"],
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "akd_mappings": akd_mappings,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

        d_key = art["date_key"]
        news_item = {
            "title": art["title"],
            "content": art["content"],
            "url": art["url"],
            "published_at": art["published_at"],
            "source_type": art["source_type"],
            "source_name": art["source_name"],
        }

        news_by_date[d_key].append(news_item)
        analyzed_by_date[d_key].append(analyzed_item)

        if idx % 100 == 0 or idx == len(filtered_articles):
            logger.info("Analyzed %d / %d articles...", idx, len(filtered_articles))

    # Save directly to PROJECT_ROOT / data / news and analysis
    news_dir = PROJECT_ROOT / "data" / "news"
    analysis_dir = PROJECT_ROOT / "data" / "analysis"
    news_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    for d in sorted(target_dates):
        n_items = news_by_date[d]
        a_items = analyzed_by_date[d]
        if not n_items:
            continue

        news_file = news_dir / f"news_{d}.json"
        analysis_file = analysis_dir / f"analysis_{d}.json"

        with open(news_file, "w", encoding="utf-8") as fp:
            json.dump(n_items, fp, ensure_ascii=False, indent=2)

        with open(analysis_file, "w", encoding="utf-8") as fp:
            json.dump(a_items, fp, ensure_ascii=False, indent=2)

        logger.info("Saved partition for %s: %d news, %d analyzed", d, len(n_items), len(a_items))

    # Re-sync combined files across all dates (1 to 24 August)
    all_news = []
    seen_n = set()
    for f in sorted(news_dir.glob("news_2026-*.json")):
        with open(f, encoding="utf-8") as fp:
            for item in json.load(fp):
                key = (item.get("url", ""), str(item.get("published_at", ""))[:10])
                if key not in seen_n:
                    seen_n.add(key)
                    all_news.append(item)

    with open(news_dir / "news_output.json", "w", encoding="utf-8") as fp:
        json.dump(all_news, fp, ensure_ascii=False, indent=2)

    all_analysis = []
    seen_a = set()
    for f in sorted(analysis_dir.glob("analysis_2026-*.json")):
        with open(f, encoding="utf-8") as fp:
            for item in json.load(fp):
                key = (item.get("url", ""), str(item.get("published_at", ""))[:10])
                if key not in seen_a:
                    seen_a.add(key)
                    all_analysis.append(item)

    with open(analysis_dir / "analysis_output.json", "w", encoding="utf-8") as fp:
        json.dump(all_analysis, fp, ensure_ascii=False, indent=2)

    logger.info("=== SYNC COMPLETE ===")
    logger.info("Total all-time news in news_output.json: %d", len(all_news))
    logger.info("Total all-time analyzed in analysis_output.json: %d", len(all_analysis))

    # Print summary breakdown
    final_dates = Counter(str(x.get("published_at", ""))[:10] for x in all_analysis)
    print("\nFINAL DATE BREAKDOWN:")
    for d in sorted(final_dates.keys()):
        print(f"  {d}: {final_dates[d]} articles")

if __name__ == "__main__":
    raw = fetch_all_feeds()
    asyncio.run(analyze_and_partition(raw))
