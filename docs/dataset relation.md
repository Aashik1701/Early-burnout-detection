1. College Student Management Dataset (by ziya07)
Link: https://www.kaggle.com/datasets/ziya07/college-student-management-dataset

Why use it: This is the top pick because it already contains the exact labels you need (Low, Medium, High risk) and features like LMS logins, course load, and attendance rates.

2. Student Dropout Prediction Dataset (by meharshanali)
Link: https://www.kaggle.com/datasets/meharshanali/student-dropout-prediction-dataset

Why use it: This is a very recent dataset (simulating 10,000 students) that includes realistic features like assignment delay days, attendance rates, and a stress index. You can easily map that stress index to synthetic NLP feedback text.

3. Student Learning Interaction Logs Dataset (by ziya07)
Link: https://www.kaggle.com/datasets/ziya07/student-learning-interaction-logs-dataset

Why use it: If you want to build a time-series model focusing heavily on granular behaviour, this dataset provides session-by-session learning interaction data.

1. College Student Management Dataset (The Quick Starter)
This dataset maps perfectly to your primary classification targets.

Maps to Input: LMS login frequency and Attendance trends.

Maps to Output: Burnout Risk Level (Low / Medium / High).

How to use it: This dataset is a massive time-saver because the target variable is already categorized exactly how the judges requested (Low/Medium/High). You can feed its lms_logins_past_month, attendance_rate, and course_load into a Random Forest or XGBoost model. The model will output the categorical risk level, and you can extract the feature weights to generate the "Key behavioural triggers" to display on your dashboard.

2. Student Dropout Prediction Dataset (The Dropout & NLP Sandbox)
This dataset gives you the granular numeric features needed for probability scoring and a clever way to implement your NLP pipeline.

Maps to Input: Assignment submission delays and Attendance trends.

Maps to Output: Dropout Probability and A Risk Score (0-100).

How to use it: It includes exact columns like Assignment_Delay_Days. Because it has a binary dropout target (0 or 1), you can train a model using .predict_proba() to output a raw percentage (e.g., 82% risk of dropping out)—satisfying the 0–100 Risk Score requirement.

The NLP Integration: It includes a Stress_Index. You can write a quick script to map high stress scores to synthetic negative feedback text (e.g., "I cannot keep up with the assignments"), and low stress to positive text. Run that text through a pre-trained transformer model (like IndicBERT or RoBERTa) to get a sentiment score, satisfying the "Sentiment analysis from feedback forms" requirement.

3. Student Learning Interaction Logs Dataset (The Anomaly Detector)
This dataset provides the time-series depth needed to prove advanced behavioural analytics.

Maps to Input: Activity pattern irregularities and LMS login frequency.

Maps to Output: Academic Disengagement Indicators.

How to use it: Instead of flat averages, this dataset tracks individual study sessions. You can engineer rolling averages to detect "drops" in behaviour. For example, if a student’s average time spent on video modules drops by 60% over two weeks, your backend can flag this as a specific Academic Disengagement Indicator and push a customized alert to your frontend UI.

The Missing Piece: "Recommended Intervention Strategy"
None of the datasets will have an "Intervention Strategy" column. You will need to build a simple rule-based engine in your Node.js or Python backend to map the model's outputs to specific actions.

Example: If the model flags "High Assignment Delays" as the top trigger -> Return intervention: "Trigger automated email to Academic Advisor & extend deadline by 48 hours."