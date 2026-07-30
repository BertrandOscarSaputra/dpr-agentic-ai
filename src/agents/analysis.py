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

# Indonesian Sentiment Keywords for Lexicon-based Scoring
POSITIVE_WORDS = {
    "dukung", "apresiasi", "setuju", "sukses", "solusi", "baik", "bantu",
    "maju", "prestasi", "puji", "komitmen", "optimis", "membangun",
    "positif", "efektif", "unggul", "transparan", "keadilan", "sejahtera",
    "reformasi", "lancar", "sinergi", "berhasil", "harapan", "manfaat",
}

NEGATIVE_WORDS = {
    "korupsi", "gagal", "kecewa", "tolak", "skandal", "rugi", "buruk",
    "lambat", "kritik", "masalah", "pelanggaran", "suap", "bencana",
    "kasus", "polemik", "ancam", "bahaya", "sengketa", "kejahatan",
    "parah", "kecewa", "keluh", "demonstrasi", "protes", "denda", "cacat",
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

        pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)

        total_matches = pos_count + neg_count
        if total_matches == 0:
            return "Netral", 0.0

        # Calculate normalized score in [-1.0, 1.0]
        raw_score = (pos_count - neg_count) / max(total_matches, 1)

        # Scale score based on match frequency relative to document length
        density = min(total_matches / min(len(words), 50), 1.0)
        sentiment_score = round(raw_score * max(density, 0.5), 2)

        # Ensure score bounds
        sentiment_score = max(min(sentiment_score, 1.0), -1.0)

        if sentiment_score > 0.15:
            sentiment = "Positif"
        elif sentiment_score < -0.15:
            sentiment = "Negatif"
        else:
            sentiment = "Netral"

        return sentiment, sentiment_score

    def _keyword_classify_akd(self, text: str) -> list[dict[str, Any]]:
        """Fallback keyword-based AKD classification when Gemini API is unavailable."""
        cleaned = sanitize_text(text).lower()
        if not cleaned:
            return []

        scores: list[tuple[dict[str, Any], int]] = []
        for akd in self.akd_list:
            name = akd.get("name", "")
            full_name = akd.get("full_name", "").lower()
            keywords = akd.get("keywords", [])

            match_count = 0
            # Check name match
            if name.lower() in cleaned:
                match_count += 3

            # Check full name match
            if full_name and full_name in cleaned:
                match_count += 4

            # Check keywords match
            for kw in keywords:
                if kw.lower() in cleaned:
                    match_count += 1

            if match_count > 0:
                scores.append((akd, match_count))

        # Sort by match count descending
        scores.sort(key=lambda x: x[1], reverse=True)

        results: list[dict[str, Any]] = []
        max_matches = scores[0][1] if scores else 1

        for rank, (akd, match_cnt) in enumerate(scores[:3], 1):
            # Normalize confidence score between 0.4 and 0.95
            confidence = round(
                min(0.4 + (match_cnt / max(max_matches, 1)) * 0.55, 0.95), 2
            )
            results.append({
                "akd_name": akd.get("name", ""),
                "akd_type": akd.get("type", "Komisi"),
                "confidence_score": confidence,
                "rank": rank,
            })

        return results

    async def classify_akd(self, text: str) -> list[dict[str, Any]]:
        """Classify text into AKD categories using Gemini AI (with fallback).

        Returns:
            List of top 1..3 AKD mapping dicts.
        """
        # Try Gemini API zero-shot classification first
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

        # Fallback to keyword-based matcher
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
