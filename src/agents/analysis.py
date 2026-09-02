"""Analysis Agent — sentiment analysis and AKD classification engine.

Uses a 3-tier hybrid architecture:
- Tier 1: Fast Regex pattern matcher for explicit mentions (0ms, $0 cost)
- Tier 2: Google Gemini Flash zero-shot LLM classifier for implicit/complex text
- Tier 3: Multi-factor weighted keyword dictionary fallback
- Policy Relevance Gatekeeper: Determines if content is actionable for DPR RI.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any

from src.utils.gemini_client import classify_akd as gemini_classify_akd
from src.utils.validators import sanitize_text

logger = logging.getLogger(__name__)

AKD_MASTER_PATH = Path(__file__).resolve().parents[2] / "kamus" / "akd_master.json"
INDOBERT_MODEL_DIR = Path(__file__).resolve().parents[2] / "indobert_sentiment_final"

# Core sentiment dictionaries
POSITIVE_WORDS = {
    "setuju", "sepakat", "dukung", "mendukung", "apresiasi", "mengapresiasi",
    "sukses", "berhasil", "prestasi", "efektif", "optimal", "positif",
    "puji", "memuji", "sambut", "menyambut", "bagus", "baik", "unggul",
    "maju", "kemajuan", "tumbuh", "pertumbuhan", "meningkat", "peningkatan",
    "pulih", "pemulihan", "harmonis", "transparan", "akuntabel", "solid",
    "kompak", "bersatu", "sinergi", "kolaborasi", "sejahtera", "kesejahteraan",
    "bantu", "bantuan", "solutif", "responsif", "terobosan", "inovasi",
    "resmikan", "meresmikan", "tuntaskan", "selesaikan", "aman", "kondusif",
}

NEGATIVE_WORDS = {
    "tolak", "menolak", "kritik", "mengkritik", "kecewa", "kekecewaan",
    "gagal", "kegagalan", "buruk", "memburuk", "rugi", "kerugian",
    "korupsi", "koruptor", "suap", "menyuap", "pungli", "gratifikasi",
    "skandal", "polemik", "kontroversi", "protes", "memprotes", "demo",
    "demonstrasi", "ricuh", "kericuhan", "bentrok", "bentrokan", "ancam",
    "mengancam", "ancaman", "bahaya", "membahayakan", "lambat", "terlambat",
    "cacat", "pelanggaran", "melanggar", "ilegal", "kejahatan", "kriminal",
    "bencana", "banjir", "kebanjiran", "longsor", "tanah longsor", "gempa", "tsunami",
    "kebakaran", "terbakar", "hangus", "ledakan", "meledak", "amblas", "tenggelam",
    "kecelakaan", "tabrakan", "korban", "tewas", "meninggal", "luka", "terluka",
    "kritis", "darurat", "waspada", "krisis", "defisit", "ambruk", "rusak", "kerusakan",
}

POLICY_GOVERNANCE_KEYWORDS = {
    "kebijakan", "regulasi", "undang-undang", "uu", "ruu", "apbn", "rapbn",
    "anggaran", "kementerian", "menteri", "pemerintah", "presiden", "wapres",
    "bumn", "bappenas", "bpk", "kpk", "kejaksaan", "polri", "tni", "bi", "ojk",
    "lps", "pajak", "subsidi", "impor", "ekspor", "bencana", "bansos",
    "parlemen", "fraksi", "pokja", "komisi", "sidang", "paripurna", "rdp",
}


def _load_akd_master() -> list[dict[str, Any]]:
    """Load 24 AKD definitions and keywords from kamus/akd_master.json."""
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
    """Runs sentiment analysis, AKD classification, and policy relevance auditing."""

    def __init__(self) -> None:
        self.akd_list = _load_akd_master()
        self.indobert_model = None
        self.indobert_tokenizer = None

        # Attempt to load fine-tuned IndoBERT model
        if INDOBERT_MODEL_DIR.exists():
            try:
                import torch
                from transformers import AutoModelForSequenceClassification, AutoTokenizer

                self.indobert_tokenizer = AutoTokenizer.from_pretrained(str(INDOBERT_MODEL_DIR))
                self.indobert_model = AutoModelForSequenceClassification.from_pretrained(str(INDOBERT_MODEL_DIR))
                self.indobert_model.eval()
                logger.info("Fine-tuned IndoBERT model loaded successfully for sentiment analysis.")
            except Exception as exc:
                logger.warning("Could not load fine-tuned IndoBERT model (%s). Using lexicon fallback.", exc)
                self.indobert_model = None
                self.indobert_tokenizer = None

        logger.info(
            "Analysis agent initialized",
            extra={"akd_count": len(self.akd_list), "indobert_active": self.indobert_model is not None},
        )

    def analyze_sentiment(self, text: str) -> tuple[str, float]:
        """Perform sentiment analysis on Indonesian text.

        Returns:
            Tuple of (sentiment_label, sentiment_score)
            sentiment_label: "Positif", "Negatif", or "Netral"
            sentiment_score: Float between -1.0 and 1.0
        """
        cleaned = sanitize_text(text)
        if not cleaned:
            return "Netral", 0.0

        # Tier 1: Fine-tuned IndoBERT Inference if available
        if self.indobert_model is not None and self.indobert_tokenizer is not None:
            try:
                import torch
                import torch.nn.functional as F

                inputs = self.indobert_tokenizer(
                    cleaned,
                    return_tensors="pt",
                    truncation=True,
                    max_length=128,
                    padding=True,
                )
                with torch.no_grad():
                    outputs = self.indobert_model(**inputs)
                    probs = F.softmax(outputs.logits, dim=-1).squeeze()
                    pred_id = int(torch.argmax(outputs.logits, dim=-1).item())
                    p_neg = float(probs[0].item())
                    p_net = float(probs[1].item())
                    p_pos = float(probs[2].item())

                id2label = {0: "Negatif", 1: "Netral", 2: "Positif"}
                label = id2label.get(pred_id, "Netral")

                # Continuous polarity score: Positif prob - Negatif prob
                score = round(p_pos - p_neg, 2)
                if label == "Netral" and abs(score) < 0.40:
                    score = 0.0

                return label, score
            except Exception as exc:
                logger.warning("IndoBERT inference error (%s), falling back to lexicon.", exc)


        # Tier 2: Offline Deterministic Lexicon Fallback
        cleaned_lower = cleaned.lower()
        words = re.findall(r"\b\w+\b", cleaned_lower)
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

        total_sentiment_words = pos_count + neg_count
        if total_sentiment_words == 0:
            return "Netral", 0.0

        raw_score = (pos_count - neg_count) / total_sentiment_words
        score = round(raw_score, 2)

        if score >= 0.15:
            return "Positif", score
        elif score <= -0.15:
            return "Negatif", score
        else:
            return "Netral", score


    def evaluate_policy_relevance(self, text: str, akd_mappings: list[dict[str, Any]]) -> tuple[bool, float]:
        """Evaluate if an article is relevant to DPR RI governance, legislation, or budget.

        Returns:
            tuple (is_dpr_relevant: bool, relevance_score: float)
        """
        if akd_mappings and len(akd_mappings) > 0:
            top_confidence = akd_mappings[0].get("confidence_score", 0.70)
            return True, top_confidence

        # Check secondary policy governance keywords
        cleaned_lower = sanitize_text(text).lower()
        matched_gov = sum(1 for kw in POLICY_GOVERNANCE_KEYWORDS if f" {kw} " in f" {cleaned_lower} ")

        if matched_gov >= 2:
            return True, round(min(0.60 + matched_gov * 0.05, 0.85), 2)

        return False, 0.20

    def _fast_explicit_akd_match(self, text: str) -> list[dict[str, Any]] | None:
        """Tier 1: Check for explicit mentions of AKD names using high-precision Regex."""
        cleaned = sanitize_text(text)
        if not cleaned:
            return None

        # Pattern: "Komisi [1-13|I-XIII]"
        komisi_match = re.search(
            r"\bKomisi\s+([1-9]|1[0-3]|I{1,3}|IV|V|VI{1,3}|IX|X|XI{1,3})\b",
            cleaned,
            re.IGNORECASE,
        )
        if komisi_match:
            raw_num = komisi_match.group(1).upper()
            roman_map = {
                "1": "I", "2": "II", "3": "III", "4": "IV", "5": "V",
                "6": "VI", "7": "VII", "8": "VIII", "9": "IX", "10": "X",
                "11": "XI", "12": "XII", "13": "XIII",
            }
            roman_num = roman_map.get(raw_num, raw_num)
            akd_name = f"Komisi {roman_num}"

            # Secondary check for partner/context keywords
            secondary_matches = self._keyword_classify_akd(cleaned, exclude_akd=akd_name)
            results = [
                {
                    "akd_name": akd_name,
                    "akd_type": "Komisi",
                    "confidence_score": 0.95,
                    "rank": 1,
                }
            ]
            for rank, sec in enumerate(secondary_matches[:2], 2):
                if sec["akd_name"] != akd_name:
                    sec["rank"] = rank
                    sec["confidence_score"] = min(sec["confidence_score"], 0.75)
                    results.append(sec)
            return results

        # Explicit check for leadership and bodies
        explicit_bodies = [
            ("Ketua DPR", "Pimpinan", [r"\bKetua DPR\b", r"\bPuan Maharani\b"]),
            ("Badan Legislasi", "Badan", [r"\bBadan Legislasi\b", r"\bBaleg\b"]),
            ("Badan Anggaran", "Badan", [r"\bBadan Anggaran\b", r"\bBanggar\b"]),
            ("Mahkamah Kehormatan Dewan", "Badan", [r"\bMahkamah Kehormatan Dewan\b", r"\bMKD\b"]),
            ("Badan Kerja Sama Antar Parlemen", "Badan", [r"\bBKSAP\b", r"\bKerja Sama Antar Parlemen\b"]),
            ("Badan Akuntabilitas Keuangan Negara", "Badan", [r"\bBAKN\b"]),
            ("Badan Urusan Rumah Tangga", "Badan", [r"\bBURT\b"]),
        ]

        for name, b_type, patterns in explicit_bodies:
            for pat in patterns:
                if re.search(pat, cleaned, re.IGNORECASE):
                    return [
                        {
                            "akd_name": name,
                            "akd_type": b_type,
                            "confidence_score": 0.95,
                            "rank": 1,
                        }
                    ]

        return None

    def _keyword_classify_akd(self, text: str, exclude_akd: str | None = None) -> list[dict[str, Any]]:
        """Tier 3: Multi-factor weighted keyword dictionary fallback."""
        cleaned = sanitize_text(text)
        cleaned_lower = cleaned.lower()
        scores: list[tuple[dict[str, Any], int]] = []

        for akd in self.akd_list:
            if exclude_akd and akd.get("name") == exclude_akd:
                continue

            match_count = 0
            keywords = akd.get("keywords", [])
            for kw in keywords:
                kw_str = str(kw).strip()
                if not kw_str:
                    continue
                if len(kw_str) <= 2:
                    if re.search(rf"\b{re.escape(kw_str)}\b", cleaned):
                        match_count += 2
                else:
                    pattern = rf"\b{re.escape(kw_str.lower())}\b"
                    if re.search(pattern, cleaned_lower):
                        match_count += 2

            if match_count > 0:
                scores.append((akd, match_count))

        scores.sort(key=lambda x: x[1], reverse=True)
        results: list[dict[str, Any]] = []
        max_matches = scores[0][1] if scores else 1

        for rank, (akd, match_cnt) in enumerate(scores[:3], 1):
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
        # Tier 1: Fast explicit regex match
        fast_matches = self._fast_explicit_akd_match(text)
        if fast_matches:
            return fast_matches

        # Tier 2: Gemini API zero-shot semantic classification
        gemini_results = await gemini_classify_akd(text)
        if gemini_results:
            type_lookup = {
                akd.get("name", ""): akd.get("type", "Komisi")
                for akd in self.akd_list
            }
            for item in gemini_results:
                name = item.get("akd_name", "")
                item["akd_type"] = type_lookup.get(name, "Komisi")
            return gemini_results

        # Tier 3: Keyword fallback
        return self._keyword_classify_akd(text)

    async def analyze(self, content: str) -> dict[str, Any]:
        """Perform full analysis (sentiment + AKD classification + DPR policy relevance).

        Returns:
            Dict containing sentiment, sentiment_score, akd_mappings, and is_dpr_relevant.
        """
        sentiment, sentiment_score = self.analyze_sentiment(content)
        akd_mappings = await self.classify_akd(content)
        is_relevant, relevance_score = self.evaluate_policy_relevance(content, akd_mappings)

        return {
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "akd_mappings": akd_mappings,
            "is_dpr_relevant": is_relevant,
            "relevance_score": relevance_score,
        }
