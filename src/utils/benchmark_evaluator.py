# -*- coding: utf-8 -*-
"""Automated Benchmark Evaluator for Sentiment Analysis against Ground Truth."""

import json
import logging
from pathlib import Path
from typing import Any

from src.agents.analysis import AnalysisAgent

logger = logging.getLogger(__name__)

BENCHMARK_JSON_PATH = Path("data/benchmark/ground_truth_100.json")


class BenchmarkEvaluator:
    """Evaluates Sentiment Analysis accuracy, precision, recall, and Macro F1 against verified Ground Truth."""

    def __init__(self, ground_truth_path: Path | str = BENCHMARK_JSON_PATH) -> None:
        self.ground_truth_path = Path(ground_truth_path)
        self.analysis_agent = AnalysisAgent()
        self.classes = ["Negatif", "Netral", "Positif"]

    def load_ground_truth(self) -> list[dict[str, Any]]:
        """Load ground truth benchmark records."""
        if not self.ground_truth_path.exists():
            raise FileNotFoundError(f"Ground truth file not found at: {self.ground_truth_path}")

        with open(self.ground_truth_path, encoding="utf-8") as f:
            return json.load(f)

    def evaluate(self, samples: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Run evaluation over ground truth samples.

        Returns:
            Dictionary with overall accuracy, macro_f1, per-class metrics, confusion matrix, and misclassifications.
        """
        data = samples if samples is not None else self.load_ground_truth()
        if not data:
            return {"error": "Empty dataset"}

        y_true: list[str] = []
        y_pred: list[str] = []
        misclassifications: list[dict[str, Any]] = []

        for item in data:
            expected = item.get("expected_sentiment", "Netral")
            text = f"{item.get('title', '')}. {item.get('content', '')}"

            predicted, score = self.analysis_agent.analyze_sentiment(text)

            y_true.append(expected)
            y_pred.append(predicted)

            if predicted != expected:
                misclassifications.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "expected": expected,
                    "predicted": predicted,
                    "score": score,
                    "akd": item.get("expected_akd"),
                })

        # Calculate metrics
        total = len(y_true)
        correct = sum(1 for yt, yp in zip(y_true, y_pred, strict=False) if yt == yp)
        accuracy = round(correct / total, 4)

        # Confusion Matrix: rows = expected, cols = predicted
        cm: dict[str, dict[str, int]] = {c1: {c2: 0 for c2 in self.classes} for c1 in self.classes}
        for yt, yp in zip(y_true, y_pred, strict=False):
            if yt in cm and yp in cm[yt]:
                cm[yt][yp] += 1

        # Precision, Recall, F1 per class
        per_class: dict[str, dict[str, float]] = {}
        f1_list: list[float] = []

        for c in self.classes:
            tp = cm[c][c]
            fp = sum(cm[other][c] for other in self.classes if other != c)
            fn = sum(cm[c][other] for other in self.classes if other != c)

            precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
            recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
            f1 = round((2 * precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0

            per_class[c] = {"precision": precision, "recall": recall, "f1_score": f1, "support": sum(cm[c].values())}
            f1_list.append(f1)

        macro_f1 = round(sum(f1_list) / len(f1_list), 4)

        results = {
            "total_samples": total,
            "correct_predictions": correct,
            "accuracy": accuracy,
            "macro_f1": macro_f1,
            "meets_target": accuracy >= 0.80 and macro_f1 >= 0.78,
            "per_class_metrics": per_class,
            "confusion_matrix": cm,
            "misclassifications_count": len(misclassifications),
            "misclassifications": misclassifications,
        }

        logger.info(
            "Benchmark evaluation completed",
            extra={"accuracy": accuracy, "macro_f1": macro_f1, "total": total},
        )
        return results
