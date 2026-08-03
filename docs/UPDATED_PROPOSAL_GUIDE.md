# 📑 Panduan Penyusunan Proposal Proyek Terbarui (Updated Project Proposal Guide)
## Agentic AI Klasifikasi AKD & Analisis Sentimen DPR RI

Dokumen ini disusun sebagai **panduan & struktur lengkap** untuk menyusun proposal proyek terbarui yang siap diajukan kepada **Dosen Pembimbing Skripsi**, **Pembimbing Magang Sekretariat Jenderal DPR RI**, maupun **Stakeholder Proyek**.

---

## 📑 DAFTAR ISI PROPOSAL

1. [Judul & Informasi Proyek](#1-judul--informasi-proyek)
2. [Latar Belakang & Rumusan Masalah](#2-latar-belakang--rumusan-masalah)
3. [Tujuan & Manfaat Proyek](#3-tujuan--manfaat-proyek)
4. [Batasan Sistem & Cakupan Data](#4-batasan-sistem--cakupan-data)
5. [Arsitektur Sistem Terbarui (Agentic AI)](#5-arsitektur-sistem-terbarui-agentic-ai)
6. [Daftar 24 AKD Master DPR RI (Periode 2024–2029)](#6-daftar-24-akd-master-dpr-ri-periode-20242029)
7. [Pencapaian Milestone Proyek (Progress Report)](#7-pencapaian-milestone-proyek-progress-report)
8. [Rencana Jadwal Pelaksanaan (Timeline 6 Bulan)](#8-rencana-jadwal-pelaksanaan-timeline-6-bulan)
9. [Target Performa & Indikator Keberhasilan (KPI)](#9-target-performa--indikator-keberhasilan-kpi)
10. [Metode Pengujian & Quality Control](#10-metode-pengujian--quality-control)

---

## 1. Judul & Informasi Proyek

### **Judul Proposal**
> **"PENGEMBANGAN SISTEM AGENTIC AI BERBASIS GEMINI DAN INDOBERT UNTUK KLASIFIKASI ALAT KELENGKAPAN DEWAN (AKD) SERTA ANALISIS SENTIMEN MEDIA MASSA DAN MEDIA SOSIAL DPR RI"**

### **Identitas Proyek**
- **Institusi Mitiga / Stakeholder**: Sekretariat Jenderal DPR RI (Sub. Analisis Media)
- **Teknologi Utama**: Python 3.11+, FastAPI, Gemini 2.5 Flash, IndoBERT, LangGraph, PostgreSQL 15, Redis 7, Celery, Streamlit
- **Periode Pelaksanaan**: 6 Bulan (Sprint 1 s.d. Sprint 8)

---

## 2. Latar Belakang & Rumusan Masalah

### **Latar Belakang**
1. **Tingginya Volume Pemberitaan & Opini Publik**: Setiap hari ribuan berita online nasional dan tweet publik membahas kinerja DPR RI, komisi, dan badan-badan di dalamnya.
2. **Keterbatasan Analisis Manual**: Sub Bagian Analisis Media DPR RI membutuhkan waktu dan sumber daya besar jika pemantauan dan pengelompokan berita dilakukan secara manual.
3. **Perubahan Struktur Komisi DPR RI (2024–2029)**: Jumlah Alat Kelengkapan Dewan (AKD) berkembang menjadi **24 AKD** (termasuk Komisi I–XIII, Bamus, Banggar, BAM, Pansus), sehingga diperlukan sistem klasifikasi otomatis yang adaptif dan akurat.

### **Rumusan Masalah**
1. Bagaimana mengotomatiskan penarikan data dari 13 portal berita online nasional dan Twitter/X secara real-time?
2. Bagaimana mengklasifikasikan isu ke dalam 24 AKD DPR RI dengan tingkat akurasi tinggi menggunakan pendekatan *Gemini Zero-Shot Multi-Label*?
3. Bagaimana mengukur orientasi sentimen publik (Positif, Negatif, Netral) secara objektif menggunakan model *IndoBERT*?
4. Bagaimana menyajikan tren anomali isu dan rekomendasi naratif kebijakan secara interaktif melalui dashboard executive Streamlit?

---

## 3. Tujuan & Manfaat Proyek

### **Tujuan Proyek**
1. Membangun pipeline penarikan data berita online (13 media RSS) dan Twitter/X (`twikit` scraper) secara otomatis.
2. Mengimplementasikan arsitektur *Multi-Agent Agentic AI* (diorkestrasi dengan LangGraph) untuk tugas pengumpulan, analisis sentimen, deteksi anomali, dan pembuatan rekomendasi.
3. Mengklasifikasikan konten ke dalam 24 AKD DPR RI dengan target akurasi Top-1 ≥ 70%.
4. Menganalisis sentimen dengan target akurasi ≥ 75%.
5. Menyediakan Dashboard Executive Streamlit dan *Automated PDF Executive Report*.

### **Manfaat Proyek**
- **Bagi Setjen DPR RI**: Mempercepat penyusunan laporan pemantauan media harian bagi pimpinan AKD.
- **Bagi Pembuat Kebijakan**: Memberikan peringatan dini (*early warning system*) jika terjadi anomali lonjakan isu negatif di AKD tertentu.

---

## 4. Batasan Sistem & Cakupan Data

1. **Sumber Data Berita**: 13 portal media online nasional Tier-1 via RSS feed (Detik, Antara, Tempo, CNN Indonesia, Republika, Liputan6, Viva, RMOL, Media Indonesia, Sindonews, Suara, RM.id, Tribunnews).
2. **Sumber Data Media Sosial**: Twitter/X via cookie session (`cookies.json` / `twikit`).
3. **Cakupan AKD**: 24 AKD Master DPR RI periode 2024–2029.
4. **Bahasa**: Bahasa Indonesia.

---

## 5. Arsitektur Sistem Terbarui (Agentic AI)

Arsitektur sistem menggunakan pendekatan multi-agent independen yang diorkestrasi oleh **LangGraph StateGraph**:

```
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT DASHBOARD                        │
│                   (Interactive Executive UI)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────────┐
│                     FastAPI BACKEND                             │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────┐  │
│  │ /analysis│  │/recommendations│  │  /reports │  │  /trends  │  │
│  └──────────┘  └──────────────┘  └───────────┘  └───────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│               LangGraph SUPERVISOR AGENT                        │
│                                                                  │
│  ┌────────────┐  ┌──────────┐  ┌───────┐  ┌─────────────────┐  │
│  │  Collect   │→│ Analyze  │→│ Trend │→│     Insight     │  │
│  │News+Twitter│  │Sentiment │  │Detect │  │Summary+Recommend│  │
│  └────────────┘  └──────────┘  └───────┘  └─────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │PostgreSQL│  │  Redis   │  │  Celery  │
    │ (Models) │  │ (Cache)  │  │ (Queue)  │
    └──────────┘  └──────────┘  └──────────┘
```

---

## 6. Daftar 24 AKD Master DPR RI (Periode 2024–2029)

| No | Nama AKD | Jenis | Lingkup Tugas Utama |
|----|----------|-------|---------------------|
| 1 | Pimpinan DPR | Pimpinan | Kinerja kelembagaan & kebijakan strategis dewan |
| 2 | Komisi I | Komisi | Pertahanan, Luar Negeri, Komunikasi & Informatika |
| 3 | Komisi II | Komisi | Pemerintahan Dalam Negeri, Otonomi Daerah, ASN, Pertanahan |
| 4 | Komisi III | Komisi | Hukum, HAM, Keamanan, KPK, Kepolisian, Kejaksaan |
| 5 | Komisi IV | Komisi | Pertanian, Kehutanan, Kelautan, Pangan |
| 6 | Komisi V | Komisi | Infrastruktur, Perhubungan, Pekerjaan Umum, Perumahan |
| 7 | Komisi VI | Komisi | Perdagangan, Perindustrian, Investasi, BUMN, UMKM |
| 8 | Komisi VII | Komisi | Perindustrian, UMKM, Ekonomi Kreatif, Pariwisata |
| 9 | Komisi VIII | Komisi | Agama, Sosial, Bencana, Kebencanaan, Kemenag |
| 10 | Komisi IX | Komisi | Kesehatan, Ketenagakerjaan, BPJS, Buruh Migran |
| 11 | Komisi X | Komisi | Pendidikan, Kebudayaan, Riset, Olahraga |
| 12 | Komisi XI | Komisi | Keuangan, Perbankan, APBN, OJK, Bank Indonesia |
| 13 | Komisi XII | Komisi | Energi, Sumber Daya Mineral, Lingkungan Hidup, Hilirisasi |
| 14 | Komisi XIII | Komisi | Reformasi Regulasi, HAM, Imigrasi, Pemasyarakatan |
| 15 | BURT | Badan | Urusan Rumah Tangga, Gaji, Tunjangan & Fasilitas Dewan |
| 16 | MKD | Badan | Mahkamah Kehormatan Dewan (Kode Etik & Sanksi) |
| 17 | Baleg | Badan | Badan Legislasi & Prolegnas |
| 18 | BAKN | Badan | Akuntabilitas Keuangan Negara & Audit BPK |
| 19 | BKSAP | Badan | Kerja Sama Antar-Parlemen & Diplomasi |
| 20 | BPKPH | Badan | Pengawasan Penyelenggaraan Pemilu & Pilkada |
| 21 | Bamus | Badan | Badan Musyawarah (Agenda Sidang & Paripurna) |
| 22 | Banggar | Badan | Badan Anggaran & Pembahasan RAPBN |
| 23 | BAM | Badan | Badan Aspirasi Masyarakat |
| 24 | Pansus | Panitia | Panitia Khusus Lintas Komisi (Ad-Hoc) |

---

## 7. Pencapaian Milestone Proyek (Progress Report)

Proposal ini menyertakan laporan capaian nyata yang telah diselesaikan sejauh ini:

1. **Infrastruktur Backend & Database**:
   - FastAPI server + PostgreSQL 15 (SQLAlchemy 2.x dengan kolom timezone `TIMESTAMPTZ`).
   - Redis 7+ cache & Celery background task queue.
2. **Data Collection Agents (Sprint 3)**:
   - `NewsCollectionAgent`: Berhasil mengumpulkan **615+ artikel berita** dari 13 media nasional ([`news_output.json`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/news_output.json)).
   - `TwitterCollectionAgent`: Berhasil menguji penarikan **560+ tweet** berbasis `twikit` ([`tweets_output.json`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/tweets_output.json)).
3. **Pengujian Kualitas (Quality Control)**:
   - Test suite mencapai **92/92 passed (100% lulus)** tanpa error.
   - Dokumen spesifikasi UI/UX prototype Figma siap pada [`docs/FIGMA_DESIGN_GUIDE.md`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/docs/FIGMA_DESIGN_GUIDE.md).

---

## 8. Rencana Jadwal Pelaksanaan (Timeline 6 Bulan)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ BULAN 1: Requirements, Kamus 24 AKD, & Architecture Setup [SELESAI ✅]     │
│ BULAN 2: Data Collection Agents (News RSS & Twitter Scraper) [SELESAI ✅]   │
│ BULAN 3: NLP Sentimen (IndoBERT) & Klasifikasi AKD Gemini   [AKTIF 🚀]     │
│ BULAN 4: Trend Window & Anomaly Detection Engine ($z > 2.0$) [UPCOMING ⏳]  │
│ BULAN 5: Recommendation Agent & Human Review Workflow        [UPCOMING ⏳]  │
│ BULAN 6: Dashboard Streamlit UI, PDF Generator, UAT & Launch [UPCOMING ⏳]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Target Performa & Indikator Keberhasilan (KPI)

| Parameter KPI | Target | Hasil / Status |
|---------------|--------|----------------|
| **Akurasi Sentimen** | ≥ 75% | Model IndoBERT + Lexicon hybrid |
| **Akurasi Klasifikasi AKD** | Top-1 ≥ 70% | Gemini 2.5 Flash zero-shot + keyword fallback |
| **Waktu Respon API** | < 2.0 Detik | FastAPI + Redis caching |
| **Kelancaran Penarikan Data** | ≥ 95% Success | Deduplikasi URL (`ON CONFLICT DO NOTHING`) |
| **Test Suite Pass Rate** | 100% | **92 / 92 Passed** ✅ |

---

## 10. Metode Pengujian & Quality Control

Sesuai dengan panduan [`docs/QUALITY_CONTROL.MD`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/docs/QUALITY_CONTROL.MD):
- **Automated Testing**: `pytest` untuk unit test seluruh modul.
- **Data Validation**: Sanitasi teks, validasi Pydantic schema, dan pengecekan nama 24 AKD.
- **Human-in-the-Loop**: Fitur review status rekomendasi (`draft` → `reviewed` → `published`).
