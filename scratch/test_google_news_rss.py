# -*- coding: utf-8 -*-
"""Test Google News RSS feeds for DPR topics."""
import feedparser
from dateutil import parser as dateutil_parser
from datetime import datetime, timezone, timedelta
from collections import Counter

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

dates = Counter()
articles = []

for q in queries:
    url = f"https://news.google.com/rss/search?q={q}&hl=id&gl=ID&ceid=ID:id"
    parsed = feedparser.parse(url)
    print(f"Query '{q}': {len(parsed.entries)} entries")
    for e in parsed.entries:
        d_str = getattr(e, "published", "")
        if d_str:
            try:
                dt = dateutil_parser.parse(d_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                dt_wib = dt.astimezone(WIB)
                date_key = dt_wib.strftime("%Y-%m-%d")
                dates[date_key] += 1
                articles.append({
                    "title": e.title,
                    "url": e.link,
                    "source_name": getattr(e, "source", {}).get("title", "Google News"),
                    "published_at": dt_wib.isoformat(),
                    "date_key": date_key
                })
            except Exception:
                pass

print("\nDate distribution from Google News:")
for d, c in sorted(dates.items()):
    print(f"  {d}: {c}")

print(f"\nTotal articles: {len(articles)}")
