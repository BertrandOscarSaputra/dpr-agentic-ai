# -*- coding: utf-8 -*-
"""Trend Agent — Sentiment-Weighted Z-Score anomaly detection for content volume per AKD."""

import json
import logging
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TrendAgent:
    """Detects anomalous spikes in content volume per AKD using Sentiment-Weighted Z-score.

    Algorithm:
    - Calculates effective volume weighting negative sentiment (weight = 2.5x)
    - Applies damping smoothing factor (k = 1.5) to prevent false positives in low-baseline AKDs
    - Flags windows where z_score >= threshold as anomalies
    - Persists detected anomalies to daily partition files (data/trends/trends_YYYY-MM-DD.json)
    """

    def __init__(
        self,
        z_threshold: float = 2.0,
        damping_k: float = 1.5,
        neg_weight: float = 2.5,
        trends_dir: str = "data/trends",
    ) -> None:
        self.z_threshold = z_threshold
        self.damping_k = damping_k
        self.neg_weight = neg_weight
        self.trends_dir = Path(trends_dir)
        self.trends_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            "Trend agent initialized",
            extra={
                "z_threshold": z_threshold,
                "damping_k": damping_k,
                "neg_weight": neg_weight,
            },
        )

    def calculate_sentiment_weighted_volume(
        self, pos_count: int, net_count: int, neg_count: int
    ) -> float:
        """Calculate effective sentiment-weighted volume.

        Formula:
            N_effective = N_netral + (1.0 * N_positif) + (neg_weight * N_negatif)
        """
        return round(float(net_count + (1.0 * pos_count) + (self.neg_weight * neg_count)), 2)

    def compute_weighted_zscore(
        self,
        current_effective: float,
        historical_counts: list[float],
    ) -> dict[str, Any]:
        """Compute Z-score with damping smoothing factor k.

        Formula:
            Z_weighted = (N_effective - mean) / (std + k)
        """
        if not historical_counts:
            return {
                "z_score": 0.0,
                "mean": current_effective,
                "std": 0.0,
                "is_anomaly": False,
            }

        all_values = historical_counts + [current_effective]
        n = len(all_values)
        mean = sum(all_values) / n
        variance = sum((x - mean) ** 2 for x in all_values) / max(1, n - 1)
        std = math.sqrt(variance)

        # Apply damping factor in denominator
        denominator = std + self.damping_k
        z_score = round((current_effective - mean) / denominator, 2)

        return {
            "z_score": z_score,
            "mean": round(mean, 2),
            "std": round(std, 2),
            "is_anomaly": z_score >= self.z_threshold,
        }

    def detect_anomalies(
        self,
        analyzed_items: list[dict[str, Any]],
        baseline_pad_to_24: bool = True,
    ) -> dict[str, Any]:
        """Detect sentiment-weighted volume anomalies across all AKDs.

        Returns:
            Dict containing akd_breakdown, anomalies, total_items, and timestamp.
        """
        akd_stats: dict[str, dict[str, int]] = {}

        for item in analyzed_items:
            sentiment = item.get("sentiment", "Netral")
            for mapping in item.get("akd_mappings", []):
                akd = mapping.get("akd_name", "Lainnya")
                if akd not in akd_stats:
                    akd_stats[akd] = {"total": 0, "positif": 0, "netral": 0, "negatif": 0}

                akd_stats[akd]["total"] += 1
                if sentiment == "Positif":
                    akd_stats[akd]["positif"] += 1
                elif sentiment == "Negatif":
                    akd_stats[akd]["negatif"] += 1
                else:
                    akd_stats[akd]["netral"] += 1

        effective_volumes: dict[str, float] = {}
        for akd, s in akd_stats.items():
            effective_volumes[akd] = self.calculate_sentiment_weighted_volume(
                pos_count=s["positif"],
                net_count=s["netral"],
                neg_count=s["negatif"],
            )

        # Baseline distribution across 24 AKDs
        all_effective = list(effective_volumes.values())
        if baseline_pad_to_24 and len(all_effective) < 24:
            padded_distribution = all_effective + [0.0] * (24 - len(all_effective))
        else:
            padded_distribution = all_effective or [0.0]

        n = len(padded_distribution)
        mean_dist = sum(padded_distribution) / n
        var_dist = sum((x - mean_dist) ** 2 for x in padded_distribution) / max(1, n - 1)
        std_dist = math.sqrt(var_dist)

        anomalies: list[dict[str, Any]] = []
        for akd, eff_vol in effective_volumes.items():
            denominator = std_dist + self.damping_k
            z = round((eff_vol - mean_dist) / denominator, 2)
            s = akd_stats[akd]
            neg_ratio = round(s["negatif"] / max(1, s["total"]), 2)

            if z >= self.z_threshold:
                severity = "CRITICAL" if (z >= 3.0 or neg_ratio >= 0.50) else "HIGH"
                anomalies.append({
                    "akd_name": akd,
                    "count": s["total"],
                    "effective_volume": eff_vol,
                    "positif_count": s["positif"],
                    "netral_count": s["netral"],
                    "negatif_count": s["negatif"],
                    "negative_ratio": neg_ratio,
                    "z_score": z,
                    "mean": round(mean_dist, 2),
                    "threshold": self.z_threshold,
                    "severity": severity,
                    "is_sentiment_driven": (eff_vol > s["total"] * 1.3),
                })

        anomalies.sort(key=lambda x: x["z_score"], reverse=True)

        return {
            "total_items": len(analyzed_items),
            "akd_stats": akd_stats,
            "effective_volumes": effective_volumes,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

    def save_anomalies_to_partition(
        self,
        trend_result: dict[str, Any],
        date_str: str | None = None,
    ) -> str:
        """Persist trend anomaly results into partition file data/trends/trends_YYYY-MM-DD.json."""
        if not date_str:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        file_path = self.trends_dir / f"trends_{date_str}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(trend_result, f, indent=2, ensure_ascii=False)

        logger.info(
            "Saved trend partition successfully",
            extra={"path": str(file_path), "anomalies": trend_result.get("anomaly_count", 0)},
        )
        return str(file_path)

    async def detect(self, akd_name: str, recent_items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Run anomaly detection for a specific AKD."""
        logger.info("Running trend detection for AKD", extra={"akd_name": akd_name})
        items = recent_items or []
        trend_data = self.detect_anomalies(items)
        akd_anomalies = [a for a in trend_data["anomalies"] if a["akd_name"] == akd_name]

        return {
            "akd_name": akd_name,
            "anomalies": akd_anomalies,
            "is_anomaly": len(akd_anomalies) > 0,
            "stats": trend_data["akd_stats"].get(akd_name, {"total": 0, "positif": 0, "netral": 0, "negatif": 0}),
        }
