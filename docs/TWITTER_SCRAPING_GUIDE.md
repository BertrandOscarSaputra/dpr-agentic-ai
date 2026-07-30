# 🐦 Panduan Lengkap: Membangun Twitter/X Scraper (Tanpa API Key) dari Nol

Dokumen ini berisi panduan *step-by-step* dari awal (*ground zero*) untuk membangun fitur penarikan data (scraping) Twitter/X tanpa perlu membeli atau menggunakan **X API v2 berbayar**, mulai dari persiapan akun, konfigurasi `.env`, penanganan Cloudflare anti-bot via `cookies.json`, hingga otomatisasi penjadwalan via Celery Beat.

---

## 📑 Daftar Isi
1. [Prasyarat & Persiapan Akun X](#1-prasyarat--persiapan-akun-x)
2. [Langkah 1: Konfigurasi Environment (`.env` & `src/config.py`)](#langkah-1-konfigurasi-environment-env--srcconfigpy)
3. [Langkah 2: Export Sesi Cookie (`cookies.json`) Bypassing Cloudflare](#langkah-2-export-sesi-cookie-cookiesjson-bypassing-cloudflare)
4. [Langkah 3: Pembuatan Query Dinamis dari Data Master AKD](#langkah-3-pembuatan-query-dinamis-dari-data-master-akd)
5. [Langkah 4: Implementasi `TwitterCollectionAgent` (`twikit`)](#langkah-4-implementasi-twittercollectionagent-twikit)
6. [Langkah 5: Menyimpan ke Database PostgreSQL](#langkah-5-menyimpan-ke-database-postgresql)
7. [Langkah 6: Otomatisasi Penjadwalan Berkala (Celery Worker & Beat)](#langkah-6-otomatisasi-penjadwalan-berkala-celery-worker--beat)
8. [Langkah 7: Pengujian (Unit Tests & Script Live)](#langkah-7-pengujian-unit-tests--script-live)

---

## 1. Prasyarat & Persiapan Akun X

### 1.1 Buat Akun X (Twitter)
1. Buka [x.com](https://x.com) dan buat satu akun X (disarankan menggunakan akun terpisah/sekunder untuk scraping).
2. Catat 3 data berikut dari akun Anda:
   - **Username**: (contoh: `totoropoporo123`)
   - **Email**: (contoh: `totoropoporo123@gmail.com`)
   - **Password**: (contoh: `PasswordKu123!`)
3. Pastikan Anda sudah login setidaknya sekali di browser (Chrome/Edge) dengan akun tersebut.

---

## Langkah 1: Konfigurasi Environment (`.env` & `src/config.py`)

### 1.1 Buat File `.env`
Di root folder proyek Anda (sejajar dengan `pyproject.toml`), buat file `.env` dan tambahkan kredensial X Anda:

```env
# X/Twitter Scraping Kredensial
X_USERNAME=totoropoporo123
X_EMAIL=totoropoporo123@gmail.com
X_PASSWORD=PasswordKu123!
X_COOKIES_PATH=cookies.json

# Pydantic JSON Array default untuk API_KEYS
API_KEYS=[]
```

> ⚠️ **Keamanan**: File `.env` dan `cookies.json` sudah dimasukkan ke `.gitignore` sehingga tidak akan ter-commit ke GitHub.

### 1.2 Sesuaikan `src/config.py` (Pydantic Settings)
Tambahkan bidang konfigurasi X pada kelas `Settings`:

```python
# src/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # X/Twitter Scraping (twikit)
    X_USERNAME: str = ""
    X_EMAIL: str = ""
    X_PASSWORD: str = ""
    X_COOKIES_PATH: str = "cookies.json"
```

---

## Langkah 2: Export Sesi Cookie (`cookies.json`) Bypassing Cloudflare

### Mengapa Perlu Cookie?
X memproteksi login otomatis berbasis script (POST request) dengan **Cloudflare Anti-Bot (HTTP 403 Forbidden)**. Dengan menggunakan cookie sesi browser asli, scraper kita **langsung lolos tanpa terblokir Cloudflare**.

### Cara Export Cookie dari Browser:
1. Buka browser (Chrome/Edge) dan login ke [x.com](https://x.com).
2. Install ekstensi browser **[Cookie-Editor](https://cookie-editor.cgenterprises.org/)**.
3. Di tab `x.com`, klik ikon **Cookie-Editor** -> **Export** -> **Export as JSON**.
4. Buat file baru bernama **`cookies.json`** di root folder proyek (`c:\Users\Lenovo\Documents\DPR\dpr-agentic-ai\cookies.json`), lalu paste isi JSON tersebut.

---

## Langkah 3: Pembuatan Query Dinamis dari Data Master AKD

Agen akan membaca daftar 18 Alat Kelengkapan Dewan (AKD) dari `kamus/akd_master.json` dan menyusun kata kunci pencarian otomatis.

### Format Query X:
$$\text{Query} = (\text{DPR} \lor \text{"DPR RI"}) \land (\text{Kata Kunci AKD}) \land \text{lang:id} \land \neg\text{is:retweet}$$

Contoh untuk **Komisi I**:
`"(DPR OR \"DPR RI\") (pertahanan OR \"luar negeri\" OR TNI) lang:id -is:retweet"`

---

## Langkah 4: Implementasi `TwitterCollectionAgent` (`twikit`)

### 4.1 Install Library `twikit`
Jalankan perintah berikut di terminal:
```bash
uv add twikit
```

### 4.2 Tulis `src/agents/twitter_collection.py`

```python
# src/agents/twitter_collection.py
import json, logging
from pathlib import Path
from typing import Any
from twikit import Client
from src.config import settings
from src.utils.validators import sanitize_text

logger = logging.getLogger(__name__)
COOKIES_PATH = Path(settings.X_COOKIES_PATH)

async def _create_twikit_client() -> Client | None:
    client = Client("id-ID")

    # 1. Buka cookies.json jika ada (Bypass Cloudflare)
    if COOKIES_PATH.exists():
        try:
            with open(COOKIES_PATH, encoding="utf-8") as f:
                cookie_data = json.load(f)

            # Konversi otomatis dari Cookie-Editor (List) ke Dictionary
            if isinstance(cookie_data, list):
                cookie_data = {
                    item["name"]: item["value"]
                    for item in cookie_data
                    if "name" in item and "value" in item
                }

            if isinstance(cookie_data, dict) and cookie_data:
                client.set_cookies(cookie_data)
                logger.info("Loaded X session cookies from file", extra={"path": str(COOKIES_PATH)})
                return client
        except Exception as e:
            logger.warning("Stored cookies.json invalid", extra={"error": str(e)})

    # 2. Login Programatis (Fallback)
    if settings.X_USERNAME and settings.X_PASSWORD:
        await client.login(
            auth_info_1=settings.X_USERNAME,
            auth_info_2=settings.X_EMAIL,
            password=settings.X_PASSWORD,
        )
        client.save_cookies(str(COOKIES_PATH))
        return client

    return None

class TwitterCollectionAgent:
    def __init__(self) -> None:
        self.max_results = settings.TWITTER_MAX_RESULTS_PER_QUERY

    def parse_tweet(self, tweet: Any) -> dict[str, Any] | None:
        tweet_id = getattr(tweet, "id", None)
        text = getattr(tweet, "text", None)
        if not tweet_id or not text:
            return None

        cleaned = sanitize_text(text)
        user = getattr(tweet, "user", None)
        username = getattr(user, "screen_name", "") if user else ""
        source_name = f"@{username}" if username else "X / Twitter"

        return {
            "source_type": "twitter",
            "source_name": source_name,
            "content": cleaned,
            "title": cleaned[:80] + "..." if len(cleaned) > 80 else cleaned,
            "url": f"https://x.com/i/status/{tweet_id}",
            "published_at": getattr(tweet, "created_at", None),
        }

    async def collect(self) -> list[dict[str, Any]]:
        client = await _create_twikit_client()
        if not client:
            return []

        all_tweets = []
        # Loop semua query AKD...
        # tweets = await client.search_tweet(query_str, "Latest")
        # all_tweets.extend(parsed_tweets)
        return all_tweets
```

---

## Langkah 5: Menyimpan ke Database PostgreSQL

Menggunakan **Repository Pattern** (`ContentRepository.save_articles`) dengan perintah `ON CONFLICT (url) DO NOTHING` agar tweet yang sudah pernah ditarik tidak duplikat di database:

```python
# src/tasks/collection.py
from src.database import get_session_factory
from src.repositories.content_repository import ContentRepository

def save_tweets_to_db(tweets: list[dict]):
    session_factory = get_session_factory()
    with session_factory() as session:
        repo = ContentRepository(session)
        saved, skipped = repo.save_articles(tweets)
        print(f"Berhasil menyimpan {saved} tweet baru, {skipped} duplikat diabaikan.")
```

---

## Langkah 6: Otomatisasi Penjadwalan Berkala (Celery Worker & Beat)

### 6.1 Celery Task (`src/tasks/collection.py`)
```python
@celery_app.task(name="tasks.collect_twitter", bind=True, max_retries=3)
def collect_twitter(self) -> dict:
    agent = TwitterCollectionAgent()
    tweets = asyncio.run(agent.collect())
    save_tweets_to_db(tweets)
    return {"status": "completed", "collected": len(tweets)}
```

### 6.2 Schedule di `src/tasks/__init__.py`
Menjadwalkan penarikan otomatis setiap 4 jam:
```python
celery_app.conf.update(
    beat_schedule={
        "collect-twitter-every-4-hours": {
            "task": "tasks.collect_twitter",
            "schedule": crontab(minute=30, hour="*/4"),
        },
    },
)
```

### 6.3 Service Docker (`docker-compose.yml`)
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

## Langkah 7: Pengujian (Unit Tests & Script Live)

### 7.1 Menjalankan Unit Tests (Mocked Client)
```bash
pytest tests/test_agents/test_twitter_collection.py -v
```

### 7.2 Script Eksekusi Live
Jalankan script python langsung dari terminal:
```python
import asyncio
from src.agents.twitter_collection import TwitterCollectionAgent

async def main():
    agent = TwitterCollectionAgent()
    tweets = await agent.collect()
    print(f"✅ BERHASIL MEMPEROLEH {len(tweets)} TWEET LIVE!")
    for t in tweets[:5]:
        print(f"- {t['source_name']}: {t['title']} ({t['url']})")

asyncio.run(main())
```
