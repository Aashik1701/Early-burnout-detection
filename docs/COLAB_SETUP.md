# Colab Setup

## Option A: Open from GitHub
1. Push this folder to GitHub.
2. In Colab: `File -> Open notebook -> GitHub`.
3. Select notebook from `notebooks/`.

## Option B: Open from Drive
1. Upload `BehAnalytics` folder to Google Drive.
2. Open notebook in Colab from Drive.

## Install dependencies in Colab
Run this once in the first notebook cell:

```python
!pip install -q -r requirements.txt
```

If path resolution fails, set manually:

```python
from pathlib import Path
PROJECT_ROOT = Path('/content/drive/MyDrive/BehAnalytics')
```
