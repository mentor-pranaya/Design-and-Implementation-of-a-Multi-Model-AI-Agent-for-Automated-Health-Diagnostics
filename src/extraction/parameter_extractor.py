import re


def extract_parameters(report_text: str):
    parameters = {}

    patterns = {
        "Hemoglobin": r"Hemoglobin\s+([\d.]+)\s*g/dL",
        "Cholesterol": r"Cholesterol\s+([\d.]+)\s*mg/dL",
        "Triglyceride": r"Triglyceride\s+H?\s*([\d.]+)\s*mg/dL",
        "Fasting Blood Sugar": r"Fasting Blood Sugar\s+H?\s*([\d.]+)\s*mg/dL",
        "HbA1c": r"HbA1c\s+H?\s*([\d.]+)\s*%"
    }

    for test, pattern in patterns.items():
        match = re.search(pattern, report_text, re.IGNORECASE)
        if match:
            parameters[test] = float(match.group(1))

    return parameters
