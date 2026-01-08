import pandas as pd
from validation.data_validator import validate_value
from models.model1_parameter_interpretation import classify_parameter

# Load dataset
df = pd.read_csv("data/milestone1_cbc_dataset_150_samples.csv")

results = []

for index, row in df.iterrows():
    report = {
        "report_id": row["report_id"]
    }

    for param in ["hemoglobin", "rbc_count", "wbc_count", "mcv", "mchc", "platelet_count"]:
        value = validate_value(row[param])
        status = classify_parameter(param, value)

        report[param] = value
        report[param + "_status"] = status

    results.append(report)

# Display first 5 reports
for r in results[:5]:
    print(r)
