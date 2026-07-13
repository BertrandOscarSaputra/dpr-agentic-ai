"""Wrapper for Google Gemini API calls."""

import logging

import google.generativeai as genai

from src.config import settings

logger = logging.getLogger(__name__)


def _configure_gemini() -> None:
    """Configure the Gemini API client with the API key."""
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
    else:
        logger.warning("GEMINI_API_KEY not set — Gemini calls will fail", extra={})


_configure_gemini()


async def gemini_classify_akd(content: str) -> list[dict]:
    """Use Gemini zero-shot to classify content into AKD categories.

    Returns:
        List of dicts with keys: akd_name, akd_type, confidence_score, rank
    """
    logger.info("Gemini AKD classification requested", extra={"content_length": len(content)})
    # TODO: Implement Gemini API call with AKD classification prompt
    return []


async def gemini_summarize(texts: list[str], context: str = "") -> str:
    """Use Gemini to generate a summary from multiple text inputs.

    Returns:
        Summary text string.
    """
    logger.info("Gemini summarization requested", extra={"text_count": len(texts)})
    # TODO: Implement Gemini API call with summarization prompt
    return ""
