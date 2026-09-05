# -*- coding: utf-8 -*-
# src/repositories/memory_repository.py
"""Repository for 30-day contextual issue memory and recommendation archive."""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path("data/dpr_agentic_memory.db")


class MemoryRepository:
    """Pengelola basis data memori kontekstual 30 hari dan arsip rekomendasi."""

    def __init__(self, db_path: Path | str = DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.init_db()

    def init_db(self) -> None:
        """Membuat tabel jika belum ada."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 1. Tabel Memori Isu 30 Hari
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    akd_name TEXT NOT NULL,
                    date_key TEXT NOT NULL,
                    sentiment_score REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 2. Tabel Arsip Rekomendasi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    akd_name TEXT NOT NULL,
                    issue_title TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    urgency TEXT NOT NULL,
                    target_stakeholders TEXT,
                    action_summary TEXT NOT NULL,
                    policy_background TEXT,
                    md3_legal_basis TEXT,
                    status TEXT DEFAULT 'draft',
                    critique_score REAL DEFAULT 0.0,
                    critique_iterations INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_context_memory(
        self,
        akd_name: str,
        date_key: str,
        sentiment_score: float,
        volume: int,
        summary: str = "",
    ) -> int:
        """Menyimpan rekaman memori harian untuk AKD tertentu."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO context_memory (
                    akd_name, date_key, sentiment_score, volume, summary
                ) VALUES (?, ?, ?, ?, ?)
            """, (akd_name, date_key, sentiment_score, volume, summary))
            conn.commit()
            return cursor.lastrowid or 0

    def get_30_day_history(self, akd_name: str, current_date: str) -> list[dict]:
        """Menarik rekam jejak isu 30 hari ke belakang."""
        curr_dt = datetime.strptime(current_date, "%Y-%m-%d")
        start_dt = (curr_dt - timedelta(days=30)).strftime("%Y-%m-%d")

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date_key, sentiment_score, volume, summary
                FROM context_memory
                WHERE akd_name = ? AND date_key BETWEEN ? AND ?
                ORDER BY date_key ASC
            """, (akd_name, start_dt, current_date))
            return [dict(r) for r in cursor.fetchall()]

    def save_recommendation(self, rec: dict) -> int:
        """Menyimpan draf rekomendasi yang sudah lolos audit ke database."""
        stakeholders = rec.get("target_stakeholders", [])
        if isinstance(stakeholders, list):
            stakeholders_str = json.dumps(stakeholders)
        else:
            stakeholders_str = str(stakeholders)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO recommendations (
                    akd_name, issue_title, action_type, urgency,
                    target_stakeholders, action_summary, policy_background,
                    md3_legal_basis, status, critique_score, critique_iterations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rec.get("akd_name", "Komisi"),
                rec.get("issue_title", "Rekomendasi Kebijakan"),
                rec.get("action_type", "Rapat Dengar Pendapat (RDP)"),
                rec.get("urgency", "MEDIUM"),
                stakeholders_str,
                rec.get("action_summary", rec.get("recommendation", "")),
                rec.get("policy_background", rec.get("summary", "")),
                rec.get("md3_legal_basis", ""),
                rec.get("status", "draft"),
                float(rec.get("critique_score", 0.85)),
                int(rec.get("critique_iterations", 1)),
            ))
            conn.commit()
            return cursor.lastrowid or 0

    def list_recommendations(self, akd_name: str | None = None) -> list[dict]:
        """Mengambil seluruh daftar rekomendasi untuk ditampilkan di web."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if akd_name:
                cursor.execute(
                    "SELECT * FROM recommendations WHERE akd_name = ? ORDER BY id DESC",
                    (akd_name,),
                )
            else:
                cursor.execute("SELECT * FROM recommendations ORDER BY id DESC")
            rows = [dict(r) for r in cursor.fetchall()]
            for row in rows:
                if isinstance(row.get("target_stakeholders"), str):
                    try:
                        row["target_stakeholders"] = json.loads(row["target_stakeholders"])
                    except Exception:
                        pass
            return rows
