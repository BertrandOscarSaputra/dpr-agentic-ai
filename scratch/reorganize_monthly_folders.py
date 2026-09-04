# -*- coding: utf-8 -*-
"""Organize data/news and data/analysis into monthly subfolders."""
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
NEWS_DIR = BASE_DIR / "data" / "news"
ANALYSIS_DIR = BASE_DIR / "data" / "analysis"

def reorganize():
    # 1. News
    aug_news_dir = NEWS_DIR / "2026-08"
    sep_news_dir = NEWS_DIR / "2026-09"
    aug_news_dir.mkdir(parents=True, exist_ok=True)
    sep_news_dir.mkdir(parents=True, exist_ok=True)

    moved_news = 0
    for f in list(NEWS_DIR.glob("news_2026-08-*.json")):
        dest = aug_news_dir / f.name
        shutil.move(str(f), str(dest))
        moved_news += 1
    print(f"Moved {moved_news} August news files to {aug_news_dir}")

    # 2. Analysis
    aug_analysis_dir = ANALYSIS_DIR / "2026-08"
    sep_analysis_dir = ANALYSIS_DIR / "2026-09"
    aug_analysis_dir.mkdir(parents=True, exist_ok=True)
    sep_analysis_dir.mkdir(parents=True, exist_ok=True)

    moved_analysis = 0
    for f in list(ANALYSIS_DIR.glob("analysis_2026-08-*.json")):
        dest = aug_analysis_dir / f.name
        shutil.move(str(f), str(dest))
        moved_analysis += 1
    print(f"Moved {moved_analysis} August analysis files to {aug_analysis_dir}")

    # Verify counts
    print(f"August news count: {len(list(aug_news_dir.glob('*.json')))}")
    print(f"August analysis count: {len(list(aug_analysis_dir.glob('*.json')))}")
    print(f"News root master exists: {(NEWS_DIR / 'news_output.json').exists()}")
    print(f"Analysis root master exists: {(ANALYSIS_DIR / 'analysis_output.json').exists()}")

if __name__ == "__main__":
    reorganize()
