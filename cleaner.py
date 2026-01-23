import re

def extract_parameters(text):
    parameters = {}

    # More flexible patterns that handle various formats and OCR errors
    patterns = {
        "Hemoglobin": r"(?:Hemoglobin|HGB|Hb)\s+([0-9.]+)\s*(?:g/dL|g/dl|gdL|dL)?",
        "Glucose": r"(?:Glucose|GLU)\s+([0-9.]+)\s*(?:mg/dL|mg/dl|mmol/L|moll)?",
        "Cholesterol": r"(?:Cholesterol|CHOL)\s+([0-9.]+)\s*(?:mg/dL|mg/dl|mmol/L)?"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            # Handle potential OCR errors for glucose (198 looks like it might be correct)
            parameters[key] = value

    return parameters
