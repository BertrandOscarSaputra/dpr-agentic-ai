# -*- coding: utf-8 -*-
"""Script to run NewsCollectionAgent and export output to news_output.json."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import asyncio
import json
from datetime import datetime
from pathlib import Path

from src.agents.news_collection import NewsCollectionAgent

OUTPUT_DIR = Path("data/news")
OUTPUT_FILE = OUTPUT_DIR / "news_output.json"


async def main():
    print("=" * 80)
    print("  RUNNING NEWS COLLECTION AGENT (RSS FEEDS)")
    print("=" * 80)

    agent = NewsCollectionAgent()
    print(f"Configured RSS Feeds: {len(agent.feeds)}")

    # Collect live news articles
    articles = await agent.collect()

    print("\n" + "=" * 80)
    print(f"  TOTAL ARTICLES COLLECTED: {len(articles)}")
    print("=" * 80 + "\n")

    # Serialize datetime to ISO strings for JSON and deduplicate by URL
    seen_urls: set[str] = set()
    serialized = []
    duplicates_removed = 0
    for article in articles:
        url = article.get("url", "")
        if url in seen_urls:
            duplicates_removed += 1
            continue
        if url:
            seen_urls.add(url)

        copy_art = dict(article)
        if isinstance(copy_art.get("published_at"), datetime):
            copy_art["published_at"] = copy_art["published_at"].isoformat()
        serialized.append(copy_art)

    if duplicates_removed:
        print(f"🔄 Removed {duplicates_removed} duplicate articles (by URL)")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Group serialized articles by published_at date (YYYY-MM-DD)
    by_date: dict[str, list[dict]] = {}
    today_fallback = datetime.now().strftime("%Y-%m-%d")

    for item in serialized:
        pub_str = item.get("published_at") or ""
        date_key = today_fallback
        if pub_str:
            try:
                date_key = pub_str[:10]  # Extract YYYY-MM-DD from ISO string
            except Exception:
                date_key = today_fallback
        if date_key not in by_date:
            by_date[date_key] = []
        by_date[date_key].append(item)

    print("📁 Partitioning articles by published date:")
    for date_key, date_articles in sorted(by_date.items()):
        month_str = date_key[:7] if len(date_key) >= 7 else "misc"
        month_dir = OUTPUT_DIR / month_str
        month_dir.mkdir(parents=True, exist_ok=True)
        daily_file = month_dir / f"news_{date_key}.json"
        with open(daily_file, "w", encoding="utf-8") as f:
            json.dump(date_articles, f, ensure_ascii=False, indent=2)
            f.flush()
        print(f"   • {date_key}: {len(date_articles)} articles -> '{month_str}/{daily_file.name}'")

    # Save all combined articles to news_output.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2)
        f.flush()

    print(f"\n✅ SUCCESS: Saved all {len(serialized)} news articles to '{OUTPUT_FILE.resolve()}'\n")

    if serialized:
        print("Sample collected news articles:")
        for i, item in enumerate(serialized[:5], 1):
            print(f"[{i}] {item.get('source_name')} | {item.get('published_at')}")
            print(f"    Title: {item.get('title')}")
            print(f"    URL:   {item.get('url')}\n")


if __name__ == "__main__":
    asyncio.run(main())
