## Early detection pipeline for student burnout/disengagement/dropout risk using behavioural datasets.

## Project Structure

- `data/` - Provided datasets (`college_student_management_data.csv`, `student_dropout_dataset_v3.csv`, `student_learning_interaction_dataset.csv`)
- `notebooks/` - Colab-ready notebooks for EDA, feature engineering, and model training
- `src/` - Reusable Python modules (prep, training, risk engine)
- `configs/` - Model and feature configuration
- `artifacts/` - Saved models, encoders, and generated datasets
- `reports/` - Metrics and charts
- `scripts/` - Optional CLI scripts for local runs

## Quick Start (Local)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

## Quick Start (Colab)

1. Upload this folder to Google Drive or clone from GitHub.
2. Open notebook `notebooks/01_data_preparation.ipynb` in Colab.
3. Run all cells to create engineered data in `artifacts/`.
4. Open notebook `notebooks/02_model_training.ipynb` and run all cells.

## Deliverables Covered

- Risk score (0-100) via dropout probability
- Burnout risk category (Low/Medium/High)
- Key behavioural triggers via feature importance
- Rule-based intervention strategy
