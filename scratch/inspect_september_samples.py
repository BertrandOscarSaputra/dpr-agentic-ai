# -*- coding: utf-8 -*-
"""Inspect sample articles for September 1, 2, 3."""
import feedparser
from dateutil import parser as dateutil_parser
from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))

queries = [
    "DPR+RI",
    "Komisi+DPR",
    "Puan+Maharani",
    "RUU+DPR",
    "sidang+paripurna+DPR",
    "Badan+Anggaran+DPR",
    "Baleg+DPR",
    "kebijakan+pemerintah+DPR"
]

by_target_date = {"2026-09-01": [], "2026-09-02": [], "2026-09-03": []}

for q in queries:
    url = f"https://news.google.com/rss/search?q={q}&hl=id&gl=ID&ceid=ID:id"
    parsed = feedparser.parse(url)
    for e in parsed.entries:
        d_str = getattr(e, "published", "")
        if d_str:
            try:
                dt = dateutil_parser.parse(d_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                dt_wib = dt.astimezone(WIB)
                date_key = dt_wib.strftime("%Y-%m-%d")
                if date_key in by_target_date:
                    by_target_date[date_key].append({
                        "title": e.title,
                        "url": e.link,
                        "source_name": getattr(e, "source", {}).get("title", "Google News"),
                        "published_at": dt_wib.isoformat(),
                        "summary": getattr(e, "summary", "")
                    })
            except Exception:
                pass

for d, arts in by_target_date.items():
    print(f"\n=== DATE: {d} ({len(arts)} articles) ===")
    for i, a in enumerate(arts[:3], 1):
        print(f"[{i}] {a['source_name']} | {a['published_at']}")
        print(f"    Title: {a['title']}")
        print(f"    URL: {a['url']}")
