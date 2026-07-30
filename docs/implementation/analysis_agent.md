# 📋 Implementation Plan: Analysis Agent (Sprint 4)

> **Fase / Sprint**: Sprint 4 — Analysis & Classification Engine (Bulan 3, Hari 41–50)  
> **Komponen**: `src/agents/analysis.py`, `src/routes/analysis.py`, `src/utils/gemini_client.py`, `tests/test_agents/test_analysis_agent.py`  
> **Status**: Draf Rencana Implementasi

---

## 🛠️ 1. Tujuan & Overview

Mengimplementasikan **AnalysisAgent** yang memproses teks berita dan tweet untuk:
1. **Analisis Sentimen (IndoBERT / Lexicon Fallback)**: Mengklasifikasikan sentimen menjadi `"Positif"`, `"Negatif"`, atau `"Netral"` beserta `sentiment_score` di rentang `[-1.0, 1.0]`.
2. **Klasifikasi AKD (Gemini Zero-Shot AI)**: Memetakan teks ke 1 s.d. 3 Alat Kelengkapan Dewan (AKD) terbaik dari 18 daftar master di `kamus/akd_master.json` beserta `confidence_score` (`[0.0, 1.0]`) dan `rank` (`1..3`).
3. **API Integration**: Menyediakan endpoint REST `POST /api/v1/analyze` dan `GET /api/v1/analysis/{id}` yang terhubung langsung ke database PostgreSQL.

---

## 🏗️ 2. Arsitektur & Pipeline Analisis

```
Input Teks (via API atau Data Collector)
       │
       ├───────────────────────────────────────────┐
       ▼                                           ▼
1. IndoBERT / Lexicon Sentiment             2. Gemini Zero-Shot AKD Classifier
   - Output: sentiment ("Positif"/"Negatif"/     - Prompt with 18 AKD definitions
     "Netral") & sentiment_score (-1..1)         - Output: Top 1..3 AKD mappings
       │                                           │
       └─────────────────────┬─────────────────────┘
                             ▼
3. Format Result Payload & DB Persistence
   - Insert to content_items
   - Insert to item_analysis
   - Insert to akd_mapping (1:N)
                             │
                             ▼
4. JSON Response (FastAPI POST /api/v1/analyze)
```

---

## 📐 3. Detail Komponen

### A. Sentiment Analysis (`IndoBERT` + Fallback)
- **Model**: `indobenchmark/indobert-base-p1` atau lexicon-based analyzer.
- **Output Mapping**:
  - `Positif`: score > +0.15 (misal: 0.85)
  - `Negatif`: score < -0.15 (misal: -0.72)
  - `Netral`: score di antara [-0.15, +0.15] (misal: 0.0)

### B. AKD Classification (`Gemini 2.5 Flash`)
- Menggunakan `src/utils/gemini_client.py`.
- Prompt mengirim daftar 18 AKD dan instruksi untuk mengembalikan JSON terstruktur:
  ```json
  {
    "akd_mappings": [
      {"akd_name": "Komisi III", "confidence_score": 0.92, "rank": 1},
      {"akd_name": "Baleg", "confidence_score": 0.65, "rank": 2}
    ]
  }
  ```
- Graceful Fallback: Jika `GEMINI_API_KEY` belum diisi, agen menggunakan keyword matcher berbasis `kamus/akd_master.json`.

---

## 📂 4. Rencana Berkas (Files to Modify/Create)

| Berkas | Jenis | Deskripsi |
|---|---|---|
| `src/utils/gemini_client.py` | **MODIFY** | Tambahkan helper zero-shot AKD classification. |
| `src/agents/analysis.py` | **REWRITE** | Implementasi penuh `AnalysisAgent` (Sentimen + AKD Classification). |
| `src/routes/analysis.py` | **REWRITE** | Implementasi `POST /analyze` dan `GET /analysis/{id}` terhubung ke DB. |
| `tests/test_agents/test_analysis_agent.py` | **MODIFY** | Unit tests komprehensif untuk analisis sentimen & AKD classification. |
| `tests/test_routes/test_analysis_routes.py` | **MODIFY** | Integration tests untuk endpoint REST analysis. |

---

## 🧪 5. Verification Plan

1. **Unit Testing (`pytest`)**:
   - Test sentimen `Positif`, `Negatif`, `Netral`.
   - Test AKD classification (mocked Gemini & keyword fallback).
   - Test schema bounds & DB persistence.
2. **Code Quality**:
   - `ruff check src/ tests/` (0 lint errors).
   - `pytest tests/` (semua test passed).
