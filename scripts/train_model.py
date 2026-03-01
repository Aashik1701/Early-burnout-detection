from pathlib import Path
import sys
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.modeling import save_artifacts, train_dropout_model
from src.risk_engine import (
    adaptive_risk_bins,
    derive_disengagement_indicators,
    extract_triggers,
    recommend_intervention,
    risk_level_from_score,
)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    artifacts_dir = root / "artifacts"
    feature_path = artifacts_dir / "engineered_features.csv"

    if not feature_path.exists():
        raise FileNotFoundError("Run scripts/prepare_data.py first to generate engineered_features.csv")

    df = pd.read_csv(feature_path)
    output = train_dropout_model(df)

    # Score all students on full feature table
    feature_cols = output["feature_cols"]
    preprocessor = output["preprocessor"]
    best_model = output["best_model"]
    scorer_model = output.get("scorer_model", best_model)
    optimal_threshold = output["optimal_threshold"]

    X_full = df[feature_cols]
    X_full_proc = preprocessor.transform(X_full)
    if hasattr(X_full_proc, "toarray"):
        X_full_proc = X_full_proc.toarray()

    probas_full = scorer_model.predict_proba(X_full_proc)[:, 1]

    predictions = df[["Student_ID"]].copy()
    predictions["dropout_probability"] = probas_full.round(4)
    predictions["risk_score"] = (probas_full * 100).round(1)

    thresh_score, high_cutoff = adaptive_risk_bins(
        predictions["risk_score"], optimal_threshold
    )
    predictions["burnout_risk_level"] = predictions["risk_score"].apply(
        lambda score: risk_level_from_score(score, thresh_score, high_cutoff)
    )

    feature_names = np.array(preprocessor.get_feature_names_out())
    importances = best_model.feature_importances_
    predictions["key_behavioural_triggers"] = extract_triggers(
        X_full_proc=X_full_proc,
        feature_names=feature_names,
        importances=importances,
        top_k=5,
    )
    predictions["academic_disengagement_indicators"] = predictions[
        "key_behavioural_triggers"
    ].apply(derive_disengagement_indicators)
    predictions["recommended_intervention_strategy"] = predictions.apply(
        lambda row: recommend_intervention(
            row["key_behavioural_triggers"], row["burnout_risk_level"]
        ),
        axis=1,
    )

    save_artifacts(output, df, predictions, artifacts_dir)

    diagnostics_path = artifacts_dir / "model_selection_diagnostics.json"
    with diagnostics_path.open("w", encoding="utf-8") as f:
        json.dump(output.get("diagnostics", []), f, indent=2, default=str)

    print("Training complete")
    print(f"Model:    {output['best_name']}")
    print(f"Calib:    {output['metrics'].get('calibration', 'none')}")
    print(f"Threshold:{output['optimal_threshold']:.4f}")
    print(f"Accuracy: {output['metrics']['accuracy']:.4f}")
    print(f"Precision:{output['metrics']['precision']:.4f}")
    print(f"Recall:   {output['metrics']['recall']:.4f}")
    print(f"F1:       {output['metrics']['f1']:.4f}")
    print(f"ROC-AUC:  {output['metrics']['roc_auc']:.4f}")
    print(f"PR-AUC:   {output['metrics'].get('pr_auc', 0.0):.4f}")
    print(f"Brier:    {output['metrics'].get('brier', 0.0):.6f}")

    mode_metrics = output["metrics"].get("mode_metrics", {})
    if mode_metrics:
        print("\nMode Comparison:")
        for mode_name in ["balanced", "high_recall"]:
            if mode_name in mode_metrics:
                mm = mode_metrics[mode_name]
                print(
                    f"  {mode_name:11s} | thr={mm['threshold']:.4f} "
                    f"acc={mm['accuracy']:.4f} prec={mm['precision']:.4f} "
                    f"rec={mm['recall']:.4f} f1={mm['f1']:.4f}"
                )
            
