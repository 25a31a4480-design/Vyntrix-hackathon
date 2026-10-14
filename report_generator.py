"""
VYNTRIX Weekly Regional Brief Generator
Produces evidence-backed operational reports in Markdown and CSV formats.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime
from vyntrix.config import (
    DEPARTMENT_MAPPING,
    SEV_HIGH,
    SEV_MEDIUM,
    SEV_LOW,
    MANDATORY_HIGH_CATEGORIES,
)


class RegionalBriefGenerator:
    @staticmethod
    def generate_markdown(
        df: pd.DataFrame,
        trend_alerts: Optional[List[Dict[str, Any]]] = None,
        region_title: str = "Northern Regional Retail Operations"
    ) -> str:
        if df.empty:
            return "# VYNTRIX Weekly Regional Brief\n\n*No feedback records found in current selection.*"

        total_records = len(df)
        high_sev_count = len(df[df["severity"] == SEV_HIGH])
        escalations_count = len(df[df["escalation_required"] == True])
        unique_stores = sorted(df["store_id"].unique())
        stores_count = len(unique_stores)

        min_date = str(df["date"].min())[:10]
        max_date = str(df["date"].max())[:10]
        generated_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        cat_counts = df["category"].value_counts()
        top_5_cats = cat_counts.head(5).index.tolist()

        md = []
        md.append(f"# VYNTRIX Voice-of-Store Weekly Regional Brief")
        md.append(f"**Region / Division:** {region_title}  ")
        md.append(f"**Reporting Period:** {min_date} to {max_date}  ")
        md.append(f"**Generated At:** {generated_timestamp}  ")
        md.append(f"**Classification Architecture:** Rule-Driven Operational Engine with Statutory Escalation  ")
        md.append("\n---\n")

        md.append("## 1. Executive Summary Metrics\n")
        md.append("| Metric | Value | Operational Note |")
        md.append("| :--- | :--- | :--- |")
        md.append(f"| **Total Processed Feedback** | {total_records:,} | Aggregated across omni-channel intake |")
        md.append(f"| **Critical High-Severity Issues** | {high_sev_count} ({round(high_sev_count/total_records*100, 1) if total_records else 0}%) | Immediate operational attention |")
        md.append(f"| **Escalations Mandated** | {escalations_count} | Routed to Department Incident Leads |")
        md.append(f"| **Active Stores Monitored** | {stores_count} | Stores: {', '.join(unique_stores)} |")
        md.append("\n")

        md.append("## 2. Emerging Store-Level Outlier Alerts\n")
        spike_alerts = [a for a in (trend_alerts or []) if a.get("is_alert", False)]
        if spike_alerts:
            md.append("The following store-level operational spikes exceeded historical baseline and evidence thresholds:\n")
            for alert in spike_alerts:
                s_id = alert["store_id"]
                cat = alert["category"]
                lvl = alert["alert_level"]
                exp = alert["explanation"]
                md.append(f"- **[{lvl.upper()}] Store {s_id} — {cat}**")
                md.append(f"  - *Diagnosis:* {exp}")
                if alert.get("quotes"):
                    md.append(f"  - *Evidence Quote:* \"{alert['quotes'][0]}\"")
            md.append("\n")
        else:
            md.append("No statistical emerging spikes exceeding minimum evidence thresholds detected for the target period.\n\n")

        md.append("## 3. Top 5 Regional Issues Deep-Dive\n")

        for rank, cat in enumerate(top_5_cats, start=1):
            sub_df = df[df["category"] == cat]
            cat_count = len(sub_df)
            cat_pct = round((cat_count / total_records) * 100, 1)
            dept = DEPARTMENT_MAPPING.get(cat, "Operations")

            h_cnt = len(sub_df[sub_df["severity"] == SEV_HIGH])
            m_cnt = len(sub_df[sub_df["severity"] == SEV_MEDIUM])
            l_cnt = len(sub_df[sub_df["severity"] == SEV_LOW])

            store_dist = sub_df["store_id"].value_counts()
            store_str = ", ".join([f"{s} ({c})" for s, c in store_dist.items()])

            sample_quotes = sub_df["original_text"].dropna().head(3).tolist()
            rec_action = sub_df["recommended_action"].iloc[0] if "recommended_action" in sub_df.columns else "Review and remediate."

            md.append(f"### Rank {rank}: {cat} ({cat_count} records, {cat_pct}% of total)")
            md.append(f"- **Responsible Department:** `{dept}`")
            md.append(f"- **Severity Distribution:** High: {h_cnt} | Medium: {m_cnt} | Low: {l_cnt}")
            md.append(f"- **Affected Stores Breakdown:** {store_str}")
            md.append(f"- **Statutory Escalation Policy:** {'MANDATORY HIGH (Legal/Safety)' if cat in MANDATORY_HIGH_CATEGORIES else 'Standard SLA'}")
            md.append("\n**Customer Evidence Quotes:**")
            for q in sample_quotes:
                cleaned_q = str(q).replace("\n", " ").strip()
                md.append(f"> \"{cleaned_q}\"")
            md.append("\n**Recommended Operational Next Steps:**")
            md.append(f"{rec_action}\n")

        md.append("## 4. Prioritized Regional Action Plan\n")
        md.append("1. **Immediate (Next 4 Hours):** Dispatch regional safety audit to all stores flagged with Safety, Hygiene, or Allergen escalations.")
        md.append("2. **Short-Term (Next 24 Hours):** Regional Inventory Planner to adjust replenishment schedules for chronic Stock Availability out-of-stock items.")
        md.append("3. **Medium-Term (End of Week):** Store Operations to review peak-hour cashier scheduling and self-checkout terminal maintenance.")
        md.append("\n---\n*Report compiled autonomously by VYNTRIX Voice-of-Store Intelligence Engine.*")

        return "\n".join(md)

    @staticmethod
    def generate_csv(df: pd.DataFrame) -> str:
        if df.empty:
            return "category,total_records,percentage,high_severity,medium_severity,low_severity,department\n"

        total_records = len(df)
        cat_group = df.groupby("category")

        rows = []
        for cat, group in cat_group:
            total_cat = len(group)
            pct = round((total_cat / total_records) * 100, 2)
            high_sev = len(group[group["severity"] == SEV_HIGH])
            med_sev = len(group[group["severity"] == SEV_MEDIUM])
            low_sev = len(group[group["severity"] == SEV_LOW])
            dept = DEPARTMENT_MAPPING.get(cat, "Manual Review")
            affected_stores = ";".join(group["store_id"].unique())
            sample_quote = group["original_text"].iloc[0].replace('"', '""').replace("\n", " ") if not group.empty else ""

            rows.append({
                "category": cat,
                "total_records": total_cat,
                "percentage_of_total": pct,
                "high_severity_count": high_sev,
                "medium_severity_count": med_sev,
                "low_severity_count": low_sev,
                "owning_department": dept,
                "affected_stores": affected_stores,
                "primary_evidence_quote": f'"{sample_quote}"'
            })

        out_df = pd.DataFrame(rows).sort_values(by="total_records", ascending=False)
        return out_df.to_csv(index=False)
