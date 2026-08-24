# 📋 Dokumentasi Lengkap Tugas Sistem Informasi (SI 1 & SI 2)
## Proyek DPR Agentic AI — Monitoring AKD & Analisis Sentimen DPR RI 2024–2029

> **Terakhir diperbarui**: 21 Agustus 2026
> **Sprint Aktif**: Sprint 4 — Genuine Agentic Architecture (Bulan 3)
> **Status Test Suite**: 77/77 Tests Passing ✅

---

## 👥 Identitas Peran

| Peran | Nama Jabatan | Tanggung Jawab Utama |
|---|---|---|
| **SI 1** | Database Architect & Executive Dashboard Specialist | Perancangan skema database, implementasi analisis sentimen, dashboard Streamlit, dan PDF briefing |
| **SI 2** | System Analyst, Technical Writer & QA Lead | Analisis kebutuhan sistem, penyusunan taksonomi AKD, dokumentasi teknis, tata kelola privasi, dan penjaminan mutu |

---

---

# 🟢 SI 1 — Database Architect & Executive Dashboard Specialist

---

## A. Perancangan & Pengelolaan Skema Database PostgreSQL 16

### A1. Perancangan 5 Tabel Utama Database ✅

**Status**: Selesai (Sprint 2)
**Lokasi File Implementasi**: `src/models/`

Merancang arsitektur database relasional PostgreSQL 16 dengan 5 tabel utama yang saling berelasi menggunakan SQLAlchemy 2.x ORM:

**Tabel 1: `content_items`** — Menyimpan seluruh artikel berita yang dikumpulkan dari 12+ portal media nasional.

```python
# File: src/models/content_item.py
class ContentItem(Base):
    __tablename__ = "content_items"
    __table_args__ = (
        UniqueConstraint("url", name="uq_content_items_url"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_name: Mapped[str | None] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(String(500))
    url: Mapped[str | None] = mapped_column(String(1000))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=...)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=...)

    # Relationships
    analyses: Mapped[list[AnalysisResult]] = relationship(back_populates="content_item")
    akd_mappings: Mapped[list[AKDMapping]] = relationship(back_populates="content_item")
```

**Tabel 2: `item_analysis`** — Menyimpan hasil analisis sentimen per artikel (Positif/Negatif/Netral + skor [-1.0, +1.0]).

```python
# File: src/models/analysis_result.py
class AnalysisResult(Base):
    __tablename__ = "item_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("content_items.id"), nullable=False)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=...)

    content_item: Mapped[ContentItem] = relationship(back_populates="analyses")
```

**Tabel 3: `akd_mapping`** — Pemetaan multi-label isu ke 24 AKD DPR RI (maks 3 AKD per artikel, dengan skor kepercayaan dan peringkat).

```python
# File: src/models/akd_mapping.py
class AKDMapping(Base):
    __tablename__ = "akd_mapping"
    __table_args__ = (
        UniqueConstraint("item_id", "akd_name", name="uq_akd_mapping_item_akd"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("content_items.id"), nullable=False)
    akd_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    akd_type: Mapped[str | None] = mapped_column(String(50))
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=...)

    content_item: Mapped[ContentItem] = relationship(back_populates="akd_mappings")
```

**Tabel 4: `trend_windows`** — Menyimpan kalkulasi Z-Score anomali volume berita harian per AKD.

```python
# File: src/models/trend_window.py
class TrendWindow(Base):
    __tablename__ = "trend_windows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    akd_name: Mapped[str] = mapped_column(String(50), nullable=False)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    z_score: Mapped[float | None] = mapped_column(Float)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=...)
```

**Tabel 5: `recommendations`** — Menyimpan rekomendasi kebijakan yang dihasilkan oleh RecommendationAgent.

```python
# File: src/models/recommendation.py
class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    akd_name: Mapped[str] = mapped_column(String(50), nullable=False)
    recommendation_text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=...)
```

---

### A2. Implementasi Deduplikasi Berita Otomatis ✅

**Status**: Selesai (Sprint 2)
**Lokasi File**: `src/repositories/content_repository.py`

Mengimplementasikan mekanisme deduplikasi berbasis constraint `UniqueConstraint("url")` menggunakan fitur PostgreSQL `INSERT ... ON CONFLICT DO NOTHING`:

```python
# File: src/repositories/content_repository.py
class ContentRepository:
    def save_articles(self, articles: list[dict], batch_size: int = 100) -> tuple[int, int]:
        """Save articles to content_items table, skipping duplicates.
        Uses PostgreSQL INSERT ... ON CONFLICT (url) DO NOTHING."""

    def _insert_batch(self, batch: list[dict]) -> tuple[int, int]:
        stmt = (
            insert(ContentItem)
            .values(values)
            .on_conflict_do_nothing(constraint="uq_content_items_url")
        )
        # Returns (inserted_count, skipped_count)

    def get_existing_urls(self, urls: list[str]) -> set[str]:
        """Check which URLs already exist in the database."""
```

**Keuntungan**: Tidak perlu melakukan query SELECT sebelum INSERT — duplikasi otomatis di-*skip* oleh database engine tanpa memunculkan error.

---

### A3. Pemeliharaan Indeks Database ✅

**Status**: Selesai (Sprint 2–4)

Indeks yang telah dibuat untuk mempercepat query:

| Tabel | Kolom | Tipe Indeks | Tujuan |
|---|---|---|---|
| `content_items` | `source_type` | B-tree Index | Filter berita per jenis sumber |
| `content_items` | `url` | Unique Constraint | Deduplikasi otomatis |
| `item_analysis` | `sentiment` | B-tree Index | Filter cepat per label sentimen |
| `akd_mapping` | `akd_name` | B-tree Index | Query distribusi per komisi |
| `akd_mapping` | `(item_id, akd_name)` | Unique Constraint | Mencegah duplikasi pemetaan |
| `trend_windows` | `is_anomaly` | B-tree Index | Query cepat daftar anomali |

---

### A4. Pengelolaan Redis 7+ Cache Layer ✅

**Status**: Selesai (Sprint 2)
**Lokasi File**: `src/cache.py`

Mengimplementasikan Redis sebagai *cache-aside* layer dengan pola:
- **Lazy Initialization**: Koneksi Redis hanya dibuat saat pertama kali diakses.
- **Connection Pooling**: Menggunakan `ConnectionPool` dengan maks 20 koneksi.
- **Graceful Degradation**: Jika Redis down, operasi cache mengembalikan `None`/`False` tanpa memunculkan crash.

```python
# File: src/cache.py
def get_cache(key: str) -> str | None:
    """Retrieve cached value. Returns None on connection failure."""

def set_cache(key: str, value: str, ttl_seconds: int = 3600) -> bool:
    """Set cached value with TTL (default 1 jam)."""

def delete_cache(key: str) -> bool:
    """Delete cached value."""
```

**Unit Tests**: 4 tests di `tests/test_cache.py` — semua passing ✅

---

### A5. Partisi Data Harian JSON ✅

**Status**: Selesai (Sprint 3)
**Lokasi Direktori**: `data/news/`, `data/analysis/`

Menyimpan data berita dan hasil analisis dalam format JSON terpartisi harian:

```text
data/
├── news/
│   ├── news_2026-08-01.json    # Berita tanggal 1 Agustus
│   ├── news_2026-08-02.json    # Berita tanggal 2 Agustus
│   ├── ...
│   └── news_2026-08-19.json    # Berita tanggal 19 Agustus
└── analysis/
    ├── analysis_2026-08-01.json  # Hasil analisis tanggal 1
    ├── ...
    └── analysis_2026-08-19.json  # Hasil analisis tanggal 19
```

**Total Data Terkoleksi**: 1,326+ artikel dari 1–19 Agustus 2026.

---

---

## B. Analisis Sentimen Publik (*Sentiment Analysis Engine*)

### B1. Pengembangan Kamus Leksikon Sentimen Indonesia ✅

**Status**: Selesai (Sprint 4)
**Lokasi File**: `src/agents/analysis.py` (baris 24–64)

Mengembangkan kamus kata kunci sentimen yang dikurasi khusus untuk konteks parlemen, legislasi, dan media Indonesia:

**Kata Positif (`POSITIVE_WORDS`)** — 60+ entri:

```python
POSITIVE_WORDS = {
    # Approval & Support
    "dukung", "mendukung", "dukungan", "apresiasi", "mengapresiasi", "setuju",
    "menyetujui", "puji", "memuji", "sepakat", "komitmen", "optimis", "harapan",
    # Success & Achievement
    "sukses", "berhasil", "keberhasilan", "prestasi", "unggul", "juara",
    "menang", "kemenangan", "gemilang", "rekor", "capaian", "lolos",
    # Improvement & Growth
    "solusi", "baik", "membaik", "terbaik", "maju", "kemajuan", "membangun",
    "pembangunan", "positif", "efektif", "transparan", "transparansi",
    "keadilan", "adil", "sejahtera", "kesejahteraan", "reformasi", "sinergi",
    "manfaat", "pulih", "pemulihan", "tumbuh", "pertumbuhan", "terobosan",
    "inovasi", "swasembada", "kolaborasi", "subsidi", "beasiswa", "bansos",
    ...
}
```

**Kata Negatif (`NEGATIVE_WORDS`)** — 80+ entri:

```python
NEGATIVE_WORDS = {
    # Crime & Law Violation
    "korupsi", "suap", "gratifikasi", "pungli", "skandal", "pencurian",
    "perampokan", "pembegalan", "penembakan", "pembunuhan", "penganiayaan",
    "kejahatan", "kriminal", "narkoba", "ilegal", "tersangka", "terdakwa",
    # Conflict & Protests
    "gagal", "kegagalan", "kecewa", "tolak", "menolak", "penolakan", "rugi",
    "buruk", "kritik", "masalah", "pelanggaran", "polemik", "ancaman",
    "sengketa", "gugatan", "demonstrasi", "bentrokan", "kerusuhan", "PHK",
    # Disasters & Casualties
    "bencana", "banjir", "longsor", "gempa", "tsunami", "kebakaran",
    "kecelakaan", "tabrakan", "korban", "tewas", "meninggal", "krisis",
    ...
}
```

---

### B2. Implementasi Algoritma Skor Sentimen Kontinu ✅

**Status**: Selesai (Sprint 4)
**Lokasi File**: `src/agents/analysis.py` — metode `analyze_sentiment()` (baris 90–136)

Algoritma menghasilkan dua output:
1. **Label Sentimen**: `"Positif"`, `"Negatif"`, atau `"Netral"`
2. **Skor Sentimen**: Float kontinu antara `-1.0` hingga `+1.0`

**Alur Kerja Algoritma**:

```text
Input: Teks artikel berita (string)
  ↓
1. Sanitasi HTML & normalisasi whitespace (sanitize_text)
  ↓
2. Tokenisasi kata (regex word boundary: \b\w+\b)
  ↓
3. Hitung jumlah kata positif (pos_count) vs negatif (neg_count)
   - Pencocokan langsung terhadap POSITIVE_WORDS & NEGATIVE_WORDS
   - Pencocokan morfologis (prefix/suffix matching)
  ↓
4. Kalkulasi skor:
   - pos > neg → Positif, skor = min(0.20 + (diff / total) * 0.60, 1.0)
   - neg > pos → Negatif, skor = max(-0.20 - (diff / total) * 0.60, -1.0)
   - pos == neg → Netral, skor = 0.0
  ↓
Output: (sentiment_label, sentiment_score)
```

**Formula Matematis**:

```
Jika pos_count > neg_count:
  score = min(0.20 + ((pos - neg) / (pos + neg)) × 0.60, 1.0)

Jika neg_count > pos_count:
  score = max(-0.20 - ((neg - pos) / (pos + neg)) × 0.60, -1.0)
```

**Ambang Batas Klasifikasi**:
- `score > 0.05` → **Positif**
- `score < -0.05` → **Negatif**
- `-0.05 ≤ score ≤ 0.05` → **Netral**

---

### B3. Pencocokan Morfologis Bahasa Indonesia ✅

**Status**: Selesai (Sprint 4)
**Lokasi File**: `src/agents/analysis.py` (baris 111–119)

Mengimplementasikan pengenalan variasi morfologis (*stemming* ringan) untuk meningkatkan cakupan leksikon tanpa memerlukan library stemmer eksternal:

```python
# Positif: mengenali derivasi akar kata positif
for root in {"sukses", "berhasil", "dukung", "apresiasi", "sejahtera"}:
    if w.startswith(root) or w.endswith(root):
        pos_count += 1

# Negatif: mengenali derivasi akar kata negatif
for root in {"korupsi", "bencana", "banjir", "maling", "curi", "begal",
             "rampok", "tembak", "bunuh", "rusak", "rugi"}:
    if w.startswith(root) or w.endswith(root):
        neg_count += 1
```

**Contoh Deteksi Morfologis**:

| Kata dalam Teks | Akar Kata Terdeteksi | Sentimen |
|---|---|---|
| "mendukung" | dukung | Positif |
| "keberhasilan" | berhasil | Positif |
| "pembegalan" | begal | Negatif |
| "perampokan" | rampok | Negatif |
| "merusak" | rusak | Negatif |

---

### B4. Unit Test Sentimen ✅

**Status**: Selesai (Sprint 4)
**Lokasi File**: `tests/test_agents/test_analysis_agent.py`

Test case yang diimplementasikan:

```python
class TestAnalysisAgent:
    def test_sentiment_positive_text(self):
        """Teks dengan kata positif dominan → label "Positif", score > 0"""

    def test_sentiment_negative_text(self):
        """Teks dengan kata negatif dominan → label "Negatif", score < 0"""

    def test_sentiment_neutral_text(self):
        """Teks tanpa kata kunci sentimen → label "Netral", score = 0.0"""
```

**Hasil**: 3/3 tests passing ✅

---

### B5. Evaluasi Akurasi Sentimen ⏳

**Status**: Upcoming (Sprint 5)

**Rencana Pelaksanaan**:
1. Memilih 100 artikel secara acak dari koleksi `data/news/`.
2. SI 2 melakukan pelabelan manual (ground truth): Positif / Negatif / Netral.
3. Menjalankan algoritma sentimen pada 100 artikel tersebut.
4. Menghitung metrik evaluasi: **Precision**, **Recall**, **F1-Score** per kelas.
5. Target: ≥ 75% akurasi keseluruhan.

---

### B6. Ekspansi Kamus Leksikon per Domain AKD ⏳

**Status**: Upcoming (Sprint 5)

**Rencana Pelaksanaan**:
Menambahkan kata kunci domain-spesifik per portofolio komisi:

| AKD | Contoh Kata Positif Domain | Contoh Kata Negatif Domain |
|---|---|---|
| Komisi III (Hukum) | "putusan adil", "keadilan", "supremasi hukum" | "vonis bebas", "mafia hukum", "impunitas" |
| Komisi IV (Pangan) | "panen raya", "swasembada", "ketahanan pangan" | "gagal panen", "hama", "kelangkaan" |
| Komisi XI (Keuangan) | "surplus", "stabilitas", "pertumbuhan ekonomi" | "defisit", "inflasi", "depresiasi", "utang" |

---

---

## C. Executive Dashboard Streamlit

### C1. Halaman Utama Dashboard ✅

**Status**: Selesai (Sprint 4)
**Lokasi File**: `dashboard/app.py`

Halaman utama menampilkan:
- **Metrik ringkasan**: Total berita terkoleksi, jumlah sumber aktif, dan tanggal terbaru.
- **Distribusi sentimen**: Persentase Positif / Negatif / Netral dalam chart donut Plotly.
- **Grafik volume harian**: Line chart volume berita per tanggal.

---

### C2. Halaman Breakdown per AKD ✅

**Status**: Selesai (Sprint 4)
**Lokasi File**: `dashboard/pages/`

Menampilkan grafik batang horizontal distribusi jumlah artikel per 24 AKD (Komisi I–XIII + 10 Badan + Pimpinan DPR RI). Setiap bar dikelompokkan berdasarkan sentimen (warna: hijau = Positif, merah = Negatif, abu = Netral).

---

### C3. Filter Interaktif Dashboard ✅

**Status**: Selesai (Sprint 4)

Filter yang tersedia di sidebar:
- **Pilihan Tanggal**: Date picker untuk memilih rentang analisis.
- **Pilihan AKD**: Multi-select dropdown 24 AKD.
- **Pilihan Sentimen**: Checkbox Positif / Negatif / Netral.

---

### C4. Tabel Detail Artikel ✅

**Status**: Selesai (Sprint 4)

Tabel interaktif (`st.dataframe()`) menampilkan kolom:
- Judul artikel
- Sumber media
- Tanggal publikasi
- Label sentimen + skor
- AKD terpeta (1–3 label)

---

### C5. Halaman Anomali & Tren ⏳

**Status**: Upcoming (Sprint 5)

**Rencana Pelaksanaan**:
- Menampilkan daftar AKD dengan Z-Score > 2.0 (anomali volume harian).
- Visualisasi *time-series* lonjakan per komisi dengan penanda area merah.
- Integrasi dengan hasil `False-Positive Self-Review` dari `TrendAgent`.

---

### C6. Personalized Executive Digest per AKD ⏳

**Status**: Upcoming (Sprint 6)

**Rencana Pelaksanaan**:
- Halaman dashboard per-komisi yang menampilkan ringkasan isu terkini hanya untuk portofolio komisi tersebut.
- Contoh: staf Komisi II hanya melihat isu Pemilu/ASN/IKN; staf Komisi XI hanya melihat inflasi/RAPBN.
- Pimpinan Fraksi melihat ringkasan agregat lintas-komisi.

---

---

## D. PDF Executive Briefing (ReportLab)

### D1. Template PDF 3 Halaman ⏳

**Status**: Upcoming (Sprint 6)

**Spesifikasi Template**:
- **Halaman 1**: Ringkasan Eksekutif — total berita, sentimen agregat, anomali terbesar hari itu.
- **Halaman 2**: Breakdown per AKD — tabel 24 komisi/badan dengan volume dan sentimen.
- **Halaman 3**: Rekomendasi Aksi — daftar aksi yang sudah divalidasi oleh Critique Loop.
- **Header/Footer**: Logo DPR RI, tanggal laporan, dan nomor halaman.

---

### D2. Implementasi ReportAgent ⏳

**Status**: Upcoming (Sprint 6)
**Lokasi File**: `src/agents/report.py`

---

### D3. Fitur Unduh PDF dari Dashboard ⏳

**Status**: Upcoming (Sprint 6)

Tombol "📄 Download Briefing PDF" di sidebar dashboard yang memanggil `ReportAgent` dan menyajikan file PDF untuk diunduh.

---

---

## E. Deteksi Anomali & Tren (Kolaborasi dengan Inf 2)

### E1. Kalkulasi Z-Score Anomaly Detection ⏳

**Status**: Upcoming (Sprint 5)
**Lokasi File**: `src/agents/trend.py`

**Formula Z-Score**:

```
Z = (X - μ) / σ

dimana:
  X = volume berita hari ini untuk AKD tertentu
  μ = rata-rata volume harian dalam window 7/14/30 hari
  σ = standar deviasi volume dalam window tersebut
```

Jika `Z > 2.0`, maka hari tersebut ditandai sebagai anomali.

---

### E2. Persistensi Anomali ke Database ⏳

**Status**: Upcoming (Sprint 5)

Menyimpan hasil deteksi ke tabel `trend_windows` dengan kolom `is_anomaly = True`.

---

### E3. Visualisasi Anomali di Dashboard ⏳

**Status**: Upcoming (Sprint 5)

Grafik time-series dengan penanda merah untuk hari-hari anomali.

---

---

---

# 🔵 SI 2 — System Analyst, Technical Writer & QA Lead

---

## F. Analisis Kebutuhan & Perancangan Sistem

### F1. Analisis Kebutuhan Fungsional & Non-Fungsional ✅

**Status**: Selesai (Sprint 1)
**Lokasi File**: `docs/FULL_PROPOSAL_GUIDE.md` — Section 13

Menyusun spesifikasi berstandar IEEE 830:

**Kebutuhan Fungsional (FR-01 s.d. FR-12)**:

| ID | Deskripsi | Agen Pelaksana | Autonomy Level |
|---|---|---|---|
| FR-01 | Ingesti otomatis berita dari 12 RSS portal nasional Tier-1 | `NewsCollectionAgent` | L2 (Semi-Autonomous) |
| FR-02 | Redaksi PII otomatis (Email/Phone Redaction) sesuai UU PDP | Text Sanitizer | L1 (Rule-Based) |
| FR-03 | Deduplikasi data in-memory berbasis URL Hash | Ingestion Deduplicator | L1 (Rule-Based) |
| FR-04 | Routing dinamis & orkestrasi siklus analisis multi-agen | `SupervisorAgent` (LangGraph) | L3 (Fully Agentic) |
| FR-05 | Klasifikasi isu 24 AKD Master DPR RI 2024–2029 | `AnalysisAgent` | L3 (Fully Agentic) |
| FR-06 | Penilaian skor sentimen kontinu (-1.0 s.d. +1.0) | Lexicon Sentiment Scorer | L1 (Rule-Based) |
| FR-07 | Kalkulasi Z-Score & penalaran akar masalah | `TrendAgent` | L3 (Fully Agentic) |
| FR-08 | Sintesis narasi isu strategis dengan memori kontekstual | `InsightAgent` | L3 (Fully Agentic) |
| FR-09 | Perumusan draf aksi kebijakan dengan Critique Loop | `RecommendationAgent` | L3 (Fully Agentic) |
| FR-10 | Visualisasi interaktif Dasbor Eksekutif Fraksi | Streamlit Dashboard | L1 (Deterministic UI) |
| FR-11 | Pembuatan Laporan Briefing PDF Rapat Pimpinan | `ReportAgent` (ReportLab) | L2 (Semi-Autonomous) |
| FR-12 | REST API Service pendukung integrasi | FastAPI Router | L1 (Deterministic API) |

**Kebutuhan Non-Fungsional (NFR)**:
1. **Availability**: Minimal 99.5% uptime.
2. **Performance**: Latensi Tier-1 = 0ms; query database < 100ms (Redis Cache).
3. **Security**: API Key dalam Environment Secrets; tidak ada PII disimpan.
4. **Fault Tolerance**: Kegagalan satu RSS feed tidak menyebabkan system crash.

---

### F2. Penyusunan Taksonomi 24 AKD DPR RI ✅

**Status**: Selesai (Sprint 1)
**Lokasi File**: `kamus/akd_master.json`

Menyusun taksonomi lengkap 24 AKD DPR RI Periode 2024–2029 beserta kata kunci domain sektoral:

```text
24 AKD DPR RI (2024-2029):
├── Pimpinan: Ketua DPR RI (Puan Maharani) & Wakil Ketua
├── 13 Komisi:
│   ├── Komisi I   : Pertahanan, Hubungan Luar Negeri, Kominfo, Siber, TNI
│   ├── Komisi II  : Pemerintahan Dalam Negeri, Otonomi Daerah, ASN, Pemilu, IKN
│   ├── Komisi III : Penegakan Hukum, Kepolisian, Kejaksaan, KPK, Peradilan
│   ├── Komisi IV  : Pertanian, Pangan, Kehutanan, Kelautan & Perikanan
│   ├── Komisi V   : Infrastruktur, Transportasi, Perumahan, BMKG, Basarnas
│   ├── Komisi VI  : Perdagangan, BUMN, Koperasi, UMKM, Investasi
│   ├── Komisi VII : Industri Manufaktur, Ekonomi Kreatif, Pariwisata
│   ├── Komisi VIII: Agama, Haji, Sosial, Kebencanaan, Perlindungan Perempuan & Anak
│   ├── Komisi IX  : Kesehatan, Ketenagakerjaan, BPJS, Kependudukan
│   ├── Komisi X   : Pendidikan, Kebudayaan, Riset, Olahraga, Timnas
│   ├── Komisi XI  : Keuangan, Perbankan, APBN, Pajak, BI, OJK
│   ├── Komisi XII : Energi Baru Terbarukan, Migas, Tambang, Lingkungan Hidup
│   └── Komisi XIII: Reformasi Regulasi, Hak Asasi Manusia, Imigrasi
└── 10 Badan & Panitia:
    Banggar, Baleg, MKD, BURT, BAKN, BKSAP, Bamus, BAM, BPKPH, Pansus
```

Setiap AKD dilengkapi dengan ratusan kata kunci domain sektoral untuk meningkatkan akurasi klasifikasi Tier-3 (Weighted Lexicon Fallback).

---

### F3. Daftar 12+ Portal Media Nasional Tier-1 ✅

**Status**: Selesai (Sprint 1)
**Lokasi File**: `kamus/feeds.json`

| No | Portal Media | Penerbit / Grup | Endpoint RSS |
|---|---|---|---|
| 1 | Antara News | LKBN Antara | `https://www.antaranews.com/rss/terkini` |
| 2 | Detik.com | Trans Media | `https://rss.detik.com/index.php/detikcom` |
| 3 | CNN Indonesia | Trans Media | `https://www.cnnindonesia.com/nasional/rss` |
| 4 | Tempo.co | Tempo Group | `https://rss.tempo.co/nasional` |
| 5 | Republika | Mahaka Media | `https://www.republika.co.id/rss` |
| 6 | Liputan6 | Emtek Group | `https://www.liputan6.com/rss` |
| 7 | CNBC Indonesia | Trans Media | `https://www.cnbcindonesia.com/news/rss` |
| 8 | Sindonews | MNC Group | `https://nasional.sindonews.com/rss` |
| 9 | Kompas.com | Kompas Gramedia | `https://rss.kompas.com/nasional` |
| 10 | Bisnis.com | Bisnis Indonesia | `https://www.bisnis.com/rss` |
| 11 | Kumparan | Kumparan Media | `https://kumparan.com/rss` |
| 12 | Suara.com | Suara Media | `https://www.suara.com/rss/nasional` |

---

### F4. Matriks Autonomy Level (L1–L3) ✅

**Status**: Selesai (Sprint 4)
**Lokasi File**: `docs/PROJECT_OVERVIEW.md`, `docs/FULL_PROPOSAL_GUIDE.md`

Mendefinisikan 3 tingkat otonomi:
- **L1 (Rule-Based)**: Deterministik, 0ms, tanpa LLM.
- **L2 (Semi-Autonomous)**: Heuristik + LLM fallback bersyarat.
- **L3 (Fully Agentic)**: Autonomous reasoning, tool calling, reflection, self-correction.

---

### F5. Matriks Strategi Komunikasi Fraksi ✅

**Status**: Selesai (Sprint 1)
**Lokasi File**: `docs/FULL_PROPOSAL_GUIDE.md` — Section 11

| Skenario | Indikator Sistem | Tindakan Fraksi |
|---|---|---|
| Lonjakan Negatif (Z > 2.0) | Sentimen Negatif > 40% | Klarifikasi pers, Position Paper, persiapan RDP |
| Tren Positif | Sentimen Positif > 30% | Amplifikasi publikasi kerja politik Fraksi |
| Isu Lintas Sektor | Multi-Label (misal: Komisi III + XIII) | Rapat Gabungan Pokja Komisi Fraksi |

---

---

## G. Dokumentasi Teknis & Proposal

### G1. Proposal Lengkap (14 Section) 🔄

**Status**: Ongoing (Sprint 1–12)
**Lokasi File**: `docs/FULL_PROPOSAL_GUIDE.md` (42KB+, 576 baris)
**Isi**: Latar belakang, rumusan masalah, arsitektur, skema database, manajemen risiko, QC/QA, timeline sprint, RACI matrix, deliverables, tata kelola data, estimasi biaya, spesifikasi IEEE 830, dan metodologi Agile Scrum.

---

### G2. Dokumen Arsitektur Sistem 🔄

**Status**: Ongoing (Sprint 1–12)
**Lokasi File**: `docs/ARCHITECTURE.md`
**Isi**: Diagram Mermaid arsitektur LangGraph Supervisor, Dynamic Tool Registry, paradigma Genuine Agentic AI, skema AgentState, model efisiensi biaya, dan 7 kapabilitas agentic lanjutan.

---

### G3. Spesifikasi Agen & Tool Registry 🔄

**Status**: Ongoing (Sprint 1–12)
**Lokasi File**: `docs/AGENTS.md`
**Isi**: Spesifikasi 7 agen (Supervisor, NewsCollector, Analysis, Trend, Insight, Recommendation, Report), tools per agen, mekanisme self-correction, dan state machine diagram.

---

### G4. Status Proyek & Roadmap Sprint 🔄

**Status**: Ongoing (Sprint 1–12)
**Lokasi File**: `docs/PROJECT_STATUS.md`
**Isi**: Arsitektur terkini, struktur direktori, fitur yang selesai, roadmap Sprint 4–6, dan hasil test suite.

---

### G5. Panduan Setup Teknis ✅

**Status**: Selesai (Sprint 1)
**Lokasi File**: `docs/SETUP.md`, `docs/TECHNICAL_SETUP_GUIDE.md`
**Isi**: Instruksi instalasi Python 3.11, `uv` package manager, Docker Compose, environment variables, dan perintah menjalankan server.

---

### G6. Dokumentasi Skema Database ✅

**Status**: Selesai (Sprint 2)
**Lokasi File**: `docs/DATABASE.md`
**Isi**: ER diagram 5 tabel, tipe kolom, constraint, indeks, dan relasi antar-tabel.

---

### G7. Dokumentasi REST API ✅

**Status**: Selesai (Sprint 3)
**Lokasi File**: `docs/API.md`
**Isi**: Daftar endpoint (`POST /api/v1/analyze`, `GET /api/v1/analysis/{id}`, `GET /api/v1/trends`, dst.), request/response schema, dan status codes.

---

### G8. Spesifikasi Desain UI/UX Dashboard ✅

**Status**: Selesai (Sprint 9 — dirancang lebih awal)
**Lokasi File**: `docs/FIGMA_DESIGN_GUIDE.md` (32KB+)
**Isi**: Wireframe, color scheme, layout halaman, tipografi, dan komponen UI.

---

---

## H. Tata Kelola Data & Kepatuhan Privasi (UU PDP)

### H1. Protokol Pembersihan PII ✅

**Status**: Selesai (Sprint 3)

Mengimplementasikan sanitasi teks otomatis:

```python
# File: src/utils/validators.py
def sanitize_text(text: str) -> str:
    """Remove potentially harmful characters and normalize whitespace."""
    text = re.sub(r"<[^>]+>", "", text)      # Strip HTML tags
    text = re.sub(r"\s+", " ", text).strip()  # Normalize whitespace
    return text
```

Prinsip: **Collect Minimum → Clean Immediately → Analyze → Aggregate → Delete Unnecessary Data**.

---

### H2. Audit Agregasi Publik ⏳

**Status**: Upcoming (Sprint 9)

Memastikan dashboard hanya menampilkan metrik agregat (distribusi sentimen %, volume per komisi), bukan identitas individu.

---

### H3. Dokumen Tata Kelola Data ✅

**Status**: Selesai (Sprint 3)
**Lokasi File**: `docs/FULL_PROPOSAL_GUIDE.md` — Section 10

Dasar hukum:
- **UU No. 27 Tahun 2022** tentang Pelindungan Data Pribadi (UU PDP)
- **UU No. 1 Tahun 2024** tentang Perubahan Kedua UU ITE

Prinsip utama: Purpose Limitation, Data Minimization, Aggregate-First, No Deanonymization, Human Review.

---

### H4. Audit Kepatuhan Privasi Berkala ⏳

**Status**: Upcoming (Sprint 11)

Menjalankan checklist audit privasi untuk memastikan tidak ada kebocoran data pribadi.

---

---

## I. Penjaminan Mutu / Quality Assurance (QA)

### I1. Test Suite Pytest ✅ 🔄

**Status**: Ongoing (Sprint 1–12)
**Lokasi Direktori**: `tests/`
**Hasil Terbaru**: **77/77 tests passing ✅ (0 warnings, 0 lint errors)**

Kategori pengujian:

| Kategori | File | Jumlah Tests | Status |
|---|---|---|---|
| Agent Tests | `tests/test_agents/test_analysis_agent.py` | 16 | ✅ |
| Agent Tests | `tests/test_agents/test_news_collection.py` | 20 | ✅ |
| Agent Tests | `tests/test_agents/test_trend_agent.py` | 3 | ✅ |
| Cache Tests | `tests/test_cache.py` | 4 | ✅ |
| Model Tests | `tests/test_models/test_content_item.py` | 4 | ✅ |
| Repository Tests | `tests/test_repositories/test_content_repository.py` | 7 | ✅ |
| Route Tests | `tests/test_routes/test_analysis_routes.py` | 5 | ✅ |
| Schema Tests | `tests/test_schemas/test_analysis_schema.py` | 7 | ✅ |
| Utility Tests | `tests/test_utils/test_validators.py` | 11 | ✅ |
| **Total** | | **77** | **✅** |

---

### I2. TDD Approach per Fitur 🔄

**Status**: Ongoing (Sprint 1–12)

Setiap fitur baru wajib memiliki unit test sebelum merge. Contoh coverage:
- Sentimen: 3 tests (positif, negatif, netral)
- AKD Matching: 6 tests (explicit, baleg, pimpinan, implicit, multiple, max-3)
- Tier Routing: 3 tests (tier1-bypass, tier2-fallback, tier3-keyword)

---

### I3. Linting & Code Quality Check 🔄

**Status**: Ongoing (Sprint 1–12)

Menjalankan `ruff` linter pada setiap perubahan kode. Hasil: **0 lint errors**.

---

### I4. User Acceptance Testing (UAT) ⏳

**Status**: Upcoming (Sprint 12)

Pelaksanaan UAT bersama Tim Ahli & Pimpinan Fraksi menggunakan formulir evaluasi terstruktur.

---

### I5. Dokumen Quality Control ✅

**Status**: Selesai (Sprint 11 — dirancang lebih awal)
**Lokasi File**: `docs/QUALITY_CONTROL.md`
**Isi**: Standar mutu, SLA, skenario pengujian, dan prosedur audit privasi.

---

---

## J. Kolaborasi pada Analisis Sentimen (SI 2 × SI 1)

### J1. Pelabelan Manual 100 Artikel ⏳

**Status**: Upcoming (Sprint 5)

**Rencana**:
1. Pilih 100 artikel secara random stratified dari `data/news/`.
2. Beri label manual: Positif / Negatif / Netral.
3. Simpan sebagai `data/validation/sentiment_labels.json`.

---

### J2. Evaluasi Precision / Recall / F1-Score ⏳

**Status**: Upcoming (Sprint 5)

**Metrik Target**:
- Overall Accuracy ≥ 75%
- F1-Score per kelas ≥ 0.70

---

### J3. Daftar Kata Domain-Spesifik per AKD ⏳

**Status**: Upcoming (Sprint 5)

Menyusun daftar kata kunci sentimen yang spesifik untuk setiap portofolio AKD guna memperkaya cakupan leksikon.

---

---

## 📊 Ringkasan Status Keseluruhan

| Area | Total Tugas | ✅ Selesai | 🔄 Ongoing | ⏳ Upcoming |
|---|---|---|---|---|
| **SI 1 — Database** | 5 | 5 | 0 | 0 |
| **SI 1 — Sentimen** | 6 | 4 | 0 | 2 |
| **SI 1 — Dashboard** | 6 | 4 | 0 | 2 |
| **SI 1 — PDF Briefing** | 3 | 0 | 0 | 3 |
| **SI 1 — Anomali/Tren** | 3 | 0 | 0 | 3 |
| **SI 2 — Analisis Kebutuhan** | 5 | 5 | 0 | 0 |
| **SI 2 — Dokumentasi** | 8 | 5 | 3 | 0 |
| **SI 2 — Privasi (UU PDP)** | 4 | 2 | 0 | 2 |
| **SI 2 — QA / Testing** | 5 | 2 | 2 | 1 |
| **SI 2 — Kolaborasi Sentimen** | 3 | 0 | 0 | 3 |
| **TOTAL** | **48** | **27 (56%)** | **5 (10%)** | **16 (34%)** |
