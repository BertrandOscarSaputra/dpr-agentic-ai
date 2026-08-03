# 📋 DPR Agentic AI — Project Status & Structure

> **Terakhir diperbarui**: 3 Agustus 2026  
> **Sprint Aktif**: Sprint 4 — Sentiment & Gemini AKD Classification Engine (Bulan 3)  
> **Status Build**: ✅ 92/92 Tests Passing | 0 Lint Errors  

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
│   │   ├── twitter_collection.py # ✅ Twikit X/Twitter scraper + cookies.json
│   │   ├── analysis.py           # 🚀 Gemini + IndoBERT analysis
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
│   │   └── collection.py         # ✅ collect_news & collect_twitter (+ retry backoff)
│   │
│   └── utils/                    # 🔧 Utility Functions
│       ├── validators.py         # AKD validation (24 AKD), text sanitization
│       └── gemini_client.py      # Gemini API client (lazy init)
│
├── dashboard/                    # 📊 Streamlit Frontend
│   ├── app.py                    # Dashboard entry point
│   ├── pages/                    # Multi-page dashboard
│   └── components/               # Reusable UI components
│
├── kamus/                        # 📚 Data Konfigurasi Master
│   ├── akd_master.json           # ✅ 24 AKD Master (2024-2029: Komisi I-XIII, Badans, Pimpinan)
│   └── feeds.json                # ✅ 13 RSS feed media nasional
│
├── tests/                        # 🧪 Test Suite (92 tests)
│   ├── test_agents/              # Agent unit tests
│   ├── test_models/              # ORM model tests
│   ├── test_repositories/        # Repository pattern tests
│   ├── test_routes/              # API endpoint tests
│   ├── test_schemas/             # Validation schema tests
│   └── test_utils/               # Utility function tests
│
├── run_news_collection.py        # 🚀 Skrip runner & JSON exporter berita
├── run_twitter_collection.py     # 🚀 Skrip runner & JSON exporter tweet
├── news_output.json              # 📄 File output JSON berita terkumpul
├── tweets_output.json            # 📄 File output JSON tweet terkumpul
├── cookies.json                  # 🔐 File sesi cookie X/Twitter
│
├── migrations/                   # 🗃️ Alembic DB Migrations
├── docs/                         # 📝 Dokumentasi
│   ├── timeline_agentic_ai_dpr_ri.md
<<<<<<< Updated upstream
│   ├── TWITTER_SCRAPING_GUIDE.md # Panduan Twitter/X scraping tanpa API key dari nol
│   ├── SCRAPING_GUIDE.md         # Panduan data collection & scraping dari awal
=======
│   ├── FIGMA_DESIGN_GUIDE.md     # 🎨 Spesifikasi UI/UX Prototype Dashboard
│   ├── TWITTER_SCRAPING_GUIDE.md # 🐦 Panduan setup scraping Twitter/X
│   ├── SCRAPING_GUIDE.md         # 📰 Panduan dasar pengumpulan data
>>>>>>> Stashed changes
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

## ✅ Fitur & Agent yang Sudah Berhasil Diselesaikan

### 1. Infrastructure & Backend (Sprint 1-2)
- [x] FastAPI server dengan CORS middleware & API Key Auth
- [x] PostgreSQL 15 database (SQLAlchemy 2.x + psycopg, `timestamptz`)
- [x] Redis 7+ cache (lazy init + connection pooling)
- [x] Celery task queue & Celery Beat scheduler
- [x] 5 ORM models + Alembic migrations
- [x] Docker Compose environment

<<<<<<< Updated upstream
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
=======
### 2. News Collection Agent (Sprint 3) ✅ **LIVE**
- [x] **13 sumber berita nasional** via RSS feeds
- [x] Parsing XML dengan `feedparser` + sanitasi teks
- [x] Error isolation per-feed
- [x] Deduplikasi URL (`ON CONFLICT DO NOTHING`)
- [x] Skrip ekspor JSON [`run_news_collection.py`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/run_news_collection.py) → [`news_output.json`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/news_output.json) (**615+ artikel**)

### 3. Twitter/X Collection Agent (Sprint 3) ✅ **LIVE**
- [x] Scraping berbasis `twikit` (bypasses Cloudflare via `cookies.json`)
- [x] Pencarian berbasis kata kunci 24 AKD master DPR RI
- [x] Penanganan recency (tweet real-time / terbaru)
- [x] Feature flag `ENABLE_TWITTER_COLLECTION` untuk kontrol eksekusi
- [x] Skrip ekspor JSON [`run_twitter_collection.py`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/run_twitter_collection.py) → [`tweets_output.json`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/tweets_output.json) (**560+ tweet**)

### 4. Master Kamus 24 AKD DPR RI (2024-2029) ✅
- [x] Komisi I s/d Komisi XIII
- [x] Badan (BURT, MKD, Baleg, BAKN, BKSAP, BPKPH, Bamus, Banggar, BAM, Pansus)
- [x] Pimpinan DPR RI
>>>>>>> Stashed changes

---

## 🚀 Fokus Selanjutnya: Sprint 4 (Bulan 3) — NLP & Klasifikasi

| Hari | Task Utama | Status | PJ |
|---|---|---|---|
| **41-45** | Integrasi pipeline analisis sentimen IndoBERT + Lexicon di `src/agents/analysis.py` | 🚀 Active | Inf 2 |
| **46-50** | Implementasi Gemini 2.5 Flash Zero-Shot Multi-Label Classifier untuk 24 AKD | 🚀 Active | Inf 2 |
| **51-55** | Penyimpanan hasil analisis ke tabel `analysis_results` & `akd_mappings` | ⏳ Upcoming | SI 1 |
| **56-60** | Evaluasi akurasi sentimen (target ≥75%) & akurasi klasifikasi AKD (target ≥70%) | ⏳ Upcoming | SI 2 |

---

## 🧪 Hasil Pengujian (Test Suite Status)

```bash
<<<<<<< Updated upstream
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
=======
92 passed in 12.8s ✅
>>>>>>> Stashed changes
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
