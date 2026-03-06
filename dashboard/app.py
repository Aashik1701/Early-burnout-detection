from pathlib import Path
import json

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
PREDICTIONS_PATH = ARTIFACTS / "predictions.csv"
METRICS_PATH = ARTIFACTS / "metrics.json"
DROPOUT_SRC_PATH = ROOT / "data" / "student_dropout_dataset_v3.csv"

st.set_page_config(
    page_title="BehAnalytics — Burnout & Dropout Risk",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────── THEME CSS ──────────────────────────────────
CUSTOM_CSS = """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root palette ── */
:root {
    --bg-primary:    #0d1117;
    --bg-secondary:  #161b22;
    --bg-card:       #1c232e;
    --bg-card-hover: #232c3a;
    --border:        rgba(99,120,160,0.18);
    --accent-blue:   #3b82f6;
    --accent-purple: #8b5cf6;
    --accent-teal:   #14b8a6;
    --risk-high:     #ef4444;
    --risk-high-bg:  rgba(239,68,68,0.12);
    --risk-med:      #f59e0b;
    --risk-med-bg:   rgba(245,158,11,0.12);
    --risk-low:      #22c55e;
    --risk-low-bg:   rgba(34,197,94,0.12);
    --text-primary:  #e6edf3;
    --text-muted:    #8b949e;
    --text-subtle:   #6e7681;
    --shadow:        0 4px 24px rgba(0,0,0,0.45);
    --radius:        12px;
    --radius-sm:     8px;
}

/* ── Hide Streamlit's white top header bar ── */
#MainMenu { visibility: hidden !important; }
header[data-testid="stHeader"] {
    background: var(--bg-primary) !important;
    border-bottom: 1px solid var(--border) !important;
    height: 0px !important;
    min-height: 0px !important;
    overflow: hidden !important;
}
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
}
.stApp {
    background: var(--bg-primary) !important;
    margin-top: 0 !important;
}
.stMainBlockContainer, .main .block-container {
    padding-top: 1.5rem !important;
}
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}

/* ══ SIDEBAR ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
/* All text / labels inside sidebar */
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* Expander header */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    margin-bottom: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}
/* Selectbox / multiselect containers */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
}
/* Text input */
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] input[type="number"],
[data-testid="stSidebar"] input {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-sm) !important;
}
/* Checkbox background */
[data-testid="stSidebar"] [data-testid="stCheckbox"] {
    background: transparent !important;
}
[data-testid="stSidebar"] [data-baseweb="checkbox"] > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
}
/* Slider track */
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
    background: var(--accent-blue) !important;
}

/* ══ MAIN AREA INPUTS ═══════════════════════════════════════════════════ */
input[type="text"], input[type="number"], textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-sm) !important;
}
[data-baseweb="select"] > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
}
/* Dropdown popup menu */
[data-baseweb="popover"], [data-baseweb="menu"],
[role="listbox"], ul[role="listbox"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
}
[data-baseweb="menu"] li, [role="option"] {
    color: var(--text-primary) !important;
}
[data-baseweb="menu"] li:hover, [role="option"]:hover {
    background: var(--bg-card-hover) !important;
}

/* ══ TABS ═════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-secondary) !important;
    border-radius: var(--radius) !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
    margin-bottom: 1.5rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 8px 16px !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent-blue) !important;
    color: #ffffff !important;
    box-shadow: 0 2px 8px rgba(59,130,246,0.4) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    background: var(--bg-card-hover) !important;
}
[data-baseweb="tab-panel"] {
    background: transparent !important;
}

/* ══ METRIC CARDS ════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem 1.25rem !important;
    box-shadow: var(--shadow) !important;
    transition: border-color 0.2s ease, transform 0.2s ease !important;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(59,130,246,0.4) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricLabel"] > div {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

/* ══ HEADINGS ════════════════════════════════════════════════════════ */
h1 {
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple)) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin-bottom: 0.25rem !important;
}
h2, h3 { color: var(--text-primary) !important; font-weight: 700 !important; }
.stMarkdown h4 {
    color: var(--text-primary) !important;
    border-bottom: 1px solid var(--border) !important;
    padding-bottom: 6px !important;
    margin-bottom: 1rem !important;
}

/* ══ DATAFRAME / TABLE ═══════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}
/* The inner glide-data-grid iframe and its host element */
[data-testid="stDataFrame"] > div,
[data-testid="stDataFrame"] iframe,
.dvn-scroller {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
}
/* Force white text inside all iframes (data grid) */
iframe { background: #1c232e !important; }

/* ══ EXPANDERS (main area) ══════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}
[data-testid="stExpander"] summary {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    background: var(--bg-card) !important;
}
[data-testid="stExpander"] summary svg { fill: var(--text-muted) !important; }

/* ══ ALERTS / BANNERS ═══════════════════════════════════════════════ */
.stAlert { border-radius: var(--radius) !important; }
[data-testid="stAlert"][kind="success"],
.stSuccess {
    background: rgba(34,197,94,0.10) !important;
    border: 1px solid rgba(34,197,94,0.30) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stAlert"][kind="info"],
.stInfo {
    background: rgba(59,130,246,0.10) !important;
    border: 1px solid rgba(59,130,246,0.30) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stAlert"][kind="warning"],
.stWarning {
    background: rgba(245,158,11,0.10) !important;
    border: 1px solid rgba(245,158,11,0.30) !important;
    border-radius: var(--radius) !important;
}
/* Alert inner text inherits from global * override below */
[data-testid="stAlert"] * { color: var(--text-primary) !important; }

/* ══ BUTTONS ═════════════════════════════════════════════════════════ */
.stDownloadButton button, .stButton button {
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.25rem !important;
    transition: opacity 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease !important;
    box-shadow: 0 2px 12px rgba(59,130,246,0.3) !important;
}
.stDownloadButton button:hover, .stButton button:hover {
    opacity: 0.90 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.5) !important;
}

/* ══ NUMBER INPUTS ═══════════════════════════════════════════════════ */
.stNumberInput > div {
    background: var(--bg-card) !important;
    border-radius: var(--radius-sm) !important;
}
.stNumberInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-sm) !important;
}
.stNumberInput button {
    background: var(--bg-card-hover) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
}

/* ══ MISC ═════════════════════════════════════════════════════════════ */
hr, .section-sep { border-color: var(--border) !important; margin: 1.25rem 0 !important; }
.stCaption, small { color: var(--text-subtle) !important; font-size: 0.78rem !important; }

/* All selectboxes / multiselect */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-sm) !important;
}
[data-baseweb="tag"] {
    background: rgba(59,130,246,0.15) !important;
    border: 1px solid rgba(59,130,246,0.30) !important;
    color: #93c5fd !important;
    border-radius: 6px !important;
}

/* ══ CUSTOM COMPONENTS ═══════════════════════════════════════════════ */
.title-bar {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 1.5rem;
    padding: 1.25rem 1.5rem;
    background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(139,92,246,0.08));
    border: 1px solid var(--border);
    border-radius: var(--radius);
}
.badge-high   { background: var(--risk-high-bg); color: var(--risk-high); border: 1px solid rgba(239,68,68,0.25); border-radius: 9999px; padding: 2px 10px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
.badge-medium { background: var(--risk-med-bg);  color: var(--risk-med);  border: 1px solid rgba(245,158,11,0.25); border-radius: 9999px; padding: 2px 10px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
.badge-low    { background: var(--risk-low-bg);  color: var(--risk-low);  border: 1px solid rgba(34,197,94,0.25);  border-radius: 9999px; padding: 2px 10px; font-size: 0.75rem; font-weight: 600; display: inline-block; }

.detail-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.detail-card .label {
    color: var(--text-muted);
    font-size: 0.72rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px;
}
.detail-card .value { color: var(--text-primary); font-size: 0.93rem; line-height: 1.5; }

.section-sep { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }
.js-plotly-plot, .plotly { border-radius: var(--radius) !important; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Plotly dark template ──────────────────────────────────────────────────────
PLOTLY_TEMPLATE = "plotly_dark"
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(28,35,46,1)",
    plot_bgcolor="rgba(28,35,46,1)",
    font=dict(family="Inter, sans-serif", color="#e6edf3", size=12),
    xaxis=dict(gridcolor="rgba(99,120,160,0.12)", linecolor="rgba(99,120,160,0.18)"),
    yaxis=dict(gridcolor="rgba(99,120,160,0.12)", linecolor="rgba(99,120,160,0.18)"),
    margin=dict(l=24, r=24, t=36, b=24),
    legend=dict(bgcolor="rgba(22,27,34,0.8)", bordercolor="rgba(99,120,160,0.18)", borderwidth=1),
)

RISK_COLORS = {
    "High":   "#ef4444",
    "Medium": "#f59e0b",
    "Low":    "#22c55e",
}


def apply_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


# ── Data loaders ─────────────────────────────────────────────────────────────
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
    return exploded[exploded != ""]


def metric_block(label: str, value: str) -> None:
    st.metric(label=label, value=value)


def risk_badge(level: str) -> str:
    cls = f"badge-{level.lower()}" if level.lower() in ("high", "medium", "low") else "badge-low"
    return f'<span class="{cls}">{level}</span>'


# ── Load data ─────────────────────────────────────────────────────────────────
df = load_predictions()
metrics = load_metrics()

mode_metrics = metrics.get("mode_metrics", {})
available_modes = [m for m in ["balanced", "high_recall"] if m in mode_metrics]
default_mode = metrics.get("mode", "balanced")
if default_mode not in available_modes and available_modes:
    default_mode = available_modes[0]

# ── Page Header ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="title-bar">
      <div>
        <h1>🎓 BehAnalytics — Student Burnout & Dropout Risk</h1>
        <p style="margin:0; color:#8b949e; font-size:0.85rem;">
          Decision-support dashboard &nbsp;·&nbsp; Model artifacts &nbsp;·&nbsp; Prioritize with human review
        </p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    st.markdown('<hr class="section-sep">', unsafe_allow_html=True)

    with st.expander("🎯 Evaluation Mode", expanded=True):
        mode = st.selectbox(
            "Mode",
            options=available_modes or ["balanced"],
            index=(available_modes.index(default_mode) if available_modes else 0),
            label_visibility="collapsed",
        )

    with st.expander("🔍 Student Filters", expanded=True):
        risk_levels = sorted(df["burnout_risk_level"].dropna().unique().tolist())
        selected_levels = st.multiselect("Risk levels", options=risk_levels, default=risk_levels)
        min_score, max_score = float(df["risk_score"].min()), float(df["risk_score"].max())
        score_range = st.slider(
            "Risk score range",
            min_value=0.0, max_value=100.0,
            value=(max(0.0, min_score), min(100.0, max_score)),
        )
        student_query = st.text_input("Search Student_ID", placeholder="e.g. 1042")
        urgent_only = st.checkbox("Only urgent interventions", value=False)

    with st.expander("📋 Outreach & Simulation", expanded=True):
        outreach_pct = st.slider(
            "Outreach capacity (% top students by risk)",
            min_value=5, max_value=50, value=20, step=5,
        )
        selected_mode_threshold = float(
            mode_metrics.get(mode, {}).get("threshold", metrics.get("threshold", 0.5))
        )
        simulator_threshold = st.slider(
            "What-if threshold simulator",
            min_value=0.01, max_value=0.99,
            value=max(0.01, min(0.99, selected_mode_threshold)),
            step=0.01,
            help="Simulates how many students would be flagged at this probability threshold.",
        )

mode_view = mode_metrics.get(mode, {})

# ── Filtering ─────────────────────────────────────────────────────────────────
filtered = df[df["burnout_risk_level"].isin(selected_levels)].copy() if selected_levels else df.copy()
filtered = filtered[
    (filtered["risk_score"] >= score_range[0]) &
    (filtered["risk_score"] <= score_range[1])
].copy()
if student_query.strip():
    filtered = filtered[
        filtered["Student_ID"].astype(str).str.contains(student_query.strip(), case=False, na=False)
    ]
if urgent_only:
    filtered = filtered[
        filtered["recommended_intervention_strategy"].fillna("").str.contains("URGENT", case=False)
    ]

high_count = int((filtered["burnout_risk_level"] == "High").sum())
high_rate = (high_count / len(filtered) * 100.0) if len(filtered) else 0.0

# ── Top KPI Row ───────────────────────────────────────────────────────────────
st.markdown("### 📊 Key Metrics")
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1: metric_block("Students (filtered)", f"{len(filtered):,}")
with c2: metric_block("High Risk", f"{high_count:,}")
with c3: metric_block("Avg Risk Score", f"{filtered['risk_score'].mean():.1f}" if len(filtered) else "0.0")
with c4: metric_block(f"Recall ({mode})", f"{mode_view.get('recall', 0):.4f}" if mode_view else "—")
with c5: metric_block("ROC-AUC", f"{metrics.get('roc_auc', 0):.4f}")
with c6: metric_block("PR-AUC", f"{metrics.get('pr_auc', 0):.4f}")

m1, m2, m3, m4, m5 = st.columns(5)
with m1: metric_block("Model", metrics.get("model", "—"))
with m2: metric_block("Threshold", f"{mode_view.get('threshold', metrics.get('threshold', 0)):.4f}")
with m3: metric_block("High-risk rate", f"{high_rate:.1f}%")
with m4: metric_block("Calibration", str(metrics.get("calibration", "none")))
with m5: metric_block("Current mode", mode)

st.markdown('<hr class="section-sep">', unsafe_allow_html=True)

# ── Mode Trade-off Comparison ─────────────────────────────────────────────────
if len(available_modes) >= 2:
    with st.expander("📈 Mode Trade-off Comparison", expanded=False):
        compare_rows = []
        for mode_name in ["balanced", "high_recall"]:
            mode_row = mode_metrics.get(mode_name)
            if mode_row:
                compare_rows.extend([
                    {"Mode": mode_name, "Metric": "Accuracy",  "Value": mode_row.get("accuracy", 0.0)},
                    {"Mode": mode_name, "Metric": "Precision", "Value": mode_row.get("precision", 0.0)},
                    {"Mode": mode_name, "Metric": "Recall",    "Value": mode_row.get("recall", 0.0)},
                    {"Mode": mode_name, "Metric": "F1",        "Value": mode_row.get("f1", 0.0)},
                ])
        compare_df = pd.DataFrame(compare_rows)
        if not compare_df.empty:
            compare_fig = px.bar(
                compare_df, x="Metric", y="Value", color="Mode",
                barmode="group", text="Value", range_y=[0, 1],
                color_discrete_map={"balanced": "#3b82f6", "high_recall": "#8b5cf6"},
                template=PLOTLY_TEMPLATE,
            )
            compare_fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
            apply_theme(compare_fig)
            st.plotly_chart(compare_fig, use_container_width=True)

            b = mode_metrics.get("balanced", {})
            h = mode_metrics.get("high_recall", {})
            d1, d2, d3 = st.columns(3)
            with d1: metric_block("Recall gain (high_recall - balanced)", f"{h.get('recall', 0.0) - b.get('recall', 0.0):+.4f}")
            with d2: metric_block("Precision drop", f"{h.get('precision', 0.0) - b.get('precision', 0.0):+.4f}")
            with d3: metric_block("Threshold shift", f"{h.get('threshold', 0.0) - b.get('threshold', 0.0):+.4f}")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "🏠 Overview",
    "⚡ Action Queue",
    "👤 Student Detail",
    "📅 Intervention Planner",
    "🎯 Program Impact",
    "🔬 Cohort Insights",
])

# ══════════════════════════════════════════════════════════════════════════════
# Tab 1 — Overview
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    left, right = st.columns(2)

    with left:
        st.markdown("#### 🔴 Risk Level Distribution")
        if len(filtered):
            level_counts = filtered["burnout_risk_level"].value_counts().reset_index()
            level_counts.columns = ["Risk Level", "Count"]
            fig_levels = px.bar(
                level_counts, x="Risk Level", y="Count",
                color="Risk Level",
                color_discrete_map=RISK_COLORS,
                template=PLOTLY_TEMPLATE,
            )
            fig_levels.update_traces(marker_line_width=0)
            apply_theme(fig_levels)
            st.plotly_chart(fig_levels, use_container_width=True)
        else:
            st.info("No rows after filtering.")

    with right:
        st.markdown("#### 📉 Risk Score Distribution")
        if len(filtered):
            fig_scores = px.histogram(
                filtered, x="risk_score", nbins=30,
                color="burnout_risk_level",
                color_discrete_map=RISK_COLORS,
                template=PLOTLY_TEMPLATE,
                opacity=0.85,
            )
            apply_theme(fig_scores)
            st.plotly_chart(fig_scores, use_container_width=True)
        else:
            st.info("No rows after filtering.")

    lower, upper = st.columns(2)

    with lower:
        st.markdown("#### 🧠 Top Behavioural Triggers")
        if len(filtered):
            trigger_series = parse_triggers(filtered["key_behavioural_triggers"])
            if len(trigger_series):
                trigger_counts = trigger_series.value_counts().head(15).reset_index()
                trigger_counts.columns = ["Trigger", "Count"]
                fig_triggers = px.bar(
                    trigger_counts, x="Count", y="Trigger",
                    orientation="h",
                    color="Count",
                    color_continuous_scale=[[0, "#14b8a6"], [1, "#3b82f6"]],
                    template=PLOTLY_TEMPLATE,
                )
                fig_triggers.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
                apply_theme(fig_triggers)
                st.plotly_chart(fig_triggers, use_container_width=True)
            else:
                st.info("No trigger text available for selected records.")
        else:
            st.info("No rows after filtering.")

    with upper:
        st.markdown("#### 💡 Intervention Strategy Mix")
        if len(filtered):
            strategy_counts = (
                filtered["recommended_intervention_strategy"]
                .fillna("Unknown")
                .value_counts()
                .head(8)           # cap to 8 for readability
                .reset_index()
            )
            strategy_counts.columns = ["Intervention", "Count"]
            fig_strategy = px.pie(
                strategy_counts, names="Intervention", values="Count",
                hole=0.55,
                color_discrete_sequence=px.colors.qualitative.Bold,
                template=PLOTLY_TEMPLATE,
            )
            fig_strategy.update_traces(
                textposition="inside",
                textinfo="percent",         # percent only inside slice — no label crowding
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
                pull=[0.03] * len(strategy_counts),
            )
            fig_strategy.update_layout(
                height=380,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    x=1.02, y=0.5,
                    font=dict(size=11, color="#e6edf3"),
                    bgcolor="rgba(28,35,46,0.85)",
                    bordercolor="rgba(99,120,160,0.18)",
                    borderwidth=1,
                ),
                margin=dict(l=0, r=160, t=20, b=20),
            )
            apply_theme(fig_strategy)
            st.plotly_chart(fig_strategy, use_container_width=True)
        else:
            st.info("No rows after filtering.")

    st.markdown("#### 📡 Outreach Planning")
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
        with p1: metric_block("Top students to contact", f"{outreach_n:,}")
        with p2: metric_block("High-risk in outreach", f"{outreach_high:,}")
        with p3: metric_block("Medium-risk in outreach", f"{outreach_medium:,}")
        with p4: metric_block("Urgent cases in outreach", f"{outreach_urgent:,}")

        r1, r2, r3 = st.columns(3)
        with r1: metric_block("Recommended threshold", f"{recommended_threshold:.4f}")
        with r2: metric_block("Expected flagged @recommended", f"{outreach_n:,}")
        with r3: metric_block("High-risk share @recommended", f"{outreach_high_coverage:.1f}%")

        st.success(
            f"✅ Recommended operating threshold for **{outreach_pct}%** outreach capacity: **{recommended_threshold:.4f}**"
        )
        st.caption("Outreach set is computed from highest risk scores in the current filtered cohort.")
    else:
        st.info("No rows after filtering.")

    st.markdown("#### 🔮 What-if Threshold Impact")
    if len(filtered):
        simulated_flag = (filtered["dropout_probability"] >= simulator_threshold).astype(int)
        simulated_flagged_count = int(simulated_flag.sum())
        simulated_flagged_rate = (simulated_flagged_count / len(filtered) * 100.0) if len(filtered) else 0.0

        high_subset = filtered[filtered["burnout_risk_level"] == "High"]
        simulated_high_coverage = (
            (high_subset["dropout_probability"] >= simulator_threshold).mean() * 100.0
            if len(high_subset) else 0.0
        )

        default_mode_threshold = float(mode_view.get("threshold", metrics.get("threshold", 0.5)))
        default_mode_flagged_count = int((filtered["dropout_probability"] >= default_mode_threshold).sum())
        flagged_delta = simulated_flagged_count - default_mode_flagged_count

        s1, s2, s3, s4 = st.columns(4)
        with s1: metric_block("Simulator threshold",  f"{simulator_threshold:.2f}")
        with s2: metric_block("Flagged students",     f"{simulated_flagged_count:,}")
        with s3: metric_block("Flagged rate",         f"{simulated_flagged_rate:.1f}%")
        with s4: metric_block("High-risk coverage",   f"{simulated_high_coverage:.1f}%")

        st.caption(
            f"Compared with current {mode} threshold ({default_mode_threshold:.4f}), "
            f"flagged count change is **{flagged_delta:+d}**."
        )

        sweep_thresholds = np.round(np.arange(0.10, 0.91, 0.05), 2)
        sweep_rows = []
        for t in sweep_thresholds:
            flagged_count_t = int((filtered["dropout_probability"] >= t).sum())
            flagged_rate_t = (flagged_count_t / len(filtered) * 100.0) if len(filtered) else 0.0
            high_cov_t = (
                (high_subset["dropout_probability"] >= t).mean() * 100.0
                if len(high_subset) else 0.0
            )
            sweep_rows.append({
                "Threshold": t,
                "Flagged Rate (%)": flagged_rate_t,
                "High-risk Coverage (%)": high_cov_t,
            })

        sweep_df = pd.DataFrame(sweep_rows)
        sweep_long = sweep_df.melt(
            id_vars="Threshold",
            value_vars=["Flagged Rate (%)", "High-risk Coverage (%)"],
            var_name="Curve", value_name="Value",
        )
        sweep_fig = px.line(
            sweep_long, x="Threshold", y="Value", color="Curve",
            markers=True,
            title="Threshold Sweep: Load vs Coverage",
            color_discrete_map={
                "Flagged Rate (%)": "#3b82f6",
                "High-risk Coverage (%)": "#ef4444",
            },
            template=PLOTLY_TEMPLATE,
        )
        sweep_fig.add_vline(
            x=simulator_threshold, line_width=2, line_dash="dash",
            line_color="#f59e0b",
            annotation_text=f"Sim {simulator_threshold:.2f}",
            annotation_position="top right",
            annotation_font_color="#f59e0b",
        )
        apply_theme(sweep_fig)
        st.plotly_chart(sweep_fig, use_container_width=True)
    else:
        st.info("No rows after filtering.")

# ══════════════════════════════════════════════════════════════════════════════
# Tab 2 — Action Queue
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("#### ⚡ Action Queue")
    st.caption("Students sorted by descending risk score. Use filters in the sidebar to narrow the list.")

    show_cols = [
        "Student_ID", "dropout_probability", "risk_score",
        "burnout_risk_level", "academic_disengagement_indicators",
        "key_behavioural_triggers", "recommended_intervention_strategy",
    ]

    if len(filtered):
        queue = filtered[show_cols].sort_values("risk_score", ascending=False)
        st.dataframe(queue, use_container_width=True, height=450)
        st.markdown("")
        st.download_button(
            label="⬇️ Download filtered queue (CSV)",
            data=queue.to_csv(index=False).encode("utf-8"),
            file_name="filtered_action_queue.csv",
            mime="text/csv",
        )
    else:
        st.warning("No students match current filters.")

# ══════════════════════════════════════════════════════════════════════════════
# Tab 3 — Student Detail
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("#### 👤 Student Detail")
    if len(filtered):
        selected_student = st.selectbox(
            "Select Student_ID",
            options=filtered["Student_ID"].astype(str).tolist(),
        )
        selected_row = filtered[filtered["Student_ID"].astype(str) == selected_student].iloc[0]
        risk_lvl = str(selected_row["burnout_risk_level"])

        d1, d2, d3 = st.columns(3)
        with d1: metric_block("Dropout probability", f"{selected_row['dropout_probability']:.4f}")
        with d2: metric_block("Risk score", f"{selected_row['risk_score']:.1f}")
        with d3: metric_block("Risk level", risk_lvl)

        st.markdown('<hr class="section-sep">', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                f"""<div class="detail-card">
                  <div class="label">🎓 Academic Disengagement Indicators</div>
                  <div class="value">{selected_row['academic_disengagement_indicators']}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f"""<div class="detail-card">
                  <div class="label">⚠️ Key Behavioural Triggers</div>
                  <div class="value">{selected_row['key_behavioural_triggers']}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""<div class="detail-card">
              <div class="label">💊 Recommended Intervention Strategy</div>
              <div class="value">{selected_row['recommended_intervention_strategy']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Mini risk gauge
        gauge_val = float(selected_row["dropout_probability"]) * 100
        gauge_color = "#ef4444" if risk_lvl == "High" else "#f59e0b" if risk_lvl == "Medium" else "#22c55e"
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=gauge_val,
            number={"suffix": "%", "font": {"color": gauge_color, "size": 32}},
            title={"text": "Dropout Probability", "font": {"color": "#8b949e", "size": 14}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#8b949e", "tickfont": {"color": "#8b949e"}},
                "bar": {"color": gauge_color, "thickness": 0.28},
                "bgcolor": "rgba(28,35,46,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 33],  "color": "rgba(34,197,94,0.08)"},
                    {"range": [33, 66], "color": "rgba(245,158,11,0.08)"},
                    {"range": [66, 100],"color": "rgba(239,68,68,0.08)"},
                ],
                "threshold": {"line": {"color": gauge_color, "width": 3}, "thickness": 0.75, "value": gauge_val},
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(28,35,46,1)",
            font_color="#e6edf3",
            height=260,
            margin=dict(l=24, r=24, t=24, b=12),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
    else:
        st.info("No rows after filtering.")

# ══════════════════════════════════════════════════════════════════════════════
# Tab 4 — Intervention Planner
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("#### 📅 Intervention Planner")
    st.caption("Convert risk into a concrete outreach plan with counselor assignments.")

    if len(filtered):
        ip1, ip2 = st.columns(2)
        with ip1:
            num_counselors = st.number_input("Available counselors", min_value=1, max_value=100, value=5, step=1)
        with ip2:
            slots_per_counselor = st.number_input("Weekly contact slots per counselor", min_value=1, max_value=50, value=10, step=1)

        total_weekly_capacity = int(num_counselors * slots_per_counselor)

        planner_df = (
            filtered[[
                "Student_ID", "dropout_probability", "risk_score",
                "burnout_risk_level", "recommended_intervention_strategy",
            ]]
            .sort_values("risk_score", ascending=False)
            .reset_index(drop=True)
        )
        planner_df["Urgency"] = planner_df["recommended_intervention_strategy"].fillna("").apply(
            lambda x: "🚨 URGENT" if "URGENT" in x.upper() else "Standard"
        )
        planner_df["Assigned_Counselor"] = [
            f"Counselor_{(i % num_counselors) + 1}" for i in range(len(planner_df))
        ]
        planner_df["Week_Slot"] = [
            f"Week {i // total_weekly_capacity + 1}" for i in range(len(planner_df))
        ]

        ic1, ic2, ic3, ic4 = st.columns(4)
        weeks_needed = max(1, -(-len(planner_df) // total_weekly_capacity))
        urgent_count = int((planner_df["Urgency"] == "🚨 URGENT").sum())
        with ic1: metric_block("Total weekly capacity", f"{total_weekly_capacity}")
        with ic2: metric_block("Students to contact", f"{len(planner_df):,}")
        with ic3: metric_block("Weeks needed", f"{weeks_needed}")
        with ic4: metric_block("Urgent cases", f"{urgent_count:,}")

        st.markdown('<hr class="section-sep">', unsafe_allow_html=True)
        st.markdown("#### Prioritized Contact List")
        week_options = sorted(planner_df["Week_Slot"].unique().tolist())
        selected_week = st.selectbox("Select week", options=week_options)
        week_df = planner_df[planner_df["Week_Slot"] == selected_week]
        st.dataframe(week_df, use_container_width=True, height=360)

        st.markdown("#### Counselor Workload")
        workload = (
            planner_df[planner_df["Week_Slot"] == selected_week]
            .groupby("Assigned_Counselor")
            .agg(
                Total=("Student_ID", "count"),
                Urgent=("Urgency", lambda x: (x == "🚨 URGENT").sum()),
                Avg_Risk=("risk_score", "mean"),
            )
            .reset_index()
        )
        workload["Avg_Risk"] = workload["Avg_Risk"].round(1)

        fig_wl = px.bar(
            workload, x="Assigned_Counselor", y="Total",
            color="Avg_Risk",
            color_continuous_scale=[[0, "#22c55e"], [0.5, "#f59e0b"], [1, "#ef4444"]],
            text="Total",
            template=PLOTLY_TEMPLATE,
        )
        fig_wl.update_traces(textposition="outside")
        apply_theme(fig_wl)
        st.plotly_chart(fig_wl, use_container_width=True)
        st.dataframe(workload, use_container_width=True)

        assignment_csv = planner_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download full assignment sheet (CSV)",
            data=assignment_csv,
            file_name="intervention_assignment_sheet.csv",
            mime="text/csv",
        )
    else:
        st.warning("No students match current filters.")

# ══════════════════════════════════════════════════════════════════════════════
# Tab 5 — Program Impact
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("#### 🎯 Program Impact")
    st.caption("Leadership-level view: projected outreach impact before acting.")

    if len(filtered):
        active_threshold = float(mode_view.get("threshold", metrics.get("threshold", 0.5)))
        flagged = filtered[filtered["dropout_probability"] >= active_threshold]
        not_flagged = filtered[filtered["dropout_probability"] < active_threshold]

        total_flagged     = len(flagged)
        total_not_flagged = len(not_flagged)
        high_in_flagged   = int((flagged["burnout_risk_level"] == "High").sum())
        high_total        = int((filtered["burnout_risk_level"] == "High").sum())
        high_capture      = (high_in_flagged / high_total * 100.0) if high_total else 0.0
        fp_count          = total_flagged - high_in_flagged
        fp_rate           = (fp_count / total_flagged * 100.0) if total_flagged else 0.0

        pi1, pi2, pi3, pi4 = st.columns(4)
        with pi1: metric_block("Students contacted", f"{total_flagged:,}")
        with pi2: metric_block("High-risk captured", f"{high_in_flagged:,} / {high_total:,}")
        with pi3: metric_block("High-risk capture %", f"{high_capture:.1f}%")
        with pi4: metric_block("False-positive load", f"{fp_count:,} ({fp_rate:.1f}%)")

        pi5, pi6, pi7 = st.columns(3)
        with pi5: metric_block("Active threshold", f"{active_threshold:.4f}")
        with pi6: metric_block("Flagged rate", f"{total_flagged / len(filtered) * 100.0:.1f}%")
        with pi7: metric_block("Students NOT flagged", f"{total_not_flagged:,}")

        st.markdown('<hr class="section-sep">', unsafe_allow_html=True)

        # Funnel chart
        fig_funnel = go.Figure(go.Funnel(
            y=["All Students", "Flagged by Model", "High-Risk Captured"],
            x=[len(filtered), total_flagged, high_in_flagged],
            textinfo="value+percent initial",
            marker={
                "color": ["#3b82f6", "#f59e0b", "#ef4444"],
                "line": {"color": ["rgba(0,0,0,0)"] * 3, "width": 0},
            },
        ))
        fig_funnel.update_layout(
            title="Intervention Funnel",
            paper_bgcolor="rgba(28,35,46,1)",
            plot_bgcolor="rgba(28,35,46,1)",
            font=dict(family="Inter, sans-serif", color="#e6edf3"),
            margin=dict(l=24, r=24, t=48, b=24),
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

        st.markdown("#### Workload by Intervention Strategy")
        if total_flagged:
            strategy_work = (
                flagged["recommended_intervention_strategy"]
                .fillna("Unassigned")
                .value_counts()
                .reset_index()
            )
            strategy_work.columns = ["Strategy", "Students"]
            strategy_work["Share %"] = (
                strategy_work["Students"] / strategy_work["Students"].sum() * 100.0
            ).round(1)
            fig_workload = px.bar(
                strategy_work, x="Students", y="Strategy",
                orientation="h", text="Students",
                color="Share %", color_continuous_scale=[[0, "#3b82f6"], [1, "#ef4444"]],
                template=PLOTLY_TEMPLATE,
            )
            fig_workload.update_layout(yaxis={"categoryorder": "total ascending"}, height=400)
            apply_theme(fig_workload)
            st.plotly_chart(fig_workload, use_container_width=True)
            st.dataframe(strategy_work, use_container_width=True)
        else:
            st.info("No students flagged at the current threshold.")

        st.markdown("#### Impact Efficiency Summary")
        st.info(
            f"At threshold **{active_threshold:.4f}** ({mode} mode), contacting "
            f"**{total_flagged:,}** students ({total_flagged / len(filtered) * 100.0:.1f}% of cohort) "
            f"captures **{high_capture:.1f}%** of high-risk students. "
            f"Approximately **{fp_count:,}** contacts ({fp_rate:.1f}%) are false positives."
        )
    else:
        st.warning("No students match current filters.")

# ══════════════════════════════════════════════════════════════════════════════
# Tab 6 — Cohort Insights
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("#### 🔬 Cohort Insights")
    st.caption("Identify where risk concentrates across cohort dimensions.")

    cohort_src = load_cohort_data()
    cohort_df = filtered.merge(cohort_src, on="Student_ID", how="left") if cohort_src is not None else filtered.copy()

    cohort_dimensions = [c for c in ["Department", "Semester", "Gender", "Part_Time_Job"] if c in cohort_df.columns]

    if not cohort_dimensions:
        st.warning(
            "No cohort dimension columns found. Place `student_dropout_dataset_v3.csv` in the `data/` folder "
            "for department, semester, gender, and job-status breakdowns."
        )
    elif len(cohort_df) == 0:
        st.info("No rows after filtering.")
    else:
        selected_dim = st.selectbox("🔎 Cohort dimension", options=cohort_dimensions)

        st.markdown(f"#### Risk Level Distribution by {selected_dim}")
        level_by_dim = (
            cohort_df.groupby([selected_dim, "burnout_risk_level"])
            .size()
            .reset_index(name="Count")
        )
        fig_stacked = px.bar(
            level_by_dim, x=selected_dim, y="Count",
            color="burnout_risk_level", barmode="stack",
            color_discrete_map=RISK_COLORS,
            template=PLOTLY_TEMPLATE,
        )
        fig_stacked.update_layout(xaxis_title=selected_dim, yaxis_title="Students")
        apply_theme(fig_stacked)
        st.plotly_chart(fig_stacked, use_container_width=True)

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
            avg_risk, x=selected_dim, y="Avg Risk Score",
            color="Avg Risk Score",
            color_continuous_scale=[[0, "#22c55e"], [0.5, "#f59e0b"], [1, "#ef4444"]],
            text="Avg Risk Score",
            template=PLOTLY_TEMPLATE,
        )
        fig_heat.update_traces(textposition="outside")
        apply_theme(fig_heat)
        st.plotly_chart(fig_heat, use_container_width=True)

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
        dim_summary["Avg_Risk"]    = dim_summary["Avg_Risk"].round(1)
        dim_summary = dim_summary.sort_values("High_Rate_%", ascending=False)
        fig_hr = px.bar(
            dim_summary, x=selected_dim, y="High_Rate_%",
            text="High_Rate_%",
            color="High_Rate_%",
            color_continuous_scale=[[0, "#22c55e"], [0.5, "#f59e0b"], [1, "#ef4444"]],
            template=PLOTLY_TEMPLATE,
        )
        fig_hr.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_hr.update_layout(xaxis_title=selected_dim, yaxis_title="High-risk rate (%)")
        apply_theme(fig_hr)
        st.plotly_chart(fig_hr, use_container_width=True)

        st.markdown(f"#### Summary Table — {selected_dim}")
        st.dataframe(dim_summary, use_container_width=True)

        if len(cohort_dimensions) >= 2:
            st.markdown("#### Cross-Dimension Heatmap (Avg Risk Score)")
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
                color_continuous_scale=[[0, "#22c55e"], [0.5, "#f59e0b"], [1, "#ef4444"]],
                labels={"color": "Avg Risk Score"},
                aspect="auto",
                template=PLOTLY_TEMPLATE,
            )
            fig_heatmap.update_layout(height=500)
            apply_theme(fig_heatmap)
            st.plotly_chart(fig_heatmap, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="section-sep">', unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align:center; color:#6e7681; font-size:0.78rem; padding: 0.5rem 0 1rem;">
      🎓 <strong>BehAnalytics</strong> &nbsp;·&nbsp;
      Modes: <em>balanced</em> for general evaluation &nbsp;|&nbsp;
      <em>high_recall</em> to maximise intervention catch rate with more false positives.
    </div>
    """,
    unsafe_allow_html=True,
)
