"""Wrapper for Google Gemini API calls (AKD classification & summarization)."""

from __future__ import annotations

import json
import logging
from typing import Any

import google.generativeai as genai

from src.config import settings

logger = logging.getLogger(__name__)

_configured = False


def _configure_gemini() -> bool:
    """Configure the Gemini API client with the API key.

    Returns:
        True if Gemini API key is configured, False otherwise.
    """
    global _configured  # noqa: PLW0603
    if not settings.GEMINI_API_KEY:
        return False
    if not _configured:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _configured = True
    return True


AKD_SYSTEM_PROMPT = """\
Anda adalah pakar analisis politik dan Parlemen DPR RI.
Tugas Anda: Klasifikasikan teks berikut ke dalam Alat Kelengkapan Dewan (AKD)
DPR RI yang relevan (maksimal 3 AKD terbaik).

Daftar AKD resmi DPR RI Periode 2024-2029:
- Ketua DPR (Ketua/Wakil Ketua/Paripurna)
- Komisi I (Pertahanan, Luar Negeri, Kominfo, TNI, BSSN)
- Komisi II (Dalam Negeri, Otonomi Daerah, ASN, Pertanahan, KPU, Pemilu)
- Komisi III (Hukum, HAM, Keamanan, Kepolisian, Kejaksaan, KPK)
- Komisi IV (Pertanian, Kehutanan, Kelautan, Pangan, Perikanan)
- Komisi V (Perhubungan, Infrastruktur, Perumahan, BMKG, Basarnas)
- Komisi VI (Perdagangan, Industri, Investasi, BUMN, UMKM, Koperasi)
- Komisi VII (Perindustrian, UMKM, Ekonomi Kreatif, Pariwisata)
- Komisi VIII (Agama, Sosial, Pemberdayaan Perempuan, Haji, Bencana)
- Komisi IX (Kesehatan, Ketenagakerjaan, Kependudukan, BPJS)
- Komisi X (Pendidikan, Kebudayaan, Riset, Olahraga, Perpustakaan)
- Komisi XI (Keuangan, APBN, Perbankan, BI, OJK, Bappenas)
- Komisi XII (Energi, Mineral, Lingkungan Hidup, Iklim, Sumber Daya Alam)
- Komisi XIII (Reformasi Hukum, HAM, Imigrasi, Pemasyarakatan)
- Banggar (Badan Anggaran)
- Bamus (Badan Musyawarah)
- BURT (Badan Urusan Rumah Tangga)
- MKD (Mahkamah Kehormatan Dewan)
- Baleg (Badan Legislasi)
- BAKN (Badan Akuntabilitas Keuangan Negara)
- BKSAP (Badan Kerja Sama Antar-Parlemen)
- BAM (Badan Aspirasi Masyarakat)

Format Response Wajib JSON:
{
  "mappings": [
    {"akd_name": "Komisi III", "confidence_score": 0.92, "rank": 1},
    {"akd_name": "Baleg", "confidence_score": 0.65, "rank": 2}
  ]
}
"""


async def gemini_classify_akd(content: str) -> list[dict[str, Any]]:
    """Use Gemini zero-shot to classify content into AKD categories.

    Returns:
        List of dicts with keys: akd_name, confidence_score, rank
    """
    if not _configure_gemini():
        logger.warning(
            "GEMINI_API_KEY not set — using fallback classification",
            extra={},
        )
        return []

    logger.info(
        "Gemini AKD classification requested",
        extra={"content_length": len(content)},
    )

    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        prompt = f"{AKD_SYSTEM_PROMPT}\n\nTeks untuk diklasifikasikan:\n{content[:2000]}"
        response = model.generate_content(prompt)

        text_resp = response.text or ""
        # Parse JSON from markdown code block if present
        if "```json" in text_resp:
            text_resp = text_resp.split("```json")[1].split("```")[0].strip()
        elif "```" in text_resp:
            text_resp = text_resp.split("```")[1].split("```")[0].strip()

        data = json.loads(text_resp)
        mappings = data.get("mappings", [])

        # Validate format
        validated: list[dict[str, Any]] = []
        for i, item in enumerate(mappings[:3], 1):
            akd_name = item.get("akd_name", "")
            score = float(item.get("confidence_score", 0.5))
            if akd_name:
                validated.append({
                    "akd_name": akd_name,
                    "confidence_score": min(max(score, 0.0), 1.0),
                    "rank": item.get("rank", i),
                })
        return validated

    except Exception as e:
        logger.error("Gemini classification failed", extra={"error": str(e)})
        return []


async def gemini_summarize(texts: list[str], context: str = "") -> str:
    """Use Gemini to generate a narrative summary from multiple text inputs.

    Returns:
        Summary text string.
    """
    if not _configure_gemini():
        logger.warning("GEMINI_API_KEY not set — summarization skipped", extra={})
        return ""

    logger.info("Gemini summarization requested", extra={"text_count": len(texts)})
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        combined_text = "\n---\n".join(t[:1000] for t in texts[:10])
        prompt = (
            f"Buatkan ringkasan naratif eksekutif untuk isu DPR RI berikut:\n"
            f"Konteks: {context}\n\nTeks Berita/Tweet:\n{combined_text}"
        )
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else ""
    except Exception as e:
        logger.error("Gemini summarization failed", extra={"error": str(e)})
        return ""
