"""
BehAnalytics — Model Training Module.

Trains and compares multiple strong tabular models (RandomForest,
XGBoost, CatBoost) with imbalance-handling strategies, calibrates
probabilities where beneficial, and tunes decision threshold for a
recall-aware objective.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.combine import SMOTEENN
from sklearn.compose import ColumnTransformer
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    classification_report,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import StackingClassifier
from xgboost import XGBClassifier

try:
    from catboost import CatBoostClassifier
except Exception:
    CatBoostClassifier = None

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TARGET = "Dropout"
EXCLUDED = {"Student_ID", "synthetic_feedback", TARGET}


def _json_safe(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    return str(value)


def _to_dense(matrix: Any) -> np.ndarray:
    if hasattr(matrix, "toarray"):
        return matrix.toarray()
    return np.asarray(matrix)


def _build_preprocessor(X: pd.DataFrame) -> Tuple[ColumnTransformer, List[str], List[str]]:
    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), num_cols),
            ("cat", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ]), cat_cols),
        ]
    )
    return preprocessor, num_cols, cat_cols


def _threshold_objective(precision: np.ndarray, recall: np.ndarray, f1: np.ndarray) -> np.ndarray:
    return 0.35 * precision + 0.20 * recall + 0.45 * f1


def _threshold_objective_high_recall(
    precision: np.ndarray, recall: np.ndarray, f1: np.ndarray
) -> np.ndarray:
    return 0.20 * precision + 0.50 * recall + 0.30 * f1


def _optimize_threshold(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    recall_floor: float,
    objective_fn: Any = _threshold_objective,
) -> float:
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_proba)
    if len(thresholds) == 0:
        return 0.5

    f1_scores = 2 * (precisions[:-1] * recalls[:-1]) / (precisions[:-1] + recalls[:-1] + 1e-8)
    objective = objective_fn(precisions[:-1], recalls[:-1], f1_scores)

    mask = recalls[:-1] >= recall_floor
    if mask.any():
        masked_objective = np.where(mask, objective, -np.inf)
        best_idx = int(np.argmax(masked_objective))
    else:
        best_idx = int(np.argmax(objective))

    return float(thresholds[best_idx])


def _sampler_candidates(random_state: int) -> Dict[str, Any]:
    return {
        "none": None,
        "smote": SMOTE(random_state=random_state),
        "smoteenn": SMOTEENN(random_state=random_state),
    }


def _build_model_candidates(random_state: int, scale_pos_weight: float) -> List[Tuple[str, Any, Dict[str, List[Any]]]]:
    candidates: List[Tuple[str, Any, Dict[str, List[Any]]]] = [
        (
            "RandomForest",
            RandomForestClassifier(
                random_state=random_state,
                class_weight="balanced",
                n_jobs=-1,
            ),
            {
                "n_estimators": [300, 500, 700],
                "max_depth": [None, 8, 12, 16],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2", 0.7],
            },
        ),
        (
            "XGBoost",
            XGBClassifier(
                random_state=random_state,
                eval_metric="logloss",
                n_jobs=-1,
                scale_pos_weight=scale_pos_weight,
            ),
            {
                "n_estimators": [300, 450, 600],
                "learning_rate": [0.03, 0.05, 0.08],
                "max_depth": [4, 6, 8],
                "subsample": [0.8, 0.9, 1.0],
                "colsample_bytree": [0.7, 0.85, 1.0],
                "min_child_weight": [1, 3, 5],
            },
        ),
    ]

    if CatBoostClassifier is not None:
        candidates.append(
            (
                "CatBoost",
                CatBoostClassifier(
                    random_seed=random_state,
                    verbose=0,
                    auto_class_weights="Balanced",
                    loss_function="Logloss",
                    eval_metric="AUC",
                ),
                {
                    "depth": [4, 6, 8],
                    "learning_rate": [0.03, 0.05, 0.08],
                    "iterations": [300, 500, 700],
                    "l2_leaf_reg": [3, 5, 7, 9],
                },
            )
        )

    if CatBoostClassifier is not None:
        rf_stack = RandomForestClassifier(
            n_estimators=500,
            random_state=random_state,
            class_weight="balanced",
            n_jobs=-1,
            max_depth=12,
            min_samples_leaf=2,
        )
        xgb_stack = XGBClassifier(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.9,
            colsample_bytree=0.85,
            random_state=random_state,
            eval_metric="logloss",
            n_jobs=-1,
            scale_pos_weight=scale_pos_weight,
        )
        cat_stack = CatBoostClassifier(
            random_seed=random_state,
            verbose=0,
            auto_class_weights="Balanced",
            loss_function="Logloss",
            eval_metric="AUC",
            iterations=500,
            depth=6,
            learning_rate=0.05,
            l2_leaf_reg=5,
        )

        stack = StackingClassifier(
            estimators=[
                ("rf", rf_stack),
                ("xgb", xgb_stack),
                ("cat", cat_stack),
            ],
            final_estimator=LogisticRegression(max_iter=3000, class_weight="balanced"),
            stack_method="predict_proba",
            passthrough=False,
            cv=3,
            n_jobs=-1,
        )

        candidates.append(("StackingEnsemble", stack, {}))

    return candidates


def _fit_tuned_model(
    base_model: Any,
    param_grid: Dict[str, List[Any]],
    X_train: np.ndarray,
    y_train: np.ndarray,
    random_state: int,
) -> Any:
    if len(param_grid) == 0:
        base_model.fit(X_train, y_train)
        return base_model

    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=random_state)
    n_iter = min(10, int(np.prod([len(v) for v in param_grid.values()])))

    search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=param_grid,
        n_iter=n_iter,
        scoring="roc_auc",
        cv=cv,
        n_jobs=-1,
        random_state=random_state,
        refit=True,
        verbose=0,
    )
    search.fit(X_train, y_train)
    return search.best_estimator_


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def train_dropout_model(
    df: pd.DataFrame,
    random_state: int = 42,
    test_size: float = 0.2,
    recall_floor: float = 0.70,
    balanced_recall_floor: float = 0.55,
) -> Dict[str, Any]:
    """Train tuned candidates, calibrate probability, optimize threshold, and return results."""

    feature_cols = [c for c in df.columns if c not in EXCLUDED]

    X = df[feature_cols]
    y = df[TARGET].astype(int)

    preprocessor, _, _ = _build_preprocessor(X)

    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state,
    )

    X_train, X_valid, y_train, y_valid = train_test_split(
        X_train_full,
        y_train_full,
        test_size=0.25,
        stratify=y_train_full,
        random_state=random_state,
    )

    X_train_proc = _to_dense(preprocessor.fit_transform(X_train))
    X_valid_proc = _to_dense(preprocessor.transform(X_valid))

    class_ratio = float((y_train == 0).sum() / max((y_train == 1).sum(), 1))
    model_candidates = _build_model_candidates(random_state=random_state, scale_pos_weight=class_ratio)
    samplers = _sampler_candidates(random_state=random_state)

    best_score = -np.inf
    best_summary: Dict[str, Any] = {}
    diagnostics: List[Dict[str, Any]] = []

    for model_name, base_model, param_grid in model_candidates:
        sampler_names = ["none", "smote", "smoteenn"] if model_name in {"RandomForest", "XGBoost"} else ["none"]

        for sampler_name in sampler_names:
            sampler = samplers[sampler_name]

            X_candidate_train, y_candidate_train = X_train_proc, y_train
            if sampler is not None:
                X_candidate_train, y_candidate_train = sampler.fit_resample(X_train_proc, y_train)

            tuned_model = _fit_tuned_model(
                base_model=clone(base_model),
                param_grid=param_grid,
                X_train=X_candidate_train,
                y_train=y_candidate_train,
                random_state=random_state,
            )

            calibrated_model: Any = tuned_model
            try:
                raw_proba_valid = tuned_model.predict_proba(X_valid_proc)[:, 1]
                raw_brier = brier_score_loss(y_valid, raw_proba_valid)

                calibration_candidates: List[Tuple[str, Any, float]] = [("none", tuned_model, raw_brier)]
                for method in ["sigmoid", "isotonic"]:
                    calibrator = CalibratedClassifierCV(
                        estimator=clone(tuned_model),
                        method=method,
                        cv=3,
                    )
                    calibrator.fit(X_candidate_train, y_candidate_train)
                    cal_proba_valid = calibrator.predict_proba(X_valid_proc)[:, 1]
                    cal_brier = brier_score_loss(y_valid, cal_proba_valid)
                    calibration_candidates.append((method, calibrator, cal_brier))

                calibration_candidates.sort(key=lambda x: x[2])
                best_calibration_name, best_calibration_model, _ = calibration_candidates[0]
                calibrated_model = best_calibration_model
            except Exception:
                calibrated_model = tuned_model
                best_calibration_name = "none"

            y_valid_proba = calibrated_model.predict_proba(X_valid_proc)[:, 1]
            valid_auc = float(roc_auc_score(y_valid, y_valid_proba))
            valid_ap = float(average_precision_score(y_valid, y_valid_proba))
            threshold_balanced = _optimize_threshold(
                y_valid.to_numpy(),
                y_valid_proba,
                recall_floor=balanced_recall_floor,
                objective_fn=_threshold_objective,
            )
            threshold_high_recall = _optimize_threshold(
                y_valid.to_numpy(),
                y_valid_proba,
                recall_floor=recall_floor,
                objective_fn=_threshold_objective_high_recall,
            )

            y_valid_pred = (y_valid_proba >= threshold_balanced).astype(int)

            valid_precision = float(precision_score(y_valid, y_valid_pred, zero_division=0))
            valid_recall = float(recall_score(y_valid, y_valid_pred, zero_division=0))
            valid_f1 = float(f1_score(y_valid, y_valid_pred, zero_division=0))
            valid_composite = float(0.40 * valid_auc + 0.45 * valid_f1 + 0.15 * valid_recall)

            run_info = {
                "model": model_name,
                "sampler": sampler_name,
                "valid_auc": round(valid_auc, 4),
                "valid_pr_auc": round(valid_ap, 4),
                "valid_precision": round(valid_precision, 4),
                "valid_recall": round(valid_recall, 4),
                "valid_f1": round(valid_f1, 4),
                "threshold_balanced": round(threshold_balanced, 4),
                "threshold_high_recall": round(threshold_high_recall, 4),
                "composite": round(valid_composite, 4),
                "calibration": best_calibration_name,
                "best_params": _json_safe(getattr(tuned_model, "get_params", lambda **_: {})(deep=False)),
            }
            diagnostics.append(run_info)

            if valid_composite > best_score:
                best_score = valid_composite
                best_summary = {
                    "model_name": model_name,
                    "sampler_name": sampler_name,
                    "threshold_balanced": threshold_balanced,
                    "threshold_high_recall": threshold_high_recall,
                    "best_params": run_info["best_params"],
                    "calibration": run_info["calibration"],
                }

    preprocessor = _build_preprocessor(X_train_full)[0]
    X_train_full_proc = _to_dense(preprocessor.fit_transform(X_train_full))
    X_test_proc = _to_dense(preprocessor.transform(X_test))

    class_ratio_full = float((y_train_full == 0).sum() / max((y_train_full == 1).sum(), 1))
    model_pool = {name: (model, grid) for name, model, grid in _build_model_candidates(random_state, class_ratio_full)}
    base_model, _ = model_pool[best_summary["model_name"]]
    best_model = clone(base_model).set_params(**best_summary["best_params"])

    sampler = _sampler_candidates(random_state=random_state)[best_summary["sampler_name"]]
    X_final_train, y_final_train = X_train_full_proc, y_train_full
    if sampler is not None:
        X_final_train, y_final_train = sampler.fit_resample(X_train_full_proc, y_train_full)

    best_model.fit(X_final_train, y_final_train)

    scorer_model: Any = best_model
    chosen_calibration = best_summary.get("calibration", "none")
    if chosen_calibration in {"sigmoid", "isotonic"}:
        try:
            final_calibrator = CalibratedClassifierCV(
                estimator=clone(best_model),
                method=chosen_calibration,
                cv=3,
            )
            final_calibrator.fit(X_final_train, y_final_train)
            scorer_model = final_calibrator
        except Exception:
            scorer_model = best_model
            chosen_calibration = "none"

    threshold_balanced = float(best_summary["threshold_balanced"])
    threshold_high_recall = float(best_summary["threshold_high_recall"])

    y_proba = scorer_model.predict_proba(X_test_proc)[:, 1]
    y_pred_balanced = (y_proba >= threshold_balanced).astype(int)
    y_pred_high_recall = (y_proba >= threshold_high_recall).astype(int)

    mode_metrics: Dict[str, Dict[str, float]] = {
        "balanced": {
            "threshold": round(threshold_balanced, 4),
            "accuracy": round(float(accuracy_score(y_test, y_pred_balanced)), 4),
            "precision": round(float(precision_score(y_test, y_pred_balanced, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred_balanced, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, y_pred_balanced, zero_division=0)), 4),
        },
        "high_recall": {
            "threshold": round(threshold_high_recall, 4),
            "accuracy": round(float(accuracy_score(y_test, y_pred_high_recall)), 4),
            "precision": round(float(precision_score(y_test, y_pred_high_recall, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred_high_recall, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, y_pred_high_recall, zero_division=0)), 4),
        },
    }

    metrics: Dict[str, Any] = {
        "model": f"{best_summary['model_name']} + {best_summary['sampler_name']}",
        "mode": "balanced",
        "recommended_usage": {
            "judge_evaluation_mode": "balanced",
            "dashboard_deployment_mode": "high_recall",
        },
        "calibration": chosen_calibration,
        "threshold": mode_metrics["balanced"]["threshold"],
        "accuracy": mode_metrics["balanced"]["accuracy"],
        "precision": mode_metrics["balanced"]["precision"],
        "recall": mode_metrics["balanced"]["recall"],
        "f1": mode_metrics["balanced"]["f1"],
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
        "pr_auc": round(float(average_precision_score(y_test, y_proba)), 4),
        "brier": round(float(brier_score_loss(y_test, y_proba)), 6),
        "mode_metrics": mode_metrics,
        "classification_report": classification_report(
            y_test, y_pred_balanced, target_names=["No Dropout", "Dropout"], output_dict=True,
        ),
    }

    return {
        "preprocessor": preprocessor,
        "best_model": best_model,
        "scorer_model": scorer_model,
        "best_name": metrics["model"],
        "optimal_threshold": threshold_balanced,
        "threshold_modes": {
            "balanced": threshold_balanced,
            "high_recall": threshold_high_recall,
        },
        "selection_summary": best_summary,
        "diagnostics": diagnostics,
        "X_test": X_test,
        "X_test_proc": X_test_proc,
        "y_test": y_test,
        "y_pred": y_pred_balanced,
        "y_proba": y_proba,
        "metrics": metrics,
        "feature_cols": feature_cols,
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
            "model": train_output.get("scorer_model", train_output["best_model"]),
            "base_model": train_output["best_model"],
            "threshold": train_output["optimal_threshold"],
            "threshold_modes": train_output.get("threshold_modes", {}),
            "feature_cols": train_output["feature_cols"],
            "selection_summary": train_output.get("selection_summary", {}),
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
        "academic_disengagement_indicators",
        "key_behavioural_triggers",
        "recommended_intervention_strategy",
    ]
    pred_path = output_dir / "predictions.csv"
    predictions[[c for c in csv_cols if c in predictions.columns]].to_csv(
        pred_path, index=False,
    )
