# 📋 DPR Agentic AI — Project Status & Structure

> **Terakhir diperbarui**: 29 Juli 2026  
> **Sprint Aktif**: Sprint 3 — Data Collection Agents (Bulan 2)  
> **Status Build**: ✅ 62/62 Tests Passing | 0 Lint Errors

---

## 🎯 Tentang Proyek

Sistem **Agentic AI** untuk klasifikasi Alat Kelengkapan Dewan (AKD) dan analisis sentimen media terhadap DPR RI. Menggunakan arsitektur multi-agent berbasis **Gemini AI** dan **IndoBERT**, diorkestrasi oleh **LangGraph**.

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT DASHBOARD                        │
│                    (dashboard/app.py)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP REST
┌────────────────────────▼────────────────────────────────────────┐
│                     FastAPI BACKEND                              │
│                     (src/main.py)                                │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────┐  │
│  │ /analysis│  │/recommendations│  │  /reports │  │  /trends  │  │
│  └──────────┘  └──────────────┘  └───────────┘  └───────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│               LangGraph SUPERVISOR AGENT                        │
│              (src/agents/supervisor.py)                          │
│                                                                  │
│  ┌────────────┐  ┌──────────┐  ┌───────┐  ┌─────────────────┐  │
│  │  Collect   │→│ Analyze  │→│ Trend │→│     Insight      │  │
│  │News+Twitter│  │Sentiment │  │Detect │  │Summary+Recommend│  │
│  └────────────┘  └──────────┘  └───────┘  └─────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │PostgreSQL│  │  Redis   │  │  Celery  │
    │  (Data)  │  │ (Cache)  │  │ (Queue)  │
    └──────────┘  └──────────┘  └──────────┘
```

---

## 📁 Struktur Direktori Proyek

```
dpr-agentic-ai/
├── src/                          # 🧠 Source code utama
│   ├── main.py                   # Entry point FastAPI + CORS
│   ├── config.py                 # Environment config (Pydantic)
│   ├── database.py               # PostgreSQL + SQLAlchemy engine
│   ├── cache.py                  # Redis client (lazy + pooling)
│   ├── auth.py                   # API Key authentication
│   ├── exceptions.py             # Custom exception classes
│   ├── logging_config.py         # Structured logging setup
│   │
│   ├── agents/                   # 🤖 Multi-Agent System
│   │   ├── supervisor.py         # LangGraph StateGraph orchestrator
│   │   ├── news_collection.py    # ✅ RSS feed collector (13 media)
│   │   ├── twitter_collection.py # ⏳ Tweepy X/Twitter collector (stub)
│   │   ├── analysis.py           # ⏳ Gemini + IndoBERT analysis
│   │   ├── trend.py              # ⏳ Z-score anomaly detection
│   │   ├── insight.py            # ⏳ Narrative summarization
│   │   ├── recommendation.py     # ⏳ Policy recommendation
│   │   └── report.py             # ⏳ PDF report generation
│   │
│   ├── models/                   # 💾 SQLAlchemy ORM Models
│   │   ├── content_item.py       # Berita/tweet yang dikumpulkan
│   │   ├── analysis_result.py    # Hasil analisis sentimen
│   │   ├── akd_mapping.py        # Pemetaan multi-label AKD
│   │   ├── trend_window.py       # Window kalkulasi tren
│   │   └── recommendation.py     # Rekomendasi kebijakan
│   │
│   ├── repositories/             # 🗄️ Database Access Layer
│   │   └── content_repository.py # ✅ CRUD + deduplication content
│   │
│   ├── routes/                   # 🌐 REST API Endpoints
│   │   ├── analysis.py           # POST /analyze, GET /analysis/{id}
│   │   ├── recommendations.py    # GET/PATCH recommendations
│   │   ├── reports.py            # POST /reports
│   │   └── trends.py             # GET /trends
│   │
│   ├── schemas/                  # 📐 Pydantic Validation Schemas
│   │   ├── analysis.py           # AnalyzeRequest, AnalysisResultCreate
│   │   └── content.py            # ContentItemCreate, ContentItemRead
│   │
│   ├── tasks/                    # ⏰ Celery Background Tasks
│   │   └── collection.py         # ✅ collect_news (+ retry backoff)
│   │
│   └── utils/                    # 🔧 Utility Functions
│       ├── validators.py         # AKD validation, text sanitization
│       └── gemini_client.py      # Gemini API client (lazy init)
│
├── dashboard/                    # 📊 Streamlit Frontend
│   ├── app.py                    # Dashboard entry point
│   ├── pages/                    # Multi-page dashboard
│   └── components/               # Reusable UI components
│
├── kamus/                        # 📚 Data Konfigurasi
│   ├── akd_master.json           # 18 AKD (Komisi I-XI, Badan, Pimpinan)
│   └── feeds.json                # 13 RSS feed media nasional
│
├── tests/                        # 🧪 Test Suite (62 tests)
│   ├── test_agents/              # Agent unit tests
│   ├── test_models/              # ORM model tests
│   ├── test_repositories/        # Repository pattern tests
│   ├── test_routes/              # API endpoint tests
│   ├── test_schemas/             # Validation schema tests
│   └── test_utils/               # Utility function tests
│
├── migrations/                   # 🗃️ Alembic DB Migrations
├── docs/                         # 📝 Dokumentasi
│   ├── timeline_agentic_ai_dpr_ri.md
│   ├── TWITTER_SCRAPING_GUIDE.md # Panduan Twitter/X scraping tanpa API key dari nol
│   ├── SCRAPING_GUIDE.md         # Panduan data collection & scraping dari awal
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DATABASE.md
│   └── SETUP.md
│
├── docker-compose.yml            # 🐳 Dev environment
├── docker-compose.prod.yml       # 🐳 Production environment
├── Dockerfile                    # Backend container
├── Dockerfile.dashboard          # Dashboard container
├── pyproject.toml                # Dependencies & config
└── .env.example                  # Environment variables template
```

---

## ✅ Fitur yang Sudah Jalan

### 1. Infrastructure & Backend (Sprint 1-2)
- [x] FastAPI server dengan CORS middleware
- [x] PostgreSQL database connection (SQLAlchemy 2.x + psycopg)
- [x] Redis cache (lazy init + connection pooling, max 20 koneksi)
- [x] Celery task queue dengan Redis broker
- [x] API Key authentication untuk write endpoints
- [x] 5 ORM models dengan timezone-aware `timestamptz`
- [x] Alembic migration setup
- [x] Docker Compose (PostgreSQL 15, Redis 7, Celery)

### 2. Data Collection Agents (Sprint 3) ✅ **LIVE**
- [x] **News Collection Agent**: 13 sumber berita nasional via RSS feeds
- [x] **Twitter/X Collection Agent**: Scraping via `twikit` (bebas API key, menggunakan kredensial X)
- [x] **Dinamis Query Builder**: Membuat kata kunci pencarian otomatis dari 18 AKD (`kamus/akd_master.json`)
- [x] **Database Persistence**: Repository pattern dengan deduplikasi URL (`ON CONFLICT DO NOTHING`)
- [x] **Celery Task Queue**: Background task `collect_news` & `collect_twitter` dengan retry + exponential backoff

### 3. Analysis & Classification Engine (Sprint 4) ✅ **LIVE**
- [x] **AnalysisAgent**: Analisis sentimen (Positif/Negatif/Netral) + skor sentimen `[-1.0, 1.0]`
- [x] **Gemini Zero-Shot AKD Classification**: Pemetaan ke top 1..3 AKD dengan `confidence_score` & `rank`
- [x] **Keyword Fallback Matcher**: Tetap berfungsi offline jika `GEMINI_API_KEY` tidak diset
- [x] **REST API Endpoints**: `POST /api/v1/analyze` (201 Created) dan `GET /api/v1/analysis/{id}` (200/404)
- [x] **Database Integration**: Menyimpan otomatis ke tabel `content_items`, `item_analysis`, dan `akd_mapping`

### 4. LangGraph Supervisor (Skeleton)
- [x] StateGraph dengan 4 nodes: collect → analyze → trend → insight
- [x] Typed `AgentState` untuk data flow antar agent

---

## 📡 Sumber Berita Aktif (13 Media)

| # | Media | Status | Rata-rata Artikel |
|---|---|---|---|
| 1 | Detik.com | ✅ Stabil | ~100 |
| 2 | Antaranews.com | ✅ Stabil | ~50 |
| 3 | Viva.co.id | ✅ Stabil | ~100 |
| 4 | RMOL.id | ⚠️ Intermiten | ~10 |
| 5 | Republika.co.id | ✅ Stabil | ~15 |
| 6 | CNN Indonesia | ✅ Stabil | ~100 |
| 7 | Liputan6.com | ✅ Stabil | ~50 |
| 8 | Tribunnews.com | ⚠️ Intermiten | ~20 |
| 9 | Tempo.co | ✅ Stabil | ~50 |
| 10 | Suara.com | ⚠️ Intermiten | ~20 |
| 11 | Mediaindonesia.com | ✅ Stabil | ~100 |
| 12 | RM.id | ⚠️ Intermiten | ~20 |
| 13 | Sindonews.com | ✅ Stabil | ~30 |

> **Note:** Kompas.com dan Kumparan.com tidak tersedia karena kedua media telah menghentikan layanan RSS secara permanen.

---

## ⏳ Yang Belum Dikerjakan (Upcoming)

### Sprint 3 (Bulan 2) — Sisa
| Hari | Task | PJ |
|---|---|---|
| 26-30 | Twitter/X Collection Agent (tweepy + AKD keywords) | Inf 2 |
| 31-32 | Deduplikasi konten & validasi source_type | SI 1 |
| 33-34 | Celery Beat: auto-collect setiap 4 jam | Inf 1 |
| 35 | Integration testing dual-source | SI 2 |
| 38-39 | Data preprocessing (bersihkan iklan/junk) | Inf 2 |

### Sprint 4 (Bulan 3) — NLP & Klasifikasi
| Hari | Task | PJ |
|---|---|---|
| 41-45 | IndoBERT sentiment analysis | Inf 2 |
| 46-50 | Gemini zero-shot AKD classification | Inf 2 |
| 51-59 | Evaluasi akurasi (target sentimen ≥75%, AKD top-1 ≥70%) | SI 2 |

### Sprint 5-8 (Bulan 4-6)
- LangGraph orkestrasi penuh + Trend Detection
- Insight Agent (narrative summarization)
- Recommendation Agent + human-in-the-loop
- Streamlit Dashboard + PDF Report Generator
- System Integration Testing (SIT) + Usability Testing

---

## 🛠️ Quick Start untuk Development

```bash
# 1. Clone repo
git clone https://github.com/BertrandOscarSaputra/dpr-agentic-ai.git
cd dpr-agentic-ai

# 2. Setup Python environment
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e .

# 3. Copy environment variables
cp .env.example .env

# 4. Start infrastructure
docker compose up -d     # PostgreSQL + Redis

# 5. Run tests
pytest tests/ -v

# 6. Start FastAPI server
uvicorn src.main:app --reload

# 7. Test news collection
python -c "
import asyncio
from src.agents.news_collection import NewsCollectionAgent
agent = NewsCollectionAgent()
articles = asyncio.run(agent.collect())
print(f'{len(articles)} articles collected')
"
```

---

## 🧪 Test Results

```
92 passed in 13s ✅
Coverage: agents, models, repositories, routes, schemas, utils, cache
```

---

## 📌 Tech Stack

| Layer | Technology |
|---|---|
| **API** | FastAPI (Python 3.11+) |
| **AI Orchestration** | LangGraph (StateGraph) |
| **NLP Sentiment** | IndoBERT (HuggingFace) |
| **AI Classification** | Gemini 2.5 Flash |
| **Database** | PostgreSQL 15 + SQLAlchemy 2.x |
| **Cache** | Redis 7+ |
| **Task Queue** | Celery + Redis broker |
| **Dashboard** | Streamlit |
| **PDF Reports** | ReportLab / WeasyPrint |
| **Containerization** | Docker + Docker Compose |
| **Testing** | pytest + ruff linter |
