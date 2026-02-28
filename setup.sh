#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name behanalytics --display-name "BehAnalytics (venv)"

echo "Environment ready. Activate with: source .venv/bin/activate"
