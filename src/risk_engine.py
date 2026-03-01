"""
BehAnalytics — Risk Scoring & Intervention Engine.

Adaptive risk bins, actionable trigger extraction (with
non-actionable keyword blocklist), and rank-order intervention
matching.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Non-actionable feature keywords (remain in model, hidden from triggers)
# ---------------------------------------------------------------------------
NON_ACTIONABLE_KEYWORDS: List[str] = [
    "family_income", "travel_time", "age", "gender", "part_time_job",
    "scholarship", "internet_access", "parental_education",
    "department", "semester",
]

# ---------------------------------------------------------------------------
# Intervention rules — checked in priority order
# ---------------------------------------------------------------------------
INTERVENTION_RULES: List[Tuple[List[str], str]] = [
    (["attendance"],
     "Engagement counselling + attendance monitoring plan"),
    (["assignment_delay", "delay", "assignment_completion"],
     "Schedule academic-advisor meeting; consider deadline extension"),
    (["stress", "sentiment"],
     "Refer to student well-being / mental-health services"),
    (["study_hours", "gpa", "cgpa", "semester_gpa"],
     "Enrol in peer-tutoring or supplemental-instruction programme"),
    (["time_spent", "pages_visited", "video_watched", "click_events", "attention_score"],
     "Digital engagement coaching — improve learning platform usage"),
    (["days_since_last", "success_rate", "session_count"],
     "Proactive outreach — schedule regular check-ins with mentor"),
]

DISENGAGEMENT_RULES: List[Tuple[List[str], str]] = [
    (["attendance"], "Attendance decline"),
    (["assignment_delay", "delay", "assignment_completion"], "Assignment delay pattern"),
    (["study_hours", "gpa", "cgpa", "semester_gpa"], "Academic performance pressure"),
    (["time_spent", "pages_visited", "video_watched", "click_events", "attention_score"], "Low LMS engagement"),
    (["days_since_last", "session_count", "success_rate"], "Irregular activity pattern"),
    (["stress", "sentiment"], "Emotional distress signal"),
]


# ---------------------------------------------------------------------------
# Risk scoring
# ---------------------------------------------------------------------------

def adaptive_risk_bins(
    risk_scores: pd.Series,
    optimal_threshold: float,
    high_percentile: int = 85,
) -> Tuple[float, float]:
    """Return (low_cutoff, high_cutoff) for adaptive risk bins.

    * Low  : score ≤ threshold_score  (≈ 30)
    * Medium: threshold_score < score ≤ 85th-percentile
    * High : above 85th-percentile
    """
    thresh_score = round(optimal_threshold * 100, 1)
    high_cutoff = float(np.percentile(risk_scores, high_percentile))
    return thresh_score, high_cutoff


def risk_level_from_score(
    score: float,
    thresh_score: float,
    high_cutoff: float,
) -> str:
    """Assign risk level using adaptive bin boundaries."""
    if score <= thresh_score:
        return "Low"
    elif score <= high_cutoff:
        return "Medium"
    return "High"


# ---------------------------------------------------------------------------
# Trigger extraction
# ---------------------------------------------------------------------------

def _is_actionable(fname: str) -> bool:
    fname_lower = fname.lower()
    return not any(kw in fname_lower for kw in NON_ACTIONABLE_KEYWORDS)


def extract_triggers(
    X_full_proc: np.ndarray,
    feature_names: np.ndarray,
    importances: np.ndarray,
    top_k: int = 5,
) -> List[str]:
    """Return a list of comma-separated top-K actionable triggers per student."""
    actionable_mask = np.array([_is_actionable(f) for f in feature_names])

    medians = np.median(X_full_proc, axis=0)
    deviations = np.abs(X_full_proc - medians)
    weighted = deviations * importances

    # Zero-out non-actionable features
    weighted_filtered = weighted.copy()
    weighted_filtered[:, ~actionable_mask] = 0.0

    triggers: List[str] = []
    for i in range(X_full_proc.shape[0]):
        top_idxs = np.argsort(weighted_filtered[i])[::-1][:top_k]
        names = [feature_names[j].split("__")[-1] for j in top_idxs]
        triggers.append(", ".join(names))
    return triggers


# ---------------------------------------------------------------------------
# Intervention recommendation
# ---------------------------------------------------------------------------

def recommend_intervention(triggers: str, risk_level: str) -> str:
    """Rank-order matching: walk triggers most-important → least, first hit wins."""
    trigger_list = [t.strip().lower() for t in triggers.split(",")]

    for trigger in trigger_list:
        for keywords, action in INTERVENTION_RULES:
            if any(kw in trigger for kw in keywords):
                if risk_level == "High":
                    return f"URGENT — {action}"
                return action

    # Fallback
    if risk_level == "High":
        return "URGENT — General academic-support check-in with counsellor"
    return "General academic-support check-in"


def derive_disengagement_indicators(triggers: str, top_n: int = 2) -> str:
    """Map trigger text into compact academic disengagement indicator labels."""
    trigger_list = [t.strip().lower() for t in triggers.split(",") if t.strip()]
    indicators: List[str] = []

    for trigger in trigger_list:
        for keywords, label in DISENGAGEMENT_RULES:
            if any(kw in trigger for kw in keywords):
                if label not in indicators:
                    indicators.append(label)
                break
        if len(indicators) >= top_n:
            break

    if not indicators:
        indicators.append("General engagement fluctuation")

    return ", ".join(indicators)


# ---------------------------------------------------------------------------
# Convenience: build full prediction payload
# ---------------------------------------------------------------------------

def build_prediction_payload(
    probability: float,
    triggers: List[str],
    thresh_score: float,
    high_cutoff: float,
) -> Dict[str, object]:
    score = round(probability * 100, 2)
    level = risk_level_from_score(score, thresh_score, high_cutoff)
    triggers_str = ", ".join(triggers)
    return {
        "dropout_probability": round(probability, 4),
        "risk_score": score,
        "burnout_risk_level": level,
        "academic_disengagement_indicators": derive_disengagement_indicators(triggers_str),
        "key_behavioural_triggers": triggers_str,
        "recommended_intervention_strategy": recommend_intervention(triggers_str, level),
    }
