# -*- coding: utf-8 -*-
"""Analyze and save daily partitions for August 20-24 and sync combined files."""
import sys
import io
import json
import asyncio
import logging
from pathlib import Path
from collections import Counter

from src.agents.analysis import AnalysisAgent

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent

async def main():
    agent = AnalysisAgent()
    dates = ["2026-08-20", "2026-08-21", "2026-08-22", "2026-08-23", "2026-08-24"]
    
    for d in dates:
        news_file = PROJECT_ROOT / "data" / "news" / f"news_{d}.json"
        if not news_file.exists():
            continue
        with open(news_file, encoding="utf-8") as fp:
            news = json.load(fp)
        
        analyzed = []
        for art in news:
            text = art.get("title", "") + ". " + art.get("content", "")
            sentiment, score = agent.analyze_sentiment(text)
            mappings = await agent.classify_akd(text)
            analyzed.append({
                "title": art.get("title", ""),
                "content": art.get("content", ""),
                "url": art.get("url", ""),
                "published_at": art.get("published_at", ""),
                "source_type": art.get("source_type", "news_online"),
                "source_name": art.get("source_name", ""),
                "sentiment": sentiment,
                "sentiment_score": score,
                "akd_mappings": mappings,
                "analyzed_at": "2026-08-24T12:00:00.000000"
            })
        
        analysis_file = PROJECT_ROOT / "data" / "analysis" / f"analysis_{d}.json"
        with open(analysis_file, "w", encoding="utf-8") as fp:
            json.dump(analyzed, fp, ensure_ascii=False, indent=2)
        logger.info("Saved analysis for %s: %d items", d, len(analyzed))

    # Re-sync combined files
    news_dir = PROJECT_ROOT / "data" / "news"
    analysis_dir = PROJECT_ROOT / "data" / "analysis"
    
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

    logger.info("Combined sync done: %d total news, %d total analyzed", len(all_news), len(all_analysis))
    
    counts = Counter(str(x.get("published_at", ""))[:10] for x in all_analysis)
    print("\nFINAL DATE COUNTS:")
    for dt in sorted(counts.keys()):
        print(f"  {dt}: {counts[dt]} articles")

if __name__ == "__main__":
    asyncio.run(main())
