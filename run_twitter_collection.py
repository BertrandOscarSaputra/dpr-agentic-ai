# -*- coding: utf-8 -*-
"""Script to run TwitterCollectionAgent and export output to tweets_output.json."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import asyncio
import json
from datetime import datetime
from pathlib import Path

from src.agents.twitter_collection import TwitterCollectionAgent

OUTPUT_DIR = Path("data/tweets")
OUTPUT_FILE = OUTPUT_DIR / "tweets_output.json"


async def main():
    print("=" * 80)
    print("  RUNNING TWITTER/X COLLECTION AGENT")
    print("=" * 80)

    agent = TwitterCollectionAgent()
    print(f"Configured AKD Queries: {len(agent.queries)}")

    # Collect live tweets
    tweets = await agent.collect()

    print("\n" + "=" * 80)
    print(f"  TOTAL TWEETS COLLECTED: {len(tweets)}")
    print("=" * 80 + "\n")

    # Serialize datetime to ISO strings for JSON
    serialized = []
    for tweet in tweets:
        copy_tw = dict(tweet)
        if isinstance(copy_tw.get("published_at"), datetime):
            copy_tw["published_at"] = copy_tw["published_at"].isoformat()
        serialized.append(copy_tw)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    daily_output_file = OUTPUT_DIR / f"tweets_{today_str}.json"

    # Save to daily file (tweets_YYYY-MM-DD.json) and latest file (tweets_output.json)
    if serialized:
        with open(daily_output_file, "w", encoding="utf-8") as f:
            json.dump(serialized, f, ensure_ascii=False, indent=2)
            f.flush()
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(serialized, f, ensure_ascii=False, indent=2)
            f.flush()
        print(f"✅ SUCCESS: Wrote {len(serialized)} items (file size: {daily_output_file.stat().st_size} bytes) to '{daily_output_file.resolve()}'\n")
    else:
        print(f"⚠️ RATE LIMIT / NO NEW TWEETS: Preserved existing tweets in '{OUTPUT_FILE.resolve()}'\n")

    if serialized:
        print("Sample collected tweets:")
        for i, item in enumerate(serialized[:5], 1):
            print(f"[{i}] {item.get('source_name')} | {item.get('published_at')}")
            print(f"    Title: {item.get('title')}")
            print(f"    URL:   {item.get('url')}\n")


if __name__ == "__main__":
    asyncio.run(main())
