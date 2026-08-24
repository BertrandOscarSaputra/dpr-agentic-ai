# 📖 Panduan Teknis & Daftar Tugas Analisis Sentimen (Sistem Informasi)
## Proyek DPR Agentic AI — Monitoring AKD & Analisis Sentimen DPR RI 2024–2029

> **Penanggung Jawab**: Tim Sistem Informasi (**SI 1** & **SI 2**)  
> **Target Akurasi**: Overall Accuracy $\ge 75\%$, F1-Score $\ge 0.70$  
> **Pendekatan**: *Domain-Specific Weighted Lexicon + Indonesian Morphological Matching*  

---

## 🎯 1. Konsep & Metodologi Analisis Sentimen

Dalam konteks pengawasan media DPR RI, analisis sentimen bertujuan mengukur polaritas pemberitaan publik terhadap kinerja 24 Alat Kelengkapan Dewan (AKD). 

```text
                                  ┌─────────────────────────────┐
                                  │   Teks Berita Masuk (RSS)   │
                                  └──────────────┬──────────────┘
                                                 │
                                  ┌──────────────▼──────────────┐
                                  │   Sanitasi Teks & HTML      │
                                  │      (sanitize_text)        │
                                  └──────────────┬──────────────┘
                                                 │
                                  ┌──────────────▼──────────────┐
                                  │  Tokenisasi & Pencocokan    │
                                  │    Kamus Leksikon + Akar    │
                                  └──────────────┬──────────────┘
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
             pos_count > neg_count                             neg_count > pos_count
                        │                                                 │
     ┌──────────────────▼──────────────────┐           ┌──────────────────▼──────────────────┐
     │  Label: "Positif"                   │           │  Label: "Negatif"                   │
     │  Score: +0.20 s.d. +1.00            │           │  Score: -0.20 s.d. -1.00            │
     └──────────────────┬──────────────────┘           └──────────────────┬──────────────────┘
                        │                                                 │
                        └────────────────────────┬────────────────────────┘
                                                 │
                                  ┌──────────────▼──────────────┐
                                  │      pos == neg == 0        │
                                  │   Label: "Netral" (0.0)     │
                                  └──────────────┬──────────────┘
                                                 │
                                  ┌──────────────▼──────────────┐
                                  │ Simpan ke DB item_analysis  │
                                  │    & Visualisasi Dasbor     │
                                  └─────────────────────────────┘
```

### A. Skala Sentimen Kontinu `[-1.0, +1.0]`
Sistem membagi output menjadi dua nilai:
1. **Label Kategorial**: `"Positif"`, `"Negatif"`, atau `"Netral"`
2. **Skor Kontinu**: Float bernilai antara `-1.0` (Sangat Negatif) hingga `+1.0` (Sangat Positif)

### B. Formula Matematis Skor Sentimen
Diterapkan pada file [`src/agents/analysis.py`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/src/agents/analysis.py):

$$\text{Jika } pos > neg: \quad \text{Score} = \min\left(0.20 + \left(\frac{pos - neg}{pos + neg}\right) \times 0.60, \; 1.0\right)$$

$$\text{Jika } neg > pos: \quad \text{Score} = \max\left(-0.20 - \left(\frac{neg - pos}{pos + neg}\right) \times 0.60, \; -1.0\right)$$

$$\text{Jika } pos = neg: \quad \text{Score} = 0.0 \quad (\text{Label: "Netral"})$$

---

## 👥 2. Pembagian Tugas Tim Sistem Informasi

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 PEMBAGIAN TUGAS ANALISIS SENTIMEN (SI)                      │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ 🟢 SI 1 (Engineering & Dashboard)    │ 🔵 SI 2 (Analyst, QA & Evaluasi)     │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 1. Pemeliharaan Kamus Leksikon       │ 1. Pelabelan Manual Ground Truth     │
│ 2. Logika Scoring & Stemming         │ 2. Evaluasi Precision, Recall, F1    │
│ 3. Database Schema & Persistence     │ 3. Pembuatan Unit Test Pytest        │
│ 4. Visualisasi Dasbor Streamlit      │ 4. SOP & Panduan Pelabelan           │
│ 5. Integrasi Anomali Sentimen Negatif│ 5. Audit Kualitas Data Sentimen      │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 🟢 3. Rincian Task & Panduan untuk SI 1 (Technical & Dashboard)

### Task SI1-01: Pemeliharaan & Ekspansi Kamus Leksikon
* **File Target**: [`src/agents/analysis.py`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/src/agents/analysis.py) (`POSITIVE_WORDS` & `NEGATIVE_WORDS`)
* **Instruksi**:
  1. Pastikan setiap kata yang dimasukkan adalah bentuk dasar atau kata kunci penting yang tidak ambigu.
  2. Tambahkan kata kunci spesifik per sektor AKD:
     * **Sektor Hukum (Komisi III/XIII)**: Positif = `"vonis adil"`, `"rehabilitasi"`, `"pemulihan hak"`. Negatif = `"korupsi"`, `"pungli"`, `"suap"`, `"pelanggaran ham"`, `"terorisme"`.
     * **Sektor Ekonomi & Keuangan (Komisi XI/Banggar)**: Positif = `"surplus"`, `"pertumbuhan"`, `"investasi masuk"`. Negatif = `"inflasi"`, `"defisit"`, `"utang membengkak"`, `"kemiskinan"`.
     * **Sektor Pertanian & Pangan (Komisi IV)**: Positif = `"panen raya"`, `"swasembada"`. Negatif = `"gagal panen"`, `"kelangkaan"`, `"hama"`, `"impor ilegal"`.

### Task SI1-02: Penyempurnaan Pencocokan Akar Kata (Morphological Stemming)
* **File Target**: [`src/agents/analysis.py`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/src/agents/analysis.py) (fungsi `analyze_sentiment`)
* **Instruksi**:
  1. Manfaatkan pemeriksaan prefix & suffix untuk mengenali afiksasi bahasa Indonesia tanpa memperberat latensi runtime:
     ```python
     # Contoh penanganan kata turunan positif
     if any(w.startswith(root) or w.endswith(root) for root in {"sukses", "berhasil", "dukung", "apresiasi", "sejahtera"} if len(w) >= 5):
         pos_count += 1

     # Contoh penanganan kata turunan negatif
     if any(w.startswith(root) or w.endswith(root) for root in {"korupsi", "bencana", "banjir", "maling", "curi", "begal", "rampok", "tembak", "bunuh", "rusak", "rugi"} if len(w) >= 4):
         neg_count += 1
     ```

### Task SI1-03: Persistensi Hasil Analisis Sentimen ke Database
* **File Target**: [`src/models/analysis_result.py`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/src/models/analysis_result.py) & [`src/repositories/content_repository.py`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/src/repositories/content_repository.py)
* **Instruksi**:
  1. Pastikan setiap artikel yang dianalisis menyimpan entri ke tabel `item_analysis`:
     * `item_id`: ID relasi ke `content_items.id`
     * `sentiment`: `"Positif" | "Negatif" | "Netral"` (Indexed)
     * `sentiment_score`: Float `-1.0` s.d. `1.0`
     * `analyzed_at`: Timestamp UTC

### Task SI1-04: Visualisasi Sentimen di Dasbor Eksekutif Streamlit
* **File Target**: [`dashboard/app.py`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/dashboard/app.py) & [`dashboard/pages/`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/dashboard/pages/)
* **Instruksi**:
  1. **Donut Chart Sentimen Agregat**: Menampilkan proporsi persentase Positif (Hijau), Negatif (Merah), dan Netral (Abu-abu/Biru).
  2. **Sentiment Breakdown per AKD**: Bar chart horizontal yang memperlihatkan distribusi sentimen untuk masing-masing dari 24 komisi/badan.
  3. **Sidebar Filter**: Menyediakan filter interaktif multi-select sentimen agar pimpinan dapat mengisolasi berita bernada negatif saja untuk ditindaklanjuti.

---

## 🔵 4. Rincian Task & Panduan untuk SI 2 (Analyst, QA & Evaluasi)

### Task SI2-01: Penyusunan Dataset Validasi Ground Truth (100–200 Artikel)
* **File Target**: `data/validation/sentiment_ground_truth.json`
* **Instruksi**:
  1. Ambil sampel 100–200 artikel acak dari folder `data/news/` yang mewakili berbagai komisi.
  2. Berikan label manual independen dengan format JSON:
     ```json
     [
       {
         "id": 1,
         "title": "DPR Apresiasi Kinerja Pemerintah dalam Penurunan Stunting",
         "ground_truth": "Positif",
         "akd_context": "Komisi IX"
       },
       {
         "id": 2,
         "title": "KPK Tangkap Tersangka Kasus Korupsi Pengadaan Barang",
         "ground_truth": "Negatif",
         "akd_context": "Komisi III"
       },
       {
         "id": 3,
         "title": "Komisi I Gelar Rapat Dengar Pendapat dengan Menkominfo",
         "ground_truth": "Netral",
         "akd_context": "Komisi I"
       }
     ]
     ```

### Task SI2-02: Perhitungan Metrik Evaluasi (Evaluation Script)
* **File Target**: `scripts/evaluate_sentiment.py`
* **Instruksi**:
  1. Bandingkan hasil prediksi `AnalysisAgent.analyze_sentiment()` terhadap `ground_truth`.
  2. Hitung metrik evaluasi standar:
     * **Confusion Matrix** (Matriks Kontingensi 3x3)
     * **Accuracy** $= \frac{TP + TN}{\text{Total Sampel}}$ (Target: $\ge 75\%$)
     * **Precision** per kelas $= \frac{TP}{TP + FP}$
     * **Recall** per kelas $= \frac{TP}{TP + FN}$
     * **F1-Score** per kelas $= 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$ (Target: $\ge 0.70$)

### Task SI2-03: Pembuatan Test Case Otomatis (Pytest)
* **File Target**: [`tests/test_agents/test_analysis_agent.py`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/tests/test_agents/test_analysis_agent.py) & [`tests/test_utils/test_validators.py`](file:///c:/Users/Lenovo/Documents/DPR/dpr-agentic-ai/tests/test_utils/test_validators.py)
* **Instruksi**:
  1. Pastikan seluruh skenario sentimen ter-cover oleh unit test:
     ```python
     def test_sentiment_positive_text():
         agent = AnalysisAgent()
         label, score = agent.analyze_sentiment("DPR RI mengapresiasi keberhasilan swasembada pangan")
         assert label == "Positif"
         assert score > 0.0

     def test_sentiment_negative_text():
         agent = AnalysisAgent()
         label, score = agent.analyze_sentiment("KPK melakukan penangkapan tersangka korupsi dan suap")
         assert label == "Negatif"
         assert score < 0.0

     def test_sentiment_neutral_text():
         agent = AnalysisAgent()
         label, score = agent.analyze_sentiment("Komisi II mengadakan rapat kerja pada hari Selasa")
         assert label == "Netral"
         assert score == 0.0
     ```

### Task SI2-04: Standar Operasional Prosedur (SOP) Pelabelan Sentimen
* **Instruksi untuk Tim Penilai**:
  * **Positif**: Artikel memuat pencapaian, apresiasi, keberhasilan program, pengesahan RUU yang didukung publik, solusi krisis, atau kepuasan publik.
  * **Negatif**: Artikel memuat skandal, korupsi, bencana alam, kritik keras terhadap dewan, penolakan kebijakan/demonstrasi, kerugian negara, atau penegakan hukum pidana.
  * **Netral**: Artikel berisi laporan prosedural rapat, jadwal sidang paripurna, pernyataan normatif tanpa muatan emosional/konflik, atau berita informatif faktual biasa.

---

## 🛠️ 5. SOP Menjalankan Pengujian Sentimen (Quick Run)

Jalankan perintah berikut pada terminal untuk memverifikasi performa modul analisis sentimen:

```bash
# 1. Menjalankan seluruh test suite analisis sentimen
uv run pytest tests/test_agents/test_analysis_agent.py -v

# 2. Menjalankan test validator sentimen
uv run pytest tests/test_utils/test_validators.py -v

# 3. Menjalankan evaluasi akurasi ground-truth (setelah script evaluasi disiapkan)
uv run python -c "
from src.agents.analysis import AnalysisAgent
agent = AnalysisAgent()
samples = [
    'DPR dukung suksesnya pembangunan infrastruktur',
    'Terjadi bencana banjir dan kerugian besar',
    'Rapat paripurna dibuka pukul 09.00 WIB'
]
for s in samples:
    label, score = agent.analyze_sentiment(s)
    print(f'[{label} | {score:+.2f}] -> {s}')
"
```

---

## 📅 6. Checklist Pelaksanaan Sprint 4–5

| Task ID | Deskripsi Tugas | PJ | Target Sprint | Status |
|---|---|:---:|:---:|:---:|
| **SI1-01** | Kurasi 140+ kata leksikon dasar (`POSITIVE_WORDS`, `NEGATIVE_WORDS`) | SI 1 | Sprint 4 | ✅ Selesai |
| **SI1-02** | Implementasi rumus skor kontinu `[-1.0, 1.0]` & stemming akar kata | SI 1 | Sprint 4 | ✅ Selesai |
| **SI1-03** | Skema ORM `item_analysis` & integrasi repository database | SI 1 | Sprint 4 | ✅ Selesai |
| **SI1-04** | Donut chart & breakdown sentimen per AKD di Dashboard Streamlit | SI 1 | Sprint 4 | ✅ Selesai |
| **SI2-03** | Pembuatan 3 unit test otomatis skenario sentimen di Pytest | SI 2 | Sprint 4 | ✅ Selesai |
| **SI1-05** | Ekspansi kamus leksikon sentimen untuk sektor spesifik 24 AKD | SI 1 | Sprint 5 | ⏳ Upcoming |
| **SI2-01** | Pembuatan 100 sampel dataset validasi ground truth | SI 2 | Sprint 5 | ⏳ Upcoming |
| **SI2-02** | Eksekusi evaluasi Confusion Matrix, Precision, Recall & F1-Score | SI 2 | Sprint 5 | ⏳ Upcoming |
| **SI2-04** | Dokumentasi laporan hasil evaluasi akurasi sentimen | SI 2 | Sprint 5 | ⏳ Upcoming |
