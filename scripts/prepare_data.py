from pathlib import Path

from src.data_pipeline import build_feature_table


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    out_dir = root / "artifacts"
    out_dir.mkdir(exist_ok=True)

    feature_df = build_feature_table(data_dir)
    feature_df.to_csv(out_dir / "engineered_features.csv", index=False)
    print(f"Saved: {out_dir / 'engineered_features.csv'}")
