# -*- coding: utf-8 -*-
"""Batch Analysis Runner — analyze news and tweets with AnalysisAgent.

Reads unanalyzed JSON files from data/news/ and data/tweets/,
deduplicates by URL, runs AnalysisAgent.analyze() on each item,
and writes enriched output to data/analysis/.
"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from src.agents.analysis import AnalysisAgent

logger = logging.getLogger(__name__)

NEWS_DIR = Path("data/news")
TWEETS_DIR = Path("data/tweets")
ANALYSIS_DIR = Path("data/analysis")


def _load_json_items(directory: Path) -> list[dict[str, Any]]:
    """Load all JSON array files from a directory."""
    items: list[dict[str, Any]] = []
    if not directory.exists():
        return items

    for json_file in sorted(directory.glob("*.json")):
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                items.extend(data)
                print(f"  📄 Loaded {len(data)} items from {json_file.name}")
        except Exception as e:
            print(f"  ⚠️ Failed to load {json_file.name}: {e}")
    return items


def _load_already_analyzed_urls() -> set[str]:
    """Load URLs already present in data/analysis/*.json to skip re-analysis."""
    analyzed_urls: set[str] = set()
    if not ANALYSIS_DIR.exists():
        return analyzed_urls

    for json_file in ANALYSIS_DIR.glob("*.json"):
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    url = item.get("url", "")
                    if url:
                        analyzed_urls.add(url)
        except Exception:
            pass
    return analyzed_urls


def _deduplicate_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicates by URL, keeping the first occurrence."""
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in items:
        url = item.get("url", "")
        title_key = (item.get("title") or "").strip().lower()

        # Skip if URL already seen
        if url and url in seen_urls:
            continue
        # Skip if same title already seen (cross-source duplicate)
        if title_key and title_key in seen_titles:
            continue

        if url:
            seen_urls.add(url)
        if title_key:
            seen_titles.add(title_key)
        unique.append(item)

    removed = len(items) - len(unique)
    if removed:
        print(f"🔄 Removed {removed} duplicate items (by URL + title)")
    return unique


async def main() -> None:
    print("=" * 80)
    print("  RUNNING ANALYSIS AGENT — BATCH PROCESSING")
    print("=" * 80)

    # Step 1: Load raw items from news & tweets
    print("\n📰 Loading news articles...")
    news_items = _load_json_items(NEWS_DIR)
    print(f"\n🐦 Loading tweets...")
    tweet_items = _load_json_items(TWEETS_DIR)

    all_items = news_items + tweet_items
    print(f"\n📊 Total raw items loaded: {len(all_items)}")

    if not all_items:
        print("❌ No items to analyze. Run news/tweet collection first.")
        return

    # Step 2: Deduplicate by URL
    unique_items = _deduplicate_items(all_items)

    # Step 3: Skip already-analyzed items (incremental mode)
    already_analyzed = _load_already_analyzed_urls()
    if already_analyzed:
        before_count = len(unique_items)
        unique_items = [
            item for item in unique_items
            if item.get("url", "") not in already_analyzed
        ]
        skipped = before_count - len(unique_items)
        if skipped:
            print(f"⏭️  Skipped {skipped} already-analyzed items")

    # Support CLI --limit flag (e.g. uv run run_analysis_batch.py --limit 10)
    limit = None
    if "--limit" in sys.argv:
        try:
            idx = sys.argv.index("--limit")
            limit = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            limit = 10
    elif "-l" in sys.argv:
        try:
            idx = sys.argv.index("-l")
            limit = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            limit = 10

    if limit is not None:
        unique_items = unique_items[:limit]
        print(f"🎯 Applying batch limit: {limit} items")

    print(f"🆕 Items to analyze in this batch: {len(unique_items)}")

    if not unique_items:
        print("✅ All items have already been analyzed. Nothing to do.")
        return

    # Step 4: Run AnalysisAgent on each item
    agent = AnalysisAgent()
    results: list[dict[str, Any]] = []
    errors = 0

    for idx, item in enumerate(unique_items, 1):
        content = item.get("content", "") or item.get("title", "")
        if not content or len(content.strip()) < 10:
            continue

        try:
            analysis = await agent.analyze(content)
            enriched = {
                **item,
                "sentiment": analysis["sentiment"],
                "sentiment_score": analysis["sentiment_score"],
                "akd_mappings": analysis["akd_mappings"],
                "analyzed_at": datetime.now().isoformat(),
            }
            results.append(enriched)

            print(f"  [{idx}/{len(unique_items)}] Analyzed: {item.get('title', '')[:60]}... -> {analysis['sentiment']} | AKD: {[m['akd_name'] for m in analysis['akd_mappings']]}")
            await asyncio.sleep(0.5)  # Rate limit protection
        except Exception as e:
            errors += 1
            logger.debug("Analysis failed for item", extra={"error": str(e)})

    print(f"\n{'=' * 80}")
    print(f"  ANALYSIS COMPLETE: {len(results)} items analyzed, {errors} errors")
    print(f"{'=' * 80}\n")

    if not results:
        print("❌ No results to save.")
        return

    # Step 5: Merge with existing results and write output
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    daily_file = ANALYSIS_DIR / f"analysis_{today_str}.json"
    output_file = ANALYSIS_DIR / "analysis_output.json"

    # Load existing daily results if present
    existing_results: list[dict[str, Any]] = []
    if daily_file.exists():
        try:
            with open(daily_file, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                existing_results = data
        except Exception:
            pass

    # Merge new results (deduplicating by URL)
    existing_urls = {item.get("url") for item in existing_results if item.get("url")}
    merged_results = list(existing_results)

    for item in results:
        url = item.get("url")
        if not url or url not in existing_urls:
            if url:
                existing_urls.add(url)
            copy_item = dict(item)
            for key in ("published_at", "analyzed_at"):
                val = copy_item.get(key)
                if isinstance(val, datetime):
                    copy_item[key] = val.isoformat()
            merged_results.append(copy_item)

    serialized = merged_results

    with open(daily_file, "w", encoding="utf-8") as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2)
        f.flush()

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2)
        f.flush()

    file_size = daily_file.stat().st_size
    print(f"✅ SUCCESS: Wrote {len(serialized)} analyzed items ({file_size:,} bytes)")
    print(f"   📁 Daily:  {daily_file.resolve()}")
    print(f"   📁 Latest: {output_file.resolve()}")

    # Print summary statistics
    sentiments = {"Positif": 0, "Negatif": 0, "Netral": 0}
    akd_counts: dict[str, int] = {}
    tier1_count = 0

    for item in serialized:
        s = item.get("sentiment", "Netral")
        sentiments[s] = sentiments.get(s, 0) + 1
        for mapping in item.get("akd_mappings", []):
            akd_name = mapping.get("akd_name", "")
            if akd_name:
                akd_counts[akd_name] = akd_counts.get(akd_name, 0) + 1
            if mapping.get("confidence_score", 0) == 0.98:
                tier1_count += 1

    print(f"\n📊 Sentiment Distribution:")
    for label, count in sorted(sentiments.items()):
        pct = (count / len(serialized)) * 100 if serialized else 0
        print(f"   {label}: {count} ({pct:.1f}%)")

    print(f"\n🏛️ Top 10 AKD by Frequency:")
    sorted_akd = sorted(akd_counts.items(), key=lambda x: x[1], reverse=True)
    for akd_name, count in sorted_akd[:10]:
        print(f"   {akd_name}: {count}")

    print(f"\n⚡ Tier-1 Fast Match: {tier1_count} classifications (0ms latency)")

    # Print sample results
    print(f"\n📝 Sample Analyzed Items:")
    for i, item in enumerate(serialized[:5], 1):
        akd_names = [m.get("akd_name", "?") for m in item.get("akd_mappings", [])]
        print(f"[{i}] {item.get('source_name', '?')} | {item.get('sentiment')} ({item.get('sentiment_score')})")
        print(f"    Title: {item.get('title', '')[:80]}")
        print(f"    AKD:   {', '.join(akd_names)}")
        print(f"    URL:   {item.get('url', '')}\n")


if __name__ == "__main__":
    asyncio.run(main())
