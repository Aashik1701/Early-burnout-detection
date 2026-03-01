from pathlib import Path
import json

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
PREDICTIONS_PATH = ARTIFACTS / "predictions.csv"
METRICS_PATH = ARTIFACTS / "metrics.json"
DROPOUT_SRC_PATH = ROOT / "data" / "student_dropout_dataset_v3.csv"

st.set_page_config(page_title="DASHBOARD", page_icon="🎓", layout="wide")


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


@st.cache_data(show_spinner=False)
def load_cohort_data() -> pd.DataFrame | None:
    """Load source dropout dataset for cohort dimensions and merge with predictions."""
    if not DROPOUT_SRC_PATH.exists():
        return None
    src = pd.read_csv(DROPOUT_SRC_PATH)
    cohort_cols = ["Student_ID"]
    for c in ["Department", "Semester", "Gender", "Part_Time_Job", "Age"]:
        if c in src.columns:
            cohort_cols.append(c)
    return src[cohort_cols].drop_duplicates(subset=["Student_ID"])


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

    selected_mode_threshold = float(mode_metrics.get(mode, {}).get("threshold", metrics.get("threshold", 0.5)))
    simulator_threshold = st.slider(
        "What-if threshold simulator",
        min_value=0.01,
        max_value=0.99,
        value=max(0.01, min(0.99, selected_mode_threshold)),
        step=0.01,
        help="Simulates how many students would be flagged at this probability threshold.",
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

if len(available_modes) >= 2:
    st.subheader("Mode Trade-off Comparison")
    compare_rows = []
    for mode_name in ["balanced", "high_recall"]:
        mode_row = mode_metrics.get(mode_name)
        if mode_row:
            compare_rows.extend(
                [
                    {"Mode": mode_name, "Metric": "Accuracy", "Value": mode_row.get("accuracy", 0.0)},
                    {"Mode": mode_name, "Metric": "Precision", "Value": mode_row.get("precision", 0.0)},
                    {"Mode": mode_name, "Metric": "Recall", "Value": mode_row.get("recall", 0.0)},
                    {"Mode": mode_name, "Metric": "F1", "Value": mode_row.get("f1", 0.0)},
                ]
            )

    compare_df = pd.DataFrame(compare_rows)
    if not compare_df.empty:
        compare_fig = px.bar(
            compare_df,
            x="Metric",
            y="Value",
            color="Mode",
            barmode="group",
            text="Value",
            range_y=[0, 1],
        )
        compare_fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        st.plotly_chart(compare_fig, use_container_width=True)

        b = mode_metrics.get("balanced", {})
        h = mode_metrics.get("high_recall", {})
        d1, d2, d3 = st.columns(3)
        with d1:
            metric_block("Recall gain (high_recall - balanced)", f"{h.get('recall', 0.0) - b.get('recall', 0.0):+.4f}")
        with d2:
            metric_block("Precision drop", f"{h.get('precision', 0.0) - b.get('precision', 0.0):+.4f}")
        with d3:
            metric_block("Threshold shift", f"{h.get('threshold', 0.0) - b.get('threshold', 0.0):+.4f}")

tabs = st.tabs(["Overview", "Action Queue", "Student Detail", "Intervention Planner", "Program Impact", "Cohort Insights"])

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
        recommended_threshold = float(outreach_df["dropout_probability"].min())
        outreach_high = int((outreach_df["burnout_risk_level"] == "High").sum())
        outreach_medium = int((outreach_df["burnout_risk_level"] == "Medium").sum())
        outreach_urgent = int(
            outreach_df["recommended_intervention_strategy"].fillna("").str.contains("URGENT", case=False).sum()
        )
        outreach_high_coverage = (
            (outreach_df["burnout_risk_level"] == "High").mean() * 100.0 if len(outreach_df) else 0.0
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

        r1, r2, r3 = st.columns(3)
        with r1:
            metric_block("Recommended threshold", f"{recommended_threshold:.4f}")
        with r2:
            metric_block("Expected flagged @recommended", f"{outreach_n:,}")
        with r3:
            metric_block("High-risk share @recommended", f"{outreach_high_coverage:.1f}%")

        st.success(
            f"Recommended operating threshold for {outreach_pct}% outreach capacity: {recommended_threshold:.4f}."
        )

        st.caption("Outreach set is computed from highest risk scores in the current filtered cohort.")
    else:
        st.info("No rows after filtering.")

    st.subheader("What-if Threshold Impact")
    if len(filtered):
        simulated_flag = (filtered["dropout_probability"] >= simulator_threshold).astype(int)
        simulated_flagged_count = int(simulated_flag.sum())
        simulated_flagged_rate = (simulated_flagged_count / len(filtered) * 100.0) if len(filtered) else 0.0

        high_subset = filtered[filtered["burnout_risk_level"] == "High"]
        simulated_high_coverage = (
            (high_subset["dropout_probability"] >= simulator_threshold).mean() * 100.0
            if len(high_subset)
            else 0.0
        )

        default_mode_threshold = float(mode_view.get("threshold", metrics.get("threshold", 0.5)))
        default_mode_flagged_count = int((filtered["dropout_probability"] >= default_mode_threshold).sum())
        flagged_delta = simulated_flagged_count - default_mode_flagged_count

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            metric_block("Simulator threshold", f"{simulator_threshold:.2f}")
        with s2:
            metric_block("Flagged students", f"{simulated_flagged_count:,}")
        with s3:
            metric_block("Flagged rate", f"{simulated_flagged_rate:.1f}%")
        with s4:
            metric_block("High-risk coverage", f"{simulated_high_coverage:.1f}%")

        st.caption(
            f"Compared with current {mode} threshold ({default_mode_threshold:.4f}), flagged count change is {flagged_delta:+d}."
        )

        sweep_thresholds = np.round(np.arange(0.10, 0.91, 0.05), 2)
        sweep_rows = []
        for t in sweep_thresholds:
            flagged_count_t = int((filtered["dropout_probability"] >= t).sum())
            flagged_rate_t = (flagged_count_t / len(filtered) * 100.0) if len(filtered) else 0.0
            high_cov_t = (
                (high_subset["dropout_probability"] >= t).mean() * 100.0
                if len(high_subset)
                else 0.0
            )
            sweep_rows.append(
                {
                    "Threshold": t,
                    "Flagged Rate (%)": flagged_rate_t,
                    "High-risk Coverage (%)": high_cov_t,
                }
            )

        sweep_df = pd.DataFrame(sweep_rows)
        sweep_long = sweep_df.melt(
            id_vars="Threshold",
            value_vars=["Flagged Rate (%)", "High-risk Coverage (%)"],
            var_name="Curve",
            value_name="Value",
        )

        sweep_fig = px.line(
            sweep_long,
            x="Threshold",
            y="Value",
            color="Curve",
            markers=True,
            title="Threshold Sweep: Load vs Coverage",
        )
        sweep_fig.add_vline(
            x=simulator_threshold,
            line_width=2,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Simulator {simulator_threshold:.2f}",
            annotation_position="top right",
        )
        st.plotly_chart(sweep_fig, use_container_width=True)
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

# ── Tab 4: Intervention Planner ──────────────────────────────────────
with tabs[3]:
    st.subheader("Intervention Planner")
    st.caption("Convert risk into a concrete outreach plan with counselor assignments.")

    if len(filtered):
        ip1, ip2 = st.columns(2)
        with ip1:
            num_counselors = st.number_input("Available counselors", min_value=1, max_value=100, value=5, step=1)
        with ip2:
            slots_per_counselor = st.number_input("Weekly contact slots per counselor", min_value=1, max_value=50, value=10, step=1)

        total_weekly_capacity = int(num_counselors * slots_per_counselor)

        # Build prioritized queue
        planner_df = (
            filtered[
                ["Student_ID", "dropout_probability", "risk_score", "burnout_risk_level",
                 "recommended_intervention_strategy"]
            ]
            .sort_values("risk_score", ascending=False)
            .reset_index(drop=True)
        )
        planner_df["Urgency"] = planner_df["recommended_intervention_strategy"].fillna("").apply(
            lambda x: "URGENT" if "URGENT" in x.upper() else "Standard"
        )
        # Assign counselors in round-robin over the planned capacity
        planner_df["Assigned_Counselor"] = [
            f"Counselor_{(i % num_counselors) + 1}" for i in range(len(planner_df))
        ]
        # Mark which students fit within this week's capacity
        planner_df["Week_Slot"] = [
            f"Week {i // total_weekly_capacity + 1}" for i in range(len(planner_df))
        ]

        ic1, ic2, ic3, ic4 = st.columns(4)
        with ic1:
            metric_block("Total weekly capacity", f"{total_weekly_capacity}")
        with ic2:
            metric_block("Students to contact", f"{len(planner_df):,}")
        with ic3:
            weeks_needed = max(1, -(-len(planner_df) // total_weekly_capacity))  # ceil div
            metric_block("Weeks needed", f"{weeks_needed}")
        with ic4:
            urgent_count = int((planner_df["Urgency"] == "URGENT").sum())
            metric_block("Urgent cases", f"{urgent_count:,}")

        st.markdown("#### Prioritized Contact List")
        # Show week-1 by default
        week_options = sorted(planner_df["Week_Slot"].unique().tolist())
        selected_week = st.selectbox("Select week", options=week_options)
        week_df = planner_df[planner_df["Week_Slot"] == selected_week]
        st.dataframe(week_df, use_container_width=True, height=360)

        # Counselor workload summary
        st.markdown("#### Counselor Workload")
        workload = (
            planner_df[planner_df["Week_Slot"] == selected_week]
            .groupby("Assigned_Counselor")
            .agg(
                Total=("Student_ID", "count"),
                Urgent=("Urgency", lambda x: (x == "URGENT").sum()),
                Avg_Risk=("risk_score", "mean"),
            )
            .reset_index()
        )
        workload["Avg_Risk"] = workload["Avg_Risk"].round(1)
        st.dataframe(workload, use_container_width=True)

        # Download assignment sheet
        assignment_csv = planner_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download full assignment sheet (CSV)",
            data=assignment_csv,
            file_name="intervention_assignment_sheet.csv",
            mime="text/csv",
        )
    else:
        st.warning("No students match current filters.")

# ── Tab 5: Program Impact ───────────────────────────────────────────
with tabs[4]:
    st.subheader("Program Impact")
    st.caption("Leadership-level view: projected outreach impact before acting.")

    if len(filtered):
        # Use the selected mode threshold
        active_threshold = float(mode_view.get("threshold", metrics.get("threshold", 0.5)))
        flagged = filtered[filtered["dropout_probability"] >= active_threshold]
        not_flagged = filtered[filtered["dropout_probability"] < active_threshold]

        total_flagged = len(flagged)
        total_not_flagged = len(not_flagged)
        high_in_flagged = int((flagged["burnout_risk_level"] == "High").sum())
        high_total = int((filtered["burnout_risk_level"] == "High").sum())
        high_capture = (high_in_flagged / high_total * 100.0) if high_total else 0.0

        # False-positive estimate: flagged but NOT actually High risk
        fp_count = total_flagged - high_in_flagged
        fp_rate = (fp_count / total_flagged * 100.0) if total_flagged else 0.0

        pi1, pi2, pi3, pi4 = st.columns(4)
        with pi1:
            metric_block("Students contacted", f"{total_flagged:,}")
        with pi2:
            metric_block("High-risk captured", f"{high_in_flagged:,} / {high_total:,}")
        with pi3:
            metric_block("High-risk capture %", f"{high_capture:.1f}%")
        with pi4:
            metric_block("False-positive load", f"{fp_count:,} ({fp_rate:.1f}%)")

        pi5, pi6, pi7 = st.columns(3)
        with pi5:
            metric_block("Active threshold", f"{active_threshold:.4f}")
        with pi6:
            metric_block("Flagged rate", f"{total_flagged / len(filtered) * 100.0:.1f}%")
        with pi7:
            metric_block("Students NOT flagged", f"{total_not_flagged:,}")

        # Workload by strategy type
        st.markdown("#### Workload by Intervention Strategy")
        if total_flagged:
            strategy_work = (
                flagged["recommended_intervention_strategy"]
                .fillna("Unassigned")
                .value_counts()
                .reset_index()
            )
            strategy_work.columns = ["Strategy", "Students"]
            strategy_work["Share %"] = (strategy_work["Students"] / strategy_work["Students"].sum() * 100.0).round(1)
            fig_workload = px.bar(
                strategy_work,
                x="Students",
                y="Strategy",
                orientation="h",
                text="Students",
                color="Share %",
                color_continuous_scale="Reds",
            )
            fig_workload.update_layout(yaxis={"categoryorder": "total ascending"}, height=400)
            st.plotly_chart(fig_workload, use_container_width=True)
            st.dataframe(strategy_work, use_container_width=True)
        else:
            st.info("No students flagged at the current threshold.")

        # Impact efficiency summary
        st.markdown("#### Impact Efficiency")
        st.info(
            f"At threshold **{active_threshold:.4f}** ({mode} mode), contacting "
            f"**{total_flagged:,}** students ({total_flagged / len(filtered) * 100.0:.1f}% of cohort) "
            f"captures **{high_capture:.1f}%** of high-risk students. "
            f"Approximately **{fp_count:,}** contacts ({fp_rate:.1f}%) are false positives — "
            f"students who are flagged but not high-risk."
        )
    else:
        st.warning("No students match current filters.")

# ── Tab 6: Cohort Insights ──────────────────────────────────────────
with tabs[5]:
    st.subheader("Cohort Insights")
    st.caption("Identify where risk concentrates across cohort dimensions.")

    cohort_src = load_cohort_data()
    if cohort_src is not None:
        cohort_df = filtered.merge(cohort_src, on="Student_ID", how="left")
    else:
        cohort_df = filtered.copy()

    cohort_dimensions = [c for c in ["Department", "Semester", "Gender", "Part_Time_Job"] if c in cohort_df.columns]

    if not cohort_dimensions:
        st.warning(
            "No cohort dimension columns found. Place `student_dropout_dataset_v3.csv` in the `data/` folder "
            "for department, semester, gender, and job-status breakdowns."
        )
    elif len(cohort_df) == 0:
        st.info("No rows after filtering.")
    else:
        selected_dim = st.selectbox("Cohort dimension", options=cohort_dimensions)

        # 1) Risk Level distribution stacked bar
        st.markdown(f"#### Risk Level Distribution by {selected_dim}")
        level_by_dim = (
            cohort_df.groupby([selected_dim, "burnout_risk_level"])
            .size()
            .reset_index(name="Count")
        )
        fig_stacked = px.bar(
            level_by_dim,
            x=selected_dim,
            y="Count",
            color="burnout_risk_level",
            barmode="stack",
            color_discrete_map={"High": "#e74c3c", "Medium": "#f39c12", "Low": "#2ecc71"},
        )
        fig_stacked.update_layout(xaxis_title=selected_dim, yaxis_title="Students")
        st.plotly_chart(fig_stacked, use_container_width=True)

        # 2) Average risk score heatmap
        st.markdown(f"#### Average Risk Score by {selected_dim}")
        avg_risk = (
            cohort_df.groupby(selected_dim)["risk_score"]
            .mean()
            .round(1)
            .reset_index()
        )
        avg_risk.columns = [selected_dim, "Avg Risk Score"]
        avg_risk = avg_risk.sort_values("Avg Risk Score", ascending=False)
        fig_heat = px.bar(
            avg_risk,
            x=selected_dim,
            y="Avg Risk Score",
            color="Avg Risk Score",
            color_continuous_scale="YlOrRd",
            text="Avg Risk Score",
        )
        fig_heat.update_traces(textposition="outside")
        fig_heat.update_layout(xaxis_title=selected_dim)
        st.plotly_chart(fig_heat, use_container_width=True)

        # 3) High-risk rate by dimension
        st.markdown(f"#### High-risk Rate by {selected_dim}")
        dim_summary = (
            cohort_df.groupby(selected_dim)
            .agg(
                Total=("Student_ID", "count"),
                High=("burnout_risk_level", lambda x: (x == "High").sum()),
                Avg_Risk=("risk_score", "mean"),
            )
            .reset_index()
        )
        dim_summary["High_Rate_%"] = (dim_summary["High"] / dim_summary["Total"] * 100.0).round(1)
        dim_summary["Avg_Risk"] = dim_summary["Avg_Risk"].round(1)
        dim_summary = dim_summary.sort_values("High_Rate_%", ascending=False)
        fig_hr = px.bar(
            dim_summary,
            x=selected_dim,
            y="High_Rate_%",
            text="High_Rate_%",
            color="High_Rate_%",
            color_continuous_scale="Reds",
        )
        fig_hr.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_hr.update_layout(xaxis_title=selected_dim, yaxis_title="High-risk rate (%)")
        st.plotly_chart(fig_hr, use_container_width=True)

        # 4) Summary table
        st.markdown(f"#### Summary Table — {selected_dim}")
        st.dataframe(dim_summary, use_container_width=True)

        # 5) If two dimensions available, show cross-tab heatmap
        if len(cohort_dimensions) >= 2:
            st.markdown("#### Cross-Dimension Heatmap (Avg Risk Score)")
            dim_a, dim_b = cohort_dimensions[0], cohort_dimensions[1]
            cross_dim_selector = st.columns(2)
            with cross_dim_selector[0]:
                dim_a = st.selectbox("Row dimension", cohort_dimensions, index=0, key="heatmap_row")
            with cross_dim_selector[1]:
                remaining = [d for d in cohort_dimensions if d != dim_a]
                dim_b = st.selectbox("Column dimension", remaining, index=0, key="heatmap_col")

            pivot = cohort_df.pivot_table(
                values="risk_score", index=dim_a, columns=dim_b, aggfunc="mean"
            ).round(1)
            fig_heatmap = px.imshow(
                pivot,
                text_auto=".1f",
                color_continuous_scale="YlOrRd",
                labels={"color": "Avg Risk Score"},
                aspect="auto",
            )
            fig_heatmap.update_layout(height=500)
            st.plotly_chart(fig_heatmap, use_container_width=True)

st.caption(
    "Modes: balanced for general evaluation; high_recall to maximize intervention catch rate with more false positives."
)
