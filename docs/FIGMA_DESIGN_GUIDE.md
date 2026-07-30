# 🎨 PANDUAN UI/UX DESIGN DASHBOARD — Figma Prototype Specifications

**Platform Target**: Streamlit (Web Dashboard)  
**Purpose**: Real-time monitoring pemberitaan & opini publik untuk DPR RI  
**Target Users**: Staf DPR RI Sub. Analisis Media + Unit Kerja (AKD)  
**Phase**: Sprint 3 (Minggu 9–12)  

---

## 📑 DAFTAR ISI

1. [Dashboard Overview & App Structure](#1-dashboard-overview--app-structure)
2. [Page 1: Home (Overview & Dashboard)](#2-page-1-home-overview--dashboard)
3. [Page 2: AKD Monitor (Per-AKD Detail View)](#3-page-2-akd-monitor-per-akd-detail-view)
4. [Page 3: Trends & Alerts (Anomaly Detection)](#4-page-3-trends--alerts-anomaly-detection)
5. [Page 4: Recommendations (Human Workflow)](#5-page-4-recommendations-human-workflow)
6. [Komponen Global (Sidebar, Header)](#6-komponen-global-sidebar-header)
7. [Design Tokens (Warna, Tipografi, Spacing, Ikon)](#7-design-tokens-warna-tipografi-spacing-ikon)
8. [Responsive Design](#8-responsive-design)
9. [Data Entity Reference](#9-data-entity-reference)
10. [Referensi: 18 AKD DPR RI](#10-referensi-18-akd-dpr-ri)
11. [Deliverables Sprint 3](#11-deliverables-sprint-3)

---

## 1. Dashboard Overview & App Structure

### Sitemap
```
Dashboard Agentic AI Monitoring DPR RI
├── 🏠 Home (Overview)
├── 🎯 AKD Monitor (Per-AKD detail)
├── 📈 Trends & Alerts (Anomaly detection)
├── 📝 Recommendations (Human workflow)
└── ⚙️ Settings (Optional)
```

### Navigation
- **Sidebar** (kiri): Navigasi antar halaman + quick filters
- **Quick Filters** (sidebar): Date range picker, AKD selector dropdown, sentiment filter
- **Header Bar** (atas): Logo, judul sistem, timestamp terakhir update

---

## 2. Page 1: HOME (Overview & Dashboard)

### Tujuan
Dashboard utama dengan KPI overview & real-time monitoring untuk manajer/supervisor.

### Wireframe Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🏛️ AGENTIC AI MONITORING DASHBOARD — DPR RI              │
│  Updated: Today 14:32 | Data Source: Twitter + Berita       │
└─────────────────────────────────────────────────────────────┘

┌─────────┬──────────┬──────────┬──────────┐
│📊 2,847 │💬Neg 45% │📈3 Anom  │🚨2 Alert │
│ +423 vs │ +8% vs   │  2 high  │ Needs    │
│yesterday│ week avg │  1 med   │ attention│
└─────────┴──────────┴──────────┴──────────┘

┌──── SENTIMEN DISTRIBUTION ────┬──── TOP 5 AKD TRENDING ────────┐
│                               │                                │
│     [Pie Chart]               │  1. 🔴 BURT         ↑↑ 245 tw │
│   Positif  32%  🟢            │  2. 🟡 Komisi III   ↑  187 tw │
│   Netral   23%  ⚪            │  3. 🟢 MKD          →  142 tw │
│   Negatif  45%  🔴            │  4. 🔵 Baleg        ↓   98 tw │
│                               │  5. 🟣 Komisi VI    ↓   87 tw │
│                               │                                │
│                               │  [Lihat Semua 18 AKD »]       │
└───────────────────────────────┴────────────────────────────────┘

┌──── RECENT ANOMALIES & ALERTS ─────────────────────────────────┐
│                                                                │
│  🚨 [HIGH] BURT — Z-Score Spike (2.8)                        │
│     135 tweets in 4-hour window (avg: 42)                     │
│     Keywords: "tunjangan DPR", "gaji anggota"                 │
│     → View Details »                                          │
│                                                                │
│  ⚠️ [MEDIUM] Komisi III — Sentiment Shift                    │
│     Negative sentiment increased 35% in last 24h              │
│     → View Details »                                          │
│                                                                │
│  ℹ️ [LOW] Baleg — Trend Reversal                              │
│     After 3-day decline, tweet volume increasing              │
│     → View Details »                                          │
│                                                                │
└────────────────────────────────────────────────────────────────┘

┌──── SENTIMENT TREND OVER TIME (LINE CHART) ────────────────────┐
│                                                                │
│  [7-day line chart — 3 garis warna]                           │
│  Y-axis: Jumlah tweet                                         │
│  X-axis: Tanggal (7 hari terakhir)                            │
│  Garis: 🟢 Positif, ⚪ Netral, 🔴 Negatif                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Komponen Detail

#### 2.1 Quick Stats Cards (4 Kolom)

| Card | Label | Contoh Nilai | Delta | Delta Color |
|------|-------|-------------|-------|-------------|
| 1 | 📊 Total Tweets (Today) | `2,847` | `+423 vs yesterday` | Hijau (naik = baik) |
| 2 | 💬 Sentiment Breakdown | `Negatif 45%` | `+8% vs week avg` | Merah (naik negatif = buruk) |
| 3 | 📈 Trending | `3 Anomalies` | `2 high, 1 medium` | Abu-abu (info) |
| 4 | 🚨 Alerts | `2 Critical` | `Needs attention` | Abu-abu (info) |

**Desain**: Card dengan border ringan, padding 16px, angka utama **36px Bold**, label 12px Caption, delta 12px dengan warna hijau/merah/abu sesuai konteks.

---

#### 2.2 Sentiment Pie Chart

- **Tipe**: Donut / Pie Chart
- **3 segmen**:
  - 🟢 Positif (`#2ecc71`) — 32%
  - ⚪ Netral (`#95a5a6`) — 23%
  - 🔴 Negatif (`#e74c3c`) — 45%
- **Judul**: "Distribusi Sentimen Tweets (Semua AKD)"
- **Hover**: Tooltip menampilkan label + persentase
- **Tinggi**: 400px

---

#### 2.3 Top 5 AKD Trending

**Tipe**: Tabel ranking dengan ikon tren warna-warni

| Kolom | Deskripsi |
|-------|-----------|
| Rank | 1–5 (angka) |
| Status | Emoji warna: 🔴 (spike), 🟡 (naik), 🟢 (stabil), 🔵 (turun) |
| AKD | Nama AKD |
| Tweets | Jumlah tweet minggu ini |
| Trend | Panah: ↑↑, ↑, →, ↓ |
| Change | Persentase perubahan: `+24%`, `-8%` |

**CTA Button** di bawah: `📋 Lihat Semua 18 AKD` → navigasi ke halaman AKD Monitor

---

#### 2.4 Recent Anomalies & Alerts

**Tipe**: List card dengan severity badge

Setiap alert card berisi:
```
┌──────────────────────────────────────────┐
│  [SEVERITY_BADGE] [AKD_NAME] — [TITLE]  │
│  Deskripsi singkat anomali...            │
│  Z-Score: 2.8 | Items: 135              │
│  → View Details »                       │
└──────────────────────────────────────────┘
```

**Severity Levels**:
| Level | Badge | Warna Background | Ikon |
|-------|-------|-------------------|------|
| HIGH | `🔴 [HIGH]` | `#fef2f2` (merah muda) | 🚨 |
| MEDIUM | `🟡 [MEDIUM]` | `#fffbeb` (kuning muda) | ⚠️ |
| LOW | `ℹ️ [LOW]` | `#eff6ff` (biru muda) | ℹ️ |

Maksimal **3 alert** ditampilkan, masing-masing memiliki tombol **"▶ Detail"**.

---

#### 2.5 Sentiment Trend Line Chart

- **Tipe**: Line chart dengan area fill
- **Periode**: 7 hari terakhir
- **Sumbu X**: Tanggal
- **Sumbu Y**: Jumlah tweet
- **3 garis**:
  - 🟢 Positif (`#2ecc71`, fill transparan)
  - ⚪ Netral (`#95a5a6`, tanpa fill)
  - 🔴 Negatif (`#e74c3c`, fill transparan)
- **Hover mode**: Unified (semua nilai tampil saat hover 1 titik)
- **Tinggi**: 400px

---

## 3. Page 2: AKD MONITOR (Per-AKD Detail View)

### Tujuan
Monitoring detail untuk **1 AKD tertentu** — digunakan oleh unit kerja AKD untuk memantau isu mereka.

### Wireframe Layout

```
┌─────────────────────────────────────────────────────┐
│  🎯 AKD MONITOR: [Dropdown: Pilih AKD ▼]          │
│  Tanggal: [Date Range Picker]                      │
└─────────────────────────────────────────────────────┘

┌──── AKD INFO ───────────────────────────────────────┐
│  📌 Lingkup Tugas: Pertahanan, Luar Negeri, ...    │
│  🔑 Keywords: pertahanan, TNI, Kemenhan, ...       │
└─────────────────────────────────────────────────────┘

┌─────────┬──────────┬──────────┬──────────┐
│📊 245   │📈 +24%   │💬Neg 58% │🔥 YA    │
│Tweets   │vs avg    │          │Z: 2.8   │
│hari ini │          │          │Trending │
└─────────┴──────────┴──────────┴──────────┘

┌──── SENTIMENT TREND (LINE CHART — 14 hari) ─────────┐
│  Y: Jumlah tweet | X: Tanggal                       │
│  3 garis: Positif, Netral, Negatif                   │
└──────────────────────────────────────────────────────┘

┌──── SENTIMENT DISTRIBUTION (HORIZONTAL BAR) ────────┐
│  Positif  ███░░░░░░        32 tweets   13%          │
│  Netral   ██░░░░░░░░░      25 tweets   10%          │
│  Negatif  █████████░      142 tweets   58%          │
└──────────────────────────────────────────────────────┘

┌──── TOP KEYWORDS (TAG CLOUD) ────────────────────────┐
│                                                      │
│    tunjangan (45)   gaji (38)   fasilitas (32)      │
│       DPR (28)   anggota (25)   naik (22)           │
│          ketimpangan (18)   kritik (15)              │
│                                                      │
└──────────────────────────────────────────────────────┘

┌──── SAMPLE TWEETS (TABLE) ───────────────────────────┐
│  Showing 1-10 of 245 | Search: [____________]       │
│                                                      │
│  Tanggal      | Author    | Tweet          | Sent.  │
│  ─────────────┼───────────┼────────────────┼────────│
│  29 Jul 14:21 | @user1    | "Tunjangan..." | 🔴-0.92│
│  29 Jul 13:05 | @user2    | "Pemerintah.." | 🔴-0.85│
│  28 Jul 08:30 | @user3    | "Terima kas.." | 🟢+0.78│
│                                                      │
│  [Load More »]                                       │
└──────────────────────────────────────────────────────┘
```

### Komponen Detail

#### 3.1 AKD Selector
- **Tipe**: Dropdown (sidebar atau inline)
- **Opsi**: 18 AKD dari kamus (lihat [Referensi AKD](#10-referensi-18-akd-dpr-ri))
- **Format tampilan**: `"Komisi I — Pertahanan, Luar Negeri, Komunikasi dan Informatika"`

#### 3.2 AKD Info Box
- **2 kolom**: Lingkup Tugas (kiri, lebar) + Keywords (kanan, compact)
- **Background**: Info blue (`#eff6ff`)
- **Data**: Diambil dari `kamus/akd_master.json`

#### 3.3 Daily Statistics (4 Metric Cards)
| Card | Label | Contoh |
|------|-------|--------|
| 1 | 📊 Tweets Hari Ini | `245` |
| 2 | 📈 Change vs Avg | `+24%` |
| 3 | 💬 % Negatif | `58%` |
| 4 | 🔥 Trending? | `YA (Z-Score: 2.8)` / `TIDAK` |

#### 3.4 Sentiment Trend Chart
- **Tipe**: Line chart, 14 hari
- **3 garis warna** seperti Home

#### 3.5 Sentiment Distribution Bar
- **Tipe**: Horizontal bar chart
- **3 bar**: Positif (hijau), Netral (abu), Negatif (merah)
- **Label**: Nama + jumlah tweet + persentase

#### 3.6 Top Keywords (Tag Cloud)
- **Tipe**: Tag cloud / word cloud
- **Font size**: Proporsional terhadap frekuensi
- **Warna**: Variasi dari primary palette
- **Data**: Kata kunci paling sering muncul dalam tweet AKD terpilih

#### 3.7 Sample Tweets Table

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| Tanggal | datetime | Format: `29 Jul 14:21` |
| Author | string | `@username` atau nama sumber |
| Tweet | text | Teks dipotong 80 karakter + `...` |
| Sentimen | badge + skor | `🔴 Negatif (0.92)` / `🟢 Positif (0.78)` |

- **Fitur**: Search box, pagination (10 per halaman), "Load More"

---

## 4. Page 3: TRENDS & ALERTS (Anomaly Detection)

### Tujuan
Monitor anomali & trend spikes per AKD — untuk quick decision-making.

### Wireframe Layout

```
┌─────────────────────────────────────────────────┐
│  📈 TRENDS & ANOMALIES MONITOR                 │
│  Filter: [Date Range] [Severity: All ▼]        │
└─────────────────────────────────────────────────┘

┌──── ACTIVE ANOMALIES ───────────────────────────┐
│                                                 │
│  🔴 [HIGH] BURT — Z-Score Spike                │
│     Detected: 2 jam lalu                       │
│     Z-Score: 2.8 (threshold: 2.0)              │
│     245 tweets/4h (avg: 42)                    │
│     Peak Sentiment: Negatif 65%                │
│     Keywords: tunjangan, gaji, fasilitas       │
│     [📋 Lihat Tweets] [✕ Dismiss]              │
│                                                 │
│  🟡 [MEDIUM] Komisi III — Sentiment Shift      │
│     Detected: 8 jam lalu                       │
│     +35% negative vs 24h avg                   │
│     78% Negative (was 43%)                     │
│     Keyword: "polisi korup"                    │
│     [📋 Lihat Tweets] [✕ Dismiss]              │
│                                                 │
│  ℹ️ [LOW] Baleg — Volume Increase              │
│     Detected: 12 jam lalu                      │
│     +22% vs 7d avg                             │
│     98 tweets/day (avg: 80)                    │
│     Sentiment: Netral (mostly news)            │
│     [📋 Lihat Tweets] [✕ Dismiss]              │
│                                                 │
└─────────────────────────────────────────────────┘

┌──── ANOMALY TIMELINE (7 DAYS) ──────────────────┐
│                                                 │
│  [Line chart + scatter markers]                 │
│  Y: Z-Score | X: Tanggal                       │
│  Garis abu: Z-Score normal                     │
│  Bintang merah ★: Titik anomali               │
│  Garis putus oranye: Threshold (2.0)           │
│                                                 │
└─────────────────────────────────────────────────┘

┌──── HISTORICAL COMPARISON ──────────────────────┐
│                                                 │
│  Minggu Ini vs Minggu Lalu                     │
│                                                 │
│  AKD          | This Week | Last Week | Change │
│  ─────────────┼───────────┼───────────┼────────│
│  BURT         |   1,245   |   847     | +47%  │
│  Komisi III   |    987    |   1,102   | -10%  │
│  MKD          |    542    |   534     |  +2%  │
│  Baleg        |    392    |   478     | -18%  │
│  Komisi VI    |    367    |   412     | -11%  │
│  ... (18 AKD) |           |           |       │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Komponen Detail

#### 4.1 Active Anomalies Cards
Setiap card menampilkan:

| Element | Deskripsi |
|---------|-----------|
| **Severity Badge** | `🔴 [HIGH]` / `🟡 [MEDIUM]` / `ℹ️ [LOW]` |
| **AKD Name** | Nama AKD yang mengalami anomali |
| **Title** | Jenis anomali: "Z-Score Spike" / "Sentiment Shift" / "Volume Increase" |
| **Detected** | Waktu relatif: "2 jam lalu" |
| **3 Metric Mini-Cards** | Z-Score, Tweet Count, Window time |
| **Sentiment Breakdown** | Distribusi sentimen dalam window anomali |
| **Top Keywords** | 3 kata kunci teratas |
| **Action Buttons** | `📋 Lihat Tweets` + `✕ Dismiss` |

**Severity Threshold**:
- **HIGH**: z_score > 3.0
- **MEDIUM**: z_score > 2.0
- **LOW**: z_score > 1.5

---

#### 4.2 Anomaly Timeline Chart

- **Tipe**: Line chart + scatter overlay
- **Y-axis**: Z-Score
- **X-axis**: Tanggal (7 hari)
- **Elemen**:
  - Garis abu-abu: Z-Score over time
  - Titik ★ merah: Anomali terdeteksi (`is_anomaly=true`)
  - Garis putus-putus oranye: Threshold line di `z_score = 2.0`
- **Tinggi**: 400px

---

#### 4.3 Historical Comparison Table

| Kolom | Deskripsi |
|-------|-----------|
| AKD | Nama AKD |
| This Week | Jumlah tweet minggu ini |
| Last Week | Jumlah tweet minggu lalu |
| Change % | Persentase perubahan (`+47%`, `-10%`) |

- **Sorting**: Default by `Change %` descending
- **Highlight**: Baris dengan change > +30% diberi warna background kuning muda

---

## 5. Page 4: RECOMMENDATIONS (Human Workflow)

### Tujuan
Human-in-the-loop workflow untuk draft → review → publish rekomendasi AI.

### Wireframe Layout

```
┌─────────────────────────────────────────────────┐
│  📝 RECOMMENDATIONS WORKFLOW                   │
│  Filter: [📝 Draft | ✅ Reviewed | 📢 Published]│
└─────────────────────────────────────────────────┘

┌──── DRAFT RECOMMENDATIONS ──────────────────────┐
│                                                 │
│  📝 [1] BURT — Respons Spike Tunjangan         │
│     Generated: 2 jam lalu | Status: DRAFT      │
│     Trigger: Z-Score Spike (2.8)               │
│                                                 │
│     📋 SUMMARY:                                │
│     Sentimen negatif terhadap tunjangan DPR     │
│     mengalami lonjakan signifikan dalam 4 jam   │
│     terakhir. Tweet mencakup kritik             │
│     ketimpangan pendapatan dan seruan reformasi. │
│                                                 │
│     💡 RECOMMENDATION:                         │
│     1. Siapkan statement official BURT         │
│     2. Koordinasi dengan Komite Tunjangan      │
│     3. Monitor sentimen 24 jam ke depan        │
│     4. Pertimbangkan press release penjelasan   │
│                                                 │
│     [✅ Approve & Publish] [✏️ Edit] [❌ Reject] │
│                                                 │
└─────────────────────────────────────────────────┘

┌──── REVIEWED (WAITING PUBLISH) ─────────────────┐
│                                                 │
│  ✅ [1] MKD — Respons Pelanggaran Etika        │
│     Reviewed By: John Doe | 1 hari lalu        │
│     Status: REVIEWED (siap publikasi)          │
│     [📢 Publish] [✏️ Edit] [❌ Reject]          │
│                                                 │
└─────────────────────────────────────────────────┘

┌──── PUBLISHED (ARCHIVE) ────────────────────────┐
│                                                 │
│  ▸ 🔗 Baleg — Strategi RUU Baru               │
│    Published: 3 hari lalu | By: Jane Smith     │
│    [↩️ Revert to Draft] [📋 Archive]            │
│                                                 │
│  ▸ 🔗 Komisi IX — Isu BPJS Kesehatan          │
│    Published: 5 hari lalu | By: John Doe       │
│    [↩️ Revert to Draft] [📋 Archive]            │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Komponen Detail

#### 5.1 Status Filter Tabs
```
[ 📝 Draft (3) | ✅ Reviewed (1) | 📢 Published (5) | Semua ]
```
- **Tipe**: Tab navigation atau segmented control
- **Badge angka**: Jumlah rekomendasi per status

#### 5.2 Draft Recommendation Card

| Element | Deskripsi |
|---------|-----------|
| **Header** | `[ID] AKD_NAME — Judul Singkat` |
| **Metadata** | Generated time + Status badge "DRAFT" |
| **Trigger** | Informasi anomali yang memicu rekomendasi |
| **Summary Box** | Rangkuman situasi (text area, read-only) |
| **Recommendation Box** | Saran tindakan AI (numbered list) |
| **Action Buttons** | `✅ Approve & Publish`, `✏️ Edit`, `❌ Reject` |

**Status Badge Colors**:
| Status | Badge Color | Text |
|--------|------------|------|
| Draft | 🟡 Kuning | `DRAFT` |
| Reviewed | 🔵 Biru | `REVIEWED` |
| Published | 🟢 Hijau | `PUBLISHED` |

---

#### 5.3 Edit Recommendation Modal / Form

| Field | Input Type | Deskripsi |
|-------|-----------|-----------|
| Summary | Textarea (150px tinggi) | Teks rangkuman — editable |
| Recommendation | Textarea (200px tinggi) | Teks rekomendasi — editable |
| Buttons | 2 kolom | `💾 Save Changes` + `❌ Cancel` |

---

#### 5.4 Published Recommendations (Archive)
- **Tipe**: Expandable / accordion list
- **Saat tertutup**: AKD name + tanggal + reviewer
- **Saat terbuka**: Menampilkan summary + recommendation lengkap
- **Action**: `↩️ Revert to Draft`, `📋 Archive`

---

## 6. Komponen Global (Sidebar, Header)

### 6.1 Sidebar Navigasi

```
┌─────────────────────────┐
│  🏛️ DPR Agentic AI      │
│  Monitoring Dashboard    │
│─────────────────────────│
│  🏠 Home                 │
│  🎯 AKD Monitor          │
│  📈 Trends & Alerts      │
│  📝 Rekomendasi          │
│─────────────────────────│
│  FILTERS                 │
│  📅 Tanggal: [picker]   │
│  🏷️ AKD: [dropdown]     │
│  💬 Sentimen: [filter]  │
│─────────────────────────│
│  ⚙️ Settings             │
└─────────────────────────┘
```

### 6.2 Header Bar

```
┌────────────────────────────────────────────────────────────────┐
│  🏛️ AGENTIC AI MONITORING DASHBOARD — DPR RI                 │
│  Updated: Today 14:32 | Data Source: Twitter + Berita Online  │
└────────────────────────────────────────────────────────────────┘
```

- **Background**: Primary Navy (`#1F4E5F`)
- **Teks**: Putih
- **Font**: Title 20px Bold

---

## 7. Design Tokens (Warna, Tipografi, Spacing, Ikon)

### 7.1 Color Palette

#### Primary Colors
| Token | Hex | Penggunaan |
|-------|-----|------------|
| `primary` | `#1F4E5F` | Header, sidebar, tombol utama |
| `primary-light` | `#2A6F7F` | Hover state |
| `background` | `#F8F9FA` | Background halaman |
| `surface` | `#FFFFFF` | Card, panel |
| `border` | `#E5E7EB` | Garis pembatas |

#### Sentiment Colors
| Token | Hex | Penggunaan |
|-------|-----|------------|
| `sentiment-positive` | `#2ecc71` | Positif — chart, badge, teks |
| `sentiment-neutral` | `#95a5a6` | Netral — chart, badge, teks |
| `sentiment-negative` | `#e74c3c` | Negatif — chart, badge, teks |

#### Alert / Severity Colors
| Token | Hex | Penggunaan |
|-------|-----|------------|
| `alert-high` | `#e74c3c` | 🔴 HIGH severity |
| `alert-high-bg` | `#fef2f2` | Background card HIGH |
| `alert-medium` | `#f39c12` | 🟡 MEDIUM severity |
| `alert-medium-bg` | `#fffbeb` | Background card MEDIUM |
| `alert-low` | `#3498db` | ℹ️ LOW severity |
| `alert-low-bg` | `#eff6ff` | Background card LOW |

#### Trend Arrow Colors
| Token | Hex | Arti |
|-------|-----|------|
| `trend-spike` | `#e74c3c` | 🔴 Volume sangat tinggi |
| `trend-up` | `#f39c12` | 🟡 Naik |
| `trend-stable` | `#2ecc71` | 🟢 Stabil |
| `trend-down` | `#3498db` | 🔵 Turun |

---

### 7.2 Typography

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Page Title | 32px | Bold (700) | `#1F4E5F` |
| Section Subtitle | 24px | Bold (700) | `#1F4E5F` |
| Heading (H3) | 20px | Semi-bold (600) | `#1F4E5F` |
| Body | 14px | Regular (400) | `#374151` |
| Caption / Label | 12px | Regular (400) | `#9CA3AF` |
| Metric Number | 36px | Bold (700) | `#111827` |
| Badge Text | 11px | Semi-bold (600) | Putih |

**Font Family**: `Inter`, `Plus Jakarta Sans`, atau system default Streamlit

---

### 7.3 Spacing

| Token | Value | Penggunaan |
|-------|-------|------------|
| `page-padding` | 24px | Padding kiri-kanan halaman |
| `section-gap` | 16px | Jarak antar section |
| `card-padding` | 16px | Padding internal card |
| `card-radius` | 8px | Border radius card |
| `button-padding` | 12px 24px | Padding tombol |
| `button-radius` | 6px | Border radius tombol |

---

### 7.4 Icon Reference

| Ikon | Konteks |
|------|---------|
| 📊 | Statistics / Data |
| 💬 | Comments / Sentiment |
| 📈 | Trends / Growth |
| 🚨 | Alerts / Critical |
| 🔥 | Hot / Popular / Trending |
| 🎯 | Target / AKD |
| 📝 | Document / Draft |
| ✅ | Approved / Done |
| ❌ | Rejected / Error |
| ⚠️ | Warning / Medium |
| ℹ️ | Info / Low severity |
| 🔑 | Keywords |
| 📌 | Pinned info |
| 📅 | Date / Calendar |

---

## 8. Responsive Design

### Desktop (1200px+)
- Full 3-column layout
- Charts: full width
- Tables: scrollable horizontal

### Tablet (768px – 1200px)
- 2-column layout
- Charts: stacked vertikal
- Tables: compact mode

### Mobile (<768px)
- 1-column layout
- Charts: scroll horizontal
- Cards: full width stacked

---

## 9. Data Entity Reference

Data yang tersedia dari backend untuk setiap komponen:

### ContentItem
| Field | Tipe | Deskripsi |
|-------|------|-----------|
| `source_type` | string | `"twitter"` / `"news"` |
| `source_name` | string | `"@dpr_ri"`, `"Detik.com"` |
| `title` | string | Judul / 80 char pertama tweet |
| `content` | text | Teks lengkap |
| `url` | string | URL sumber |
| `published_at` | datetime | Waktu terbit |

### AnalysisResult
| Field | Tipe | Deskripsi |
|-------|------|-----------|
| `sentiment` | string | `"Positif"` / `"Negatif"` / `"Netral"` |
| `sentiment_score` | float | `-1.0` s/d `+1.0` |

### AKDMapping
| Field | Tipe | Deskripsi |
|-------|------|-----------|
| `akd_name` | string | `"Komisi I"`, `"BURT"` |
| `akd_type` | string | `"Komisi"` / `"Badan"` / `"Pimpinan"` |
| `confidence_score` | float | `0.0` – `1.0` |

### TrendWindow
| Field | Tipe | Deskripsi |
|-------|------|-----------|
| `akd_name` | string | Nama AKD |
| `window_start` / `window_end` | datetime | Rentang jendela |
| `item_count` | integer | Jumlah konten |
| `z_score` | float | >2.0 = anomali |
| `is_anomaly` | boolean | Flag anomali |

### Recommendation
| Field | Tipe | Deskripsi |
|-------|------|-----------|
| `akd_name` | string | AKD tujuan |
| `summary` | text | Rangkuman isu |
| `recommendation` | text | Saran AI |
| `status` | string | `"draft"` / `"reviewed"` / `"published"` |
| `reviewed_by` | string | Nama reviewer |

---

## 10. Referensi: 18 AKD DPR RI

Gunakan data ini sebagai opsi dropdown, label chart, dan data dummy Figma:

### Badan (6)
| Nama | Nama Lengkap |
|------|-------------|
| BURT | Badan Urusan Rumah Tangga |
| MKD | Mahkamah Kehormatan Dewan |
| Baleg | Badan Legislasi |
| BAKN | Badan Akuntabilitas Keuangan Negara |
| BKSAP | Badan Kerja Sama Antar-Parlemen |
| BPKPH | Badan Pembentukan Komisi Pemilihan, Penyelenggaraan dan Pengawasan Pemilu |

### Komisi (11)
| Nama | Bidang |
|------|--------|
| Komisi I | Pertahanan, Luar Negeri, Komunikasi dan Informatika |
| Komisi II | Dalam Negeri, Otonomi Daerah, Aparatur Negara dan Agraria |
| Komisi III | Hukum, HAM dan Keamanan |
| Komisi IV | Pertanian, Kehutanan, Kelautan dan Pangan |
| Komisi V | Perhubungan, Pekerjaan Umum, Perumahan Rakyat |
| Komisi VI | Perdagangan, Perindustrian, Investasi, Koperasi, UKM dan BUMN |
| Komisi VII | Energi, Sumber Daya Mineral, Riset dan Teknologi, Lingkungan Hidup |
| Komisi VIII | Agama, Sosial dan Pemberdayaan Perempuan |
| Komisi IX | Kesehatan, Ketenagakerjaan dan Kependudukan |
| Komisi X | Pendidikan, Kebudayaan, Pariwisata dan Ekonomi Kreatif |
| Komisi XI | Keuangan, Perencanaan Pembangunan Nasional, Perbankan |

### Pimpinan (1)
| Nama | Nama Lengkap |
|------|-------------|
| Pimpinan DPR | Pimpinan Dewan Perwakilan Rakyat |

---

## 11. Deliverables Sprint 3

**Minggu 9–10:**
- [ ] Prototype Figma: Homepage (KPIs + charts)
- [ ] Prototype Figma: AKD Monitor page
- [ ] Design system (colors, typography, components)

**Minggu 11:**
- [ ] Prototype Figma: Trends & Alerts page
- [ ] Prototype Figma: Recommendations page
- [ ] Interactive prototyping (click flows)

**Minggu 12:**
- [ ] UI/UX polish & review
- [ ] Handoff ke developer (Streamlit implementation)
- [ ] User acceptance testing (UAT) dengan stakeholder

---

**Next Step:** Mulai desain Figma halaman Home dengan SI 1 pada Sprint 3 Minggu 9! 🚀
