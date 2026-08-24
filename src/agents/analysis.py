"""Analysis Agent — performs sentiment analysis and AKD classification.

Uses IndoBERT/Lexicon hybrid for sentiment analysis (Positif/Negatif/Netral)
and Gemini zero-shot (with keyword fallback) for multi-label AKD classification.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from src.utils.gemini_client import gemini_classify_akd
from src.utils.validators import sanitize_text

logger = logging.getLogger(__name__)

AKD_MASTER_PATH = (
    Path(__file__).resolve().parents[2] / "kamus" / "akd_master.json"
)

# Comprehensive Indonesian Sentiment Keywords for Lexicon-based Scoring
POSITIVE_WORDS = {
    # Approval & Support
    "dukung", "mendukung", "dukungan", "apresiasi", "mengapresiasi", "setuju", "menyetujui",
    "puji", "memuji", "sepakat", "komitmen", "optimis", "optimisme", "harapan",
    # Success & Achievement
    "sukses", "berhasil", "keberhasilan", "prestasi", "unggul", "keunggulan", "juara",
    "menang", "kemenangan", "gemilang", "rekor", "capaian", "mencapai", "lolos",
    # Improvement & Growth
    "solusi", "baik", "membaik", "terbaik", "bantu", "membantu", "bantuan", "maju", "kemajuan",
    "membangun", "pembangunan", "positif", "efektif", "efektivitas", "transparan", "transparansi",
    "keadilan", "adil", "sejahtera", "kesejahteraan", "reformasi", "lancar", "sinergi", "sinergis",
    "manfaat", "bermanfaat", "pulih", "pemulihan", "tumbuh", "pertumbuhan", "meningkat",
    "peningkatan", "terobosan", "inovasi", "inovatif", "swasembada", "panen", "berkah",
    "selamat", "aman", "tertib", "kondusif", "stabil", "stabilitas", "resmikan", "meresmikan",
    "kolaborasi", "berkolaborasi", "subsidi", "beasiswa", "bansos", "renovasi", "mengatasi",
}

NEGATIVE_WORDS = {
    # Crime & Law Violation
    "korupsi", "suap", "menyuap", "penyuapan", "gratifikasi", "pungli", "skandal",
    "maling", "kemalingan", "curi", "mencuri", "pencurian", "rampok", "merampok", "perampokan",
    "begal", "membegal", "pembegalan", "tembak", "menembak", "penembakan", "tembakan",
    "bunuh", "membunuh", "pembunuhan", "aniaya", "menganiaya", "penganiayaan", "perkosa",
    "kejahatan", "kriminal", "kriminalitas", "narkoba", "miras", "judi", "judol", "ilegal",
    "tangkap", "menangkap", "penangkapan", "tahan", "ditahan", "penahanan", "tersangka",
    "terdakwa", "vonis", "terpidana", "jerat", "terjerat", "polisi", "kepergok",
    # Conflict & Protests
    "gagal", "kegagalan", "kecewa", "kekecewaan", "tolak", "menolak", "penolakan", "rugi",
    "kerugian", "buruk", "memburuk", "lambat", "kritik", "mengkritik", "masalah", "bermasalah",
    "pelanggaran", "melanggar", "polemik", "ancam", "mengancam", "ancaman", "bahaya",
    "berbahaya", "sengketa", "persengketaan", "gugat", "menggugat", "gugatan", "tuntut",
    "tuntutan", "keluh", "keluhan", "mengeluh", "protes", "memprotes", "demonstrasi", "demo",
    "ricuh", "kericuhan", "bentrok", "bentrokan", "tawuran", "rusuh", "kerusuhan", "mogok",
    "PHK", "pecat", "pemecatan", "denda", "cacat", "horor", "teror", "terorisme", "teroris",
    # Disasters & Casualties
    "bencana", "banjir", "kebanjiran", "longsor", "tanah longsor", "gempa", "tsunami",
    "kebakaran", "terbakar", "hangus", "ledakan", "meledak", "amblas", "tenggelam",
    "kecelakaan", "tabrakan", "korban", "tewas", "meninggal", "luka", "terluka",
    "kritis", "darurat", "waspada", "krisis", "defisit", "ambruk", "rusak", "kerusakan",
}


def _load_akd_master() -> list[dict[str, Any]]:
    """Load 18 AKD definitions and keywords from kamus/akd_master.json."""
    if not AKD_MASTER_PATH.exists():
        return []
    try:
        with open(AKD_MASTER_PATH, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("akd", [])
    except Exception as e:
        logger.error("Failed loading akd_master.json", extra={"error": str(e)})
        return []


class AnalysisAgent:
    """Runs sentiment analysis and AKD classification on text content."""

    def __init__(self) -> None:
        self.akd_list = _load_akd_master()
        logger.info(
            "Analysis agent initialized",
            extra={"akd_count": len(self.akd_list)},
        )

    def analyze_sentiment(self, text: str) -> tuple[str, float]:
        """Perform sentiment analysis on Indonesian text.

        Returns:
            Tuple of (sentiment_label, sentiment_score)
            sentiment_label: "Positif", "Negatif", or "Netral"
            sentiment_score: Float between -1.0 and 1.0
        """
        cleaned = sanitize_text(text).lower()
        if not cleaned:
            return "Netral", 0.0

        # Tokenize text into words
        words = re.findall(r"\b\w+\b", cleaned)
        if not words:
            return "Netral", 0.0

        pos_count = 0
        for w in words:
            if w in POSITIVE_WORDS:
                pos_count += 1
            elif any(w.startswith(root) or w.endswith(root) for root in {"sukses", "berhasil", "dukung", "apresiasi", "sejahtera"} if len(w) >= 5):
                pos_count += 1

        neg_count = 0
        for w in words:
            if w in NEGATIVE_WORDS:
                neg_count += 1
            elif any(w.startswith(root) or w.endswith(root) for root in {"korupsi", "bencana", "banjir", "maling", "curi", "begal", "rampok", "tembak", "bunuh", "rusak", "rugi"} if len(w) >= 4):
                neg_count += 1

        if pos_count == 0 and neg_count == 0:
            return "Netral", 0.0

        if pos_count > neg_count:
            diff = pos_count - neg_count
            sentiment_score = round(min(0.20 + (diff / max(pos_count + neg_count, 1)) * 0.60, 1.0), 2)
            sentiment = "Positif"
        elif neg_count > pos_count:
            diff = neg_count - pos_count
            sentiment_score = round(max(-0.20 - (diff / max(pos_count + neg_count, 1)) * 0.60, -1.0), 2)
            sentiment = "Negatif"
        else:
            sentiment = "Netral"
            sentiment_score = 0.0

        return sentiment, sentiment_score

    def _fast_explicit_akd_match(self, text: str) -> list[dict[str, Any]]:
        """Tier 1: Fast deterministic regex matcher for explicit AKD mentions."""
        cleaned = sanitize_text(text)
        if not cleaned:
            return []

        # Find explicit Komisi matches (e.g. "Komisi III", "Komisi I")
        matches: list[dict[str, Any]] = []
        seen_names = set()

        for akd in self.akd_list:
            name = akd.get("name", "")
            if not name:
                continue

            # Build regex pattern for exact word boundary match
            # e.g., "Komisi I" -> r"\bkomisi\s+i\b"
            escaped_name = re.escape(name.lower())
            pattern = rf"\b{escaped_name}\b"

            if re.search(pattern, cleaned.lower()):
                if name not in seen_names:
                    seen_names.add(name)
                    matches.append({
                        "akd_name": name,
                        "akd_type": akd.get("type", "Komisi"),
                        "confidence_score": 0.98,
                        "rank": len(matches) + 1,
                    })
                if len(matches) >= 3:
                    break

        return matches

    def _keyword_classify_akd(self, text: str) -> list[dict[str, Any]]:
        """Tier 3: Multi-factor keyword-based AKD classification fallback."""
        cleaned = sanitize_text(text)
        if not cleaned:
            return []
        cleaned_lower = cleaned.lower()

        scores: list[tuple[dict[str, Any], int]] = []
        for akd in self.akd_list:
            name = akd.get("name", "")
            full_name = akd.get("full_name", "").lower()
            keywords = akd.get("keywords", [])

            match_count = 0
            # Check name match with word boundary
            if name and re.search(rf"\b{re.escape(name.lower())}\b", cleaned_lower):
                match_count += 5

            # Check full name match
            if full_name and full_name in cleaned_lower:
                match_count += 6

            # Check keywords match with word boundary
            for kw in keywords:
                kw_str = str(kw).strip()
                if not kw_str:
                    continue
                # For very short 2-letter acronyms (e.g. "AS", "BI", "SAR"), require exact standalone match
                if len(kw_str) <= 2:
                    if re.search(rf"\b{re.escape(kw_str)}\b", cleaned):
                        match_count += 2
                else:
                    pattern = rf"\b{re.escape(kw_str.lower())}\b"
                    if re.search(pattern, cleaned_lower):
                        match_count += 2

            if match_count > 0:
                scores.append((akd, match_count))

        # Sort by match count descending
        scores.sort(key=lambda x: x[1], reverse=True)

        results: list[dict[str, Any]] = []
        max_matches = scores[0][1] if scores else 1

        for rank, (akd, match_cnt) in enumerate(scores[:3], 1):
            # Normalize confidence score between 0.60 and 0.95
            confidence = round(
                min(0.60 + (match_cnt / max(max_matches, 1)) * 0.35, 0.95), 2
            )
            results.append({
                "akd_name": akd.get("name", ""),
                "akd_type": akd.get("type", "Komisi"),
                "confidence_score": confidence,
                "rank": rank,
            })

        return results

    async def classify_akd(self, text: str) -> list[dict[str, Any]]:
        """Classify text into AKD categories using Tier-1 Fast Match -> Tier-2 Gemini LLM -> Tier-3 Keyword Fallback.

        Returns:
            List of top 1..3 AKD mapping dicts.
        """
        # Tier 1: Try fast explicit regex match first (0ms latency, zero API cost)
        fast_matches = self._fast_explicit_akd_match(text)
        if fast_matches:
            logger.debug(
                "Tier 1 fast-path AKD match succeeded",
                extra={"matches": [m["akd_name"] for m in fast_matches]},
            )
            return fast_matches

        # Tier 2: Try Gemini API zero-shot semantic classification
        gemini_results = await gemini_classify_akd(text)
        if gemini_results:
            # Enrich with akd_type from master list
            type_lookup = {
                akd.get("name", ""): akd.get("type", "Komisi")
                for akd in self.akd_list
            }
            for item in gemini_results:
                name = item.get("akd_name", "")
                item["akd_type"] = type_lookup.get(name, "Komisi")
            return gemini_results

        # Tier 3: Fallback to multi-factor keyword matcher
        logger.info("Using keyword fallback for AKD classification", extra={})
        return self._keyword_classify_akd(text)

    async def analyze(self, content: str) -> dict[str, Any]:
        """Perform full analysis (sentiment + AKD classification) on content.

        Args:
            content: Text content string to analyze.

        Returns:
            Dict containing sentiment, sentiment_score, and akd_mappings.
        """
        logger.info(
            "Analyzing content",
            extra={"content_length": len(content)},
        )

        sentiment, sentiment_score = self.analyze_sentiment(content)
        akd_mappings = await self.classify_akd(content)

        return {
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "akd_mappings": akd_mappings,
        }
