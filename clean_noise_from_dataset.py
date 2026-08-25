# -*- coding: utf-8 -*-
"""Filter out consumer noise from existing daily news and analysis JSON partitions."""

import sys
import io
import json
from pathlib import Path
from collections import Counter

from src.agents.news_collection import is_consumer_or_entertainment_noise

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent
NEWS_DIR = PROJECT_ROOT / "data" / "news"
ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"


def clean_partitions():
    print("=" * 80)
    print("🧹 MEMBERSIHKAN DATASET DARI NOISE KONSUMEN & HIBURAN")
    print("=" * 80)

    total_news_before = 0
    total_news_after = 0
    total_dropped = 0

    dropped_samples = []

    # Clean daily news files
    for news_file in sorted(NEWS_DIR.glob("news_2026-*.json")):
        with open(news_file, encoding="utf-8") as f:
            articles = json.load(f)

        total_news_before += len(articles)
        clean_articles = []

        for art in articles:
            is_noise, reason = is_consumer_or_entertainment_noise(
                art.get("title", ""), art.get("content", "")
            )
            if is_noise:
                total_dropped += 1
                if len(dropped_samples) < 10:
                    dropped_samples.append((art.get("title", ""), reason))
            else:
                clean_articles.append(art)

        total_news_after += len(clean_articles)
        with open(news_file, "w", encoding="utf-8") as f:
            json.dump(clean_articles, f, ensure_ascii=False, indent=2)

    # Clean analysis files by matching clean URLs
    clean_urls = set()
    for news_file in sorted(NEWS_DIR.glob("news_2026-*.json")):
        with open(news_file, encoding="utf-8") as f:
            for item in json.load(f):
                clean_urls.add(item.get("url"))

    total_analysis_before = 0
    total_analysis_after = 0

    for analysis_file in sorted(ANALYSIS_DIR.glob("analysis_2026-*.json")):
        with open(analysis_file, encoding="utf-8") as f:
            analyzed = json.load(f)

        total_analysis_before += len(analyzed)
        clean_analyzed = [a for a in analyzed if a.get("url") in clean_urls]
        total_analysis_after += len(clean_analyzed)

        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(clean_analyzed, f, ensure_ascii=False, indent=2)

    # Re-sync combined files
    all_news = []
    seen_n = set()
    for f in sorted(NEWS_DIR.glob("news_2026-*.json")):
        with open(f, encoding="utf-8") as fp:
            for item in json.load(fp):
                key = (item.get("url", ""), str(item.get("published_at", ""))[:10])
                if key not in seen_n:
                    seen_n.add(key)
                    all_news.append(item)

    with open(NEWS_DIR / "news_output.json", "w", encoding="utf-8") as fp:
        json.dump(all_news, fp, ensure_ascii=False, indent=2)

    all_analysis = []
    seen_a = set()
    for f in sorted(ANALYSIS_DIR.glob("analysis_2026-*.json")):
        with open(f, encoding="utf-8") as fp:
            for item in json.load(fp):
                key = (item.get("url", ""), str(item.get("published_at", ""))[:10])
                if key not in seen_a:
                    seen_a.add(key)
                    all_analysis.append(item)

    with open(ANALYSIS_DIR / "analysis_output.json", "w", encoding="utf-8") as fp:
        json.dump(all_analysis, fp, ensure_ascii=False, indent=2)

    print(f"\n📊 HASIL PEMBERSIHAN DATASET:")
    print(f"   • Total Artikel Sebelum Pembersihan : {total_news_before} artikel")
    print(f"   • Total Sampah/Noise Dibuang        : {total_dropped} artikel")
    print(f"   • Total Artikel Bersih (Kebijakan)  : {len(all_analysis)} artikel")

    print(f"\n🗑️ CONTOH SAMPEL ARTIKEL YANG BERHASIL DIBUANG DARI DATASET:")
    for idx, (title, reason) in enumerate(dropped_samples, 1):
        print(f"   [{idx}] {title[:75]}...")
        print(f"       👉 Alasan Dibuang: {reason}")

    print("\n" + "=" * 80)
    print("✅ RE-SYNC DATASET SELESAI (100% BEBAS DARI NOISE KONSUMEN/TIPS/GOSIP)!")
    print("=" * 80)


if __name__ == "__main__":
    clean_partitions()
