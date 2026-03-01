from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
PREDICTIONS_PATH = ARTIFACTS / "predictions.csv"
METRICS_PATH = ARTIFACTS / "metrics.json"

st.set_page_config(page_title="BehAnalytics Dashboard", page_icon="🎓", layout="wide")


@st.cache_data(show_spinner=False)
def load_predictions() -> pd.DataFrame:
    if not PREDICTIONS_PATH.exists():
        st.error("Missing artifacts/predictions.csv. Run scripts/train_model.py first.")
        st.stop()
    return pd.read_csv(PREDICTIONS_PATH)


@st.cache_data(show_spinner=False)
def load_metrics() -> dict:
    if not METRICS_PATH.exists():
        st.error("Missing artifacts/metrics.json. Run scripts/train_model.py first.")
        st.stop()
    with METRICS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_triggers(series: pd.Series) -> pd.Series:
    exploded = (
        series.fillna("")
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
    )
    exploded = exploded[exploded != ""]
    return exploded


def metric_block(label: str, value: str) -> None:
    st.metric(label=label, value=value)


df = load_predictions()
metrics = load_metrics()

mode_metrics = metrics.get("mode_metrics", {})
available_modes = [mode for mode in ["balanced", "high_recall"] if mode in mode_metrics]
default_mode = metrics.get("mode", "balanced")
if default_mode not in available_modes and available_modes:
    default_mode = available_modes[0]

st.title("🎓 Student Burnout & Dropout Risk Dashboard")
st.caption("Decision-support view over model artifacts. Use for prioritization with human review.")

with st.sidebar:
    st.header("Controls")
    mode = st.selectbox(
        "Evaluation mode",
        options=available_modes or ["balanced"],
        index=(available_modes.index(default_mode) if available_modes else 0),
    )

    risk_levels = sorted(df["burnout_risk_level"].dropna().unique().tolist())
    selected_levels = st.multiselect(
        "Risk levels",
        options=risk_levels,
        default=risk_levels,
    )

    min_score, max_score = float(df["risk_score"].min()), float(df["risk_score"].max())
    score_range = st.slider(
        "Risk score range",
        min_value=0.0,
        max_value=100.0,
        value=(max(0.0, min_score), min(100.0, max_score)),
    )

    student_query = st.text_input("Search Student_ID")
    urgent_only = st.checkbox("Only urgent interventions", value=False)

    outreach_pct = st.slider(
        "Outreach capacity (% top students by risk)",
        min_value=5,
        max_value=50,
        value=20,
        step=5,
    )

mode_view = mode_metrics.get(mode, {})

if selected_levels:
    filtered = df[df["burnout_risk_level"].isin(selected_levels)].copy()
else:
    filtered = df.copy()

filtered = filtered[
    (filtered["risk_score"] >= score_range[0]) &
    (filtered["risk_score"] <= score_range[1])
].copy()

if student_query.strip():
    filtered = filtered[filtered["Student_ID"].astype(str).str.contains(student_query.strip(), case=False, na=False)]

if urgent_only:
    filtered = filtered[
        filtered["recommended_intervention_strategy"].fillna("").str.contains("URGENT", case=False)
    ]

high_count = int((filtered["burnout_risk_level"] == "High").sum())
high_rate = (high_count / len(filtered) * 100.0) if len(filtered) else 0.0

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_block("Students (filtered)", f"{len(filtered):,}")
with c2:
    metric_block("High risk (filtered)", f"{high_count:,}")
with c3:
    metric_block("Avg risk score", f"{filtered['risk_score'].mean():.1f}" if len(filtered) else "0.0")
with c4:
    metric_block(
        f"Recall ({mode})",
        f"{mode_view.get('recall', 0):.4f}" if mode_view else "-",
    )

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_block("Model", metrics.get("model", "-"))
with m2:
    metric_block("ROC-AUC", f"{metrics.get('roc_auc', 0):.4f}")
with m3:
    metric_block("PR-AUC", f"{metrics.get('pr_auc', 0):.4f}")
with m4:
    metric_block("Threshold", f"{mode_view.get('threshold', metrics.get('threshold', 0)):.4f}")

o1, o2, o3 = st.columns(3)
with o1:
    metric_block("High-risk rate", f"{high_rate:.1f}%")
with o2:
    metric_block("Calibration", str(metrics.get("calibration", "none")))
with o3:
    metric_block("Current mode", mode)

tabs = st.tabs(["Overview", "Action Queue", "Student Detail"])

with tabs[0]:
    left, right = st.columns(2)
    with left:
        st.subheader("Risk Level Distribution")
        if len(filtered):
            level_counts = filtered["burnout_risk_level"].value_counts().reset_index()
            level_counts.columns = ["Risk Level", "Count"]
            fig_levels = px.bar(level_counts, x="Risk Level", y="Count", color="Risk Level")
            st.plotly_chart(fig_levels, use_container_width=True)
        else:
            st.info("No rows after filtering.")

    with right:
        st.subheader("Risk Score Distribution")
        if len(filtered):
            fig_scores = px.histogram(filtered, x="risk_score", nbins=30, color="burnout_risk_level")
            st.plotly_chart(fig_scores, use_container_width=True)
        else:
            st.info("No rows after filtering.")

    lower, upper = st.columns(2)
    with lower:
        st.subheader("Top Behavioural Triggers")
        if len(filtered):
            trigger_series = parse_triggers(filtered["key_behavioural_triggers"])
            if len(trigger_series):
                trigger_counts = trigger_series.value_counts().head(15).reset_index()
                trigger_counts.columns = ["Trigger", "Count"]
                fig_triggers = px.bar(trigger_counts, x="Count", y="Trigger", orientation="h")
                fig_triggers.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig_triggers, use_container_width=True)
            else:
                st.info("No trigger text available for selected records.")
        else:
            st.info("No rows after filtering.")

    with upper:
        st.subheader("Intervention Strategy Mix")
        if len(filtered):
            strategy_counts = (
                filtered["recommended_intervention_strategy"]
                .fillna("Unknown")
                .value_counts()
                .head(12)
                .reset_index()
            )
            strategy_counts.columns = ["Intervention", "Count"]
            fig_strategy = px.pie(strategy_counts, names="Intervention", values="Count", hole=0.45)
            st.plotly_chart(fig_strategy, use_container_width=True)
        else:
            st.info("No rows after filtering.")

    st.subheader("Outreach Planning")
    if len(filtered):
        ranked = filtered.sort_values("risk_score", ascending=False)
        outreach_n = max(1, int(len(ranked) * outreach_pct / 100.0))
        outreach_df = ranked.head(outreach_n)
        outreach_high = int((outreach_df["burnout_risk_level"] == "High").sum())
        outreach_medium = int((outreach_df["burnout_risk_level"] == "Medium").sum())
        outreach_urgent = int(
            outreach_df["recommended_intervention_strategy"].fillna("").str.contains("URGENT", case=False).sum()
        )

        p1, p2, p3, p4 = st.columns(4)
        with p1:
            metric_block("Top students to contact", f"{outreach_n:,}")
        with p2:
            metric_block("High-risk in outreach", f"{outreach_high:,}")
        with p3:
            metric_block("Medium-risk in outreach", f"{outreach_medium:,}")
        with p4:
            metric_block("Urgent cases in outreach", f"{outreach_urgent:,}")

        st.caption("Outreach set is computed from highest risk scores in the current filtered cohort.")
    else:
        st.info("No rows after filtering.")

with tabs[1]:
    st.subheader("Action Queue")
    show_cols = [
        "Student_ID",
        "dropout_probability",
        "risk_score",
        "burnout_risk_level",
        "academic_disengagement_indicators",
        "key_behavioural_triggers",
        "recommended_intervention_strategy",
    ]

    if len(filtered):
        queue = filtered[show_cols].sort_values("risk_score", ascending=False)
        st.dataframe(queue, use_container_width=True, height=420)

        st.download_button(
            label="Download filtered queue (CSV)",
            data=queue.to_csv(index=False).encode("utf-8"),
            file_name="filtered_action_queue.csv",
            mime="text/csv",
        )
    else:
        st.warning("No students match current filters.")

with tabs[2]:
    st.subheader("Student Detail")
    if len(filtered):
        selected_student = st.selectbox(
            "Select Student_ID",
            options=filtered["Student_ID"].astype(str).tolist(),
        )
        selected_row = filtered[filtered["Student_ID"].astype(str) == selected_student].iloc[0]

        d1, d2, d3 = st.columns(3)
        with d1:
            metric_block("Dropout probability", f"{selected_row['dropout_probability']:.4f}")
        with d2:
            metric_block("Risk score", f"{selected_row['risk_score']:.1f}")
        with d3:
            metric_block("Risk level", str(selected_row["burnout_risk_level"]))

        st.markdown(f"**Academic disengagement indicators:** {selected_row['academic_disengagement_indicators']}")
        st.markdown(f"**Key behavioural triggers:** {selected_row['key_behavioural_triggers']}")
        st.markdown(f"**Recommended intervention:** {selected_row['recommended_intervention_strategy']}")
    else:
        st.info("No rows after filtering.")

st.caption(
    "Modes: balanced for general evaluation; high_recall to maximize intervention catch rate with more false positives."
)
