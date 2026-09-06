# -*- coding: utf-8 -*-
from src.utils.benchmark_evaluator import BenchmarkEvaluator

evaluator = BenchmarkEvaluator()
results = evaluator.evaluate()

print(f"Total Samples        : {results['total_samples']}")
print(f"Correct Predictions  : {results['correct_predictions']}/{results['total_samples']}")
print(f"Accuracy             : {results['accuracy']*100:.2f}%")
print(f"Macro F1 Score       : {results['macro_f1']:.4f}")
print(f"Target Met (>=80%)   : {results['meets_target']}")
print("\nPer-Class Performance:")
for cls_name, m in results['per_class_metrics'].items():
    print(f"  - {cls_name:<8}: Precision={m['precision']:.4f} | Recall={m['recall']:.4f} | F1={m['f1_score']:.4f} (Support={m['support']})")

print("\nConfusion Matrix (Rows: Expected, Cols: Predicted):")
print(f"  {'':<10} {'Negatif':<10} {'Netral':<10} {'Positif':<10}")
for expected, preds in results['confusion_matrix'].items():
    print(f"  {expected:<10} {preds['Negatif']:<10} {preds['Netral']:<10} {preds['Positif']:<10}")
