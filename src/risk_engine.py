from __future__ import annotations

from typing import Dict, List


def risk_level_from_score(score_0_100: float) -> str:
    if score_0_100 <= 33:
        return "Low"
    if score_0_100 <= 66:
        return "Medium"
    return "High"


def recommend_intervention(triggers: List[str], risk_level: str) -> str:
    trigger_text = " ".join(t.lower() for t in triggers)

    if "assignment_delay" in trigger_text:
        return "Notify academic advisor and provide 48-hour assignment extension with follow-up check-in."
    if "attendance" in trigger_text:
        return "Schedule attendance counseling and weekly mentor tracking for the next month."
    if "stress" in trigger_text or "sentiment" in trigger_text:
        return "Refer to wellbeing counselor and enable low-load study plan for 2 weeks."

    if risk_level == "High":
        return "Initiate immediate advisor intervention and weekly progress monitoring."
    if risk_level == "Medium":
        return "Assign faculty mentor and monitor behavioural indicators bi-weekly."
    return "Continue current support plan with monthly progress review."


def build_prediction_payload(probability: float, triggers: List[str]) -> Dict[str, object]:
    score = round(probability * 100, 2)
    level = risk_level_from_score(score)
    return {
        "dropout_probability": round(probability, 4),
        "risk_score": score,
        "burnout_risk_level": level,
        "key_behavioural_triggers": triggers,
        "recommended_intervention_strategy": recommend_intervention(triggers, level),
    }
