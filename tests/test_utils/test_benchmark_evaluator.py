# -*- coding: utf-8 -*-
"""Unit tests for Automated Benchmark Evaluator."""

from src.utils.benchmark_evaluator import BenchmarkEvaluator


class TestBenchmarkEvaluator:
    """Test suite for BenchmarkEvaluator."""

    def test_evaluator_loads_ground_truth(self) -> None:
        """Verify BenchmarkEvaluator successfully loads ground truth samples."""
        evaluator = BenchmarkEvaluator()
        data = evaluator.load_ground_truth()
        assert len(data) >= 30
        assert all("expected_sentiment" in d for d in data)
        assert all("expected_akd" in d for d in data)

    def test_evaluate_computes_accuracy_and_f1(self) -> None:
        """Verify evaluate() returns accuracy, macro F1, and confusion matrix."""
        evaluator = BenchmarkEvaluator()
        result = evaluator.evaluate()

        assert "total_samples" in result
        assert result["total_samples"] >= 30
        assert "accuracy" in result
        assert "macro_f1" in result
        assert "per_class_metrics" in result
        assert "confusion_matrix" in result

        # Precision, recall, f1 for all 3 classes
        for c in ["Negatif", "Netral", "Positif"]:
            assert c in result["per_class_metrics"]
            metrics = result["per_class_metrics"][c]
            assert "precision" in metrics
            assert "recall" in metrics
            assert "f1_score" in metrics

        # Accuracy should be high on our curated benchmark
        assert result["accuracy"] >= 0.70
        assert result["macro_f1"] >= 0.70
