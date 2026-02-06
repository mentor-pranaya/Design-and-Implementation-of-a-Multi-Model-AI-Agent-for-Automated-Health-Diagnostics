import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from models.model1_parameter_interpretation import interpret_parameters
from models.model2_pattern_recognition import detect_health_patterns
from models.risk_score import calculate_risk_score

df = pd.read_csv("data/blood_count_dataset.csv")

pattern_counts = {}
risk_scores = []

for _, row in df.iterrows():
    params = {
        "hemoglobin": row["hemoglobin"],
        "rbc_count": row["rbc_count"],
        "wbc_count": row["wbc_count"],
        "platelet_count": row["platelet_count"],
        "mcv": row["mcv"]
    }

    model1_results = interpret_parameters(params)
    patterns = detect_health_patterns(model1_results)

    score = calculate_risk_score(model1_results, patterns)
    risk_scores.append(score)

    for p in patterns:
        name = p["pattern"]
        pattern_counts[name] = pattern_counts.get(name, 0) + 1

print("Detected Health Patterns:")
for k, v in pattern_counts.items():
    print(f"{k}: {v}")

print("\nAverage Risk Score:", sum(risk_scores) / len(risk_scores))
