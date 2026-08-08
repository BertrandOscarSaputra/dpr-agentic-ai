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

    # Serialize datetime to ISO strings for JSON
    serialized = []
    for article in articles:
        copy_art = dict(article)
        if isinstance(copy_art.get("published_at"), datetime):
            copy_art["published_at"] = copy_art["published_at"].isoformat()
        serialized.append(copy_art)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    daily_output_file = OUTPUT_DIR / f"news_{today_str}.json"

    # Save to daily file (news_YYYY-MM-DD.json) and latest file (news_output.json)
    with open(daily_output_file, "w", encoding="utf-8") as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2)

    print(f"✅ SUCCESS: Exported {len(serialized)} news articles to '{daily_output_file.resolve()}' and '{OUTPUT_FILE.resolve()}'\n")

    if serialized:
        print("Sample collected news articles:")
        for i, item in enumerate(serialized[:5], 1):
            print(f"[{i}] {item.get('source_name')} | {item.get('published_at')}")
            print(f"    Title: {item.get('title')}")
            print(f"    URL:   {item.get('url')}\n")


if __name__ == "__main__":
    asyncio.run(main())
