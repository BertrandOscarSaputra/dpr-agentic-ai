# -*- coding: utf-8 -*-
"""Build clean training and validation splits from human-verified annotations and IndoNLU corpus."""

import html
from pathlib import Path
import re
import pandas as pd
from sklearn.model_selection import train_test_split

VERIFIED_CSV = Path("data/annotation/sample_for_manual_verification.csv")
OUTPUT_DIR = Path("data")


def clean_indonesian_text(text: str) -> str:
    """Sanitasi teks berita tanpa merusak struktur tata bahasa."""
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+|#\w+", " ", text)
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)
    text = re.sub(r"[^\w\s\.,\?!-]", " ", text)
    return " ".join(text.split()).strip()


def build_verified_splits(
    verified_file: Path | str = VERIFIED_CSV,
    include_indonlu_smsa: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Process human-verified labels and generate train.csv & val.csv splits.

    Args:
        verified_file: CSV file containing manually reviewed labels.
        include_indonlu_smsa: Whether to merge with IndoNLU SmSA gold dataset.
    """
    records = []

    # 1. Process Human-Verified DPR Samples
    v_path = Path(verified_file)
    if v_path.exists():
        df_manual = pd.read_csv(v_path)
        # Filter rows where human has filled manual_verified_label
        valid_rows = df_manual[df_manual["manual_verified_label"].notna() & (df_manual["manual_verified_label"] != "")]
        print(f"[INFO] Ditemukan {len(valid_rows)} baris yang telah diverifikasi manual oleh manusia.")

        for _, row in valid_rows.iterrows():
            title = str(row.get("title", ""))
            content = str(row.get("content_preview", ""))
            label = int(row.get("manual_verified_label", 1))
            cleaned = clean_indonesian_text(f"{title}. {content}")
            if len(cleaned) > 15:
                records.append({"text": cleaned, "label": label, "source": "dpr_human_verified"})

    # 2. Optionally Merge with IndoNLU SmSA Dataset (11.000 human-labeled benchmark)
    if include_indonlu_smsa:
        try:
            from datasets import load_dataset
            print("[INFO] Mengunduh korpus benchmark manusia IndoNLU SmSA (IndoBenchmark)...")
            dataset = load_dataset("indonlp/indo4b", "smsa", trust_remote_code=True)
            # Label mapping in SmSA: 0 -> positive, 1 -> neutral, 2 -> negative
            # Remap to our standard: 0 -> Negatif, 1 -> Netral, 2 -> Positif
            smsa_remap = {0: 2, 1: 1, 2: 0}
            for item in dataset["train"]:
                raw_text = clean_indonesian_text(item["text"])
                raw_label = item["label"]
                if raw_label in smsa_remap and len(raw_text) > 10:
                    records.append({
                        "text": raw_text,
                        "label": smsa_remap[raw_label],
                        "source": "indonlu_smsa"
                    })
            print("[OK] Berhasil menggabungkan 11.000 data IndoNLU SmSA berlabel manusia!")
        except Exception as e:
            print(f"[WARN] IndoNLU SmSA tidak dapat diunduh otomatis ({e}). Menggunakan data terverifikasi manual lokal.")

    if not records:
        raise ValueError("Belum ada data berlabel valid! Pastikan file CSV verifikasi manual sudah diisi.")

    df_final = pd.DataFrame(records)
    print(f"[INFO] Total Dataset Latih Siap Pakai: {len(df_final)} baris.")

    # Stratified Split 80% Train, 10% Val, 10% Test
    train_df, temp_df = train_test_split(df_final, test_size=0.20, random_state=42, stratify=df_final["label"])
    val_df, test_df = train_test_split(temp_df, test_size=0.50, random_state=42, stratify=temp_df["label"])

    train_df.to_csv(OUTPUT_DIR / "train.csv", index=False)
    val_df.to_csv(OUTPUT_DIR / "val.csv", index=False)
    test_df.to_csv(OUTPUT_DIR / "test.csv", index=False)

    print(f"[OK] File berhasil disimpan di: data/train.csv ({len(train_df)}), data/val.csv ({len(val_df)}), data/test.csv ({len(test_df)}).")

    return train_df, val_df


if __name__ == "__main__":
    build_verified_splits()
