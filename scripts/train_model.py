from pathlib import Path

import pandas as pd

from src.modeling import save_artifacts, train_dropout_model


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    artifacts_dir = root / "artifacts"
    feature_path = artifacts_dir / "engineered_features.csv"

    if not feature_path.exists():
        raise FileNotFoundError("Run scripts/prepare_data.py first to generate engineered_features.csv")

    df = pd.read_csv(feature_path)
    output = train_dropout_model(df)
    save_artifacts(output, artifacts_dir)

    print("Training complete")
    print(f"Accuracy: {output['metrics']['accuracy']:.4f}")
    print(f"ROC-AUC:  {output['metrics']['roc_auc']:.4f}")
