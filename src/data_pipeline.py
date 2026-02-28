from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


def _feedback_from_stress(stress: float) -> str:
    if pd.isna(stress):
        return "I am managing, but I need occasional support."
    if stress >= 7.5:
        return "I feel overwhelmed with deadlines and cannot keep up with coursework."
    if stress >= 5.0:
        return "I am under pressure and struggling to balance studies."
    return "I feel confident and on track with my learning goals."


def _sentiment_from_feedback(text: str) -> float:
    text_l = text.lower()
    negative_words = ["overwhelmed", "struggling", "cannot", "pressure"]
    positive_words = ["confident", "on track", "goals", "managing"]
    score = 0
    for word in negative_words:
        if word in text_l:
            score -= 1
    for word in positive_words:
        if word in text_l:
            score += 1
    return float(np.clip(score / 4, -1, 1))


def load_dropout_data(data_dir: Path) -> pd.DataFrame:
    return pd.read_csv(data_dir / "student_dropout_dataset_v3.csv")


def load_interaction_data(data_dir: Path) -> pd.DataFrame:
    return pd.read_csv(data_dir / "student_learning_interaction_dataset.csv")


def aggregate_interactions(interactions: pd.DataFrame) -> pd.DataFrame:
    df = interactions.copy()
    df["student_num"] = df["student_id"].str.replace("S", "", regex=False).astype(int)
    agg = (
        df.groupby("student_num", as_index=False)
        .agg(
            session_count=("session_id", "count"),
            avg_time_spent_minutes=("time_spent_minutes", "mean"),
            avg_pages_visited=("pages_visited", "mean"),
            avg_video_watched_percent=("video_watched_percent", "mean"),
            avg_click_events=("click_events", "mean"),
            avg_attention_score=("attention_score", "mean"),
            avg_days_since_last_activity=("days_since_last_activity", "mean"),
            success_rate=("success_label", "mean"),
        )
    )
    return agg


def build_feature_table(data_dir: Path) -> pd.DataFrame:
    dropout_df = load_dropout_data(data_dir)
    interactions_df = load_interaction_data(data_dir)
    inter_agg = aggregate_interactions(interactions_df)

    merged = dropout_df.merge(
        inter_agg,
        left_on="Student_ID",
        right_on="student_num",
        how="left",
    ).drop(columns=["student_num"], errors="ignore")

    merged["synthetic_feedback"] = merged["Stress_Index"].apply(_feedback_from_stress)
    merged["sentiment_score"] = merged["synthetic_feedback"].apply(_sentiment_from_feedback)

    numeric_cols = merged.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = merged.select_dtypes(exclude=[np.number]).columns.tolist()

    for col in numeric_cols:
        merged[col] = merged[col].fillna(merged[col].median())
    for col in categorical_cols:
        merged[col] = merged[col].fillna("Unknown")

    return merged
