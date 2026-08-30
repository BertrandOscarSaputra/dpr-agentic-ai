# -*- coding: utf-8 -*-
"""Dynamic Tool Registry for DPR Agentic AI Multi-Agent System.

Provides standard @tool decorated functions for LangChain/LangGraph agents to
invoke specialized capabilities (collection, classification, sentiment, z-score,
and AKD taxonomy lookups).
"""

import json
import logging
import math
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

from src.agents.analysis import AnalysisAgent
from src.agents.news_collection import NewsCollectionAgent

logger = logging.getLogger(__name__)

# Cache AKD Master dictionary
_AKD_MASTER_CACHE: dict[str, Any] | None = None


def _get_akd_master() -> dict[str, Any]:
    global _AKD_MASTER_CACHE
    if _AKD_MASTER_CACHE is None:
        akd_file = Path("kamus/akd_master.json")
        if akd_file.exists():
            with open(akd_file, encoding="utf-8") as f:
                _AKD_MASTER_CACHE = json.load(f)
        else:
            _AKD_MASTER_CACHE = {}
    return _AKD_MASTER_CACHE


@tool
def fetch_rss_tool(feed_limit: int = 5) -> list[dict]:
    """Fetch and deduplicate latest news articles from Tier-1 national media RSS feeds."""
    logger.info("Tool invoked: fetch_rss_tool", extra={"feed_limit": feed_limit})
    agent = NewsCollectionAgent()
    if feed_limit and len(agent.feeds) > feed_limit:
        agent.feeds = agent.feeds[:feed_limit]
    import asyncio
    return asyncio.run(agent.collect())


@tool
def classify_akd_tool(text: str) -> list[dict]:
    """Classify the text into 24 DPR RI AKDs (Komisi I-XIII, Baleg, Banggar, etc.) using 3-tier matching."""
    logger.info("Tool invoked: classify_akd_tool", extra={"text_len": len(text)})
    agent = AnalysisAgent()
    import asyncio
    return asyncio.run(agent.classify_akd(text))


@tool
def analyze_sentiment_tool(text: str) -> dict:
    """Analyze the sentiment of Indonesian political news text and return label and continuous score (-1.0 to +1.0)."""
    logger.info("Tool invoked: analyze_sentiment_tool", extra={"text_len": len(text)})
    agent = AnalysisAgent()
    label, score = agent.analyze_sentiment(text)
    return {
        "sentiment": label.lower(),
        "sentiment_score": score,
        "confidence": abs(score) if label.lower() != "netral" else 0.85,
    }


@tool
def calculate_zscore_tool(
    daily_counts: list[int],
    current_count: int,
    damping_k: float = 1.5,
    neg_count: int = 0,
    neg_weight: float = 2.5,
) -> dict:
    """Calculate Sentiment-Weighted Z-Score anomaly for an AKD volume time-series.

    Applies negative sentiment weighting and damping factor k to prevent false alarms on small baselines.
    Returns z_score, is_anomaly (True if z_score >= 2.0), mean, std, and effective_volume.
    """
    logger.info(
        "Tool invoked: calculate_zscore_tool",
        extra={"history_len": len(daily_counts), "current_count": current_count, "neg_count": neg_count},
    )
    # Effective volume weighting
    effective_current = current_count + (neg_count * (neg_weight - 1.0)) if neg_count > 0 else float(current_count)

    if not daily_counts or len(daily_counts) < 2:
        return {
            "z_score": 0.0,
            "is_anomaly": False,
            "mean": float(effective_current),
            "std": 0.0,
            "effective_volume": round(effective_current, 2),
        }

    n = len(daily_counts)
    mean = sum(daily_counts) / n
    variance = sum((x - mean) ** 2 for x in daily_counts) / (n - 1)
    std = math.sqrt(variance)

    denominator = std + damping_k
    z_score = round((effective_current - mean) / denominator, 2)

    return {
        "z_score": z_score,
        "is_anomaly": z_score >= 2.0,
        "mean": round(mean, 2),
        "std": round(std, 2),
        "effective_volume": round(effective_current, 2),
    }



@tool
def lookup_akd_metadata_tool(akd_name: str) -> dict:
    """Look up official mandate, scope of duties, and partner ministries for a DPR RI AKD."""
    logger.info("Tool invoked: lookup_akd_metadata_tool", extra={"akd_name": akd_name})
    master = _get_akd_master()
    akd_list = master.get("akd", [])

    # Search list of AKD dicts
    for item in akd_list:
        name = item.get("name", "")
        if name.lower() == akd_name.lower():
            return {"found": True, "akd_name": name, "metadata": item}

    return {
        "found": False,
        "akd_name": akd_name,
        "message": f"AKD '{akd_name}' not found in official taxonomy.",
    }


# Standard Registry of all available tools
ALL_AGENTIC_TOOLS = [
    fetch_rss_tool,
    classify_akd_tool,
    analyze_sentiment_tool,
    calculate_zscore_tool,
    lookup_akd_metadata_tool,
]
