# -*- coding: utf-8 -*-
"""Probe live RSS feeds and inspect article date distributions."""
import asyncio
from datetime import datetime
from collections import Counter
from src.agents.news_collection import NewsCollectionAgent

async def probe():
    agent = NewsCollectionAgent()
    print(f"Configured Feeds: {len(agent.feeds)}")
    articles = await agent.collect()
    print(f"Total articles collected from feeds: {len(articles)}")

    dates = Counter()
    sources = Counter()
    september_articles = []

    for a in articles:
        dt = a.get("published_at")
        d_str = dt.strftime("%Y-%m-%d") if isinstance(dt, datetime) else str(dt)[:10]
        dates[d_str] += 1
        sources[a.get("source_name", "Unknown")] += 1
        if d_str.startswith("2026-09"):
            september_articles.append(a)

    print("\nDate breakdown:")
    for d, c in sorted(dates.items()):
        print(f"  {d}: {c} articles")

    print(f"\nTotal September articles: {len(september_articles)}")
    print("\nSource breakdown (top 10):")
    for s, c in sources.most_common(10):
        print(f"  {s}: {c}")

if __name__ == "__main__":
    asyncio.run(probe())
