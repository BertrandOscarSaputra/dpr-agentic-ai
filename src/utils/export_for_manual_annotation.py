# -*- coding: utf-8 -*-
"""Tool to export dataset samples into a spreadsheet for Human-in-the-Loop manual verification."""

import glob
import json
from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path("data/annotation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def export_samples_for_manual_labeling(
    samples_per_category: int = 100,
    source_folder: str = "data/analysis",
) -> str:
    """Export balanced sample articles for SI 2 to inspect and manually verify labels.

    Output format (CSV):
    - id: Unique row ID
    - title: News headline
    - content_preview: First 300 characters of news content
    - initial_ai_sentiment: Sentiment guessed by current baseline
    - manual_verified_sentiment: [EMPTY - TO BE FILLED BY HUMAN: Positif / Netral / Negatif]
    - manual_verified_label: [EMPTY - TO BE FILLED BY HUMAN: 0 (Negatif), 1 (Netral), 2 (Positif)]
    - notes: Optional notes for edge cases / political nuances
    """
    records = []
    for file_path in sorted(glob.glob(f"{source_folder}/analysis_*.json")):
        with open(file_path, "r", encoding="utf-8") as f:
            items = json.load(f)
            for item in items:
                title = item.get("title", "").strip()
                content = item.get("content", "").strip()
                sentiment = item.get("sentiment", "Netral")

                if len(title) > 10 and len(content) > 20:
                    records.append({
                        "title": title,
                        "content_preview": content[:300],
                        "initial_ai_sentiment": sentiment,
                        "manual_verified_sentiment": "",  # To be filled by SI 2
                        "manual_verified_label": "",      # 0, 1, or 2
                        "notes": "",
                    })

    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError("No records found in data/analysis/*.json")

    # Shuffle and sample balanced batches per category
    df = df.sample(frac=1.0, random_state=42)
    sampled_df = df.groupby("initial_ai_sentiment").head(samples_per_category).reset_index(drop=True)
    sampled_df.insert(0, "id", range(1, len(sampled_df) + 1))

    output_csv = OUTPUT_DIR / "sample_for_manual_verification.csv"
    sampled_df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"[OK] Berhasil mengekspor {len(sampled_df)} sampel artikel ke '{output_csv}'!")
    print("-> Buka file tersebut di Excel / Google Sheets untuk diverifikasi manual oleh SI 2.")
    return str(output_csv)



if __name__ == "__main__":
    export_samples_for_manual_labeling(samples_per_category=100)
