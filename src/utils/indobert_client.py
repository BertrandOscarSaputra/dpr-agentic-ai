"""Wrapper for IndoBERT sentiment analysis model."""

import logging

logger = logging.getLogger(__name__)

# Model will be loaded lazily to avoid slow startup
_model = None
_tokenizer = None


def _load_model() -> None:
    """Lazy-load the IndoBERT sentiment model and tokenizer."""
    global _model, _tokenizer  # noqa: PLW0603
    if _model is not None:
        return
    logger.info("Loading IndoBERT sentiment model", extra={})
    # TODO: Load from HuggingFace transformers
    # from transformers import AutoModelForSequenceClassification, AutoTokenizer
    # _tokenizer = AutoTokenizer.from_pretrained("indobenchmark/indobert-base-p1")
    # _model = AutoModelForSequenceClassification.from_pretrained(...)


async def predict_sentiment(text: str) -> dict:
    """Predict sentiment for the given Indonesian text.

    Returns:
        Dict with keys: sentiment (Positif|Negatif|Netral), sentiment_score (float)
    """
    _load_model()
    logger.info("IndoBERT sentiment prediction", extra={"text_length": len(text)})
    # TODO: Tokenize, infer, post-process
    return {"sentiment": "Netral", "sentiment_score": 0.0}
