"""
BehAnalytics — Model Training Module.

Trains RandomForest and XGBoost on SMOTE-balanced data, picks the
winner by ROC-AUC, and tunes the classification threshold to
maximise F1 with recall ≥ 0.70.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TARGET = "Dropout"
EXCLUDED = {"Student_ID", "synthetic_feedback", TARGET}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def train_dropout_model(
    df: pd.DataFrame,
    random_state: int = 42,
    test_size: float = 0.2,
    recall_floor: float = 0.70,
) -> Dict[str, Any]:
    """Train RF vs XGBoost with SMOTE, threshold-tune, and return results."""

    feature_cols = [c for c in df.columns if c not in EXCLUDED]

    X = df[feature_cols]
    y = df[TARGET].astype(int)

    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()

    # ── Preprocessor ──────────────────────────────────────────
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), num_cols),
            ("cat", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ]), cat_cols),
        ]
    )

    # ── Split ─────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state,
    )

    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)

    if hasattr(X_train_proc, "toarray"):
        X_train_proc = X_train_proc.toarray()
    if hasattr(X_test_proc, "toarray"):
        X_test_proc = X_test_proc.toarray()

    # ── SMOTE (training set only) ─────────────────────────────
    smote = SMOTE(random_state=random_state)
    X_train_sm, y_train_sm = smote.fit_resample(X_train_proc, y_train)

    # ── Model A: RandomForest ─────────────────────────────────
    rf = RandomForestClassifier(
        n_estimators=400, random_state=random_state,
        class_weight="balanced", n_jobs=-1,
    )
    rf.fit(X_train_sm, y_train_sm)
    rf_auc = roc_auc_score(y_test, rf.predict_proba(X_test_proc)[:, 1])

    # ── Model B: XGBoost ──────────────────────────────────────
    xgb = XGBClassifier(
        n_estimators=400, learning_rate=0.05, max_depth=6,
        scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
        random_state=random_state, eval_metric="logloss",
        use_label_encoder=False, n_jobs=-1,
    )
    xgb.fit(X_train_sm, y_train_sm)
    xgb_auc = roc_auc_score(y_test, xgb.predict_proba(X_test_proc)[:, 1])

    # ── Pick winner ───────────────────────────────────────────
    if xgb_auc >= rf_auc:
        best_model, best_name = xgb, "XGBoost"
    else:
        best_model, best_name = rf, "RandomForest"

    # ── Threshold tuning ──────────────────────────────────────
    y_proba = best_model.predict_proba(X_test_proc)[:, 1]
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba)
    f1_scores = 2 * (precisions[:-1] * recalls[:-1]) / (precisions[:-1] + recalls[:-1] + 1e-8)

    mask = recalls[:-1] >= recall_floor
    if mask.any():
        best_idx = np.argmax(f1_scores * mask)
    else:
        best_idx = np.argmax(f1_scores)

    optimal_threshold = float(thresholds[best_idx])

    y_pred = (y_proba >= optimal_threshold).astype(int)

    metrics: Dict[str, Any] = {
        "model": best_name,
        "threshold": round(optimal_threshold, 4),
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred)), 4),
        "recall": round(float(recall_score(y_test, y_pred)), 4),
        "f1": round(float(f1_score(y_test, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
        "classification_report": classification_report(
            y_test, y_pred, target_names=["No Dropout", "Dropout"], output_dict=True,
        ),
    }

    return {
        "preprocessor": preprocessor,
        "best_model": best_model,
        "best_name": best_name,
        "optimal_threshold": optimal_threshold,
        "X_test": X_test,
        "X_test_proc": X_test_proc,
        "y_test": y_test,
        "y_pred": y_pred,
        "y_proba": y_proba,
        "metrics": metrics,
        "feature_cols": feature_cols,
        "rf_auc": rf_auc,
        "xgb_auc": xgb_auc,
    }


def save_artifacts(
    train_output: Dict[str, Any],
    df: pd.DataFrame,
    predictions: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Persist model bundle, metrics JSON, and predictions CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Model bundle
    model_path = output_dir / "dropout_model.joblib"
    joblib.dump(
        {
            "preprocessor": train_output["preprocessor"],
            "model": train_output["best_model"],
            "threshold": train_output["optimal_threshold"],
            "feature_cols": train_output["feature_cols"],
        },
        model_path,
    )

    # Metrics JSON
    metrics_path = output_dir / "metrics.json"
    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump(train_output["metrics"], f, indent=2)

    # Predictions CSV
    csv_cols = [
        "Student_ID",
        "dropout_probability",
        "risk_score",
        "burnout_risk_level",
        "key_behavioural_triggers",
        "recommended_intervention_strategy",
    ]
    pred_path = output_dir / "predictions.csv"
    predictions[[c for c in csv_cols if c in predictions.columns]].to_csv(
        pred_path, index=False,
    )
