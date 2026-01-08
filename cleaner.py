import re

def extract_parameters(text):
    parameters = {}

    patterns = {
        "Hemoglobin": r"Hemoglobin[:\s]+(\d+\.?\d*)",
        "Glucose": r"Glucose[:\s]+(\d+\.?\d*)",
        "Cholesterol": r"Cholesterol[:\s]+(\d+\.?\d*)"
    }

    for param, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parameters[param] = float(match.group(1))

    return parameters
