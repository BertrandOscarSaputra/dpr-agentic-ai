"""Input validation and sanitization utilities."""

import re


def sanitize_text(text: str) -> str:
    """Remove potentially harmful characters and normalize whitespace."""
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def validate_akd_name(akd_name: str) -> bool:
    """Validate that the AKD name is in the known list."""
    valid_akd_names = {
        "BURT", "MKD", "Baleg", "BAKN", "BKSAP", "BPKPH",
        "Komisi I", "Komisi II", "Komisi III", "Komisi IV",
        "Komisi V", "Komisi VI", "Komisi VII", "Komisi VIII",
        "Komisi IX", "Komisi X", "Komisi XI",
        "Pimpinan DPR",
    }
    return akd_name in valid_akd_names


def validate_sentiment(sentiment: str) -> bool:
    """Validate that the sentiment value is one of the allowed values."""
    return sentiment in {"Positif", "Negatif", "Netral"}
