# 📖 Panduan Lengkap: Membangun Data Collection Engine (RSS News & Twitter/X Scraper) dari Nol

Dokumen ini berisi panduan *step-by-step* tentang bagaimana arsitektur data collection (pengumpulan berita & Twitter) pada proyek **DPR Agentic AI System** dirancang dan dibangun dari commit awal hingga siap pakai (*production-ready*).

---

## 📑 Daftar Isi
1. [Prinsip Desain & Kebutuhan System](#1-prinsip-desain--kebutuhan-system)
2. [Langkah 1: Desain Skema Database & Repository Pattern](#langkah-1-desain-skema-database--repository-pattern)
3. [Langkah 2: Membangun News Collection Agent (RSS Feeds)](#langkah-2-membangun-news-collection-agent-rss-feeds)
4. [Langkah 3: Membangun Twitter/X Collection Agent (`twikit`)](#langkah-3-membangun-twitterx-collection-agent-twikit)
5. [Langkah 4: Otomatisasi via Celery Worker & Beat Scheduler](#langkah-4-otomatisasi-via-celery-worker--beat-scheduler)
6. [Langkah 5: Pengujian (Unit Test & Live Execution)](#langkah-5-pengujian-unit-test--live-execution)

---

## 1. Prinsip Desain & Kebutuhan System

Sistem data collection dirancang untuk memantau **18 Alat Kelengkapan Dewan (AKD)** DPR RI (Komisi I–XI, Baleg, BURT, MKD, BAKN, BKSAP, BPKPH, dan Pimpinan DPR) yang terdaftar pada `kamus/akd_master.json`.

### Prinsip Utama:
1. **Standardized Content Model**: Semua data berita maupun tweet dinormalisasi ke skema tunggal `ContentItem`.
2. **Deduplikasi Otomatis**: Menggunakan URL sebagai *unique identifier* (`ON CONFLICT DO NOTHING`).
3. **Resilience & Error Isolation**: Kegagalan pada 1 sumber berita/tweet tidak boleh menghentikan proses pengumpulan dari sumber lainnya.
4. **Bebas Ketergantungan API Mahal**: Twitter/X dikumpulkan menggunakan `twikit` (sesi cookie browser), menghindari biaya X API v2 yang mahal.

---

## Langkah 1: Desain Skema Database & Repository Pattern

### 1.1 Model Database (`src/models/content_item.py`)
Semua sumber data yang dikumpulkan disimpan ke tabel `content_items` menggunakan SQLAlchemy 2.x dengan kolom berzona waktu (`TIMESTAMPTZ`):

```python
# src/models/content_item.py
from datetime import UTC, datetime
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base

class ContentItem(Base):
    __tablename__ = "content_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "news" | "twitter"
    source_name: Mapped[str | None] = mapped_column(String(200), nullable=True)  # "@dpr_ri" / "Detik.com"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    url: Mapped[str | None] = mapped_column(String(1000), unique=True, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
```

### 1.2 Repository Pattern (`src/repositories/content_repository.py`)
Gunakan PostgreSQL native upsert untuk efisiensi penyimpanan massal (*batch insert*):

```python
# src/repositories/content_repository.py
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from src.models.content_item import ContentItem

class ContentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_articles(self, articles: list[dict]) -> tuple[int, int]:
        """Menyimpan list artikel/tweet dengan deduplikasi URL."""
        if not articles:
            return 0, 0

        valid_articles = [a for a in articles if a.get("url")]
        skipped = len(articles) - len(valid_articles)

        # Batch Insert dengan ON CONFLICT DO NOTHING
        stmt = insert(ContentItem).values(valid_articles)
        stmt = stmt.on_conflict_do_nothing(index_elements=["url"])
        
        result = self.session.execute(stmt)
        self.session.commit()
        
        saved = result.rowcount
        skipped += len(valid_articles) - saved
        return saved, skipped
```

---

## Langkah 2: Membangun News Collection Agent (RSS Feeds)

`NewsCollectionAgent` (`src/agents/news_collection.py`) menarik berita nasional dari 13 RSS feeds (Detik, Kompas, Antara, Tempo, Republika, CNN Indonesia, dll.).

### Komponen Utama:
1. **User-Agent Spoofing**: Menyediakan `User-Agent` browser modern agar tidak diblokir server berita.
2. **Date Parsing Multi-Format**: Menggunakan `python-dateutil` untuk memproses berbagai format tanggal (RFC 822 / ISO 8601).
3. **HTML Sanitization**: Membersihkan tag HTML (`<b>`, `<p>`, `<a>`) via `sanitize_text()`.

```python
# src/agents/news_collection.py
import asyncio, httpx, feedparser
from src.utils.validators import sanitize_text

class NewsCollectionAgent:
    def __init__(self, feeds: list[str] | None = None) -> None:
        self.feeds = feeds or DEFAULT_NEWS_FEEDS
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."}

    async def fetch_feed(self, client: httpx.AsyncClient, url: str) -> list[dict]:
        try:
            resp = await client.get(url, headers=self.headers, timeout=15)
            parsed = feedparser.parse(resp.text)
            articles = []
            for entry in parsed.entries:
                articles.append({
                    "source_type": "news",
                    "source_name": parsed.feed.get("title", "RSS News"),
                    "title": entry.get("title"),
                    "content": sanitize_text(entry.get("summary", "")),
                    "url": entry.get("link"),
                    "published_at": self._parse_date(entry.get("published")),
                })
            return articles
        except Exception:
            return []  # Isolated failure
```

---

## Langkah 3: Membangun Twitter/X Collection Agent (`twikit`)

`TwitterCollectionAgent` (`src/agents/twitter_collection.py`) mengumpulkan tweet berdasarkan topik 18 AKD tanpa menggunakan Twitter API berbayar.

### 3.1 Pembuatan Query Otomatis dari AKD Master
Memuat `kamus/akd_master.json` dan menyusun query pencarian X API v2 format:
$$\text{Query} = (\text{DPR} \lor \text{"DPR RI"}) \land (\text{Kata Kunci AKD}) \land \text{lang:id} \land \neg\text{is:retweet}$$

### 3.2 Autentikasi Bebas Cloudflare (Session Cookie Bypass)
Karena login otomatis via script diblokir Cloudflare Anti-Bot (HTTP 403), agen menggunakan file **`cookies.json`** yang diexport dari browser:

```python
# src/agents/twitter_collection.py
import json, logging
from pathlib import Path
from twikit import Client

COOKIES_PATH = Path("cookies.json")

async def _create_twikit_client() -> Client | None:
    client = Client("id-ID")
    
    # 1. Buka cookies.json jika ada
    if COOKIES_PATH.exists():
        with open(COOKIES_PATH, encoding="utf-8") as f:
            cookie_data = json.load(f)
            
        # Format konversi dari Cookie-Editor (List of dict) ke Dictionary
        if isinstance(cookie_data, list):
            cookie_data = {item["name"]: item["value"] for item in cookie_data if "name" in item and "value" in item}

        client.set_cookies(cookie_data)
        return client

    # 2. Login Programatis (Fallback jika cookies.json tidak ada)
    await client.login(auth_info_1=username, auth_info_2=email, password=password)
    client.save_cookies(str(COOKIES_PATH))
    return client
```

---

## Langkah 4: Otomatisasi via Celery Worker & Beat Scheduler

### 4.1 Celery Tasks (`src/tasks/collection.py`)
Membungkus fungsi agen dalam Celery tasks dengan *exponential backoff retry*:

```python
# src/tasks/collection.py
import asyncio
from src.tasks import celery_app
from src.agents.news_collection import NewsCollectionAgent
from src.agents.twitter_collection import TwitterCollectionAgent

@celery_app.task(name="tasks.collect_news", bind=True, max_retries=3)
def collect_news(self) -> dict:
    agent = NewsCollectionAgent()
    articles = asyncio.run(agent.collect())
    # Save to DB via ContentRepository ...

@celery_app.task(name="tasks.collect_twitter", bind=True, max_retries=3)
def collect_twitter(self) -> dict:
    agent = TwitterCollectionAgent()
    tweets = asyncio.run(agent.collect())
    # Save to DB via ContentRepository ...
```

### 4.2 Celery Beat Periodic Schedule (`src/tasks/__init__.py`)
Menjadwalkan penarikan data berkala setiap 4 jam:

```python
# src/tasks/__init__.py
from celery.schedules import crontab

celery_app.conf.update(
    beat_schedule={
        "collect-news-every-4-hours": {
            "task": "tasks.collect_news",
            "schedule": crontab(minute=0, hour="*/4"),  # Pukul 00:00, 04:00, 08:00, dst.
        },
        "collect-twitter-every-4-hours": {
            "task": "tasks.collect_twitter",
            "schedule": crontab(minute=30, hour="*/4"), # Pukul 00:30, 04:30, 08:30, dst.
        },
    },
)
```

### 4.3 Container Service (`docker-compose.yml`)
Menambahkan container scheduler `celery-beat`:

```yaml
  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile
      target: dev
    container_name: dpr-celery-beat-dev
    command: celery -A src.tasks beat --loglevel=info
    depends_on:
      - postgres
      - redis
      - celery
```

---

## Langkah 5: Pengujian (Unit Test & Live Execution)

### 5.1 Unit Testing dengan Pytest
Menjangkau 100% skenario tanpa memanggil network asli:

```bash
# Menjalankan seluruh test suite (92 test passing)
pytest tests/ -v
```

### 5.2 Uji Coba Penarikan Data Live
Dapat diuji langsung dari terminal:

```python
import asyncio
from src.agents.twitter_collection import TwitterCollectionAgent

async def run():
    agent = TwitterCollectionAgent()
    tweets = await agent.collect()
    print(f"Berhasil mengumpulkan {len(tweets)} tweet live.")

asyncio.run(run())
```
