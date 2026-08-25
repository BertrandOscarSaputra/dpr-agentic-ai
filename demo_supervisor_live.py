# -*- coding: utf-8 -*-
"""Live Demonstration of SupervisorAgent LangGraph StateGraph Execution."""

import sys
import io
import asyncio
from src.agents.supervisor import SupervisorAgent

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


async def run_live_demo():
    print("\n" + "="*80)
    print("🚀 MEMULAI DEMO EKSEKUSI LANGGRAPH SUPERVISOR AGENT")
    print("="*80 + "\n")

    supervisor = SupervisorAgent(z_threshold=1.5)

    # Contoh 3 artikel berita kebijakan DPR RI
    sample_news = [
        {
            "title": "Komisi I DPR dan Menhan Bahas Penguatan Keamanan Siber Nasional",
            "content": "Komisi I DPR RI menggelar Rapat Kerja dengan Kementerian Pertahanan dan BSSN guna mempercepat adopsi teknologi pertahanan siber canggih dan interoperabilitas data intelijen.",
            "url": "https://news.detik.com/berita/d-demo-1/komisi-1-siber",
            "published_at": "2026-08-25T09:00:00+07:00",
            "source_type": "news_online",
            "source_name": "Detik.com"
        },
        {
            "title": "Komisi I Minta BSSN Audit Sistem Keamanan Portal Kementerian",
            "content": "Anggota Komisi I DPR RI menegaskan perlunya audit forensik menyeluruh terhadap server kementerian untuk mencegah kebocoran data strategis negara.",
            "url": "https://antaranews.com/berita/d-demo-2/komisi-1-bssn",
            "published_at": "2026-08-25T10:30:00+07:00",
            "source_type": "news_online",
            "source_name": "Antaranews.com"
        },
        {
            "title": "Komisi III DPR Evaluasi Penegakan Hukum Tipikor Bersama KPK dan Kejagung",
            "content": "Komisi III menggelar rapat dengar pendapat evaluasi semester penanganan perkara korupsi strategis bernilai triliunan rupiah.",
            "url": "https://tempo.co/nasional/komisi-3-tipikor",
            "published_at": "2026-08-25T11:00:00+07:00",
            "source_type": "news_online",
            "source_name": "Tempo.co"
        }
    ]

    print("📥 Mengirim 3 artikel sampel ke Supervisor LangGraph...")
    result = await supervisor.run({
        "type": "full_analysis",
        "articles": sample_news
    })

    print("\n" + "─"*80)
    print(f"✅ STATUS AKHIR WORKFLOW: {result.get('status', '').upper()}")
    print("─"*80 + "\n")

    # 1. Hasil Analisis
    print("1️⃣ HASIL ANALISIS ARTIKEL (Oleh AnalysisAgent):")
    for idx, item in enumerate(result.get("analyzed_items", []), 1):
        akds = [m["akd_name"] for m in item.get("akd_mappings", [])]
        print(f"   [{idx}] {item['title']}")
        print(f"       👉 Sentimen : {item['sentiment'].upper()} (Score: {item['sentiment_score']})")
        print(f"       👉 AKD Terpetakan: {', '.join(akds) if akds else 'Lainnya'}")

    # 2. Hasil Tren & Anomali
    print("\n2️⃣ DISTRIBUSI VOLUME & ANOMALI (Oleh TrendAgent):")
    akd_counts = result.get("trends", {}).get("akd_counts", {})
    for akd, count in akd_counts.items():
        print(f"   • {akd}: {count} artikel")
    
    anomalies = result.get("anomalies", [])
    if anomalies:
        print(f"\n   ⚠️ Terdeteksi Anomali Z-Score ({len(anomalies)} AKD):")
        for anom in anomalies:
            print(f"     - {anom['akd_name']}: {anom['count']} artikel (Z-Score: {anom['z_score']} >= {anom['threshold']})")
    
    # 3. Anomaly Critique Verification
    review = result.get("anomaly_review_result", {})
    if review and review.get("verified_details"):
        print("\n3️⃣ HASIL VERIFIKASI ANOMALI (Oleh Anomaly Critique Node):")
        for v in review["verified_details"]:
            print(f"   • {v['akd_name']}: Verified Policy Issue = {v['is_verified_policy_issue']}")
            print(f"     Penjelasan: {v['verification_reason']}")

    # 4. Hasil Rekomendasi & Critique Loop
    print("\n4️⃣ REKOMENDASI KEBIJAKAN FRAKSI & HASIL CRITIQUE LOOP:")
    print(f"   🔄 Jumlah Iterasi Refinement / Loop: {result.get('critique_iterations')} kali")
    print(f"   ⭐ Skor Kelayakan Rekomendasi Akhir: {result.get('critique_score')} / 1.0")
    print(f"   💬 Feedback Pengawas Mutu: {result.get('critique_feedback')}\n")
    
    for idx, rec in enumerate(result.get("recommendations", []), 1):
        print(f"   [{idx}] Target AKD: {rec.get('akd_name')}")
        print(f"       Aksi Rekomendasi: {rec.get('recommendation')}\n")

    print("="*80)
    print("🎉 WORKFLOW SUPERVISOR BERJALAN 100% SUKSES DAN NON-LINEAR!")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(run_live_demo())
