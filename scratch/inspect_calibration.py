# -*- coding: utf-8 -*-
import csv
import json
import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained('indobert_sentiment_final')
tokenizer = AutoTokenizer.from_pretrained('indobert_sentiment_final')
model.eval()

# 1. Load Ground Truth 100
with open('data/benchmark/ground_truth_100.json', encoding='utf-8') as f:
    gt_items = json.load(f)

# 2. Load 298 Manual Verification
manual_items = []
id2label = {'0': 'Negatif', '1': 'Netral', '2': 'Positif'}

with open('data/annotation/sample_for_manual_verification.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        lbl = str(r.get('manual_verified_label', '')).strip()
        if lbl in id2label:
            r['clean_label'] = id2label[lbl]
            manual_items.append(r)

print(f"Loaded {len(gt_items)} ground truth samples and {len(manual_items)} manual verified samples.")

def eval_dataset(items, text_fn, label_fn, name="Dataset"):
    print(f"\n==================== EVALUATING {name} ({len(items)} samples) ====================")
    
    # Pre-extract probabilities
    cached = []
    for item in items:
        text = text_fn(item)
        inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=128, padding=True)
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = F.softmax(logits, dim=-1).squeeze()
        cached.append((float(probs[0].item()), float(probs[1].item()), float(probs[2].item()), label_fn(item)))

    for thresh in [0.0, 0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20]:
        correct = 0
        cm = {c1: {c2: 0 for c2 in ['Negatif', 'Netral', 'Positif']} for c1 in ['Negatif', 'Netral', 'Positif']}
        for p_neg, p_net, p_pos, true_label in cached:
            # Negative is highly confident, so if p_neg is highest:
            if p_neg > p_pos and p_neg > p_net:
                pred = "Negatif"
            elif p_pos > p_net and (p_pos - p_net) >= thresh:
                pred = "Positif"
            else:
                pred = "Netral"

            if true_label in cm and pred in cm[true_label]:
                cm[true_label][pred] += 1
            if pred == true_label:
                correct += 1
                
        acc = correct / len(cached)
        
        # Macro F1
        f1s = []
        for c in ['Negatif', 'Netral', 'Positif']:
            tp = cm[c][c]
            fp = sum(cm[o][c] for o in ['Negatif', 'Netral', 'Positif'] if o != c)
            fn = sum(cm[c][o] for o in ['Negatif', 'Netral', 'Positif'] if o != c)
            p = tp / (tp + fp) if (tp + fp) > 0 else 0
            r = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0
            f1s.append(f1)
        macro_f1 = sum(f1s) / len(f1s)
        
        print(f"Threshold margin={thresh:4.2f} -> Accuracy: {acc*100:5.2f}% | Macro F1: {macro_f1:.4f} | Neg(R): {cm['Negatif']['Negatif']} | Net(R): {cm['Netral']['Netral']} | Pos(R): {cm['Positif']['Positif']}")

eval_dataset(
    gt_items,
    text_fn=lambda x: f"{x['title']}. {x['content']}",
    label_fn=lambda x: x['expected_sentiment'],
    name="Ground Truth (30 samples)"
)

eval_dataset(
    manual_items,
    text_fn=lambda x: f"{x['title']}. {x.get('content_preview', '')}",
    label_fn=lambda x: x['clean_label'],
    name="Manual Verification (298 samples)"
)
