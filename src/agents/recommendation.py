# -*- coding: utf-8 -*-
# src/agents/recommendation.py
"""Recommendation Agent — generates actionable recommendations via Gemini or fallback."""

import json
import logging
from typing import Any

from src.utils.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

RECOMMENDATION_SYSTEM_PROMPT = """Anda adalah Staf Ahli Senior Fraksi di DPR RI (Periode 2024-2029).
Tugas Anda adalah merumuskan draf aksi kebijakan konkret untuk pimpinan Komisi atau Fraksi DPR RI berdasarkan hasil deteksi isu berita dan sentimen publik.

PANDUAN PENULISAN:
1. Rekomendasi harus operasional dan konkret (misal: Panggilan RDP dengan Menteri, Sidak/Kunjungan Kerja Lapangan, Rilis Sikap Media 1x24 jam, atau Pembentukan Panja).
2. Sesuaikan mitra kementerian dengan portofolio komisi terkait (UU MD3).
3. Berikan rujukan pasal kewenangan pengawasan UU MD3.

OUTPUT HARUS BERUPA JSON VALID SEPERTI INI:
{
  "akd_name": "Komisi XII",
  "issue_title": "Kelangkaan Gas Elpiji 3 Kg Bersubsidi di 5 Wilayah",
  "action_type": "Rapat Dengar Pendapat (RDP) & Sidak Lapangan",
  "urgency": "HIGH",
  "target_stakeholders": ["Kementerian ESDM", "PT Pertamina Patra Niaga", "BPH Migas"],
  "action_summary": "Jadwalkan RDP darurat dengan Dirut Pertamina untuk audit distribusi kuota subsidi dan lakukan sidak ke pangkalan agen daerah.",
  "policy_background": "Sentimen negatif publik melonjak 82% akibat antrean warga dan lonjakan harga di atas HET.",
  "md3_legal_basis": "UU MD3 Pasal 98 terkait wewenang pengawasan komisi terhadap mitra kerja sektor energi."
}
"""


class RecommendationAgent:
    """Agen AI yang merumuskan rekomendasi kebijakan parlemen."""

    def __init__(self) -> None:
        self.client = get_gemini_client()

    async def generate_recommendation(
        self,
        akd_name: str,
        issue_summary: str,
        historical_context: str = "",
        critique_feedback: str = "",
    ) -> dict[str, Any]:
        """Merumuskan draf rekomendasi aksi kebijakan."""
        logger.info("RecommendationAgent: Menulis rekomendasi untuk %s", akd_name)

        prompt = f"""Target AKD: {akd_name}
Ringkasan Masalah: {issue_summary}
Rekam Jejak Historis (30 Hari Terakhir): {historical_context or 'Belum ada catatan krisis sebelumnya.'}
Catatan Evaluasi / Koreksi Sebelumnya: {critique_feedback or 'Draf pertama (belum ada revisi).'}

Tuliskan draf aksi kebijakan terbaik:"""

        try:
            if self.client:
                response = await self.client.generate_async(
                    prompt=prompt,
                    system_instruction=RECOMMENDATION_SYSTEM_PROMPT,
                    temperature=0.2,
                )
                # Bersihkan format markdown jika ada
                clean_json = response.strip().removeprefix("```json").removesuffix("```").strip()
                parsed = json.loads(clean_json)
                parsed["status"] = "draft"
                parsed.setdefault("summary", parsed.get("policy_background", issue_summary))
                parsed.setdefault("recommendation", parsed.get("action_summary", ""))
                return parsed
        except Exception as e:
            logger.warning("Gemini tidak dapat dihubungi (%s), beralih ke template aturan cerdas.", e)

        # Cadangan Otomatis (Fallback) jika API Offline
        action_summary = (
            f"Dorong Pokja {akd_name} Fraksi menjadwalkan RDP klarifikasi bersama kementerian mitra "
            f"dan menyiapkan rilis pers sikap resmi."
        )
        policy_bg = issue_summary[:250] if issue_summary else f"Pemantauan isu prioritas terkait bidang kerja {akd_name}."

        return {
            "akd_name": akd_name,
            "issue_title": f"Respons Pengawasan Isu Prioritas {akd_name}",
            "action_type": "Rapat Dengar Pendapat (RDP) & Pernyataan Sikap",
            "urgency": "HIGH" if any(w in issue_summary.lower() for w in ["krisis", "korupsi", "langka", "demo"]) else "MEDIUM",
            "target_stakeholders": ["Kementerian Mitra Terkait", "Pemerintah Daerah"],
            "action_summary": action_summary,
            "policy_background": policy_bg,
            "md3_legal_basis": "UU MD3 Pasal 98 ayat (3) terkait fungsi pengawasan parlemen.",
            "status": "draft",
            "summary": policy_bg,
            "recommendation": action_summary,
        }

    async def generate(self, akd_name: str, insight_summary: str = "", **kwargs: Any) -> dict[str, Any]:
        """Backward-compatible alias for generate_recommendation."""
        return await self.generate_recommendation(
            akd_name=akd_name,
            issue_summary=insight_summary,
            historical_context=kwargs.get("historical_context", ""),
            critique_feedback=kwargs.get("critique_feedback", ""),
        )
