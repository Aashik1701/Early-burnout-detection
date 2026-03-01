### Project Overview and Core Objectives

The fundamental challenge educational institutions face is that they typically identify academic distress only after a student’s performance has demonstrably dropped, at which point effective intervention becomes exceedingly difficult. To solve this, you are building an advanced behavioural analytics system engineered to predict three critical metrics: the student's Burnout Risk Level categorized as Low, Medium, or High, specific Academic Disengagement Indicators, and an overall Dropout Probability percentage. By analyzing early behavioural signals rather than lagging grade indicators, this platform shifts the paradigm from reactive to proactive student management. The final output of your solution must provide a quantifiable Risk Score ranging from 0 to 100, explicitly isolate the key behavioural triggers that are influencing the prediction, and dynamically output a recommended intervention strategy tailored to that specific student's profile.

### Data Strategy and Synthetic Engineering

Because genuine student behavioural data is heavily restricted by privacy regulations, your strategy relies on a hybrid approach utilizing a public dataset augmented with intelligently simulated features to fulfill the specific hackathon constraints. You will utilize a robust, publicly available dataset from Kaggle—such as the "Student Dropout Prediction Dataset"—which provides thousands of realistic baseline records containing essential tabular features like attendance trends and assignment submission delays. However, to strictly satisfy the hackathon’s suggestion to incorporate sentiment analysis from feedback forms, you will programmatically engineer a new text-based feature. By writing a Python script that correlates the dataset's existing numerical stress index with predefined arrays of synthetic student feedback, you generate realistic textual data. For instance, students with high delays and poor attendance will be assigned synthetically generated negative feedback indicating they feel overwhelmed. This crucial step not only provides the necessary data for your NLP pipeline but also fulfills the mandatory submission requirement to explicitly document what behavioural features you engineered from the public data.

### Predictive Machine Learning and NLP Architecture

The intelligence of this platform relies on a dual-pronged machine learning architecture that processes both numerical behaviours and natural language simultaneously. First, the synthetically engineered student feedback text is passed through an advanced transformer model, such as IndicBERT or RoBERTa, to perform rigorous sentiment analysis. This NLP pipeline extracts a granular sentiment polarity score, converting qualitative human emotion into a quantitative metric. This sentiment score is then concatenated with the student's tabular behavioural data, including their LMS login frequency and assignment delays, to form a comprehensive feature vector. This combined data is fed into a powerful classification algorithm, like XGBoost or a Random Forest model, which is trained to output the precise Dropout Probability and the categorical Burnout Risk Level. Furthermore, by leveraging the model's feature importance attributes, the system can dynamically isolate and explain the key behavioural triggers driving the prediction, allowing educators to understand exactly why a student was flagged.

### Full-Stack Integration and Visualization Dashboard

While the problem statement notes that a visualization dashboard is optional but encouraged, deploying a highly responsive, interactive web interface is the definitive way to secure top marks in the "Visualization and presentation quality" evaluation criterion. You will architect a decoupled full-stack application utilizing a robust React frontend and a Node.js backend, with MongoDB serving as the central database for all student records. The trained machine learning model will be exported as a serialized file and wrapped in a lightweight Python FastAPI or Flask service. When a university administrator accesses the React dashboard, the Node.js backend retrieves the latest student metrics from MongoDB and securely queries the Python API to generate real-time risk predictions. The frontend will feature a comprehensive global overview of the student body's health, alongside detailed individual profiles that visually map the 0-100 Risk Score, highlight the exact behavioural triggers, and display a rule-based recommended intervention strategy—such as automatically scheduling an academic advising appointment if extreme assignment delays are detected.



1. The Project: What Are You Building?
You are building an AI-powered early warning system for universities. The goal is to detect academic issues before a student's performance completely drops, at which point intervention is difficult.

The system analyzes early behavioural signals—like LMS login frequency, attendance changes, and assignment delays—to catch burnout risk.

The Final Output: When a judge looks at your React dashboard, they will click on a student's profile and immediately see:

A Risk Score (0-100) and Categorical Burnout Level (Low/Medium/High).

The specific behavioural triggers causing that score (e.g., "7-day assignment delay + negative feedback").

A recommended intervention strategy (e.g., "Schedule academic advising").

2. The Dataset Strategy: The Hybrid Approach
Do not waste time simulating 10,000 rows of math from scratch. Use the Student Dropout Prediction Dataset (by meharshanali) from Kaggle, and engineer the missing pieces.

The Core Data: This public dataset gives you ready-to-use columns for Attendance_Rate and Assignment_Delay_Days mapped to a Dropout outcome.

The NLP Engineering: The dataset contains a Stress_Index. You will write a Python script to map high stress scores to synthetic negative feedback text, and low stress scores to positive text. This fulfills the requirement to use sentiment analysis from feedback forms.

3. The Tech Stack (Optimized for Your Strengths)
You need a decoupled architecture so your AI heavy lifting doesn't crash your web interface.

The ML Brain (Python): Use Scikit-Learn to train an XGBoost or Random Forest classifier on the numerical data.

The NLP Engine (HuggingFace): Implement a pre-trained transformer model like IndicBERT or RoBERTa. You can process the simulated feedback text incredibly fast to extract a sentiment polarity score (-1.0 to 1.0) and feed it into your XGBoost model.

The API Bridge (FastAPI/Flask): Wrap your trained .pkl model in a lightweight Python API that accepts JSON data and returns a prediction.

The Backend (Node.js + Express & MongoDB): Set up your Node.js server to handle frontend requests, query your MongoDB database containing the student records, and ping the Python API for the live risk scores.

The Frontend Dashboard (React): Build a responsive, clean UI. A sleek visualization dashboard is highly encouraged and will easily set you apart during evaluation.
+1

4. The Hackathon Execution Plan 
Phase 1: Model & Data Engineering 

Fire up Google Colab. Download the Kaggle dataset.

Write the script to generate the synthetic feedback text based on the Stress_Index.

Run the text through your NLP transformer to generate sentiment scores.

Train your XGBoost model to predict the dropout risk.

Extract the "Feature Importances" chart from your model (save this image for your presentation!). Export the model as a .pkl file.

Phase 2: Backend & API Setup (Saturday 9:00 PM - 1:00 AM)

Build the Python FastAPI to serve the .pkl model.

Initialize the Node.js server and MongoDB.

Write a simple rule-based engine in Node.js for the interventions (e.g., if top_trigger == 'assignment_delay' return 'Extend deadline by 48 hours').

Phase 3: The React Dashboard 

Build a grid view showing all students and their high-level risk categories.

Build the individual student modal/page showing the exact 0-100 score, the triggers, and the intervention strategy.

Phase 4: Documentation & Polish 

GitHub Repository: Ensure your repo is public. Include clean, well-structured source code. Update the README to explicitly state the public dataset source, why it fits behavioural analytics, and the behavioural features you engineered (the NLP sentiment).
+2


Model Explanation Document: Write this PDF strictly under the 5-page limit. Detail your feature engineering logic, model selection reasoning, and the behavioural insights derived.
