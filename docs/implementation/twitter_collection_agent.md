# 📋 Implementation Plan: Twitter/X Collection Agent

> **Fase / Sprint**: Sprint 3 — Data Collection Agents (Bulan 2, Hari 26–30)  
> **Komponen**: `src/agents/twitter_collection.py`, `src/tasks/collection.py`, `tests/test_agents/test_twitter_collection.py`  
> **Status**: Draf Rencana Implementasi

---

## 🛠️ 1. Tujuan & Overview

Mengimplementasikan **TwitterCollectionAgent** untuk mengumpulkan postingan (tweets) dari Twitter/X yang relevan dengan topik **18 Alat Kelengkapan Dewan (AKD) DPR RI**. 

Data tweet yang didapatkan akan dinormalisasi ke struktur `ContentItem` (`source_type="twitter"`) dan disimpan ke database PostgreSQL secara batch dengan deduplikasi berbasis URL/Tweet ID (`ON CONFLICT DO NOTHING`).

---

## 🏗️ 2. Arsitektur & Alur Data

```
kamus/akd_master.json (18 AKD keywords)
       │
       ▼
TwitterCollectionAgent (src/agents/twitter_collection.py)
  ├─ 1. Load AKD keywords & construct queries (e.g. "(DPR OR #DPRRI) (Komisi I OR pertahanan)")
  ├─ 2. Call X API v2 via `tweepy.Client.search_recent_tweets()`
  ├─ 3. Handle Rate Limits (429 HTTP response & tweepy.TooManyRequests)
  ├─ 4. Normalize tweet data to ContentItem format
  └─ 5. Handle mock/fallback when TWITTER_BEARER_TOKEN is not set
       │
       ▼ list[dict]
ContentRepository (src/repositories/content_repository.py)
  ├─ Batch INSERT ON CONFLICT DO NOTHING
  └─ Deduplicate by Tweet URL (https://x.com/i/status/{tweet_id})
       │
       ▼
content_items table (PostgreSQL)
       │
       ▼ triggered by
collect_twitter Celery task (src/tasks/collection.py)
```

---

## 🔍 3. Strategi Query Pencarian AKD

Pencarian tweet memerlukan pembentukan query yang efisien agar tidak membuang kuota API.

### Konstruksi Query:
```python
# Format Query untuk X API v2:
# (DPR OR "DPR RI" OR @DPR_RI) (<keywords_akd>) lang:id -is:retweet
```

Contoh Query per AKD:
- **Komisi I**: `(DPR OR "DPR RI") (pertahanan OR "luar negeri" OR Kemenkominfo OR TNI) lang:id -is:retweet`
- **Komisi III**: `(DPR OR "DPR RI") (hukum OR HAM OR kejaksaan OR kepolisian OR KPK) lang:id -is:retweet`
- **Baleg**: `(DPR OR "DPR RI") (legislasi OR RUU OR prolegnas) lang:id -is:retweet`

---

## 📐 4. Normalisasi Data (Tweet ➔ ContentItem)

Tweet yang diambil via API v2 akan dipetakan ke atribut `ContentItem` sebagai berikut:

| Atribut `ContentItem` | Data dari Tweepy Tweet | Contoh Value |
|---|---|---|
| `source_type` | Hardcoded | `"twitter"` |
| `source_name` | User handle / Name | `"@user_handle"` atau `"X / Twitter"` |
| `content` | `tweet.text` (sanitized) | Teks tweet bersih tanpa HTML / control char |
| `title` | Truncated tweet text (first 80 chars) | `"Pernyataan Komisi III mengenai RUU..."` |
| `url` | Computed Tweet URL | `https://x.com/i/status/18123456789` |
| `published_at` | `tweet.created_at` (UTC) | `2026-07-29T10:00:00Z` |
| `collected_at` | UTC Now | `2026-07-29T12:00:00Z` |

---

## 🛡️ 5. Handling Rate Limit & API Key Fallback

1. **Handling Limit X API v2 (Basic/Essential Tier)**:
   - Menambahkan sleep/delay antar query AKD.
   - Menangkap exception `tweepy.TooManyRequests` atau `tweepy.TweepyException`.
   - Mengembalikan data yang sudah berhasil ditarik daripada crash total.
2. **Graceful Fallback saat Token Belum Ada**:
   - Jika `TWITTER_BEARER_TOKEN` belum diisi di `.env`, agen akan mencatat log `WARNING` dan mengembalikan list kosong (mencegah crash di unit test/CI environment).

---

## 📂 6. Rencana Perubahan Berkas (Files to Create/Modify)

| Berkas | Tindakan | Deskripsi |
|---|---|---|
| `src/agents/twitter_collection.py` | **REWRITE** | Implementasi penuh `TwitterCollectionAgent` dengan query builder, `tweepy` client, dan sanitasi. |
| `src/config.py` | **MODIFY** | Tambahkan `TWITTER_COLLECTION_BATCH_SIZE` dan `TWITTER_MAX_RESULTS_PER_QUERY`. |
| `src/tasks/collection.py` | **MODIFY** | Tambahkan Celery task `collect_twitter` dengan retry backoff. |
| `tests/test_agents/test_twitter_collection.py` | **NEW** | Unit test komprehensif (mocking `tweepy.Client`). |

---

## 🧪 7. Rencana Verifikasi & Pengujian

### 1. Automated Unit Testing
- Test inisialisasi agen dengan/tanpa Bearer Token.
- Test query builder dari `kamus/akd_master.json`.
- Test normalisasi data tweet ke dict `ContentItem`.
- Test penanganan exception `TooManyRequests` & API error via `unittest.mock.MagicMock`.

### 2. Manual Smoke Test & Code Quality Check
- Run `ruff check src/ tests/` (0 lint errors).
- Run `pytest tests/` (62 + tests baru passing).
- Smoke test script `scratch/smoke_test_twitter.py` (eksekusi live jika API key tersedia).
