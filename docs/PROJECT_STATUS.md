# 📋 DPR Agentic AI — Project Status & Structure

> **Terakhir diperbarui**: 20 Agustus 2026
> **Sprint Aktif**: Sprint 4 — Genuine Agentic Architecture & Advanced Capabilities (Bulan 3)
> **Status Build**: ✅ 77/77 Tests Passing | 0 Lint Errors | 0 Warnings

---

## 🎯 Tentang Proyek

Sistem **Genuine Agentic AI** untuk klasifikasi 24 Alat Kelengkapan Dewan (AKD) dan analisis sentimen media nasional terhadap DPR RI. Menggunakan arsitektur multi-agent berbasis **LangGraph Supervisor StateGraph**, **Dynamic Tool Registry**, **Self-Correction Critique Loops**, dan **Active Contextual Memory**, diorkestrasi oleh **Google Gemini GenAI SDK**.

---

## 🏗️ Arsitektur Sistem (Genuine Agentic Architecture)

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
│             🏛️ LangGraph SUPERVISOR AGENT (L3)                  │
│              (src/agents/supervisor.py)                          │
│                                                                  │
│  ┌────────────┐  ┌──────────┐  ┌───────┐  ┌─────────────────┐  │
│  │  Collect   │→│ Analyze  │→│ Trend │→│     Insight      │  │
│  │ News (L2) │  │ AKD (L3) │  │ (L3)  │  │ + Recommend(L3) │  │
│  └────────────┘  └──────────┘  └───────┘  └────────┬────────┘  │
│                                                     │           │
│                                            ┌────────▼────────┐  │
│                                            │ Critique Loop   │  │
│                                            │ Self-Correction │  │
│                                            └────────┬────────┘  │
│                                                     │           │
│                                            ┌────────▼────────┐  │
│                                            │ Report Agent    │  │
│                                            │ PDF Export (L2) │  │
│                                            └─────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │PostgreSQL│  │  Redis   │  │  Celery  │
    │16 (Data) │  │7 (Cache) │  │ (Queue)  │
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
│   ├── agents/                   # 🤖 Genuine Multi-Agent System
│   │   ├── supervisor.py         # LangGraph StateGraph orchestrator (L3)
│   │   ├── news_collection.py    # ✅ RSS feed collector — 12+ media (L2)
│   │   ├── analysis.py           # ✅ 3-Tier AKD + Sentiment engine (L3)
│   │   ├── trend.py              # 📈 Z-score anomaly + root-cause reasoning (L3)
│   │   ├── insight.py            # 💡 Narrative synthesis + historical memory (L3)
│   │   ├── recommendation.py     # 📝 Policy recommendation + critique loop (L3)
│   │   └── report.py             # 📄 PDF report generation (L2)
│   │
│   ├── models/                   # 💾 SQLAlchemy ORM Models
│   │   ├── content_item.py       # Berita yang dikumpulkan
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
│       ├── validators.py         # AKD validation (24 AKD), text sanitization
│       └── gemini_client.py      # Google GenAI SDK client (gemini-3.6-flash)
│
├── dashboard/                    # 📊 Streamlit Frontend
│   ├── app.py                    # Dashboard entry point
│   ├── pages/                    # Multi-page dashboard
│   └── components/               # Reusable UI components
│
├── kamus/                        # 📚 Data Konfigurasi Master
│   ├── akd_master.json           # ✅ 24 AKD Master (2024-2029) + domain keywords
│   └── feeds.json                # ✅ 12+ RSS feed media nasional Tier-1
│
├── data/                         # 📂 Partitioned Data Storage
│   ├── news/                     # Partisi harian berita (news_2026-08-XX.json)
│   └── analysis/                 # Partisi harian analisis (analysis_2026-08-XX.json)
│
├── tests/                        # 🧪 Test Suite (77 tests)
│   ├── test_agents/              # Agent unit tests
│   ├── test_models/              # ORM model tests
│   ├── test_repositories/        # Repository pattern tests
│   ├── test_routes/              # API endpoint tests
│   ├── test_schemas/             # Validation schema tests
│   └── test_utils/               # Utility function tests
│
├── run_news_collection.py        # 🚀 Skrip runner & JSON exporter berita
│
├── migrations/                   # 🗃️ Alembic DB Migrations
├── docs/                         # 📝 Dokumentasi
│   ├── ARCHITECTURE.md           # Cetak biru arsitektur Genuine Agentic AI
│   ├── AGENTS.md                 # Spesifikasi agen, tools, & critique loops
│   ├── PROJECT_OVERVIEW.md       # Ringkasan sistem & Autonomy Levels
│   ├── FULL_PROPOSAL_GUIDE.md    # Proposal lengkap & estimasi biaya
│   ├── FIGMA_DESIGN_GUIDE.md     # 🎨 Spesifikasi UI/UX Prototype Dashboard
│   ├── DATABASE.md               # Skema database
│   ├── API.md                    # Dokumentasi REST API
│   └── SETUP.md                  # Panduan instalasi
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

### 1. Infrastructure & Backend (Sprint 1-2) ✅
- [x] FastAPI server dengan CORS middleware & API Key Auth
- [x] PostgreSQL 16 database (SQLAlchemy 2.x + psycopg, `timestamptz`)
- [x] Redis 7+ cache (lazy init + connection pooling)
- [x] Celery task queue & Celery Beat scheduler
- [x] 5 ORM models + Alembic migrations
- [x] Docker Compose environment

### 2. News Collection Agent (Sprint 3) ✅ **LIVE**
- [x] **12+ sumber berita nasional Tier-1** via RSS feeds (Detik, Antara, CNN Indonesia, Tempo, Republika, dll.)
- [x] Parsing XML dengan `feedparser` + sanitasi HTML teks
- [x] Error isolation per-feed (kegagalan satu feed tidak mempengaruhi yang lain)
- [x] Deduplikasi URL (`ON CONFLICT DO NOTHING`)
- [x] Partisi data harian (`data/news/news_2026-08-XX.json`)
- [x] Celery Background Task `collect_news` dengan retry + exponential backoff
- [x] **1,326+ artikel** terkoleksi (1–19 Agustus 2026)

### 3. Analysis & Classification Engine (Sprint 3-4) ✅ **LIVE**
- [x] **3-Tier Hybrid AI Classification**: Regex Fast Match → Gemini LLM → Weighted Lexicon
- [x] **AnalysisAgent**: Analisis sentimen (Positif/Negatif/Netral) + skor sentimen `[-1.0, 1.0]`
- [x] **Gemini Zero-Shot AKD Classification**: Pemetaan ke top 1..3 AKD dengan `confidence_score` & `rank`
- [x] **Keyword Fallback Matcher**: Berfungsi offline jika `GEMINI_API_KEY` tidak diset
- [x] **REST API Endpoints**: `POST /api/v1/analyze` (201 Created) dan `GET /api/v1/analysis/{id}` (200/404)
- [x] **Enriched AKD Master Kamus** (`kamus/akd_master.json`): 24 portofolio dengan ratusan domain keywords
- [x] ~80% klasifikasi AKD berhasil dipetakan (turun dari 52.9% "Tidak Terklasifikasi")

### 4. LangGraph Supervisor (Skeleton) ✅
- [x] StateGraph dengan 4 nodes: collect → analyze → trend → insight
- [x] Typed `AgentState` untuk data flow antar agent

### 5. SDK & Deprecation Migrations ✅
- [x] Migrasi `google.generativeai` → `google.genai` SDK modern (`gemini-3.6-flash`)
- [x] Penggantian Streamlit `use_container_width` → `width="stretch"`
- [x] Penghapusan seluruh komponen Twitter/X (kode, dependensi, konfigurasi, data)

---

## 🚀 Roadmap Sprint 4–6: Penguatan Kapabilitas Genuine Agentic AI

### Sprint 4 (Saat Ini) — Fondasi Agentic

| Task | Deskripsi | Autonomy Level | Status |
|---|---|---|---|
| LangGraph Supervisor StateGraph Aktif | Mengubah stub menjadi orchestrator graf dinamis penuh | L3 | ⏳ Upcoming |
| Dynamic Tool Registry | Registrasi tools eksplisit per agen | L3 | ⏳ Upcoming |
| Multi-Label Dynamic Calibration (B1) | Agen menilai bobot proporsional multi-AKD | L3 | ⏳ Upcoming |
| Dead/Broken Source Detection (A3) | Agen mendeteksi feed RSS yang tidak aktif | L2 | ⏳ Upcoming |

### Sprint 5 — Reasoning & Reflection

| Task | Deskripsi | Autonomy Level | Status |
|---|---|---|---|
| False-Positive Self-Review (C3) | Review anomali: sinyal nyata atau noise/spam? | L3 | ⏳ Upcoming |
| Cross-AKD Correlation Detection (C2) | Mendeteksi efek domino antar-komisi | L3 | ⏳ Upcoming |
| Self-Correction Critique Loop | Validasi mandiri draft rekomendasi | L3 | ⏳ Upcoming |
| Comparative Historical Trend (C1) | Membandingkan pola saat ini dengan histori | L3 | ⏳ Upcoming |
| Adaptive Fallback & Error Strategy (D1) | Strategi retry cerdas berdasarkan jenis kegagalan | L3 | ⏳ Upcoming |

### Sprint 6 — Presentation & User Interaction

| Task | Deskripsi | Autonomy Level | Status |
|---|---|---|---|
| Personalized AKD Digest (E1) | Ringkasan terpersonalisasi per unit komisi | L3 | ⏳ Upcoming |
| ReportAgent PDF Briefing 3-Halaman | Export PDF eksekutif berlogo DPR RI | L2 | ⏳ Upcoming |

---

## 🧪 Hasil Pengujian (Test Suite Status)

```
============================= 77 passed in 10.84s =============================
0 warnings | 0 lint errors
Coverage: agents, models, repositories, routes, schemas, utils, cache
```

---

## 📌 Tech Stack

| Layer | Technology |
|---|---|
| **API** | FastAPI (Python 3.11+) |
| **AI Orchestration** | LangGraph (StateGraph) |
| **NLP Sentiment** | Lexicon-based weighted scorer |
| **AI Classification** | Google GenAI SDK (Gemini 3.6 Flash / 3.7 Flash) |
| **Database** | PostgreSQL 16 + SQLAlchemy 2.x |
| **Cache** | Redis 7+ |
| **Task Queue** | Celery + Redis broker |
| **Dashboard** | Streamlit + Plotly |
| **PDF Reports** | ReportLab |
| **Containerization** | Docker + Docker Compose |
| **Testing** | pytest + ruff linter |
