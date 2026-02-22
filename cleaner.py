import re

def extract_parameters(text):
    parameters = {}

    patterns = {
        "Hemoglobin": r"hemoglobin[^0-9]*([\d]+\.?\d*)",
        "Glucose": r"glucose[^0-9]*([\d]+\.?\d*)",
        "Cholesterol": r"cholesterol[^0-9]*([\d]+\.?\d*)",
        "LDL": r"ldl[^0-9]*([\d]+\.?\d*)",
        "HDL": r"hdl[^0-9]*([\d]+\.?\d*)",
        "Triglycerides": r"triglycerides[^0-9]*([\d]+\.?\d*)",
        "Creatinine": r"creatinine[^0-9]*([\d]+\.?\d*)",
        "WBC": r"wbc|white blood cell[^0-9]*([\d]+\.?\d*)",
        "RBC": r"rbc|red blood cell[^0-9]*([\d]+\.?\d*)",
        "Platelets": r"platelets[^0-9]*([\d]+\.?\d*)"
    }

    for param, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parameters[param] = float(match.group(1))

    return parameters
