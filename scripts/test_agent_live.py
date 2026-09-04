# -*- coding: utf-8 -*-
"""Script Pengujian Langsung Multi-Agent DPR Agentic AI (LangGraph StateGraph).

Cara menjalankan:
    uv run python scripts/test_agent_live.py
"""

import asyncio
import os
import sys

# Konfigurasi encoding UTF-8 untuk terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Tambahkan root path proyek
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import settings
from src.agents.supervisor import SupervisorAgent


def print_banner():
    print("=" * 75)
    print("🏛️   PENGUJIAN LANGSUNG AI AGENT — DPR AGENTIC AI (LANGGRAPH)")
    print("=" * 75)

    # Cek API Key
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
        masked_key = settings.GEMINI_API_KEY[:6] + "..." + settings.GEMINI_API_KEY[-4:]
        print(f"🔑 Status GEMINI_API_KEY : ✅ TERDETEKSI ({masked_key})")
        print("🧠 Mode Eksekusi         : 🚀 AI Reasoning Penuh (Google Gemini 3.6 Flash)")
    else:
        print("🔑 Status GEMINI_API_KEY : ⚠️ BELUM DIISI di file .env")
        print("🛡️ Mode Eksekusi         : 🔄 Offline Fallback Mode (Leksikon & Heuristik Mandiri)")
    print("-" * 75)


async def main():
    print_banner()

    # Siapkan data artikel simulasi untuk pengujian cepat
    sample_articles = [
        {
            "title": "Warga Antre 3 Jam Demi Gas 3 Kg, Komisi XII Minta Pertamina Tindak Agen Nakal",
            "content": "Kelangkaan gas elpiji melon 3 kg semakin parah di Jawa Tengah. Warga mengeluhkan harga menembus Rp35.000 per tabung. Anggota Komisi XII mendesak Pertamina dan BPH Migas melakukan audit mendalam ke pangkalan distribusi.",
            "url": "https://news.example.com/gas-melon-langka-komisi-xii",
            "source_name": "Detikcom",
            "source_type": "news_online",
            "published_at": "2026-09-04T08:00:00Z",
        },
        {
            "title": "KPK Periksa Pejabat Kemenhub Terkait Dugaan Korupsi Jalur Kereta Api",
            "content": "Komisi Pemberantasan Korupsi menjadwalkan pemeriksaan terhadap pejabat Kemenhub terkait kasus dugaan suap proyek pemeliharaan jalur rel kereta api di Jawa dan Sumatera.",
            "url": "https://news.example.com/kpk-kemenhub-suap",
            "source_name": "Antara",
            "source_type": "news_online",
            "published_at": "2026-09-04T09:15:00Z",
        },
        {
            "title": "Panen Raya Padi Petani Sukoharjo Sukses Lampaui Target Swasembada",
            "content": "Petani di Sukoharjo mencatat rekor panen raya padi varietas unggul baru dengan dukungan bantuan pupuk dan alsintan dari Kementerian Pertanian dan Komisi IV DPR RI.",
            "url": "https://news.example.com/panen-sukoharjo-berhasil",
            "source_name": "Tempo",
            "source_type": "news_online",
            "published_at": "2026-09-04T10:30:00Z",
        },
    ]

    print(f"📥 Menginput {len(sample_articles)} artikel sampel pengujian...")
    print("🤖 Menjalankan LangGraph Supervisor Agent (Siklus Multi-Agen Otonom)...")
    print("-" * 75)

    supervisor = SupervisorAgent()

    # Eksekusi StateGraph
    initial_state = {
        "task_type": "full_analysis",
        "articles": sample_articles,
        "errors": [],
    }

    final_state = await supervisor.run(initial_state)

    print("✅ SIKLUS MULTI-AGEN BERHASIL DIEKSEKUSI!")
    print("=" * 75)

    # 1. Hasil Analisis Sentimen & AKD
    print("\n🔍 1. HASIL ANALISIS SENTIMEN & PEMETAAN 24 AKD:")
    analyzed_items = final_state.get("analyzed_items", [])
    for idx, item in enumerate(analyzed_items, 1):
        mappings = [m.get("akd_name") for m in item.get("akd_mappings", [])]
        print(f"   [{idx}] {item.get('title')}")
        print(f"       • Sentimen : {item.get('sentiment')} (Skor: {item.get('sentiment_score'):+.2f})")
        print(f"       • AKD      : {', '.join(mappings) if mappings else 'Tidak Terklasifikasi'}")

    # 2. Hasil Deteksi Anomali
    print("\n📈 2. EVALUASI TREN & ANOMALI KEBIJAKAN (SIMPUL C3):")
    trends = final_state.get("trends", {})
    print(f"   • Total Artikel Dianalisis: {trends.get('total_items', 0)}")
    print(f"   • Distribusi AKD          : {trends.get('akd_counts', {})}")
    anomalies = final_state.get("anomalies", [])
    if anomalies:
        for anom in anomalies:
            print(f"   🚨 Anomali Terdeteksi : {anom.get('akd_name')} (Z-Score: {anom.get('z_score', 0):.2f})")
    else:
        print("   ℹ️ Tidak ada anomali lonjakan ekstrem (Volume dalam batas normal)")

    # 3. Hasil Sintesis Narasi Isu
    print("\n💡 3. SINTESIS NARASI ISU (INSIGHT AGENT):")
    insights = final_state.get("insights", [])
    for ins in insights:
        print(f"   🏛️ [{ins.get('akd_name')}]:")
        print(f"      {ins.get('summary')}")

    # 4. Hasil Rekomendasi Tindakan Parlemen & Critique Loop
    print("\n🏛️ 4. HASIL REKOMENDASI KEBIJAKAN & CRITIQUE AUDIT LOOP:")
    recs = final_state.get("recommendations", [])
    for idx, rec in enumerate(recs, 1):
        print(f"   📌 Draf Aksi Dewan #{idx} ({rec.get('akd_name')}):")
        print(f"      • Uraian Rekomendasi: {rec.get('recommendation')}")
        print(f"      • Status Workflow   : {rec.get('status')}")

    print(f"\n🛡️ 5. STATUS CRITIQUE AUDIT MUTU:")
    print(f"   • Skor Kelayakan Mutu  : {final_state.get('critique_score', 0.0):.2f} / 1.00")
    print(f"   • Putaran Revisi Otomatis: {final_state.get('critique_iterations', 1)} kali")
    print(f"   • Catatan Tim Audit    : {final_state.get('critique_feedback', '-')}")

    if final_state.get("errors"):
        print(f"\n⚠️ Catatan Error Terisolasi: {final_state.get('errors')}")

    print("\n" + "=" * 75)
    print("🎉 PENGUJIAN SELESAI DENGAN SUKSES!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(main())
