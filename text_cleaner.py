"""
VYNTRIX Text Cleaning & Preprocessing Pipeline
Preserves audit trail while normalising noise, emojis, and typos.
"""

import re
import unicodedata
from typing import Dict, Any, Tuple
import pandas as pd


def normalize_whitespace(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_noisy_repetitions(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r"(.)\1{2,}", r"\1\1", text)


def normalize_punctuation(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"!+", "!", text)
    text = re.sub(r"\?+", "?", text)
    text = re.sub(r"\.+", ".", text)
    return text


def clean_text_for_nlp(text: str) -> str:
    if text is None or pd.isna(text):
        return ""
    text = str(text)
    text = normalize_whitespace(text)
    text = normalize_noisy_repetitions(text)
    text = normalize_punctuation(text)
    return text.strip()


def process_feedback_dataframe(df: pd.DataFrame, text_col: str = "original_text") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    df = df.copy()
    if text_col not in df.columns:
        raise ValueError(f"Column '{text_col}' not found in dataframe.")

    total_records = len(df)
    missing_mask = df[text_col].isna() | (df[text_col].astype(str).str.strip() == "")
    missing_count = int(missing_mask.sum())

    if "original_text" not in df.columns:
        df["original_text"] = df[text_col].fillna("").astype(str)
    else:
        df["original_text"] = df["original_text"].fillna("").astype(str)

    df["original_text"] = df["original_text"].replace("", "[No Text Provided]")

    df["cleaned_text"] = df["original_text"].apply(
        lambda t: clean_text_for_nlp(t) if t != "[No Text Provided]" else "[No Text Provided]"
    )

    valid_text_mask = df["cleaned_text"] != "[No Text Provided]"
    df["is_duplicate"] = False
    if valid_text_mask.any():
        df.loc[valid_text_mask, "is_duplicate"] = df.loc[valid_text_mask].duplicated(subset=["cleaned_text"], keep="first")
    duplicate_count = int(df["is_duplicate"].sum())

    audit_summary = {
        "total_records": total_records,
        "clean_records": total_records - missing_count - duplicate_count,
        "missing_text_count": missing_count,
        "duplicate_count": duplicate_count,
        "duplicate_rate_pct": round((duplicate_count / total_records * 100) if total_records > 0 else 0, 1),
        "data_completeness_pct": round(((total_records - missing_count) / total_records * 100) if total_records > 0 else 0, 1)
    }

    return df, audit_summary
