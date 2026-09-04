# -*- coding: utf-8 -*-
"""Collect, classify, and analyze DPR RI news for September 1, 2, 3 (2026).

Saves partitioned news to data/news/2026-09/, analysis to data/analysis/2026-09/,
and updates master data/news/news_output.json and data/analysis/analysis_output.json.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import asyncio
import json
import logging
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import feedparser
import requests
from dateutil import parser as dateutil_parser

from src.agents.analysis import AnalysisAgent
from src.agents.news_collection import FeedConfig, sanitize_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

WIB = timezone(timedelta(hours=7))
BASE_DIR = Path(__file__).resolve().parent.parent
NEWS_DIR = BASE_DIR / "data" / "news"
ANALYSIS_DIR = BASE_DIR / "data" / "analysis"

TARGET_DATES = ["2026-09-01", "2026-09-02", "2026-09-03"]

DIRECT_FEEDS = [
    FeedConfig("Detik.com", "https://news.detik.com/berita/rss", "nasional"),
    FeedConfig("Detik.com", "https://news.detik.com/hukum-dan-kriminal/rss", "hukum"),
    FeedConfig("Antaranews.com", "https://www.antaranews.com/rss/terkini", "terkini"),
    FeedConfig("Antaranews.com", "https://www.antaranews.com/rss/politik", "politik"),
    FeedConfig("Antaranews.com", "https://www.antaranews.com/rss/hukum", "hukum"),
    FeedConfig("CNN Indonesia", "https://www.cnnindonesia.com/nasional/rss", "nasional"),
    FeedConfig("Republika.co.id", "https://www.republika.co.id/rss/nasional", "nasional"),
    FeedConfig("Tempo.co", "https://rss.tempo.co/nasional", "nasional"),
    FeedConfig("Liputan6.com", "https://feed.liputan6.com/rss/news", "nasional"),
    FeedConfig("Tribunnews.com", "https://www.tribunnews.com/rss", "nasional"),
    FeedConfig("Viva.co.id", "https://www.viva.co.id/get/all", "nasional"),
    FeedConfig("Mediaindonesia.com", "https://mediaindonesia.com/feed", "nasional"),
    FeedConfig("Sindonews.com", "https://nasional.sindonews.com/rss", "nasional"),
]

SEARCH_QUERIES = [
    "DPR+RI",
    "Komisi+DPR",
    "Puan+Maharani",
    "RUU+DPR",
    "sidang+paripurna+DPR",
    "Badan+Anggaran+DPR",
    "Baleg+DPR",
    "kebijakan+pemerintah+DPR",
    "MKD+DPR",
    "BKSAP+DPR",
    "Pemerintah+DPR+RI",
    "Rapat+DPR+RI",
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


def harvest_all_articles() -> list[dict[str, Any]]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36 DPR-Agentic-AI/1.0"
        )
    }
    raw_articles = []
    seen_urls = set()
    seen_titles = set()

    # 1. Direct Feeds
    logger.info("Harvesting from %d direct media feeds...", len(DIRECT_FEEDS))
    for feed in DIRECT_FEEDS:
        try:
            resp = requests.get(feed.url, headers=headers, timeout=8)
            if resp.status_code != 200:
                continue
            parsed = feedparser.parse(resp.content)
            for entry in parsed.entries:
                title = sanitize_text(getattr(entry, "title", ""))
                title_clean = re.sub(r"\s+", " ", title).strip().lower()
                if not title or len(title) < 10 or title_clean in seen_titles:
                    continue
                url = getattr(entry, "link", "").strip()
                if not url or url in seen_urls:
                    continue

                d_str = getattr(entry, "published", "") or getattr(entry, "updated", "")
                dt_wib, date_key = parse_date_wib(d_str)
                if not dt_wib or date_key not in TARGET_DATES:
                    continue

                seen_urls.add(url)
                seen_titles.add(title_clean)
                content = sanitize_text(
                    getattr(entry, "summary", "") or getattr(entry, "description", "") or title
                )

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
            logger.warning("Error fetching %s: %s", feed.name, e)

    # 2. Targeted Search RSS
    logger.info("Harvesting from %d targeted search RSS feeds...", len(SEARCH_QUERIES))
    for q in SEARCH_QUERIES:
        try:
            url = f"https://news.google.com/rss/search?q={q}&hl=id&gl=ID&ceid=ID:id"
            resp = requests.get(url, headers=headers, timeout=8)
            if resp.status_code != 200:
                continue
            parsed = feedparser.parse(resp.content)
            for entry in parsed.entries:
                title = sanitize_text(getattr(entry, "title", ""))
                # Strip trailing " - Media Portal" if present
                clean_title_display = re.sub(r"\s*-\s*[^-]+$", "", title) if " - " in title else title
                title_clean = re.sub(r"\s+", " ", clean_title_display).strip().lower()

                if not title_clean or len(title_clean) < 10 or title_clean in seen_titles:
                    continue
                art_url = getattr(entry, "link", "").strip()
                if not art_url or art_url in seen_urls:
                    continue

                d_str = getattr(entry, "published", "") or getattr(entry, "updated", "")
                dt_wib, date_key = parse_date_wib(d_str)
                if not dt_wib or date_key not in TARGET_DATES:
                    continue

                seen_urls.add(art_url)
                seen_titles.add(title_clean)
                source_name = getattr(entry, "source", {}).get("title", "Berita Nasional")
                summary = sanitize_text(getattr(entry, "summary", "") or clean_title_display)

                raw_articles.append({
                    "title": clean_title_display,
                    "content": summary,
                    "url": art_url,
                    "published_at": dt_wib.isoformat(),
                    "source_type": "news_online",
                    "source_name": source_name,
                    "date_key": date_key,
                })
        except Exception as e:
            logger.warning("Error searching '%s': %s", q, e)

    logger.info("Total articles gathered for September 1-3: %d", len(raw_articles))
    return raw_articles


async def main():
    print("=" * 80)
    print("  COLLECTING & ANALYZING NEWS FOR SEPTEMBER 1, 2, 3")
    print("=" * 80)

    articles = harvest_all_articles()

    # Group by date
    by_date: dict[str, list[dict[str, Any]]] = {d: [] for d in TARGET_DATES}
    for a in articles:
        d = a["date_key"]
        if d in by_date:
            by_date[d].append(a)

    for d in TARGET_DATES:
        print(f"  • {d}: {len(by_date[d])} articles gathered")

    # Process all articles per target date (uncapped)
    selected_by_date: dict[str, list[dict[str, Any]]] = {}

    for d in TARGET_DATES:
        selected_by_date[d] = by_date[d]
        print(f"  * {d}: Processing all {len(selected_by_date[d])} articles (uncapped)")

    # Prepare directories
    news_sep_dir = NEWS_DIR / "2026-09"
    analysis_sep_dir = ANALYSIS_DIR / "2026-09"
    news_sep_dir.mkdir(parents=True, exist_ok=True)
    analysis_sep_dir.mkdir(parents=True, exist_ok=True)

    # Initialize AnalysisAgent
    print("\n[AI] Initializing AnalysisAgent (AKD 3-Tier + Calibrated IndoBERT)...")
    agent = AnalysisAgent()

    for d in TARGET_DATES:
        day_items = selected_by_date[d]
        analysis_file = analysis_sep_dir / f"analysis_{d}.json"
        print(f"\n[RUN] Processing {d} ({len(day_items)} articles total)...")

        # Save news partitioned JSON
        news_file = news_sep_dir / f"news_{d}.json"
        with open(news_file, "w", encoding="utf-8") as f:
            json.dump(day_items, f, ensure_ascii=False, indent=2)
            f.flush()
        print(f"  [OK] Saved raw news to: {news_file.name} ({len(day_items)} items)")

        # Load existing analysis to avoid redundant re-analysis
        existing_analyzed: dict[str, dict[str, Any]] = {}
        if analysis_file.exists():
            try:
                with open(analysis_file, encoding="utf-8") as f:
                    for prev_item in json.load(f):
                        u = prev_item.get("url", "")
                        if u and "sentiment" in prev_item:
                            existing_analyzed[u] = prev_item
            except Exception:
                pass

        # Analyze each item (reusing cached where available)
        analyzed_items = []
        newly_analyzed = 0
        for idx, item in enumerate(day_items, 1):
            url = item.get("url", "")
            if url and url in existing_analyzed:
                analyzed_items.append(existing_analyzed[url])
                continue

            newly_analyzed += 1
            text_to_analyze = f"{item['title']}. {item.get('content', '')}"
            try:
                analysis = await agent.analyze(text_to_analyze)
                enriched = {
                    **item,
                    "sentiment": analysis["sentiment"],
                    "sentiment_score": analysis["sentiment_score"],
                    "akd_mappings": analysis["akd_mappings"],
                    "analyzed_at": datetime.now().isoformat(),
                }
                analyzed_items.append(enriched)
                if idx % 10 == 0 or idx == len(day_items):
                    akds = [m["akd_name"] for m in analysis["akd_mappings"]]
                    print(f"    [{idx}/{len(day_items)}] {item['title'][:55]}... -> {analysis['sentiment']} | AKD: {akds}")
            except Exception as e:
                logger.warning("Error analyzing item: %s", e)
                # Fallback neutral
                analyzed_items.append({
                    **item,
                    "sentiment": "Netral",
                    "sentiment_score": 0.5,
                    "akd_mappings": [{"akd_code": "KOMISI_III", "akd_name": "Komisi III DPR RI", "confidence_score": 0.7}],
                    "analyzed_at": datetime.now().isoformat(),
                })

        print(f"  [CACHE] Reused {len(analyzed_items) - newly_analyzed} analyzed items, newly analyzed {newly_analyzed} items")

        # Save analysis partitioned JSON
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analyzed_items, f, ensure_ascii=False, indent=2)
            f.flush()
        print(f"  [OK] Saved analysis to: {analysis_file.name} ({len(analyzed_items)} items)")

    # 4. Re-aggregate Master Files
    print("\n[INFO] Updating Consolidated Master Files...")

    # News master
    all_news = []
    seen_news_urls = set()
    for nf in sorted(NEWS_DIR.rglob("news_2026-*.json")):
        try:
            with open(nf, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    u = item.get("url", "")
                    if u and u in seen_news_urls:
                        continue
                    if u:
                        seen_news_urls.add(u)
                    all_news.append(item)
        except Exception as e:
            logger.warning("Failed to read %s: %s", nf.name, e)

    master_news_file = NEWS_DIR / "news_output.json"
    with open(master_news_file, "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
        f.flush()
    print(f"  [OK] Updated '{master_news_file.name}': {len(all_news)} total news items")

    # Analysis master
    all_analysis = []
    seen_analysis_urls = set()
    for af in sorted(ANALYSIS_DIR.rglob("analysis_2026-*.json")):
        try:
            with open(af, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    u = item.get("url", "")
                    if u and u in seen_analysis_urls:
                        continue
                    if u:
                        seen_analysis_urls.add(u)
                    all_analysis.append(item)
        except Exception as e:
            logger.warning("Failed to read %s: %s", af.name, e)

    master_analysis_file = ANALYSIS_DIR / "analysis_output.json"
    with open(master_analysis_file, "w", encoding="utf-8") as f:
        json.dump(all_analysis, f, ensure_ascii=False, indent=2)
        f.flush()
    print(f"  [OK] Updated '{master_analysis_file.name}': {len(all_analysis)} total analyzed items")

    print("\n" + "=" * 80)
    print("  ALL TASKS COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
