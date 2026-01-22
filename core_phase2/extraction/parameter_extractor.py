import re
from typing import Dict

PARAMETER_PATTERNS = {
    "Hemoglobin": {
        "pattern": r"hemoglobin\s+[^\d]*([\d\.]+)\s*g/dl",
        "unit": "g/dL"
    },
    "WBC": {
        "pattern": r"wbc\s+count[^\d]*([\d,]+)\s*/cmm",
        "unit": "cells/mm3"
    },
    "Platelet Count": {
        "pattern": r"platelet\s+count[^\d]*([\d]+)\s*/",
        "unit": "cells/mm3"
    },
    "Fasting Blood Sugar": {
        "pattern": r"fasting\s+blood\s+sugar[^\d]+h?\s*([\d\.]+)\s*mg/dl",
        "unit": "mg/dL"
    },
    "HbA1c": {
        "pattern": r"result\s+unit[^\d]+h?\s*([\d\.]+)\s*%",
        "unit": "%"
    },
    "Total Cholesterol": {
        "pattern": r"total\s+cholesterol[^\d]*([\d\.]+)\s*mg/dl",
        "unit": "mg/dL"
    },
    "Triglyceride": {
        "pattern": r"triglyceride[^\d]+result[^\d]*([\d\.]+)\s*mg/dl",
        "unit": "mg/dL"
    },
    "HDL Cholesterol": {
        "pattern": r"hdl\s+cholesterol[^\d]+result[^\d]*([\d\.]+)\s*mg/dl",
        "unit": "mg/dL"
    },
    "LDL Cholesterol": {
        "pattern": r"(?:direct\s+)?ldl[^\d]+result[^\d]*([\d\.]+)\s*mg/dl",
        "unit": "mg/dL"
    },
    "Creatinine": {
        "pattern": r"creatinine[^\d]+result[^\d]*([\d\.]+)\s*mg/dl",
        "unit": "mg/dL"
    },
    "TSH": {
        "pattern": r"tsh[^\d]+([\d\.]+)\s*microiu/ml",
        "unit": "µIU/mL"
    },
    "T3": {
        "pattern": r"t3[^\d]+([\d\.]+)\s*ng/ml",
        "unit": "ng/mL"
    },
    "T4": {
        "pattern": r"t4[^\d]+([\d\.]+)\s*mg/ml",
        "unit": "µg/dL"
    }
}

def extract_parameters(text: str) -> Dict:
    extracted = {}
    text = text.lower()

    for param, config in PARAMETER_PATTERNS.items():
        match = re.search(config["pattern"], text, re.IGNORECASE | re.DOTALL)
        if not match:
            continue

        value_str = match.group(1).replace(",", "")
        value = float(value_str)

        if param == "Platelet Count":
            # Platelet values are often large numbers
            if value < 10000:  # Likely in lakhs
                value *= 100000

        extracted[param] = {
            "value": value,
            "unit": config["unit"]
        }

    return extracted
