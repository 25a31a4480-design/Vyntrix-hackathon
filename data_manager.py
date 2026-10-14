"""
VYNTRIX Data Management, Ingestion, and Validation Module
Handles dataset ingestion, flexible column alias mapping, data quality audits,
and synthetic baseline generation.
"""

from typing import Dict, Any, List, Tuple, Optional
import os
import io
import pandas as pd
from datetime import datetime
from vyntrix.config import (
    CANONICAL_COLUMNS,
    COLUMN_ALIASES,
    DEMO_STORES,
    FEEDBACK_CHANNELS,
    CAT_OTHER
)
from vyntrix.text_cleaner import process_feedback_dataframe
from vyntrix.classifier import FeedbackClassifier

CANDIDATE_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "data", "vyntrix_demo_feedback.csv"),
    os.path.join(os.getcwd(), "data", "vyntrix_demo_feedback.csv"),
    "/working_dir/c_d78fc9c61280cfe4/data/vyntrix_demo_feedback.csv"
]


def map_column_aliases(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    df = df.copy()
    col_mapping = {}
    lower_cols = {str(c).strip().lower(): c for c in df.columns}

    for canonical, aliases in COLUMN_ALIASES.items():
        matched_actual = None
        for alias in aliases:
            if alias.lower() in lower_cols:
                matched_actual = lower_cols[alias.lower()]
                break
        if matched_actual:
            col_mapping[matched_actual] = canonical

    df = df.rename(columns=col_mapping)
    return df, col_mapping


def generate_sample_template_csv() -> str:
    sample_rows = [
        {
            "feedback_id": "VYN-SAMPLE-001",
            "original_text": "Spilled cooking oil in aisle 4 near condiments, customer almost slipped. Severe hazard! ⚠️",
            "store_id": "STR-101",
            "date": "2026-02-15",
            "channel": "In-App Feedback"
        },
        {
            "feedback_id": "VYN-SAMPLE-002",
            "original_text": "Waited over 35 minutes in checkout line with only 1 register open on a busy Saturday.",
            "store_id": "STR-102",
            "date": "2026-02-15",
            "channel": "Google Review"
        },
        {
            "feedback_id": "VYN-SAMPLE-003",
            "original_text": "Bakery cookies contain undeclared peanuts, my child with nut allergy had a severe reaction! 🥜",
            "store_id": "STR-103",
            "date": "2026-02-16",
            "channel": "Customer Support Transcript"
        },
        {
            "feedback_id": "VYN-SAMPLE-004",
            "original_text": "Shelves completely empty in dairy section, no 2% milk or unsalted butter for 3 days.",
            "store_id": "STR-101",
            "date": "2026-02-16",
            "channel": "Store Shift Notes"
        }
    ]
    df_sample = pd.DataFrame(sample_rows)
    return df_sample.to_csv(index=False)


def validate_and_process_dataset(
    source: Any,
    classifier: Optional[FeedbackClassifier] = None
) -> Tuple[pd.DataFrame, Dict[str, Any], List[str]]:
    messages = []

    if isinstance(source, pd.DataFrame):
        df = source.copy()
    elif isinstance(source, (str, bytes, io.StringIO, io.BytesIO)):
        try:
            df = pd.read_csv(source)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(), {}, ["Validation Error: Uploaded CSV file is empty or contains no records."]
        except Exception as e:
            return pd.DataFrame(), {}, [f"Fatal Error: Failed to parse CSV file: {str(e)}"]
    else:
        return pd.DataFrame(), {}, ["Fatal Error: Unsupported input type for dataset processing."]

    if df.empty:
        return pd.DataFrame(), {}, ["Validation Error: Uploaded CSV file is empty or contains no records."]

    df, col_mapping = map_column_aliases(df)
    messages.append(f"Mapped {len(col_mapping)} recognized column(s): {', '.join([f'{k} -> {v}' for k, v in col_mapping.items()])}")

    if "original_text" not in df.columns:
        return pd.DataFrame(), {}, [
            "Validation Error: Missing feedback text column! CSV must contain a text column "
            "(e.g., 'original_text', 'feedback_text', 'text', 'comment', or 'review')."
        ]

    if "feedback_id" not in df.columns:
        df["feedback_id"] = [f"VYN-GEN-{i+1:05d}" for i in range(len(df))]
        messages.append("Notice: 'feedback_id' was missing; auto-generated sequential IDs.")

    if "store_id" not in df.columns:
        df["store_id"] = "STR-UNKNOWN"
        messages.append("Warning: 'store_id' was missing; assigned default 'STR-UNKNOWN'.")
    else:
        df["store_id"] = df["store_id"].fillna("STR-UNKNOWN").astype(str).str.strip()

    if "date" not in df.columns:
        df["date"] = datetime.utcnow().strftime("%Y-%m-%d")
        messages.append("Warning: 'date' column missing; defaulted to current UTC date.")
    else:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
        invalid_dates = df["date"].isna().sum()
        if invalid_dates > 0:
            df["date"] = df["date"].fillna(datetime.utcnow().strftime("%Y-%m-%d"))
            messages.append(f"Warning: Replaced {invalid_dates} invalid or unparseable date(s) with default current date.")

    if "channel" not in df.columns:
        df["channel"] = "In-App Feedback"
        messages.append("Notice: 'channel' missing; defaulted to 'In-App Feedback'.")
    else:
        df["channel"] = df["channel"].fillna("In-App Feedback").astype(str).str.strip()

    df, audit_summary = process_feedback_dataframe(df, text_col="original_text")
    if audit_summary["missing_text_count"] > 0:
        messages.append(f"Data Quality: Flagged {audit_summary['missing_text_count']} record(s) with blank/missing text.")
    if audit_summary["duplicate_count"] > 0:
        messages.append(f"Data Quality: Identified {audit_summary['duplicate_count']} exact duplicate record(s).")

    if classifier is None:
        classifier = FeedbackClassifier()

    needs_classification = ("category" not in df.columns) or ("severity" not in df.columns) or ("department" not in df.columns)

    if needs_classification:
        df = classifier.batch_classify(df, text_col="cleaned_text")
        messages.append("Automated Classification: All records routed through VYNTRIX Rule & Statutory Escalation Engine.")
    else:
        if "category" not in df.columns:
            df["category"] = CAT_OTHER
        if "severity" not in df.columns:
            df["severity"] = "Low"
        if "department" not in df.columns:
            df["department"] = "Manual Review"
        if "escalation_required" not in df.columns:
            df["escalation_required"] = False
        if "recommended_action" not in df.columns:
            df["recommended_action"] = "Review feedback in store queue."

    audit_summary["messages"] = messages
    return df, audit_summary, messages


def load_demo_dataset() -> pd.DataFrame:
    for path in CANDIDATE_PATHS:
        if os.path.exists(path):
            return pd.read_csv(path)
    raise FileNotFoundError(f"Demonstration dataset not found in any expected location: {CANDIDATE_PATHS}")
