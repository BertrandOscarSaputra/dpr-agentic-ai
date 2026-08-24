# Scraping Setup Guide — Multi-Channel Ingestion Pipeline

## Overview

The **DPR Agentic AI** platform relies on real-time, authentic multi-channel data ingestion from two primary sources:
1. **Tier-1 Indonesian Online Mass Media**: Scraped via 12+ configured RSS feeds.
2. **Social Media (X / Twitter)**: Scraped via **TwitterAPI.io** REST Service endpoints.

This guide details the setup, configuration, query definitions, deduplication logic, rate limiting, and failure handling for both channels.

---

## Channel 1: Online News RSS Feeds Ingestion

### Configured Media Sources (`kamus/feeds.json`)
The system polls RSS XML endpoints across 12 major Indonesian news portals:

| Source | Category | Endpoint URL |
|---|---|---|
| **Detik.com** | General News | `https://rss.detik.com/index.php/detikcom` |
| **Antara News** | National Wire | `https://www.antaranews.com/rss/terkini.xml` |
| **CNN Indonesia** | Politics/National | `https://www.cnnindonesia.com/nasional/rss` |
| **Tempo.co** | National | `https://rss.tempo.co/nasional` |
| **Republika** | National | `https://www.republika.co.id/rss` |
| **Liputan6** | News | `https://feed.liputan6.com/rss` |
| **CNBC Indonesia** | Economy/Politics | `https://www.cnbcindonesia.com/news/rss` |
| **Sindonews** | National | `https://metro.sindonews.com/rss` |
| **Kompas.com** | National | `https://news.kompas.com/rss` |
| **Merdeka.com** | Politics | `https://www.merdeka.com/feed/` |
| **JPNN** | National | `https://www.jpnn.com/index.php?mib=rss` |
| **Viva.co.id** | Politics | `https://www.viva.co.id/get/all` |

### Feed Parsing & Content Sanitization (`src/agents/news_collection.py`)
- **Timeout Protection**: Each feed fetch is guarded by a configurable HTTP timeout (`NEWS_FEED_TIMEOUT = 10s`).
- **Resilience & Fault Isolation**: If a single media portal's RSS feed is down or times out, errors are caught per-feed without disrupting the remaining 11 sources.
- **HTML Sanitization**: Raw entry content is passed through `sanitize_text()`, stripping HTML tags, script snippets, and normalizing whitespace.

### Multi-Level In-Memory Deduplication
To prevent duplicate articles across overlapping feeds (e.g. general RSS vs category RSS):
- **URL Hash Check**: Articles with identical URLs are dropped.
- **Normalized Title Key**: Titles are stripped, lowercased, and deduplicated in-memory.

---

## Channel 2: X / Twitter Ingestion via TwitterAPI.io

### REST API Integration Architecture
To capture public discourse on Twitter/X in real-time, `TwitterCollectionAgent` integrates with **TwitterAPI.io** REST endpoints:
- **API Endpoint**: `https://api.twitterapi.io/twitter/tweet/advanced_search`
- **Authentication**: Bearer token headers via `X-API-Key`.
- **Language Filtering**: Forced Indonesian language content matching (`lang:id`).
- **Noise Filtering**: Exclusion of retweets (`-filter:retweets`) to retain original public opinions.

### AKD Keyword Extraction & Selection Methodology
Targeted search queries for 24 AKD units are created using a 4-layer taxonomy:
1. **Official DPR Regulations**: Regulatory scope defined in parliamentary rules for Komisi I–XIII and parliamentary bodies.
2. **K/L Partner Ministries & Acronyms**: Inclusion of key agency acronyms (e.g., *KPK, Kejaksaan, Polri, BSSN, BIN, KPU, Bawaslu, IKN, PLN, Pertamina, BPJS, BPOM, BPK*).
3. **Substantive Policy Terms**: Key policy domain keywords (e.g., *alutsista, siber, pertanahan, korupsi, pangan, APBN, energi, imigrasi*).
4. **Boolean Query Construction**: Combining terms with `OR`, `AND`, exact phrase quotes `""`, and language constraints.

```json
{
  "queries": [
    {
      "akd_name": "Ketua DPR",
      "query": "Puan Maharani DPR OR \"Ketua DPR\" lang:id -filter:retweets"
    },
    {
      "akd_name": "Komisi I",
      "query": "\"Komisi I\" DPR OR \"Komisi I DPR RI\" OR (TNI Kemenhan BSSN) lang:id -filter:retweets"
    },
    {
      "akd_name": "Komisi III",
      "query": "\"Komisi III\" DPR OR \"Komisi III DPR RI\" OR (KPK Kejaksaan Polri) lang:id -filter:retweets"
    },
    {
      "akd_name": "Komisi XII",
      "query": "\"Komisi XII\" DPR OR \"Komisi 12 DPR\" OR (Pertamina PLN ESDM) lang:id -filter:retweets"
    },
    {
      "akd_name": "Komisi XIII",
      "query": "\"Komisi XIII\" DPR OR \"Komisi 13 DPR\" OR (Imigrasi Lapas HAM) lang:id -filter:retweets"
    }
  ]
}
```

---

## Daily Partitioning & Incremental Data Pipeline

Collected articles and tweets are stored in structured daily JSON partitions under `data/`:

```text
data/
├── news/
│   ├── news_2026-08-09.json   # 163 articles
│   ├── news_2026-08-10.json   # 243 articles
│   └── news_output.json       # Combined latest feed
├── tweets/
│   ├── tweets_2026-08-09.json # Daily tweet partition
│   └── tweets_output.json     # Combined latest tweets
```

### Batch Analysis Incremental Skipping (`run_analysis_batch.py`)
When executing batch analysis:
1. The script loads all raw JSON files from `data/news/` and `data/tweets/`.
2. `_deduplicate_items()` removes duplicate URLs and normalized titles across files.
3. `_load_already_analyzed_urls()` checks existing `data/analysis/*.json` files.
4. Previously analyzed articles are **skipped with 0ms latency and 0 API cost**.

---

## Rate Limiting & Quota Management

- **TwitterAPI.io Quota Handling**: Per-query rate limit isolation ensures API responses with HTTP 429 are logged cleanly without generating hallucinated data.
- **Batch Processing Rate Limit**: `run_analysis_batch.py` enforces a `0.5s` delay between items when invoking external LLMs to avoid hitting API rate limits.
- **CLI Batch Limit Flag**: Supports testing small sample batches:
  ```bash
  uv run run_analysis_batch.py --limit 10
  ```
