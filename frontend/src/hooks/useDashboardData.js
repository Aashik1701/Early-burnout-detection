import { useState, useEffect, useMemo } from 'react';
import Papa from 'papaparse';

export function useDashboardData() {
    const [predictions, setPredictions] = useState([]);
    const [cohortData, setCohortData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                // Load predictions
                const predRes = await fetch('/data/predictions.csv');
                if (!predRes.ok) throw new Error("Could not find predictions.csv");
                const predText = await predRes.text();
                const predParsed = Papa.parse(predText, { header: true, dynamicTyping: true, skipEmptyLines: true });

                // Load cohort data
                const cohortRes = await fetch('/data/student_dropout_dataset_v3.csv');
                if (!cohortRes.ok) throw new Error("Could not find cohort dataset");
                const cohortText = await cohortRes.text();
                const cohortParsed = Papa.parse(cohortText, { header: true, dynamicTyping: true, skipEmptyLines: true });

                // Clean arrays
                setPredictions(predParsed.data);

                // the python code creates a cohort merged data on Student_ID
                // We do it by creating a Map for O(1) lookups
                const cohortMap = new Map();
                cohortParsed.data.forEach(row => {
                    if (row.Student_ID) {
                        cohortMap.set(row.Student_ID, {
                            Department: row.Department,
                            Semester: row.Semester,
                            Gender: row.Gender,
                            Part_Time_Job: row.Part_Time_Job,
                            Age: row.Age
                        });
                    }
                });

                // Merge df and cohort
                const merged = predParsed.data.map(predRow => {
                    const cData = cohortMap.get(predRow.Student_ID) || {};
                    return {
                        ...predRow,
                        ...cData
                    };
                });

                setCohortData(merged);

            } catch (err) {
                setError(err.message);
                console.error("Data loading error", err);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    // Metrics (mocking the metrics.json logic from the dashboard)
    const metrics = useMemo(() => {
        return {
            model: "Random Forest",
            roc_auc: 0.9421,
            pr_auc: 0.8931,
            calibration: "isotonic",
            threshold: 0.5200,
            mode: "balanced",
            mode_metrics: {
                balanced: { accuracy: 0.89, precision: 0.82, recall: 0.86, f1: 0.84, threshold: 0.5200 },
                high_recall: { accuracy: 0.85, precision: 0.71, recall: 0.95, f1: 0.81, threshold: 0.3500 }
            }
        };
    }, []);

    return { data: cohortData, predictions, metrics, loading, error };
}
