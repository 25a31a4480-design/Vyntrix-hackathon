"""
VYNTRIX — Voice-of-Store Intelligence Engine
Talent AP Mega Hackathon 2026, Track R5: "Turning Store Chatter Into Action"

Main Streamlit Application
"""

import os
import io
import pandas as pd
import numpy as np
from datetime import datetime

try:
    import streamlit as st
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    # Fallback message if executed directly without Streamlit
    print("Streamlit or Plotly not installed in current environment.")
    print("Please install requirements: pip install -r requirements.txt")
    print("Then run: streamlit run app.py")

from vyntrix.config import (
    ALL_CATEGORIES,
    DEPARTMENT_MAPPING,
    MANDATORY_HIGH_CATEGORIES,
    SEV_HIGH,
    SEV_MEDIUM,
    SEV_LOW,
    COLORS,
    DEMO_STORES,
    FEEDBACK_CHANNELS
)
from vyntrix.classifier import FeedbackClassifier
from vyntrix.trend_engine import TrendIntelligenceEngine
from vyntrix.report_generator import RegionalBriefGenerator
from vyntrix.data_manager import (
    validate_and_process_dataset,
    generate_sample_template_csv,
    load_demo_dataset
)


# --- Page Configuration ---
st.set_page_config(
    page_title="VYNTRIX — Voice-of-Store Intelligence Engine",
    page_icon="🏬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling: Enterprise Navy & Teal SaaS Palette ---
CUSTOM_CSS = """
<style>
    /* Global Typography & Palette */
    :root {
        --primary-dark: #0F172A;
        --secondary-dark: #1E293B;
        --teal-accent: #0D9488;
        --teal-light: #14B8A6;
        --bg-slate: #F8FAFC;
    }
    
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.1rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748B;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-sub {
        font-size: 0.82rem;
        color: #0D9488;
        margin-top: 0.3rem;
        font-weight: 500;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-high {
        background-color: #FEE2E2;
        color: #DC2626;
        border: 1px solid #FCA5A5;
    }
    .badge-med {
        background-color: #FEF3C7;
        color: #D97706;
        border: 1px solid #FCD34D;
    }
    .badge-low {
        background-color: #DCFCE7;
        color: #16A34A;
        border: 1px solid #86EFAC;
    }
    .badge-escalate {
        background-color: #7F1D1D;
        color: #FFFFFF;
        font-weight: 700;
        padding: 0.3rem 0.7rem;
        border-radius: 4px;
    }

    /* Alert Banner */
    .alert-box {
        background-color: #FFF1F2;
        border-left: 4px solid #E11D48;
        padding: 1rem;
        border-radius: 0 6px 6px 0;
        margin-bottom: 1rem;
    }

    /* Quote Box */
    .quote-box {
        background-color: #F8FAFC;
        border-left: 3px solid #0D9488;
        padding: 0.6rem 0.9rem;
        margin: 0.4rem 0;
        font-style: italic;
        color: #334155;
        font-size: 0.9rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --- Session State Initialization ---
if "classifier" not in st.session_state:
    st.session_state.classifier = FeedbackClassifier()

if "trend_engine" not in st.session_state:
    st.session_state.trend_engine = TrendIntelligenceEngine(min_evidence_threshold=3)

if "df_master" not in st.session_state:
    try:
        st.session_state.df_master = load_demo_dataset()
    except Exception as e:
        st.session_state.df_master = pd.DataFrame()


# --- Sidebar Navigation & Branding ---
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
        <span style="font-size: 1.8rem;">🏬</span>
        <div>
            <h2 style="margin: 0; font-size: 1.4rem; color: #0F172A; font-weight: 800; letter-spacing: -0.02em;">VYNTRIX</h2>
            <p style="margin: 0; font-size: 0.75rem; color: #0D9488; font-weight: 600; text-transform: uppercase;">Voice-of-Store Intelligence</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Talent AP Mega Hackathon 2026 • Track R5")
    st.markdown("---")

    nav_choice = st.radio(
        "Navigation",
        [
            "Executive Dashboard",
            "Feedback Explorer",
            "Interactive Feedback Analyzer",
            "Store-Level Trend Intelligence",
            "Weekly Regional Brief",
            "Data Import & Dataset Management"
        ],
        index=0
    )

    st.markdown("---")

    # Global Filters (Apply to Dashboard, Explorer, and Brief)
    st.markdown("### 🎯 Global Filters")
    df_raw = st.session_state.df_master

    if not df_raw.empty:
        # Stores filter
        available_stores = sorted(df_raw["store_id"].unique())
        selected_stores = st.multiselect(
            "Filter Stores",
            options=available_stores,
            default=available_stores,
            help="Select one or more retail stores to analyze."
        )

        # Channels filter
        available_channels = sorted(df_raw["channel"].unique())
        selected_channels = st.multiselect(
            "Filter Channels",
            options=available_channels,
            default=available_channels
        )

        # Severities filter
        available_severities = [SEV_HIGH, SEV_MEDIUM, SEV_LOW]
        selected_severities = st.multiselect(
            "Filter Severity",
            options=available_severities,
            default=available_severities
        )

        # Categories filter
        available_cats = sorted(df_raw["category"].unique())
        selected_cats = st.multiselect(
            "Filter Categories",
            options=available_cats,
            default=available_cats
        )

        # Apply Filters
        filtered_df = df_raw[
            (df_raw["store_id"].isin(selected_stores)) &
            (df_raw["channel"].isin(selected_channels)) &
            (df_raw["severity"].isin(selected_severities)) &
            (df_raw["category"].isin(selected_cats))
        ]
    else:
        filtered_df = pd.DataFrame()

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.75rem; color: #64748B;">
        <b>Engine Mode:</b> Transparent Rule Engine<br>
        <b>Statutory Policy:</b> Strict Escalation Active<br>
        <b>Dataset:</b> Synthetic Retail Benchmark (2026)
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 1: EXECUTIVE DASHBOARD
# ==============================================================================
if nav_choice == "Executive Dashboard":
    st.markdown('<div class="main-header">Executive Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time operational synthesis across omni-channel retail feedback</div>', unsafe_allow_html=True)

    if filtered_df.empty:
        st.warning("⚠️ No feedback records match the active global filters. Please adjust the sidebar filters.")
    else:
        # Top KPI Metrics
        total_records = len(filtered_df)
        high_sev = len(filtered_df[filtered_df["severity"] == SEV_HIGH])
        escalations = len(filtered_df[filtered_df["escalation_required"] == True])
        affected_stores = filtered_df["store_id"].nunique()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Feedback</div>
                <div class="metric-value">{total_records:,}</div>
                <div class="metric-sub">Across 4 omni-channels</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            high_pct = round((high_sev / total_records) * 100, 1) if total_records else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">High-Priority Issues</div>
                <div class="metric-value" style="color: #DC2626;">{high_sev:,}</div>
                <div class="metric-sub" style="color: #DC2626;">{high_pct}% of total volume</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Escalations Mandated</div>
                <div class="metric-value" style="color: #991B1B;">{escalations:,}</div>
                <div class="metric-sub" style="color: #991B1B;">Immediate action required</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Monitored Stores</div>
                <div class="metric-value" style="color: #0D9488;">{affected_stores}</div>
                <div class="metric-sub">Active retail locations</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts Row 1: Issue Category Distribution & Channel Distribution
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.subheader("Issue Category Distribution")
            cat_counts = filtered_df["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Feedback Count"]

            fig_cat = px.bar(
                cat_counts,
                x="Feedback Count",
                y="Category",
                orientation="h",
                color="Feedback Count",
                color_continuous_scale=["#99F6E4", "#0D9488", "#0F172A"],
                text="Feedback Count"
            )
            fig_cat.update_layout(
                yaxis=dict(autorange="reversed"),
                margin=dict(l=0, r=20, t=10, b=10),
                coloraxis_showscale=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=320
            )
            st.plotly_chart(fig_cat, use_container_width=True)

        with chart_col2:
            st.subheader("Feedback Channel Intake")
            chan_counts = filtered_df["channel"].value_counts().reset_index()
            chan_counts.columns = ["Channel", "Records"]

            fig_chan = px.pie(
                chan_counts,
                names="Channel",
                values="Records",
                hole=0.45,
                color_discrete_sequence=["#0F172A", "#0D9488", "#14B8A6", "#64748B"]
            )
            fig_chan.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=320
            )
            st.plotly_chart(fig_chan, use_container_width=True)

        # Charts Row 2: Weekly Trends
        st.subheader("Weekly Category Dynamics")
        df_ts = st.session_state.trend_engine.prepare_time_series(filtered_df)
        weekly_cats = df_ts.groupby(["year_week", "category"]).size().reset_index(name="Count")

        fig_weekly = px.bar(
            weekly_cats,
            x="year_week",
            y="Count",
            color="category",
            barmode="stack",
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_weekly.update_layout(
            xaxis_title="Calendar Week",
            yaxis_title="Record Count",
            margin=dict(l=10, r=10, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=340
        )
        st.plotly_chart(fig_weekly, use_container_width=True)

        # Top 5 Operational Issues Table
        st.subheader("Top 5 Operational Issues & Owning Departments")
        top_cats = filtered_df["category"].value_counts().head(5)
        top_rows = []
        for cat, count in top_cats.items():
            sub = filtered_df[filtered_df["category"] == cat]
            h_count = len(sub[sub["severity"] == SEV_HIGH])
            top_rows.append({
                "Rank": len(top_rows) + 1,
                "Issue Category": cat,
                "Owning Department": DEPARTMENT_MAPPING.get(cat, "Manual Review"),
                "Total Count": count,
                "High Severity": h_count,
                "% High Severity": f"{round(h_count/count*100, 1)}%",
                "Statutory Mandate": "⚠️ Mandatory Escalation" if cat in MANDATORY_HIGH_CATEGORIES else "Standard SLA"
            })
        st.dataframe(pd.DataFrame(top_rows), use_container_width=True, hide_index=True)

        # Critical Alerts Section
        st.subheader("🚨 Critical Incidents Awaiting Escalation (Recent Sample)")
        crit_sample = filtered_df[filtered_df["escalation_required"] == True].head(5)
        if crit_sample.empty:
            st.info("No critical escalations in current filtered selection.")
        else:
            for _, row in crit_sample.iterrows():
                st.markdown(f"""
                <div class="alert-box">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <b>[{row['category'].upper()}] — Store {row['store_id']} ({row['date']})</b>
                        <span class="badge badge-escalate">ESCALATION REQUIRED</span>
                    </div>
                    <p style="margin: 0.4rem 0 0.2rem 0; color: #0F172A;">"{row['original_text']}"</p>
                    <div style="font-size: 0.8rem; color: #64748B;">
                        <b>Department:</b> {row['department']} &nbsp;|&nbsp; <b>Channel:</b> {row['channel']}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 2: FEEDBACK EXPLORER
# ==============================================================================
elif nav_choice == "Feedback Explorer":
    st.markdown('<div class="main-header">Feedback Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Search, inspect, and audit customer feedback supporting classification decisions</div>', unsafe_allow_html=True)

    if filtered_df.empty:
        st.warning("No records match the current filters.")
    else:
        # Search Box
        search_query = st.text_input("🔍 Search within original customer text (e.g., 'expired', 'peanut', 'cashier', 'slip')", "")

        view_df = filtered_df.copy()
        if search_query.strip():
            view_df = view_df[view_df["original_text"].str.contains(search_query, case=False, na=False)]

        st.markdown(f"**Showing {len(view_df)} of {len(filtered_df)} filtered feedback records**")

        # Table Display
        display_cols = [
            "feedback_id", "original_text", "store_id", "date",
            "channel", "category", "severity", "department", "escalation_required"
        ]
        st.dataframe(
            view_df[display_cols],
            column_config={
                "original_text": st.column_config.TextColumn("Customer Feedback Text", width="large"),
                "store_id": st.column_config.TextColumn("Store", width="small"),
                "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "severity": st.column_config.TextColumn("Severity"),
                "escalation_required": st.column_config.CheckboxColumn("Escalation?"),
            },
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.subheader("🔍 Deep-Dive Record Inspector")
        record_ids = view_df["feedback_id"].tolist()
        if record_ids:
            selected_id = st.selectbox("Select a Record to Inspect Full Audit Trail:", options=record_ids)
            rec = view_df[view_df["feedback_id"] == selected_id].iloc[0]

            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"**Feedback ID:** `{rec['feedback_id']}`")
                st.markdown(f"**Store Location:** `{rec['store_id']}` ({DEMO_STORES.get(rec['store_id'], 'Regional Branch')})")
                st.markdown(f"**Submission Date:** `{rec['date']}` | **Channel:** `{rec['channel']}`")
                st.markdown("**Original Customer Voice:**")
                st.markdown(f'<div class="quote-box">"{rec["original_text"]}"</div>', unsafe_allow_html=True)

            with col2:
                st.markdown(f"**Assigned Category:** `{rec['category']}`")
                st.markdown(f"**Severity Tier:** `{rec['severity']}`")
                st.markdown(f"**Owning Department:** `{rec['department']}`")
                st.markdown(f"**Escalation Decision:** `{'YES - MANDATORY ESCALATION' if rec['escalation_required'] else 'NO - STANDARD'}`")
                if "classification_explanation" in rec and pd.notna(rec["classification_explanation"]):
                    st.info(f"**Audit Rationale:** {rec['classification_explanation']}")
                if "recommended_action" in rec and pd.notna(rec["recommended_action"]):
                    st.success(f"**Tactical Action:** {rec['recommended_action']}")


# ==============================================================================
# PAGE 3: INTERACTIVE FEEDBACK ANALYZER
# ==============================================================================
elif nav_choice == "Interactive Feedback Analyzer":
    st.markdown('<div class="main-header">Interactive Feedback Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Simulate live ingestion: enter unstructured store chatter and run automated classification</div>', unsafe_allow_html=True)

    st.markdown("##### Quick Test Presets:")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        if st.button("🥜 Allergen Violation"):
            st.session_state.analyzer_input = "Bakery cookies contain undeclared peanuts, my child with nut allergy had severe hives! 🥜"
    with col_p2:
        if st.button("⚠️ Physical Safety Hazard"):
            st.session_state.analyzer_input = "Spilled cooking oil in aisle 4 near condiments, customer almost slipped. Severe hazard! ⚠️"
    with col_p3:
        if st.button("🐀 Hygiene Pest Sighting"):
            st.session_state.analyzer_input = "Saw a live rat scurrying under the bakery display counter!! Disgusting health code violation 🐀"
    with col_p4:
        if st.button("⏱️ Long Checkout Queue"):
            st.session_state.analyzer_input = "Waited 40 mins in line with only 1 register open on Saturday afternoon rush! 😡"

    col_p5, col_p6, col_p7, col_p8 = st.columns(4)
    with col_p5:
        if st.button("🥛 Product Quality (Expired)"):
            st.session_state.analyzer_input = "Bought milk that expired 4 days ago, smelled completely sour and curdled milkkkk! 🤢"
    with col_p6:
        if st.button("📦 Stock Availability (Empty)"):
            st.session_state.analyzer_input = "Shelves completely empty in dairy section, no 2% milk or butter for 3 days in a row"
    with col_p7:
        if st.button("😠 Rude Staff Conduct"):
            st.session_state.analyzer_input = "Cashier was extremely rude, rolled her eyes and threw my change on the counter"
    with col_p8:
        if st.button("🛒 Routine Minor Feedback"):
            st.session_state.analyzer_input = "Shopping cart wheels are squeaking and slightly hard to push around"

    default_text = st.session_state.get(
        "analyzer_input",
        "Spilled cooking oil in aisle 4 near condiments, customer almost slipped. Severe hazard! ⚠️"
    )

    user_text = st.text_area(
        "Enter Raw Customer Feedback, Shift Note, or Support Transcript:",
        value=default_text,
        height=110,
        placeholder="Type customer comments, employee shift notes, or app reviews here..."
    )

    if st.button("⚡ Run Operational Analysis", type="primary"):
        if not user_text.strip():
            st.warning("Please enter feedback text to analyze.")
        else:
            classifier = st.session_state.classifier
            result = classifier.classify_text(user_text)

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Analysis Results & Routing Intelligence")

            # Badges Row
            res_col1, res_col2, res_col3, res_col4 = st.columns(4)
            with res_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Predicted Category</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #0F172A;">{result['category']}</div>
                </div>
                """, unsafe_allow_html=True)

            with res_col2:
                sev_color = "#DC2626" if result['severity'] == "High" else ("#D97706" if result['severity'] == "Medium" else "#16A34A")
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Severity Level</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: {sev_color};">{result['severity']}</div>
                </div>
                """, unsafe_allow_html=True)

            with res_col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Responsible Department</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #0D9488;">{result['department']}</div>
                </div>
                """, unsafe_allow_html=True)

            with res_col4:
                esc_status = "YES — ESCALATE" if result['escalation_required'] else "NO — STANDARD"
                esc_color = "#991B1B" if result['escalation_required'] else "#16A34A"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Escalation Required?</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: {esc_color};">{esc_status}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Details
            col_info1, col_info2 = st.columns([1, 1])
            with col_info1:
                st.markdown("##### 📋 Classification Explanation & Cues")
                st.info(result['explanation'])

                st.markdown("##### 🔍 Detected Evidence Tokens")
                if result['evidence_snippets']:
                    st.write(", ".join([f"`{tok}`" for tok in result['evidence_snippets']]))
                else:
                    st.write("None (Classified via contextual fallback)")

                st.caption(f"Engine Architecture: {result['model_type']}")

            with col_info2:
                st.markdown("##### 🚀 Recommended Operational Action")
                st.success(result['recommended_action'])

                st.markdown("##### 📝 Verbatim Input Evidence")
                st.markdown(f'<div class="quote-box">"{user_text}"</div>', unsafe_allow_html=True)


# ==============================================================================
# PAGE 4: STORE-LEVEL TREND INTELLIGENCE
# ==============================================================================
elif nav_choice == "Store-Level Trend Intelligence":
    st.markdown('<div class="main-header">Store-Level Trend Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Detect localized operational spikes using store-normalized rates and historical baselines</div>', unsafe_allow_html=True)

    if st.session_state.df_master.empty:
        st.warning("No data available.")
    else:
        trend_engine = st.session_state.trend_engine
        df_ts = trend_engine.prepare_time_series(st.session_state.df_master)
        all_weeks = sorted(df_ts["year_week"].unique())

        # Parameters
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
        with col_ctrl1:
            target_week = st.selectbox("Select Target Evaluation Week:", options=all_weeks, index=len(all_weeks) - 1)
        with col_ctrl2:
            min_thresh = st.slider("Minimum Evidence Threshold (Records):", min_value=1, max_value=10, value=3)
        with col_ctrl3:
            multiplier = st.slider("Spike Threshold Multiplier:", min_value=1.1, max_value=3.0, value=1.5, step=0.1)

        # Run Trend Engine
        trend_engine.min_evidence_threshold = min_thresh
        trend_engine.spike_multiplier = multiplier
        alerts = trend_engine.detect_emerging_issues(st.session_state.df_master, recent_week=target_week)

        flagged_alerts = [a for a in alerts if a.get("is_alert", False)]
        insufficient_stores = [a for a in alerts if a.get("status") == "INSUFFICIENT_BASELINE_DATA"]

        # Alert Summary Cards
        st.markdown("<br>", unsafe_allow_html=True)
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Flagged Emerging Spikes", len(flagged_alerts))
        with col_m2:
            st.metric("Stores Evaluated", len(df_ts["store_id"].unique()))
        with col_m3:
            st.metric("Stores with Insufficient History", len(insufficient_stores))

        st.markdown("<br>", unsafe_allow_html=True)

        # Emerging Outlier Alerts
        st.subheader("🚩 Emerging Outlier Spikes Requiring Investigation")
        if not flagged_alerts:
            st.info("No emerging operational spikes exceeded the baseline and minimum evidence threshold for this week.")
        else:
            for alert in flagged_alerts:
                s_id = alert["store_id"]
                cat = alert["category"]
                lvl = alert["alert_level"]
                exp = alert["explanation"]
                quotes = alert.get("quotes", [])

                st.markdown(f"""
                <div class="alert-box">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <b style="font-size: 1.1rem; color: #0F172A;">Store {s_id} ({DEMO_STORES.get(s_id, 'Location')}) — {cat}</b>
                        <span class="badge badge-high">{lvl.upper()} SPIKE</span>
                    </div>
                    <p style="margin: 0.5rem 0 0.3rem 0; font-size: 0.95rem; color: #1E293B;"><b>Diagnosis:</b> {exp}</p>
                    <div style="font-size: 0.85rem; color: #475569;">
                        <b>Recent Week Rate:</b> {alert['recent_rate_pct']}% ({alert['recent_count']} records) &nbsp;|&nbsp;
                        <b>Baseline Rate:</b> {alert['baseline_rate_pct']}% &nbsp;|&nbsp;
                        <b>WoW Change:</b> {alert['wow_change_pp']:+.1f} pp
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if quotes:
                    with st.expander(f"View Supporting Customer Quotes for Store {s_id} ({cat})"):
                        for q in quotes:
                            st.markdown(f'<div class="quote-box">"{q}"</div>', unsafe_allow_html=True)

        # Insufficient Baseline Data Notice (Requirement 9)
        if insufficient_stores:
            st.markdown("---")
            st.subheader("ℹ️ Stores with Insufficient Baseline Data (Monitoring Only)")
            st.caption("To prevent false alarms, stores with less than 2 distinct historical baseline weeks are not flagged for statistical spikes.")
            for inst in insufficient_stores:
                st.warning(f"**Store {inst['store_id']}:** {inst['explanation']}")

        # Full Store-Category Baseline Comparison Table
        st.markdown("---")
        st.subheader("📊 Full Store-Category Normalized Baseline Table")
        table_rows = []
        for a in alerts:
            if a.get("status") != "INSUFFICIENT_BASELINE_DATA":
                table_rows.append({
                    "Store": a["store_id"],
                    "Category": a["category"],
                    "Recent Rate (%)": f"{a['recent_rate_pct']}%",
                    "Baseline Rate (%)": f"{a['baseline_rate_pct']}%",
                    "Delta (pp)": f"{a.get('base_delta_pp', 0.0):+.1f}",
                    "WoW (pp)": f"{a.get('wow_change_pp', 0.0):+.1f}",
                    "Recent Count": a["recent_count"],
                    "Status": a["status"]
                })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)


# ==============================================================================
# PAGE 5: WEEKLY REGIONAL BRIEF
# ==============================================================================
elif nav_choice == "Weekly Regional Brief":
    st.markdown('<div class="main-header">Weekly Regional Brief</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Autonomously generate evidence-backed regional briefing reports for executive review</div>', unsafe_allow_html=True)

    if filtered_df.empty:
        st.warning("No records selected. Please clear filters to generate brief.")
    else:
        region_title = st.text_input("Regional Territory / Division Title:", "Northern Regional Retail Operations")

        trend_alerts = st.session_state.trend_engine.detect_emerging_issues(filtered_df)

        # Generate Reports
        md_content = RegionalBriefGenerator.generate_markdown(filtered_df, trend_alerts, region_title)
        csv_content = RegionalBriefGenerator.generate_csv(filtered_df)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="📥 Download Regional Brief (Markdown .md)",
                data=md_content,
                file_name=f"VYNTRIX_Regional_Brief_{datetime.utcnow().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                type="primary",
                use_container_width=True
            )
        with col_d2:
            st.download_button(
                label="📥 Download Regional Summary (CSV)",
                data=csv_content,
                file_name=f"VYNTRIX_Regional_Summary_{datetime.utcnow().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Render Markdown Document in UI
        st.markdown("### Document Preview:")
        st.markdown(md_content)


# ==============================================================================
# PAGE 6: DATA IMPORT & DATASET MANAGEMENT
# ==============================================================================
elif nav_choice == "Data Import & Dataset Management":
    st.markdown('<div class="main-header">Data Import & Dataset Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload custom store chatter CSVs, validate schemas, and audit data hygiene</div>', unsafe_allow_html=True)

    col_u1, col_u2 = st.columns([2, 1])

    with col_u1:
        uploaded_file = st.file_uploader(
            "Upload Retail Feedback CSV:",
            type=["csv"],
            help="Upload custom customer feedback, shift notes, or support transcripts."
        )

        if uploaded_file is not None:
            st.info("File uploaded. Parsing and applying column alias mapping...")
            df_new, audit_new, msgs_new = validate_and_process_dataset(
                uploaded_file, classifier=st.session_state.classifier
            )

            if df_new.empty:
                st.error("Upload Failed:")
                for m in msgs_new:
                    st.write(f"- {m}")
            else:
                st.success(f"Successfully processed {len(df_new)} records!")
                st.session_state.df_master = df_new

                st.subheader("Data Validation & Quality Audit:")
                for m in msgs_new:
                    st.write(f"• {m}")

                st.markdown("##### Preview of Processed Dataset:")
                st.dataframe(df_new.head(5), use_container_width=True, hide_index=True)

    with col_u2:
        st.markdown("##### Dataset Actions:")

        template_csv = generate_sample_template_csv()
        st.download_button(
            label="📄 Download Sample CSV Template",
            data=template_csv,
            file_name="vyntrix_upload_template.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔄 Reset to Benchmark Demonstration Dataset", use_container_width=True):
            st.session_state.df_master = load_demo_dataset()
            st.success("Master dataset reset to default 265-record synthetic benchmark!")
            st.experimental_rerun() if hasattr(st, "experimental_rerun") else st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; border-radius: 6px; font-size: 0.85rem;">
            <b>Recognized Column Aliases:</b><br>
            • <b>Text:</b> <code>original_text</code>, <code>comment</code>, <code>review</code>, <code>text</code><br>
            • <b>Store:</b> <code>store_id</code>, <code>store</code>, <code>location</code><br>
            • <b>Date:</b> <code>date</code>, <code>timestamp</code>, <code>created_at</code><br>
            • <b>Channel:</b> <code>channel</code>, <code>source</code>
        </div>
        """, unsafe_allow_html=True)
