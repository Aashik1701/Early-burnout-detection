# BehAnalytics — Project Presentation Content

---

## Slide 1: Title Slide

**BehAnalytics**
Early Burnout & Dropout Detection System for Higher Education

- AI-powered behavioural analytics pipeline
- Identifies at-risk students before academic decline
- Personalised intervention recommendations at scale
- Interactive decision-support dashboard for counselors & leadership

---

## Slide 2: Problem Statement

**The Problem**

- Student dropout rates in higher education range from 20% to 50% globally
- Each dropout = lost institutional investment + lost student potential
- Current detection is reactive — institutions notice only after grades collapse or attendance is critically low
- By then, it's too late for effective intervention

**Core Question**

> How can we identify students likely to burn out or drop out *early enough* — using behavioural and academic signals — so that targeted interventions can be deployed before the point of no return?

**What's Missing Today**

- No early-warning system using behavioural signals
- No personalised intervention recommendations per student
- No resource-aware planning (counselor capacity is limited)
- No transparency into *why* a student is flagged

---

## Slide 3: Problem Statement — Requirements

**System Requirements**

| Requirement | What it means |
|-------------|---------------|
| Early Detection | Flag students using behavioural signals — not just end-of-term grades |
| Actionable Output | Every flagged student gets a personalised intervention recommendation |
| Dual Operating Modes | Balanced mode for evaluation, high-recall mode for deployment |
| Transparency | Per-student behavioural triggers explain *why* the model flagged them |
| Scalability | Score 10,000+ students in batch with a dashboard for non-technical staff |
| Resource Awareness | Plan outreach in weekly counselor slots, not just a flat risk list |

---

## Slide 4: Data & Features — Data Sources

**Three Complementary Datasets**

| Dataset | Records | Columns | Role |
|---------|---------|---------|------|
| Student Dropout Records | 10,000 students | 19 | Primary — demographics, academics, stress, target label |
| Learning Interaction Logs | 9,000 sessions | 22 | LMS behaviour — time spent, clicks, video, quiz, attention |
| College Student Management | 1,545 students | 15 | Reference — GPA, course load, LMS logins |

**Target Variable:** Dropout (binary)
- Retained: 7,646 (76.5%)
- Dropped out: 2,354 (23.5%)

---

## Slide 5: Data & Features — Feature Groups

**27 Raw Features + 2 Engineered = 29 Total**

| Group | Features | Type |
|-------|----------|------|
| Demographics | Age, Gender, Family_Income, Parental_Education | Context (non-actionable) |
| Socioeconomic | Internet_Access, Travel_Time, Part_Time_Job, Scholarship | Access factors |
| Academic | GPA, Semester_GPA, CGPA, Semester, Department | Performance signals |
| Behavioural | Study_Hours, Attendance_Rate, Assignment_Delay, Stress_Index | Core actionable |
| LMS Engagement | avg_time_spent, avg_pages_visited, avg_video_watched, avg_click_events, avg_attention_score, avg_days_since_last_activity, session_count, success_rate | Digital behaviour |
| Derived | sentiment_score (from stress-based synthetic feedback) | Emotional signal |

---

## Slide 6: Data & Features — Feature Engineering Pipeline

**Pipeline Steps**

1. Load dropout dataset (10,000 × 19)
2. Load LMS interaction logs (9,000 × 22)
3. Aggregate interactions per student → 8 features (mean, count)
4. LEFT JOIN on Student_ID → 10,000 × 27
5. Generate synthetic feedback from Stress_Index → sentiment_score
6. Impute: median for numeric, mode for categorical
7. Output: **10,000 × 29** engineered feature table

**Key Design Decision:** Sentiment score derived from stress levels provides an emotional distress signal without requiring manual student surveys.

---

## Slide 7: Model — Training Strategy

**Comprehensive Model Selection Tournament**

- 4 model architectures: RandomForest, XGBoost, CatBoost, StackingEnsemble
- 3 imbalance strategies: None, SMOTE, SMOTEENN
- 3 calibration methods: None, Sigmoid (Platt), Isotonic
- = 8 candidate configurations evaluated

**Hyperparameter Tuning**
- RandomizedSearchCV: 10 iterations, 3-fold stratified CV
- Scoring: ROC-AUC

**Selection Criteria — Composite Score**
- 0.40 × AUC + 0.45 × F1 + 0.15 × Recall
- Balances discrimination, balance, and catch rate

---

## Slide 8: Model — Tournament Results

**8 Candidates Evaluated**

| Rank | Model | Sampler | AUC | F1 | Recall | Composite |
|------|-------|---------|-----|-----|--------|-----------|
| **1** | **RandomForest** | **SMOTE** | **0.8026** | **0.5749** | **0.7452** | **0.6915** |
| 2 | CatBoost | None | 0.8071 | 0.5911 | 0.6645 | 0.6885 |
| 3 | StackingEnsemble | None | 0.8047 | 0.5932 | 0.6624 | 0.6882 |
| 4 | XGBoost | None | 0.8027 | 0.5886 | 0.6773 | 0.6875 |

**Winner: RandomForest + SMOTE**
- Highest composite (0.6915) — best recall among top contenders
- Raw probabilities already well-calibrated (Brier = 0.1402) — no post-calibration needed

---

## Slide 9: Model — Dual-Threshold System

**Two Operating Modes for Different Use Cases**

| Mode | Threshold | Use Case |
|------|-----------|----------|
| **Balanced** | 0.2884 | General evaluation — judges, reports, audits |
| **High Recall** | 0.1219 | Deployment — maximise catch rate for student welfare |

**Balanced Objective:** 0.35 × Precision + 0.20 × Recall + 0.45 × F1
**High-Recall Objective:** 0.20 × Precision + 0.50 × Recall + 0.30 × F1

Both respect minimum recall floors:
- Balanced: recall ≥ 0.55
- High-recall: recall ≥ 0.70

---

## Slide 10: Architecture — System Overview

**Three-Layer Architecture**

| Layer | Components | Role |
|-------|-----------|------|
| **Data Layer** | 3 CSV datasets | Raw student records + LMS logs |
| **Processing Layer** | data_pipeline.py, modeling.py, risk_engine.py | Feature engineering → model training → risk scoring |
| **Serving Layer** | dashboard/app.py (Streamlit + Plotly) | 6-tab interactive dashboard |

**Artifact-Driven Design**
- Processing layer writes: predictions.csv, metrics.json, model.joblib, diagnostics.json
- Serving layer reads artifacts at runtime — no live inference needed
- Decoupled: model can be retrained independently of the dashboard

---

## Slide 11: Architecture — Pipeline Flow

**End-to-End Execution**

1. `prepare_data.py` → fuses 3 datasets → engineered_features.csv (10K × 29)
2. `train_model.py` → runs model tournament → selects best candidate
3. Risk engine scores all 10,000 students:
   - Probability → Risk Score (0–100)
   - Adaptive bins → Risk Level (Low / Medium / High)
   - Feature importance × deviation → Top-5 behavioural triggers per student
   - Trigger matching → Personalised intervention recommendation
4. Saves: model bundle, predictions CSV, metrics JSON, diagnostics JSON
5. `streamlit run dashboard/app.py` → serves interactive dashboard

---

## Slide 12: Architecture — Risk Engine

**Per-Student Risk Pipeline**

| Step | Input | Output |
|------|-------|--------|
| Risk Score | Dropout probability | Score 0–100 (probability × 100) |
| Risk Level | Score + adaptive bins | Low / Medium / High |
| Triggers | Feature values + importances | Top-5 actionable behavioural features |
| Disengagement Labels | Trigger keywords | Human-readable labels (e.g., "Attendance decline") |
| Intervention | Triggers + risk level | Personalised action (URGENT prefix if High) |

**Intervention Priority Rules (first-match wins):**
1. Attendance → Engagement counselling + attendance monitoring
2. Assignment delay → Academic-advisor meeting + deadline extension
3. Stress/sentiment → Refer to mental-health services
4. GPA/study hours → Peer-tutoring programme
5. LMS engagement → Digital engagement coaching
6. Activity gaps → Proactive mentor check-ins

---

## Slide 13: Results — Key Metrics

**Model Performance**

| Metric | Value | What it means |
|--------|-------|---------------|
| **ROC-AUC** | 0.8044 | 80% chance the model ranks a true dropout higher than a retained student |
| **PR-AUC** | 0.5709 | >2× random baseline (0.235) for minority class detection |
| **Brier Score** | 0.1402 | Well-calibrated probabilities (0 = perfect) |

**Mode Comparison on Test Set (2,000 students)**

| Metric | Balanced (θ=0.2884) | High Recall (θ=0.1219) |
|--------|---------------------|------------------------|
| Accuracy | 72.95% | 52.50% |
| Precision | 45.51% | 32.19% |
| Recall | **75.37%** | **91.93%** |
| F1 | 56.75% | 47.69% |

---

## Slide 14: Results — Scoring Summary

**10,000 Students Scored**

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Low | 6,817 | 68.2% |
| Medium | 1,685 | 16.9% |
| High | 1,498 | 15.0% |

- Mean dropout probability: **26.1%**
- URGENT interventions assigned: **1,498 students** (all High-risk)
- Every student receives: probability, risk score, risk level, disengagement indicators, behavioural triggers, intervention recommendation

---

## Slide 15: Results — Classification Detail

**Balanced Mode Classification Report**

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------|
| No Dropout | 90.5% | 72.2% | 80.3% | 1,529 |
| Dropout | 45.5% | 75.4% | 56.8% | 471 |
| Weighted Avg | 79.9% | 73.0% | 74.8% | 2,000 |

**Key Takeaway:** The model catches **3 out of 4** at-risk students in balanced mode and **9 out of 10** in high-recall mode. The trade-off is more false positives — but in student welfare, missing a dropout is worse than an unnecessary check-in.

---

## Slide 16: Behavioural Insights — Feature Importance

**Top Predictive Signals (ranked by model importance)**

1. **Attendance_Rate** — strongest single predictor of dropout
2. **GPA** — academic performance directly correlates with risk
3. **CGPA** — cumulative trend amplifies current-semester signal
4. **Stress_Index** — emotional load as a leading indicator
5. **Study_Hours_per_Day** — engagement proxy
6. **Assignment_Delay_Days** — early warning of disengagement
7. **sentiment_score** — derived emotional distress measure
8. **avg_video_watched_percent** — LMS engagement depth
9. **avg_attention_score** — digital attention quality
10. **avg_time_spent_minutes** — time investment in learning

**Insight:** The top predictors are all *behavioural* — things that change before grades collapse.

---

## Slide 17: Behavioural Insights — Actionable vs Non-Actionable

**Design Decision: Separate prediction from explanation**

| Used for Prediction (all features) | Shown to Counselors (actionable only) |
|-------------------------------------|--------------------------------------|
| Family_Income, Age, Gender | Attendance_Rate, GPA, CGPA |
| Travel_Time, Part_Time_Job | Study_Hours, Assignment_Delay |
| Scholarship, Internet_Access | Stress_Index, sentiment_score |
| Parental_Education, Department | avg_video_watched, avg_attention_score |

**Why:** Telling a counselor "this student is at risk because of low family income" is not actionable. Telling them "attendance dropped and assignment delays are increasing" gives them something to work with.

**Non-actionable features are blocked from trigger extraction** but remain in the model for prediction accuracy.

---

## Slide 18: Behavioural Insights — Disengagement Indicators

**Raw triggers are translated into counselor-friendly labels**

| Trigger Pattern | Disengagement Label |
|-----------------|---------------------|
| attendance | Attendance decline |
| assignment_delay | Assignment delay pattern |
| gpa, cgpa, study_hours | Academic performance pressure |
| time_spent, video_watched, click_events | Low LMS engagement |
| days_since_last, session_count | Irregular activity pattern |
| stress, sentiment | Emotional distress signal |

**Example Output:**
> Student #42: "Attendance decline, Academic performance pressure"
> → Triggers: Attendance_Rate, GPA, CGPA, Stress_Index, Study_Hours
> → Intervention: URGENT — Engagement counselling + attendance monitoring plan

---

## Slide 19: Practical Impact — Dashboard Overview

**6-Tab Interactive Dashboard (Streamlit + Plotly)**

| Tab | For Whom | What It Does |
|-----|----------|-------------|
| **Overview** | Everyone | 11 KPI cards, risk distribution charts, threshold simulator, sweep chart |
| **Action Queue** | Counselors | Sortable table of all flagged students + CSV download |
| **Student Detail** | Counselors | Per-student deep dive — probability, triggers, intervention |
| **Intervention Planner** | Operations | Counselor assignment, weekly slots, workload balancing |
| **Program Impact** | Leadership | Students contacted, high-risk capture, false-positive load |
| **Cohort Insights** | Policy makers | Risk by department, semester, gender, job status + heatmaps |

**Sidebar Controls:** Mode toggle, risk filters, score range, student search, outreach capacity, what-if threshold slider

---

## Slide 20: Practical Impact — Operational Estimates

**What BehAnalytics delivers at scale**

| Scenario | Result |
|----------|--------|
| Contact top 20% by risk score | Captures ~83% of all High-risk students |
| 5 counselors × 10 slots/week | 50 contacts/week; ~40 weeks to cover all 10K students |
| Balanced mode | ~75% of actual dropouts caught; ~45% precision |
| High-recall mode | ~92% of actual dropouts caught; only ~8% missed |

**Intervention Planner Features:**
- Input: number of counselors + weekly contact slots
- Output: round-robin assignment, week-by-week schedule, per-counselor workload
- Download: full assignment sheet as CSV

**What-if Simulator:** Slide the threshold → instantly see flagged count, high-risk coverage, and load impact

---

## Slide 21: Practical Impact — Cohort Insights

**Identify where risk concentrates**

- **By Department:** Which departments have the highest dropout concentration?
- **By Semester:** Is first semester riskier than later semesters?
- **By Gender:** Are there gender-based differences in risk profiles?
- **By Job Status:** How does part-time work affect dropout probability?
- **Cross-dimension heatmap:** Find intersectional hotspots (e.g., "Part-time students in Engineering have 2× average risk")

**Policy Use:** Data-driven resource allocation — direct counselor hours where risk is highest.

---

## Slide 22: Future Scope — Short Term

| Enhancement | Impact |
|-------------|--------|
| **SHAP explanations** | Per-student waterfall plots showing which features push risk up/down — improves counselor trust |
| **Governance tab** | Model version, training date, calibration status, limitations — audit readiness |
| **Data quality monitoring** | Missing value rates, feature drift, outlier detection — proactive data hygiene |
| **Custom theming** | Branded colors, card-style KPIs, dark mode — visual polish |

---

## Slide 23: Future Scope — Medium & Long Term

**Medium Term**

| Enhancement | Impact |
|-------------|--------|
| Longitudinal tracking | Compare risk scores across semesters; trend-based alerts |
| Intervention feedback loop | Record outcomes → measure actual effectiveness |
| LMS API integration | Live data from Moodle/Canvas → real-time risk updates |
| A/B testing framework | Randomised intervention comparison → evidence-based selection |

**Long Term**

| Enhancement | Impact |
|-------------|--------|
| Multi-institution deployment | Docker-containerised; per-institution model training |
| Real-time streaming | Kafka/Flink for session events → sub-hour detection |
| Causal inference | DoWhy/causalml → understand *why* students drop out, not just *who* |
| Student-facing portal | Self-service risk awareness + suggested actions |
| Automated outreach | Email/SMS nudges triggered when risk crosses threshold |

---

## Slide 24: Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Language | Python 3.14 | Core runtime |
| ML | scikit-learn | Preprocessing, RandomForest, calibration, metrics |
| Boosting | XGBoost, CatBoost | Gradient and ordered boosting candidates |
| Imbalance | imbalanced-learn | SMOTE, SMOTEENN oversampling |
| Explainability | SHAP | Feature contribution analysis |
| Serialisation | joblib | Model persistence |
| Dashboard | Streamlit 1.54 | Interactive web frontend |
| Charts | Plotly Express 5.x | Interactive visualisations |
| Data | pandas, numpy | Data manipulation and computation |

---

## Slide 25: Summary

**BehAnalytics at a Glance**

- **Problem:** Reactive dropout detection fails students — we need early, behavioural warning
- **Data:** 3 fused datasets → 29 engineered features → 10,000 students scored
- **Model:** 8-candidate tournament → RandomForest + SMOTE → ROC-AUC 0.8044
- **Architecture:** Artifact-driven pipeline → decoupled training and serving
- **Results:** 75% recall (balanced) / 92% recall (high-recall) — catches 3-in-4 or 9-in-10 at-risk students
- **Insights:** Attendance, GPA, and stress are the strongest behavioural signals; non-actionable features hidden from counselors
- **Impact:** 6-tab dashboard converts risk scores into counselor assignments, weekly plans, and policy insights
- **Future:** SHAP explanations, LMS integration, causal inference, automated outreach

> Every flagged student comes with a reason and a plan — not just a number.
