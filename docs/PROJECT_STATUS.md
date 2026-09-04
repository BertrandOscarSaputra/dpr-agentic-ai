# 📋 DPR Agentic AI — Project Status & Structure

> **Terakhir Diperbarui**: 3 September 2026  
> **Sprint Aktif**: **Sprint 6 — RecommendationAgent, Self-Correction Critique Loop & Active Contextual Memory** (Hari 51–60)  
> **Status Build**: ✅ **102/102 Tests Passing (100%)** | 0 Lint Errors | 0 Failures  
> **Model IndoBERT Sentimen**: ✅ **Terkalibrasi (Akurasi 90.00%, Macro F1 0.8997, INT8 Quantized)** ([Dokumentasi Model](docs/DOKUMENTASI_MODEL_INDOBERT_FINAL.md))  
> **Volume Data Master**: 📰 **4,511 Berita & Analisis** (Lengkap 31 Partisi Harian: 1–31 Agustus 2026)

---

## 🎯 Tentang Proyek

Sistem **Genuine Agentic AI** untuk klasifikasi 24 Alat Kelengkapan Dewan (AKD) dan analisis sentimen media nasional terhadap DPR RI periode keanggotaan **2024–2029**. 

Menggunakan arsitektur multi-agent berbasis **LangGraph Supervisor StateGraph**, **Dynamic Tool Registry**, **Hybrid Sentiment-Weighted Z-Score Anomaly Detection**, **Self-Correction Critique Loops**, dan **Active Contextual Memory**, didukung oleh **IndoBERT Fine-Tuning** dan **Google Gemini GenAI SDK**.

---

## 🏗️ Arsitektur Sistem Terkini

```
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT DASHBOARD                        │
│                    (dashboard/app.py)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP REST / Async
┌────────────────────────▼────────────────────────────────────────┐
│                     FastAPI BACKEND                             │
│                     (src/main.py)                               │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────┐  │
│  │ /analysis│  │/recommendations│  │  /reports │  │  /trends  │  │
│  └──────────┘  └──────────────┘  └───────────┘  └───────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│             🏛️ LangGraph SUPERVISOR AGENT (L3)                  │
│              (src/agents/supervisor.py)                         │
│                                                                 │
│  ┌────────────┐  ┌──────────┐  ┌────────────────┐               │
│  │  Collect   │→│ Analyze  │→│  TrendAgent     │               │
│  │ News (L2)  │  │ AKD (L3) │  │  Z-Score Damped│               │
│  └────────────┘  └──────────┘  └───────┬────────┘               │
│                                        │                        │
│                               ┌────────▼────────┐               │
│                               │ Anomaly Critique│               │
│                               │  (Simpul C3)    │               │
│                               └────────┬────────┘               │
│                                        │                        │
│                               ┌────────▼────────┐               │
│                               │ Active Memory   │               │
│                               │ 30-Day Context  │               │
│                               └────────┬────────┘               │
│                                        │                        │
│  ┌────────────┐               ┌────────▼────────┐               │
│  │Report Agent│               │ Recommendation  │               │
│  │ PDF Export │               │ Action Formulate│               │
│  └──────▲─────┘               └────────┬────────┘               │
│         │                              │                        │
│         │                     ┌────────▼────────┐               │
│         └─────────────────────┤ Critique Loop   │               │
│             (Score >= 0.75)   │ Self-Correction │               │
│                               └────────┬────────┘               │
│                                        │ (Score < 0.75: Loop)   │
│                                        └────────────────────────┘
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

## 📁 Struktur Direktori & Komponen

```
dpr-agentic-ai/
├── src/                          # 🧠 Source code utama
│   ├── main.py                   # Entry point FastAPI + CORS
│   ├── config.py                 # Environment config (Pydantic Settings)
│   ├── database.py               # PostgreSQL 16 + SQLAlchemy engine
│   ├── cache.py                  # Redis client (connection pooling)
│   ├── auth.py                   # API Key authentication
│   ├── exceptions.py             # Custom domain exception classes
│   ├── logging_config.py         # Structured low-cardinality logging
│   │
│   ├── agents/                   # 🤖 Multi-Agent Reasoning System
│   │   ├── supervisor.py         # ✅ LangGraph Cyclic StateGraph orchestrator (L3)
│   │   ├── tools.py              # ✅ Dynamic Tool Registry (@tool decorators)
│   │   ├── news_collection.py    # ✅ Ingestion engine + Dead Feed Health Monitor (L2)
│   │   ├── analysis.py           # ✅ 3-Tier AKD & Sentiment Classifier (L3)
│   │   ├── trend.py              # ✅ Sentiment-Weighted Damped Z-Score Engine (L3)
│   │   ├── insight.py            # 💡 Narrative synthesis & Cross-AKD correlation (L3)
│   │   ├── recommendation.py     # 📝 Policy action formulation + LLM reasoner (L3)
│   │   └── report.py             # 📄 PDF executive briefing compiler (L2)
│   │
│   ├── models/                   # 💾 SQLAlchemy ORM Models
│   │   ├── content_item.py       # Berita & artikel media
│   │   ├── analysis_result.py    # Hasil sentimen & skor
│   │   ├── akd_mapping.py        # Relasi multi-label AKD
│   │   ├── trend_window.py       # Partisi anomali Z-score harian
│   │   └── recommendation.py     # Rekomendasi aksi kebijakan
│   │
│   ├── repositories/             # 🗄️ Data Access Layer
│   │   ├── content_repository.py # ✅ CRUD + SHA-256 URL deduplication
│   │   ├── trend_repository.py   # ✅ Persistensi anomali Z-score
│   │   └── memory_repository.py  # 💾 Active contextual memory 30 hari
│   │
│   ├── routes/                   # 🌐 REST API Endpoints
│   │   ├── analysis.py           # POST /api/v1/analyze, GET /analysis/{id}
│   │   ├── agents.py             # POST /api/v1/agents/run, GET /health/feeds
│   │   ├── recommendations.py    # GET /recommendations, PATCH status
│   │   ├── reports.py            # POST /reports/generate-pdf
│   │   └── trends.py             # GET /trends/anomalies
│   │
│   ├── schemas/                  # 📐 Pydantic Data Validation
│   │   ├── analysis.py           # AnalyzeRequest, AnalysisResultCreate
│   │   ├── content.py            # ContentItemCreate, ContentItemRead
│   │   └── recommendation_schema.py # RecommendationItem, UrgencyLevel
│   │
│   ├── tasks/                    # ⏰ Background Tasks (Celery)
│   │   └── collection.py         # Async ingestion scheduler
│   │
│   └── utils/                    # 🔧 Utility & Benchmark Tools
│       ├── benchmark_evaluator.py # ✅ Automated Accuracy & Macro F1 evaluator
│       ├── build_verified_dataset.py # ✅ IndoNLU + Human annotation merger
│       ├── export_for_manual_annotation.py # ✅ Sample exporter for human labeling
│       ├── gemini_client.py      # ✅ Google GenAI SDK (gemini-3.6-flash)
│       └── validators.py         # ✅ 24 AKD taxonomy & text sanitizers
│
├── dashboard/                    # 📊 Streamlit Frontend UI
│   ├── app.py                    # Dashboard entry point
│   ├── pages/                    # Multi-page executive views
│   └── components/               # Visual KPI cards & breakdown charts
│
├── data/                         # 📂 Partitioned Data Lake
│   ├── news/                     # ✅ 31 Partisi Harian (news_2026-08-01 s.d. 31)
│   ├── analysis/                 # ✅ 31 Partisi Analisis (analysis_2026-08-01 s.d. 31)
│   ├── annotation/               # ✅ sample_for_manual_verification.csv (298 terisi)
│   └── benchmark/                # ✅ ground_truth_100.json (Gold Standard)
│
├── kamus/                        # 📚 Konfigurasi Master Parlemen
│   ├── akd_master.json           # ✅ 24 AKD Master (2024-2029) + Domain Keywords
│   └── feeds.json                # ✅ 17 RSS feeds media nasional Tier-1
│
├── notebooks/                    # 📓 Training Notebooks
│   └── train_indobert_colab.ipynb # 🚀 Colab notebook untuk training IndoBERT T4 GPU
│
├── tests/                        # 🧪 Test Suite (102 Tests Passing)
│   ├── test_agents/              # Agent unit tests (Trend, Analysis, Supervisor, Tools)
│   ├── test_models/              # ORM models tests
│   ├── test_repositories/        # Repository pattern tests
│   ├── test_routes/              # REST API endpoint tests
│   ├── test_schemas/             # Pydantic validation tests
│   └── test_utils/               # Evaluator & validator tests
│
└── docs/                         # 📝 Dokumentasi Teknis
    ├── DAY_TO_DAY_TIMELINE.md    # 📅 Roadmap 120 hari per sprint
    ├── PANDUAN_TASK_INFORMATIKA_SPRINT_6.md # 🟪 Guide teknis tim Informatika
    ├── PANDUAN_OPERASIONAL_SENTIMEN_SI1_SI2.md # 🔵 Guide praktis Zeavani & Marshanda
    ├── PROJECT_OVERVIEW.md       # 🏛️ Ringkasan arsitektur & Autonomy Level
    └── PROJECT_STATUS.md         # 📋 Status pengerjaan real-time
```

---

## 📊 Matriks Progres Per Sprint

| Sprint | Nama & Fokus | Status | Pencapaian Kunci |
|:---:|---|:---:|---|
| **Sprint 1** | Inisialisasi & Fondasi Arsitektur | ✅ Selesai | FastAPI backend, PostgreSQL 16, Redis 7, Pydantic v2 schemas. |
| **Sprint 2** | Model Database & AKD Taxonomy | ✅ Selesai | 24 Portofolio AKD (2024–2029), ORM models, Alembic migrations. |
| **Sprint 3** | Multi-Source Ingestion & 3-Tier Classifier | ✅ Selesai | 17 RSS Feeds Tier-1, Regex + Gemini + Lexicon 3-Tier Classification. |
| **Sprint 4** | LangGraph StateGraph & Dynamic Tools | ✅ Selesai | StateGraph dinamis, `@tool` registry, Dead Feed Health Monitor. |
| **Sprint 5** | Sentiment-Weighted Z-Score & IndoBERT Final | ✅ Selesai | IndoBERT Fine-Tuned (Akurasi 90.00%, F1 0.8997, INT8), Z-Score $Z_{\text{weighted}} \ge 2.0$, Ground Truth 100. |
| **Sprint 6** | **RecommendationAgent, Critique & Memory** | ⏳ **Aktif** | Formulasi aksi adaptif (RDP, Kunker, Pers), Reflexion Loop, Active Memory 30 hari. |
| **Sprint 7** | Human-in-the-Loop Gate & Approval API | 📅 Terjadwal | Workflow status $\text{draft} \rightarrow \text{reviewed} \rightarrow \text{published}$. |
| **Sprint 8** | Cross-AKD Domino Correlation & Narrative | 📅 Terjadwal | Deteksi efek isu lintas-komisi (Simpul C2) & ringkasan 1-paragraf. |
| **Sprint 9** | Streamlit Executive UI & RBAC | 📅 Terjadwal | UI/UX berstandar DPR RI, personalized digest, JWT Auth. |
| **Sprint 10** | ReportLab PDF Executive Briefing 3-Halaman | 📅 Terjadwal | Renderer dokumen resmi PDF berlogo DPR RI siap cetak. |

---

## 📈 Status Kualitas & Metrik Uji

```text
============================= 102 passed in 18.06s =============================
Status: 100% Lulus (0 Failed, 0 Errors, 1 Deprecation Warning)
Cakupan:
├── Agents        : Supervisor, TrendAgent, AnalysisAgent, NewsCollection, Tools
├── Repositories  : ContentRepository, TrendRepository
├── Routes        : Agent Routes, Analysis Routes
├── Schemas       : Analysis & Content Schemas
└── Utils         : Benchmark Evaluator (Accuracy 83.33%, Macro F1 0.8354), Validators
```

---

## 👥 Pembagian Peran Tim Aktif

| Nama / Peran | Tanggung Jawab Utama | Deliverable Aktif |
|---|---|---|
| **Zeavani (SI 1)** | Data & Model Engineering Lead | Menjalankan `build_verified_dataset.py` & Fine-Tuning IndoBERT di Colab T4 GPU. |
| **Marshanda (SI 2)** | System Analyst & QA Lead | Verifikasi 298 data anotasi manual, pengujian benchmark F1, kuantisasi INT8. |
| **Inf 1 (Informatika)** | Backend & Database Lead | Membangun `MemoryRepository` 30 hari & endpoint REST API rekomendasi. |
| **Inf 2 (Informatika)** | Agentic AI & Reasoning Lead | Mengembangkan `RecommendationAgent` & Self-Correction Critique Loop di LangGraph. |
