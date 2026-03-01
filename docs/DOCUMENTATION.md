# Sentinal AI — Project Documentation

> **Early Burnout & Dropout Detection System for Higher Education**
>
> A behavioural-analytics pipeline that identifies at-risk students before severe academic decline, produces personalised intervention recommendations, and serves results through an interactive decision-support dashboard.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Data & Features](#2-data--features)
3. [Model](#3-model)
4. [Architecture](#4-architecture)
5. [Results](#5-results)
6. [Behavioural Insights](#6-behavioural-insights)
7. [Practical Impact](#7-practical-impact)
8. [Future Scope](#8-future-scope)
9. [Appendix — Diagrams & Flowcharts](#9-appendix--diagrams--flowcharts)

---

## 1. Problem Statement

### 1.1 Context

Student dropout in higher education is a persistent, costly problem. Globally, dropout rates range from 20 % to 50 % depending on institution type. Each dropout represents:

- **Lost institutional investment** — recruitment, onboarding, and partial-year instruction costs that are never recovered.
- **Lost student potential** — interrupted career trajectories, accumulated debt without a credential, and diminished lifetime earnings.
- **Delayed detection** — most institutions discover a student is at risk only after grades collapse or attendance reaches critical thresholds, leaving little time for effective intervention.

### 1.2 The Core Problem

> **How can an institution identify students who are likely to burn out or drop out *early enough* — using behavioural and academic signals — so that targeted, resource-efficient interventions can be deployed before the point of no return?**

### 1.3 Requirements

| Requirement | Description |
|-------------|-------------|
| **Early detection** | Flag at-risk students using behavioural signals (engagement patterns, sentiment, attendance drift) — not just end-of-term grades. |
| **Actionable output** | Every flagged student must come with a personalised intervention recommendation, not just a risk label. |
| **Dual operating modes** | Support a *balanced* mode for general evaluation and a *high-recall* mode for deployment to maximise catch rate. |
| **Transparency** | Provide per-student behavioural triggers so counselors understand *why* the model flagged a student. |
| **Scalability** | Score 10,000+ students in batch, with a dashboard for non-technical staff. |
| **Resource awareness** | Respect limited counselor capacity — plan outreach in weekly slots, not just a flat list. |

### 1.4 Scope Boundaries

- **In scope:** Binary dropout prediction, risk scoring, burnout-risk classification, trigger extraction, intervention recommendation, interactive dashboard.
- **Out of scope:** Real-time streaming inference, integration with LMS APIs (future scope), longitudinal tracking across semesters.

---

## 2. Data & Features

### 2.1 Data Sources

The system fuses **three complementary datasets** to build a 360° behavioural profile of each student:

```
┌─────────────────────────────────────┐
│  student_dropout_dataset_v3.csv     │  10,000 rows × 19 columns
│  Primary student records            │  Target: Dropout (0/1)
│  Demographics, academics, stress    │
└──────────────┬──────────────────────┘
               │  JOIN on Student_ID
               ▼
┌─────────────────────────────────────┐
│  student_learning_interaction.csv   │  9,000 rows × 22 columns
│  LMS session-level interactions     │  Aggregated per student
│  Time spent, clicks, quiz, video    │
└──────────────┬──────────────────────┘
               │  Reference / validation
               ▼
┌─────────────────────────────────────┐
│  college_student_management.csv     │  1,545 rows × 15 columns
│  Supplementary management records   │  GPA, course load, LMS logins
└─────────────────────────────────────┘
```

### 2.2 Dataset Details

#### Dataset 1 — Student Dropout Records (Primary)

| Property | Value |
|----------|-------|
| File | `student_dropout_dataset_v3.csv` |
| Rows | 10,000 |
| Columns | 19 |
| Target | `Dropout` — binary (0 = retained, 1 = dropped out) |
| Class balance | 7,646 retained (76.5 %) vs 2,354 dropout (23.5 %) |

**Feature groups:**

| Group | Features | Role |
|-------|----------|------|
| Demographics | Age, Gender, Family_Income, Parental_Education | Context — non-actionable but predictive |
| Access | Internet_Access, Travel_Time_Minutes, Part_Time_Job, Scholarship | Socioeconomic factors |
| Academic | GPA, Semester_GPA, CGPA, Semester, Department | Performance signals |
| Behavioural | Study_Hours_per_Day, Attendance_Rate, Assignment_Delay_Days, Stress_Index | Core actionable features |

#### Dataset 2 — Learning Interaction Logs

| Property | Value |
|----------|-------|
| File | `student_learning_interaction_dataset.csv` |
| Rows | 9,000 session-level records |
| Columns | 22 |
| Key features | time_spent_minutes, pages_visited, video_watched_percent, click_events, attention_score, days_since_last_activity, quiz_score, success_label |

These are **aggregated per student** (mean, count) during feature engineering to produce:
- `session_count`, `avg_time_spent_minutes`, `avg_pages_visited`
- `avg_video_watched_percent`, `avg_click_events`, `avg_attention_score`
- `avg_days_since_last_activity`, `success_rate`

#### Dataset 3 — College Student Management (Reference)

| Property | Value |
|----------|-------|
| File | `college_student_management_data.csv` |
| Rows | 1,545 |
| Columns | 15 |
| Role | Supplementary validation; confirms feature directions (GPA, attendance, LMS logins) |

### 2.3 Feature Engineering Pipeline

```
Raw CSV Files
     │
     ▼
┌───────────────────────────────────────────────┐
│  src/data_pipeline.py                         │
│                                               │
│  1. load_dropout_data()                       │  ← 10,000 × 19
│  2. load_interaction_data()                   │  ← 9,000 × 22
│  3. aggregate_interactions()                  │  ← group by student → 8 features
│  4. merge on Student_ID                       │  ← LEFT JOIN → 10,000 × 27
│  5. _feedback_from_stress(Stress_Index)       │  ← synthetic feedback text
│  6. _sentiment_from_feedback(text)            │  ← sentiment score [-1, 1]
│  7. Impute: median (numeric), mode (cat)      │
│                                               │
│  Output: 10,000 × 29                          │
│  (27 original + synthetic_feedback +          │
│   sentiment_score)                            │
└───────────────────────────────────────────────┘
     │
     ▼
  artifacts/engineered_features.csv  (10,000 × 29)
```

### 2.4 Engineered Feature Table (29 columns)

| # | Feature | Type | Source |
|---|---------|------|--------|
| 1 | Student_ID | ID | Dropout dataset |
| 2 | Age | Numeric | Dropout dataset |
| 3 | Gender | Categorical | Dropout dataset |
| 4 | Family_Income | Numeric | Dropout dataset |
| 5 | Internet_Access | Categorical | Dropout dataset |
| 6 | Study_Hours_per_Day | Numeric | Dropout dataset |
| 7 | Attendance_Rate | Numeric | Dropout dataset |
| 8 | Assignment_Delay_Days | Numeric | Dropout dataset |
| 9 | Travel_Time_Minutes | Numeric | Dropout dataset |
| 10 | Part_Time_Job | Categorical | Dropout dataset |
| 11 | Scholarship | Categorical | Dropout dataset |
| 12 | Stress_Index | Numeric | Dropout dataset |
| 13 | GPA | Numeric | Dropout dataset |
| 14 | Semester_GPA | Numeric | Dropout dataset |
| 15 | CGPA | Numeric | Dropout dataset |
| 16 | Semester | Numeric | Dropout dataset |
| 17 | Department | Categorical | Dropout dataset |
| 18 | Parental_Education | Categorical | Dropout dataset |
| 19 | Dropout | Binary target | Dropout dataset |
| 20 | synthetic_feedback | Text (derived) | Stress_Index → rule-based |
| 21 | sentiment_score | Numeric [-1, 1] | Feedback → keyword scoring |
| 22 | session_count | Numeric | LMS interactions (aggregated) |
| 23 | avg_time_spent_minutes | Numeric | LMS interactions (aggregated) |
| 24 | avg_pages_visited | Numeric | LMS interactions (aggregated) |
| 25 | avg_video_watched_percent | Numeric | LMS interactions (aggregated) |
| 26 | avg_click_events | Numeric | LMS interactions (aggregated) |
| 27 | avg_attention_score | Numeric | LMS interactions (aggregated) |
| 28 | avg_days_since_last_activity | Numeric | LMS interactions (aggregated) |
| 29 | success_rate | Numeric [0, 1] | LMS interactions (aggregated) |

### 2.5 Data Flow Diagram

```
┌──────────────┐   ┌──────────────────┐   ┌──────────────────────┐
│  Dropout CSV │   │ Interaction CSV  │   │  Management CSV      │
│  10K × 19    │   │  9K × 22         │   │  1.5K × 15 (ref)     │
└──────┬───────┘   └────────┬─────────┘   └──────────────────────┘
       │                    │
       │         ┌──────────┘
       │         │ aggregate_interactions()
       │         ▼
       │    ┌────────────┐
       │    │ Agg: 8 cols│
       │    │per student │
       │    └─────┬──────┘
       │          │
       ▼          ▼
  ┌──────────────────────┐
  │  LEFT JOIN on        │
  │  Student_ID          │
  │  10,000 × 27         │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │  Synthetic features: │
  │ + synthetic_feedback │
  │ + sentiment_score    │
  │ → 10,000 × 29        │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │  Imputation:         │
  │  median (numeric)    │
  │  mode (categorical)  │
  └──────────┬───────────┘
             │
             ▼
    engineered_features.csv
       (10,000 × 29)
```

---

## 3. Model

### 3.1 Training Strategy

The system implements a **comprehensive model selection tournament** — not a single algorithm, but a systematic search across:

- **4 model architectures** × **3 imbalance-handling strategies** × **3 calibration methods**
- Evaluated via a **composite scoring function** that balances AUC, F1, and recall

```
Model Selection Flow
━━━━━━━━━━━━━━━━━━━━

   ┌─────────────────────────────────────────────────────┐
   │  4 Base Models                                      │
   │  ┌──────────────┐ ┌──────────┐ ┌────────-─┐ ┌─────┐ │
   │  │ RandomForest │ │ XGBoost  │ │CatBoost  │ │Stack│ │
   │  │ 400-700 trees│ │ gradient │ │ ordered  │ │RF+  │ │
   │  │ balanced wt  │ │ boosting │ │ boosting │ │XGB+ │ │
   │  │ sqrt features│ │ logloss  │ │ AUC opt  │ │Cat  │ │
   │  └──────┬───────┘ └────┬─────┘ └──-──┬───-┘ └──┬──┘ │
   │         └───────┬──────┴──────┬──────┘         │    │
   │                 ▼             ▼                ▼    │
   │  ┌────────────────────────────────────────────-─┐   │
   │  │  3 Sampling Strategies (per model*)          │   │
   │  │  ┌──────┐  ┌───────┐  ┌──────────┐           │   │
   │  │  │ None │  │ SMOTE │  │ SMOTEENN │           │   │
   │  │  └──────┘  └───────┘  └──────────┘           │   │
   │  │  * RF & XGBoost try all 3; others use none   │   │
   │  └──────────────────┬─────────────────────────-─┘   │
   │                     ▼                               │
   │  ┌────────────────────────────────────────────-─┐   │
   │  │  RandomizedSearchCV (10 iters, 3-fold CV)    │   │
   │  │  Scoring: ROC-AUC                            │   │
   │  └──────────────────┬──────────────────────-────┘   │
   │                     ▼                               │
   │  ┌─────────────────────────────────────────-────┐   │
   │  │  3 Calibration Options                       │   │
   │  │  ┌──────┐  ┌─────────┐  ┌──────────┐         │   │
   │  │  │ None │  │ Sigmoid │  │ Isotonic │         │   │
   │  │  └──────┘  └─────────┘  └──────────┘         │   │
   │  │  Winner: lowest Brier score on validation    │   │
   │  └──────────────────┬────────────────────────-──┘   │
   │                     ▼                               │
   │  ┌───────────────────────────────────────────-──┐   │
   │  │  Composite Score:                            │   │
   │  │  0.40 × AUC + 0.45 × F1 + 0.15 × Recall      │   │
   │  └──────────────────┬────────────────────────-──┘   │
   │                     ▼                               │
   │              Best Candidate                         │
   └─────────────────────────────────────────────────────┘
```

### 3.2 Model Candidates Evaluated

| Rank | Model | Sampler | AUC | F1 | Recall | Composite | Calibration |
|------|-------|---------|-----|-----|--------|-----------|-------------|
| **1** | **RandomForest** | **SMOTE** | **0.8026** | **0.5749** | **0.7452** | **0.6915** | **none** |
| 2 | CatBoost | none | 0.8071 | 0.5911 | 0.6645 | 0.6885 | sigmoid |
| 3 | StackingEnsemble | none | 0.8047 | 0.5932 | 0.6624 | 0.6882 | sigmoid |
| 4 | XGBoost | none | 0.8027 | 0.5886 | 0.6773 | 0.6875 | sigmoid |
| 5 | RandomForest | none | 0.8049 | 0.5888 | 0.6688 | 0.6872 | sigmoid |
| 6 | RandomForest | SMOTEENN | 0.7949 | 0.5613 | 0.7728 | 0.6865 | none |
| 7 | XGBoost | SMOTE | 0.7875 | 0.5605 | 0.7028 | 0.6727 | isotonic |
| 8 | XGBoost | SMOTEENN | 0.7844 | 0.5604 | 0.7091 | 0.6723 | isotonic |

**Winner:** RandomForest + SMOTE — highest composite score (0.6915), strong recall (0.7452) balancing catch rate with precision.

### 3.3 Dual-Threshold Optimisation

Instead of a single threshold, the system optimises **two operating points** with different objective functions:

```
Threshold Optimisation
━━━━━━━━━━━━━━━━━━━━━━

  Precision-Recall Curve
  │
  │     ╲                    Balanced Objective:
  │      ╲                   0.35 × Precision + 0.20 × Recall + 0.45 × F1
  │       ╲   ← balanced     → Threshold = 0.2884
  │        ╲    (0.2884)
  │         ╲
  │    │╲    ╲               High-Recall Objective:
  │    │ ╲    ╲              0.20 × Precision + 0.50 × Recall + 0.30 × F1
  │    │  ╲    ╲             → Threshold = 0.1219
  │    │   ╲    ╲
  │    ↑    ╲    ╲
  │  high    ╲    ╲
  │  recall   ╲    ╲
  │  (0.1219)  ╲    ╲
  └─────────────────────→  Recall

  Both thresholds respect minimum recall constraints:
  - Balanced:    recall_floor = 0.55
  - High-recall: recall_floor = 0.70
```

| Mode | Threshold | Accuracy | Precision | Recall | F1 |
|------|-----------|----------|-----------|--------|-----|
| **Balanced** | 0.2884 | 0.7295 | 0.4551 | 0.7537 | 0.5675 |
| **High Recall** | 0.1219 | 0.5250 | 0.3219 | 0.9193 | 0.4769 |

### 3.4 Preprocessing Pipeline

```
Input Features (27 cols, excluding Student_ID + synthetic_feedback)
     │
     ├─── Numeric Features ──→  SimpleImputer(strategy="median")
     │
     └─── Categorical Features ──→  SimpleImputer(strategy="most_frequent")
                                        │
                                        └──→  OneHotEncoder(handle_unknown="ignore")
     │
     ▼
  ColumnTransformer output (single dense matrix)
     │
     ▼
  [Optional] SMOTE oversampling on training split
     │
     ▼
  Model.fit()
```

### 3.5 Imbalance Handling

The target has a **76.5 : 23.5** class split (not retained vs dropout). Three strategies are evaluated:

| Strategy | How it works | When it helps |
|----------|-------------|---------------|
| **None** | No resampling; rely on model's class_weight="balanced" | When model handles imbalance natively |
| **SMOTE** | Synthetic Minority Over-sampling — creates synthetic dropout examples by interpolating between nearest neighbours | When minority class is underrepresented; avoids information loss |
| **SMOTEENN** | SMOTE + Edited Nearest Neighbours — oversample then clean noisy boundary samples | When class overlap is high; produces cleaner decision boundary |

**Result:** SMOTE paired with RandomForest yielded the best composite score, confirming that oversampling the dropout class improves recall without excessive precision loss.

### 3.6 Calibration

Post-training, each model is tested with three probability calibration methods:

| Method | Approach | Selected for winner? |
|--------|----------|---------------------|
| None | Raw model probabilities | **Yes** (lowest Brier score) |
| Sigmoid (Platt scaling) | Fits a logistic regression on raw predictions | No |
| Isotonic regression | Non-parametric monotonic fit | No |

The winning RandomForest + SMOTE model's raw probabilities had Brier score = **0.140185**, which was already lower than calibrated variants.

---

## 4. Architecture

### 4.1 System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                                 Sentinal AI                                    │
│                                                                                │
│  ┌─────────────┐    ┌──────────────────┐    ┌─────────────────────────┐        │
│  │ Data Layer  │    │ Processing Layer │    │     Serving Layer       │        │
│  │             │    │                  │    │                         │        │
│  │  3 CSV      │──→ │  data_pipeline   │ ──→│  dashboard/app.py       │        │
│  │  datasets   │    │  (feature eng.)  │    │  (Streamlit + Plotly)   │        │
│  │             │    │                  │    │                         │        │
│  └─────────────┘    │  modeling        │    │  6 Interactive Tabs:    │        │
│                     │  (train + select)│    │  • Overview             │        │
│                     │                  │    │  • Action Queue         │        │
│                     │  risk_engine     │    │  • Student Detail       │        │
│                     │  (score + advise)│    │  • Intervention Planner │        │
│                     │                  │    │  • Program Impact       │        │
│                     └────────┬─────────┘    │  • Cohort Insights      │        │
│                              │              └────────────┬────────────┘        │
│                              ▼                           │                     │
│                     ┌──────────────────┐                 │                     │
│                     │  Artifacts Layer │◀────────────-───┘                     │
│                     │                  │  (reads at runtime)                   │
│                     │  predictions.csv │                                       │
│                     │  metrics.json    │                                       │
│                     │  model.joblib    │                                       │
│                     │  diagnostics.json│                                       │
│                     └──────────────────┘                                       │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Module Architecture

```
SentinalAi/
│
├── data/                              # Raw input datasets
│   ├── student_dropout_dataset_v3.csv
│   ├── student_learning_interaction_dataset.csv
│   └── college_student_management_data.csv
│
├── src/                               # Core Python modules
│   ├── __init__.py
│   ├── data_pipeline.py               # Feature engineering & data fusion
│   ├── modeling.py                     # Model training, selection, calibration
│   └── risk_engine.py                  # Risk scoring & intervention engine
│
├── scripts/                           # Executable entry points
│   ├── prepare_data.py                # Step 1: CSV → engineered_features.csv
│   └── train_model.py                 # Step 2: Train → model + predictions + metrics
│
├── dashboard/
│   └── app.py                         # Streamlit frontend (6 tabs)
│
├── artifacts/                         # Generated outputs (gitignored heavy files)
│   ├── engineered_features.csv        # 10K × 29 feature table
│   ├── dropout_model.joblib           # Serialised model bundle
│   ├── predictions.csv                # 10K scored students
│   ├── metrics.json                   # Evaluation metrics + mode comparison
│   └── model_selection_diagnostics.json  # 8-candidate tournament results
│
├── public/image/                      # Visualisation exports
├── requirements.txt
├── README.md
└── DOCUMENTATION.md                   # ← This file
```

### 4.3 End-to-End Pipeline Flowchart

```
    ┌───────────────────┐
    │   START           │
    └─────────┬─────────┘
              ▼
    ┌───────────────────┐
    │ scripts/          │
    │ prepare_data.py   │    Calls data_pipeline.build_feature_table()
    │                    │    Merges 3 datasets → 10K × 29
    └─────────┬─────────┘
              ▼
    ┌───────────────────┐
    │ artifacts/        │
    │ engineered_       │    Persisted feature table
    │ features.csv      │
    └─────────┬─────────┘
              ▼
    ┌───────────────────┐
    │ scripts/          │
    │ train_model.py    │
    │                   │
    │  ┌─────────────┐  │
    │  │ Preprocess  │  │    ColumnTransformer (impute + encode)
    │  └──────┬──────┘  │
    │         ▼         │
    │  ┌─────────────┐  │
    │  │ Train/Valid │  │    80/20 split, then 75/25 within train
    │  │ /Test split │  │    Stratified on Dropout
    │  └──────┬──────┘  │
    │         ▼         │
    │  ┌─────────────┐  │
    │  │ Model       │  │    4 models × 3 samplers = up to 8 candidates
    │  │ Tournament  │  │    RandomizedSearchCV (10 iters, 3-fold)
    │  └──────┬──────┘  │
    │         ▼         │
    │  ┌─────────────┐  │
    │  │ Calibration │  │    3 methods per candidate → lowest Brier wins
    │  │ Selection   │  │
    │  └──────┬──────┘  │
    │         ▼         │
    │  ┌─────────────┐  │
    │  │ Composite   │  │    0.40 × AUC + 0.45 × F1 + 0.15 × Recall
    │  │ Scoring     │  │    → Best: RandomForest + SMOTE (0.6915)
    │  └──────┬──────┘  │
    │         ▼         │
    │  ┌─────────────┐  │
    │  │ Dual        │  │    Balanced: 0.2884  |  High-recall: 0.1219
    │  │ Threshold   │  │
    │  └──────┬──────┘  │
    │         ▼         │
    │  ┌─────────────┐  │
    │  │ Score all   │  │    10,000 students scored with probabilities
    │  │ students    │  │
    │  └──────┬──────┘  │
    │         ▼         │
    │  ┌─────────────┐  │
    │  │ Risk Engine │  │    risk_engine.py:
    │  │             │  │    • adaptive_risk_bins()
    │  │             │  │    • extract_triggers()
    │  │             │  │    • derive_disengagement_indicators()
    │  │             │  │    • recommend_intervention()
    │  └──────┬──────┘  │
    │         ▼         │
    │  ┌─────────────┐  │
    │  │ save_       │  │    → dropout_model.joblib
    │  │ artifacts() │  │    → predictions.csv
    │  │             │  │    → metrics.json
    │  │             │  │    → model_selection_diagnostics.json
    │  └─────────────┘  │
    └─────────┬─────────┘
              ▼
    ┌──────────────────-─┐
    │ dashboard/app.py   │    streamlit run dashboard/app.py
    │                    │
    │ Reads:             │
    │ • predictions.csv  │    10K scored students
    │ • metrics.json     │    Model performance metrics
    │ • dropout data     │    Cohort dimensions (dept, gender, etc.)
    │                    │
    │ Serves 6 tabs      │
    └────────────────-───┘
```

### 4.4 Risk Engine Flowchart

```
    Student Probability (0.0 – 1.0)
              │
              ▼
    ┌───────────────────────┐
    │  Risk Score = P × 100 │    e.g. 0.37 → 37.3
    └──────────┬────────────┘
               ▼
    ┌───────────────────────┐
    │  adaptive_risk_bins() │
    │                       │
    │  low_cutoff = threshold × 100 = 28.8
    │  high_cutoff = 85th percentile of scores
    │                       │
    │  Low:    score ≤ 28.8 │
    │  Medium: 28.8 < score ≤ high_cutoff
    │  High:   score > high_cutoff
    └──────────┬────────────┘
               ▼
    ┌────────────────────------------------------───┐
    │  extract_triggers()                           │
    │                                               │
    │  Per student:                                 │
    │  1. Compute |feature_value − median|          │
    │  2. Weight by feature_importance              │
    │  3. Zero-out non-actionable features          │
    │     (age, gender, income, etc.)               │
    │  4. Top-5 by weighted deviation               │
    │                                               │
    │  Output: "GPA, Attendance_Rate, CGPA, ..."    │
    └──────────┬────────────────────────────────────┘
               ▼
    ┌─────────────────────────────────────────────────┐
    │  derive_disengagement                           │
    │  _indicators()                                  │
    │                                                 │
    │  Map triggers → labels                          │
    │  attendance → "Attendance decline"              │
    │  stress     → "Emotional distress signal"       │
    │  gpa/cgpa   → "Academic performance pressure".  │
    │  etc.                                           │ 
    └──────────┬──────────────────────────────────--──┘
               ▼
    ┌──────────────────────────────────────────────────┐
    │  recommend_intervention()                        │
    │                                                  │
    │  Walk triggers in priority order:                │
    │  First match → intervention action               │
    │  If risk_level == "High":                        │ 
    │    prefix with "URGENT — "                       │
    │                                                  │
    │  Fallback: "General academic-support check-in".  │
    └──────────────────────────────────────────────────┘
```

### 4.5 Intervention Rule Table

| Priority | Trigger Keywords | Intervention |
|----------|------------------|-------------|
| 1 | attendance | Engagement counselling + attendance monitoring plan |
| 2 | assignment_delay, delay | Academic-advisor meeting; deadline extension |
| 3 | stress, sentiment | Refer to well-being / mental-health services |
| 4 | study_hours, gpa, cgpa | Peer-tutoring or supplemental instruction |
| 5 | time_spent, pages_visited, video, click, attention | Digital engagement coaching |
| 6 | days_since_last, success_rate, session_count | Proactive outreach — mentor check-ins |
| — | *(no match)* | General academic-support check-in |

---

## 5. Results

### 5.1 Primary Evaluation Metrics

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **ROC-AUC** | 0.8044 | Strong discrimination — 80 % chance the model ranks a true dropout higher than a retained student |
| **PR-AUC** | 0.5709 | Solid for 23.5 % base rate; >2× random baseline (0.235) |
| **Brier Score** | 0.1402 | Well-calibrated probabilities (0 = perfect, 0.25 = random) |

### 5.2 Mode Comparison

| Metric | Balanced (θ = 0.2884) | High Recall (θ = 0.1219) | Delta |
|--------|----------------------|--------------------------|-------|
| Accuracy | 0.7295 | 0.5250 | −0.2045 |
| Precision | 0.4551 | 0.3219 | −0.1332 |
| Recall | 0.7537 | 0.9193 | **+0.1656** |
| F1 | 0.5675 | 0.4769 | −0.0906 |

### 5.3 Classification Report (Balanced Mode)

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| No Dropout (0) | 0.905 | 0.722 | 0.803 | 1,529 |
| Dropout (1) | 0.455 | 0.754 | 0.568 | 471 |
| **Weighted Avg** | **0.799** | **0.730** | **0.748** | **2,000** |

### 5.4 Scoring Summary (10,000 Students)

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Low | 6,817 | 68.2 % |
| Medium | 1,685 | 16.9 % |
| High | 1,498 | 15.0 % |
| **URGENT interventions** | **1,498** | **15.0 %** |

Mean dropout probability across all students: **0.2609** (26.1 %).

### 5.5 Visual Results

The following visualisations are available in `public/image/`:

| File | Description |
|------|-------------|
| `risk score distribution with adaptive bin boundaries.png` | Histogram of risk scores with Low/Medium/High boundaries |
| `Behavioural Risk Profile.png` | Radar chart of at-risk vs. not-at-risk feature profiles |
| `confusion matric roc auc.png` | Confusion matrix and ROC curve |
| `cumulative_gains_chart.png` | Cumulative gains / lift chart |
| `dropout_heatmap_dept_year.png` | Dropout heatmap by department and semester |
| `feature importance.png` | Top feature importances from the trained model |
| `precision f1 recall.png` | Precision, recall, and F1 across thresholds |
| `Intervention Strategy Distribution (Treemap).png` | Treemap of intervention strategy assignments |

---

## 6. Behavioural Insights

### 6.1 Key Findings from Feature Importance

The model reveals which **behavioural signals** most strongly predict dropout risk:

```
Feature Importance (Top Predictors)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Attendance_Rate     ████████████████████████  ← Strongest signal
  GPA                 ██████████████████████
  CGPA                ████████████████████
  Stress_Index        ████████████████
  Study_Hours_per_Day ██████████████
  Assignment_Delay    ████████████
  sentiment_score     ██████████
  avg_video_watched   ████████
  avg_attention_score ███████
  avg_time_spent      ██████
```

### 6.2 Actionable vs Non-Actionable Feature Design

A critical design decision: the model uses **all predictive features** for accuracy, but the trigger extraction system **filters out non-actionable factors** when generating student-facing reports:

| Non-Actionable (used for prediction, hidden from triggers) | Actionable (shown to counselors) |
|---|---|
| Family_Income, Age, Gender | Attendance_Rate, GPA, CGPA |
| Travel_Time_Minutes | Study_Hours_per_Day |
| Part_Time_Job, Scholarship | Assignment_Delay_Days |
| Internet_Access | Stress_Index, sentiment_score |
| Parental_Education, Department, Semester | avg_video_watched, avg_attention_score |

**Why this matters:** Telling a counselor "this student is at risk because of low family income" is not actionable. Telling them "this student's attendance has dropped and assignment delays are increasing" gives them something they can work with.

### 6.3 Disengagement Indicator Mapping

The system translates raw feature triggers into **human-readable disengagement labels**:

| Raw Trigger Pattern | Disengagement Label |
|---------------------|---------------------|
| `attendance` | Attendance decline |
| `assignment_delay`, `delay` | Assignment delay pattern |
| `gpa`, `cgpa`, `study_hours` | Academic performance pressure |
| `time_spent`, `video_watched`, `click_events` | Low LMS engagement |
| `days_since_last`, `session_count` | Irregular activity pattern |
| `stress`, `sentiment` | Emotional distress signal |

### 6.4 Intervention Strategy Distribution

The 10,000 scored students receive the following intervention recommendations:

- **URGENT** prefix is added to all High-risk students (1,498 students)
- Most common interventions centre around attendance monitoring and peer-tutoring
- When a student's top trigger is attendance-related, they receive "Engagement counselling + attendance monitoring plan"
- Multi-signal students (e.g., both attendance and stress) get the **highest-priority matching rule**

---

## 7. Practical Impact

### 7.1 Dashboard as a Decision Tool

The Streamlit dashboard translates model outputs into **operational decisions** with 6 purpose-built tabs:

```
Dashboard Tab Architecture
━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────────────────────────────────────────┐
│  Sidebar Controls (always visible)                   │
│  • Mode selector (balanced / high_recall)            │
│  • Risk level filter       • Score range slider      │
│  • Student search          • Urgent-only toggle      │
│  • Outreach capacity %     • What-if threshold slider│
└──────────────────────────────────────────────────────┘

Tab 1: OVERVIEW
├── 11 KPI cards (students, high-risk, recall, AUC, PR-AUC, threshold, etc.)
├── Mode trade-off comparison (grouped bar chart)
├── Risk level distribution (bar) + Score histogram (colored by risk)
├── Top behavioural triggers (horizontal bar)
├── Intervention strategy mix (donut chart)
├── Outreach planning (capacity-based recommended threshold)
└── What-if threshold simulator + sweep chart

Tab 2: ACTION QUEUE
├── Full sortable table (Student_ID, probability, risk, triggers, intervention)
└── CSV download button

Tab 3: STUDENT DETAIL
├── Student selector → 3 KPI cards (probability, score, level)
└── Markdown: disengagement indicators, triggers, intervention

Tab 4: INTERVENTION PLANNER
├── Counselor capacity + weekly slot configuration
├── Round-robin counselor assignment by risk priority
├── Week-by-week schedule with week selector
├── Counselor workload summary table
└── Downloadable assignment sheet (CSV)

Tab 5: PROGRAM IMPACT
├── Leadership KPIs: contacted, captured, false-positive load
├── Workload by intervention strategy (horizontal bar)
└── Impact efficiency narrative

Tab 6: COHORT INSIGHTS
├── Dimension selector (Department / Semester / Gender / Part_Time_Job)
├── Risk level distribution stacked bar by cohort
├── Average risk score bar (color-scaled)
├── High-risk rate bar by cohort
├── Summary table
└── Cross-dimension heatmap (e.g., Department × Gender)
```

### 7.2 Operational Impact Estimates

| Scenario | Metric | Value |
|----------|--------|-------|
| Contact top 20 % by risk score | Students contacted | ~2,000 |
| | High-risk capture | ~83 % of all High-risk students |
| | Counselor efficiency | 5 counselors × 10 slots/week = 50/week → ~40 weeks |
| Balanced mode (θ = 0.2884) | Students flagged | Varies by cohort; ~30-40 % |
| | False-positive rate | ~54.5 % of flagged are not High-risk |
| High-recall mode (θ = 0.1219) | Students flagged | ~60-70 % |
| | Missed dropouts | Only ~8 % of true at-risk students missed |

### 7.3 Resource Planning Features

The **Intervention Planner** tab provides concrete operational planning:

1. **Input:** Number of counselors + weekly contact slots per counselor
2. **Output:** Round-robin assignment, week-by-week schedule, workload per counselor
3. **Download:** Full assignment sheet as CSV for import into scheduling systems

The **What-if Threshold Simulator** enables stakeholders to:
- Slide the threshold to see immediate impact on flagged count and high-risk coverage
- View the trade-off sweep chart to find the optimal operating point
- Auto-compute a recommended threshold based on outreach capacity percentage

### 7.4 Cohort-Level Insights for Policy

The **Cohort Insights** tab enables institutional leaders to:
- Identify which **departments** have the highest dropout concentration
- Compare risk profiles across **semesters** (e.g., first-year vs. later)
- Examine **gender** and **part-time job** status effects on risk
- Use the **cross-dimension heatmap** to find intersectional risk hotspots (e.g., "Part-time working students in Engineering have 2× the average risk score")

---

## 8. Future Scope

### 8.1 Short Term (Next Iteration)

| Enhancement | Description | Impact |
|-------------|-------------|--------|
| **SHAP explanations** | Per-student SHAP waterfall plots showing which features push risk up/down | Improved counselor trust and understanding |
| **Governance tab** | Model version, training date, calibration status, limitations, threshold rationale | Audit readiness |
| **Data quality tab** | Missing value rates, feature drift detection, outlier counts | Proactive data hygiene |
| **Dark mode + theming** | Custom CSS, branded colors, card-style KPIs | Visual polish |

### 8.2 Medium Term

| Enhancement | Description | Impact |
|-------------|-------------|--------|
| **Longitudinal tracking** | Compare student risk scores across semesters; detect trend direction | Early trend-based alerts |
| **Feedback loop** | Record which interventions were deployed and whether students were retained | Measure actual intervention effectiveness |
| **LMS API integration** | Live data from Moodle/Canvas instead of static CSV | Real-time risk updates |
| **A/B testing framework** | Randomly assign intervention strategies; measure comparative effectiveness | Evidence-based intervention selection |

### 8.3 Long Term

| Enhancement | Description | Impact |
|-------------|-------------|--------|
| **Multi-institution deployment** | Containerised (Docker) deployment with institution-specific model training | Scale across universities |
| **Real-time streaming** | Kafka/Flink for session-level event processing; instant risk updates | Sub-hour detection latency |
| **Causal inference** | Move beyond correlation to causal models (DoWhy, causalml) | Understand *why* students drop out, not just *who* |
| **Student-facing portal** | Self-service risk awareness with suggested actions | Student agency and self-regulation |
| **Automated outreach** | Trigger email/SMS nudges when risk crosses threshold | Zero-latency lightweight intervention |

---

## 9. Appendix — Diagrams & Flowcharts

### 9.1 Complete Data Flow (Source to Dashboard)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW — END TO END                         │
│                                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────┐                     │
│  │ Dropout  │  │ Interaction  │  │ Management     │                     │
│  │ CSV      │  │ CSV          │  │ CSV (ref)      │                     │
│  │ 10K × 19 │  │ 9K × 22      │  │ 1.5K × 15      │                     │
│  └────┬─────┘  └──────┬───────┘  └────────────────┘                     │
│       │               │                                                 │
│       │    ┌──────────┘                                                 │
│       │    │ aggregate per student                                      │
│       │    ▼                                                            │
│       │  ┌────────────┐                                                 │
│       │  │ 8 LMS cols │                                                 │
│       │  └─────┬──────┘                                                 │
│       │        │                                                        │
│       ▼        ▼                                                        │
│  ┌────────────────────┐                                                 │
│  │ LEFT JOIN          │                                                 │
│  │ + synthetic feats  │                                                 │
│  │ + imputation       │                                                 │
│  │ → 10K × 29         │                                                 │
│  └─────────┬──────────┘                                                 │
│            ▼                                                            │
│  ┌──────────────────-──┐    ┌─────────────────────────────────────┐     │
│  │ engineered_         │    │          MODEL TRAINING             │     │
│  │ features.csv        │──→ │                                     │     │
│  │                     │    │  Train/Valid/Test split (60/20/20)  │     │
│  └─────────────────────┘    │  8 candidate evaluations            │     │
│                             │  Calibration selection              │     │
│                             │  Dual threshold optimization        │     │
│                             │                                     │     │
│                             │  Winner: RF + SMOTE                 │     │
│                             │  Balanced θ: 0.2884                 │     │
│                             │  High-recall θ: 0.1219              │     │
│                             └──────────────┬──────────────────────┘     │
│                                            │                            │
│                                            ▼                            │
│                             ┌─────────────────────────────────────┐     │
│                             │          RISK ENGINE                │     │
│                             │                                     │     │
│                             │  Score → Risk Level (Low/Med/High)  │     │
│                             │  Features → Behavioural Triggers    │     │
│                             │  Triggers → Disengagement Labels    │     │
│                             │  Triggers + Level → Intervention    │     │
│                             └──────────────┬──────────────────────┘     │
│                                            │                            │
│                                            ▼                            │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                        ARTIFACTS                                │    │
│  │                                                                 │    │
│  │  dropout_model.joblib  │  metrics.json  │  predictions.csv      │    │
│  │  (model + preprocessor │  (AUC, F1,     │  (10K students ×      │    │
│  │   + thresholds)        │   thresholds,  │   probability, score, │    │
│  │                        │   mode metrics)│   level, triggers,    │    │
│  │                        │                │   intervention)       │    │
│  │  model_selection_diagnostics.json (8 candidate results)         │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                            │                            │
│                                            ▼                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    STREAMLIT DASHBOARD                           │   │
│  │                                                                  │   │
│  │   Reads artifacts at runtime (no live inference)                 │   │
│  │                                                                  │   │
│  │   ┌─────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐               │   │
│  │   │Overview │ │ Action   │ │Student │ │Interven- │               │   │
│  │   │(KPIs,   │ │ Queue    │ │Detail  │ │tion      │               │   │
│  │   │charts,  │ │(table,   │ │(per-   │ │Planner   │               │   │
│  │   │sweep)   │ │download) │ │student)│ │(schedule)│               │   │
│  │   └───────-─┘ └──────────┘ └────────┘ └──────────┘               │   │
│  │   ┌───────────┐ ┌───────────────┐                                │   │
│  │   │ Program   │ │ Cohort        │                                │   │
│  │   │ Impact    │ │ Insights      │                                │   │
│  │   │(leaders)  │ │(heatmaps)     │                                │   │
│  │   └───────────┘ └───────────────┘                                │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Model Selection Tournament Flow

```
    8 Candidates Evaluated
    ━━━━━━━━━━━━━━━━━━━━━━

    ┌─────────────────┐     ┌─────────────────┐
    │ RandomForest    │     │ XGBoost         │
    │ ├── none        │     │ ├── none        │
    │ ├── SMOTE ★     │     │ ├── SMOTE       │
    │ └── SMOTEENN    │     │ └── SMOTEENN    │
    └─────────────────┘     └─────────────────┘
    ┌─────────────────┐     ┌─────────────────┐
    │ CatBoost        │     │ StackingEnsemble│
    │ └── none        │     │ └── none        │
    └─────────────────┘     └─────────────────┘

    Each candidate goes through:

    ┌───────────────────────────────────────────┐
    │ 1. Resample training data (if applicable) │
    │ 2. RandomizedSearchCV (10 iter, 3-fold)   │
    │ 3. Calibrate: none vs sigmoid vs isotonic │
    │ 4. Evaluate on validation set             │
    │ 5. Compute composite score                │
    └───────────────────────────────────────────┘

    Winner: RandomForest + SMOTE
    Composite: 0.6915
    (0.40 × 0.8026 + 0.45 × 0.5749 + 0.15 × 0.7452)
```

### 9.3 Prediction Payload Structure

For each of the 10,000 students, the system produces:

```json
{
    "Student_ID": 42,
    "dropout_probability": 0.7536,
    "risk_score": 75.4,
    "burnout_risk_level": "High",
    "academic_disengagement_indicators": "Attendance decline, Academic performance pressure",
    "key_behavioural_triggers": "Attendance_Rate, GPA, CGPA, Stress_Index, Study_Hours_per_Day",
    "recommended_intervention_strategy": "URGENT — Engagement counselling + attendance monitoring plan"
}
```

### 9.4 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Language | Python | 3.14 | Core runtime |
| ML Framework | scikit-learn | latest | Preprocessing, RF, calibration, metrics |
| Gradient Boosting | XGBoost | latest | XGB candidate |
| Ordered Boosting | CatBoost | latest | CatBoost candidate |
| Imbalance Handling | imbalanced-learn | latest | SMOTE, SMOTEENN |
| Explainability | SHAP | latest | Feature contribution analysis |
| Serialisation | joblib | latest | Model persistence |
| Dashboard | Streamlit | 1.54.0 | Interactive frontend |
| Charting | Plotly Express | 5.x | Interactive visualisations |
| Data | pandas, numpy | latest | Data manipulation |

---

