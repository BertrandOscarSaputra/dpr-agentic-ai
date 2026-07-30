"""Input validation and sanitization utilities."""

import json
import re
from functools import lru_cache
from pathlib import Path

AKD_MASTER_PATH = Path(__file__).resolve().parents[2] / "kamus" / "akd_master.json"


@lru_cache(maxsize=1)
def get_valid_akd_names() -> frozenset[str]:
    """Load AKD names from the master JSON file (single source of truth)."""
    with open(AKD_MASTER_PATH, encoding="utf-8") as f:
        data = json.load(f)
    names = set()
    for entry in data.get("akd", []):
        name = entry.get("name", "")
        if name:
            names.add(name)
            if name == "Ketua DPR":
                names.add("Pimpinan DPR")
    return frozenset(names)


def sanitize_text(text: str) -> str:
    """Remove potentially harmful characters and normalize whitespace."""
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def validate_akd_name(akd_name: str) -> bool:
    """Validate that the AKD name is in the known list."""
    return akd_name in get_valid_akd_names()


def validate_sentiment(sentiment: str) -> bool:
    """Validate that the sentiment value is one of the allowed values."""
    return sentiment in {"Positif", "Negatif", "Netral"}
