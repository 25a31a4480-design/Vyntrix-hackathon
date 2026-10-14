"""
VYNTRIX Store-Level Trend Intelligence Engine
Computes store-normalized rates, baseline deviations, WoW trajectories,
evidence thresholds, and audit explanations.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class TrendIntelligenceEngine:
    def __init__(self, min_evidence_threshold: int = 3, spike_multiplier: float = 1.5, min_pp_delta: float = 5.0):
        self.min_evidence_threshold = min_evidence_threshold
        self.spike_multiplier = spike_multiplier
        self.min_pp_delta = min_pp_delta

    def prepare_time_series(self, df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
        df = df.copy()
        df["datetime"] = pd.to_datetime(df[date_col], errors="coerce")
        df["datetime"] = df["datetime"].fillna(pd.Timestamp("2026-01-01"))
        iso_cal = df["datetime"].dt.isocalendar()
        df["year_week"] = iso_cal["year"].astype(str) + "-W" + iso_cal["week"].astype(str).str.zfill(2)
        df["week_start"] = df["datetime"].dt.to_period("W").dt.start_time
        return df

    def compute_store_weekly_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        if "year_week" not in df.columns:
            df = self.prepare_time_series(df)

        store_week_totals = df.groupby(["store_id", "year_week"]).size().reset_index(name="store_week_total")
        cat_counts = df.groupby(["store_id", "year_week", "category"]).size().reset_index(name="issue_count")

        rates_df = pd.merge(cat_counts, store_week_totals, on=["store_id", "year_week"], how="left")
        rates_df["rate_pct"] = (rates_df["issue_count"] / rates_df["store_week_total"]) * 100.0
        rates_df["rate_pct"] = rates_df["rate_pct"].round(2)

        return rates_df

    def detect_emerging_issues(
        self,
        df: pd.DataFrame,
        recent_week: Optional[str] = None,
        min_evidence: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if min_evidence is None:
            min_evidence = self.min_evidence_threshold

        df_ts = self.prepare_time_series(df)
        all_weeks = sorted(df_ts["year_week"].unique())

        if len(all_weeks) < 2:
            return [{
                "store_id": "ALL",
                "category": "All Categories",
                "status": "INSUFFICIENT_GLOBAL_HISTORY",
                "alert_level": "Info",
                "is_alert": False,
                "explanation": "Dataset contains less than 2 distinct weeks of records. A minimum of 2 weeks is required to establish baseline.",
                "recent_count": len(df_ts),
                "recent_rate_pct": 0.0,
                "baseline_rate_pct": 0.0,
                "wow_change_pp": 0.0,
                "quotes": []
            }]

        if recent_week is None or recent_week not in all_weeks:
            recent_week = all_weeks[-1]

        recent_idx = all_weeks.index(recent_week)
        if recent_idx == 0:
            prev_week = None
            baseline_weeks = []
        else:
            prev_week = all_weeks[recent_idx - 1]
            baseline_weeks = all_weeks[:recent_idx]

        alerts = []
        unique_stores = sorted(df_ts["store_id"].unique())

        for store in unique_stores:
            store_df = df_ts[df_ts["store_id"] == store]
            store_weeks = sorted(store_df["year_week"].unique())
            store_baseline_weeks = [w for w in baseline_weeks if w in store_weeks]

            if len(store_baseline_weeks) < 2:
                recent_store_records = store_df[store_df["year_week"] == recent_week]
                alerts.append({
                    "store_id": store,
                    "category": "All Issues",
                    "status": "INSUFFICIENT_BASELINE_DATA",
                    "alert_level": "Neutral",
                    "is_alert": False,
                    "explanation": (
                        f"Store {store} has only {len(store_baseline_weeks)} historical baseline week(s) "
                        f"before {recent_week}. At least 2 baseline weeks are required to prevent false alarms."
                    ),
                    "recent_count": len(recent_store_records),
                    "recent_rate_pct": 0.0,
                    "baseline_rate_pct": 0.0,
                    "wow_change_pp": 0.0,
                    "quotes": []
                })
                continue

            base_slice = df_ts[(df_ts["store_id"] == store) & (df_ts["year_week"].isin(store_baseline_weeks))]
            base_total = len(base_slice)

            rec_slice = df_ts[(df_ts["store_id"] == store) & (df_ts["year_week"] == recent_week)]
            rec_total = len(rec_slice)

            if rec_total == 0:
                continue

            prev_slice = df_ts[(df_ts["store_id"] == store) & (df_ts["year_week"] == prev_week)] if prev_week else pd.DataFrame()
            prev_total = len(prev_slice)

            store_categories = df_ts["category"].unique()
            for cat in store_categories:
                rec_cat_count = len(rec_slice[rec_slice["category"] == cat])
                rec_rate = (rec_cat_count / rec_total * 100.0) if rec_total > 0 else 0.0

                base_cat_count = len(base_slice[base_slice["category"] == cat])
                base_rate = (base_cat_count / base_total * 100.0) if base_total > 0 else 0.0

                prev_cat_count = len(prev_slice[prev_slice["category"] == cat]) if prev_total > 0 else 0
                prev_rate = (prev_cat_count / prev_total * 100.0) if prev_total > 0 else 0.0

                wow_pp = round(rec_rate - prev_rate, 2)
                base_delta_pp = round(rec_rate - base_rate, 2)

                quotes = (
                    rec_slice[rec_slice["category"] == cat]["original_text"]
                    .dropna()
                    .head(3)
                    .tolist()
                )

                is_alert = False
                status = "STABLE"
                alert_level = "Normal"

                if rec_cat_count < min_evidence:
                    status = "BELOW_EVIDENCE_THRESHOLD"
                    explanation = (
                        f"Store {store}: '{cat}' recorded {rec_cat_count} occurrence(s) in {recent_week}. "
                        f"Evidence is below the minimum threshold ({min_evidence}) — alert suppressed."
                    )
                else:
                    rate_ratio = (rec_rate / base_rate) if base_rate > 0 else (99.0 if rec_rate > 0 else 1.0)

                    if (base_rate == 0 and rec_cat_count >= min_evidence) or (
                        rate_ratio >= self.spike_multiplier and base_delta_pp >= self.min_pp_delta
                    ):
                        is_alert = True
                        status = "EMERGING_SPIKE"
                        alert_level = "Critical" if base_delta_pp >= 15.0 or rate_ratio >= 2.5 else "Warning"
                        explanation = (
                            f"Emerging Issue Flagged: '{cat}' at store {store} rose to {rec_rate:.1f}% "
                            f"({rec_cat_count}/{rec_total} feedback items) in {recent_week} vs historical "
                            f"baseline of {base_rate:.1f}% (+{base_delta_pp:+.1f} pp, {rate_ratio:.1f}x baseline). "
                            f"Meets evidence threshold ({rec_cat_count} >= {min_evidence}). "
                            f"WoW change: {wow_pp:+.1f} pp."
                        )
                    elif base_delta_pp < -5.0:
                        status = "IMPROVING"
                        alert_level = "Positive"
                        explanation = (
                            f"Positive Trend: '{cat}' at store {store} decreased to {rec_rate:.1f}% "
                            f"vs baseline {base_rate:.1f}% ({base_delta_pp:+.1f} pp)."
                        )
                    else:
                        status = "CONTROLLED_VARIATION"
                        alert_level = "Normal"
                        explanation = (
                            f"Normal Variation: '{cat}' at store {store} is at {rec_rate:.1f}% "
                            f"(baseline: {base_rate:.1f}%, delta: {base_delta_pp:+.1f} pp)."
                        )

                alerts.append({
                    "store_id": store,
                    "category": cat,
                    "status": status,
                    "alert_level": alert_level,
                    "is_alert": is_alert,
                    "explanation": explanation,
                    "recent_count": rec_cat_count,
                    "recent_rate_pct": round(rec_rate, 2),
                    "baseline_rate_pct": round(base_rate, 2),
                    "base_delta_pp": base_delta_pp,
                    "wow_change_pp": wow_pp,
                    "quotes": quotes
                })

        return alerts
