import re
from typing import Dict

# Define patterns for common blood parameters
PARAMETER_PATTERNS = {
    "Hemoglobin": {
        "pattern": r"(hemoglobin|hb)[^\d]*([\d\.]+)\s*(g/dl|g\/dl)?",
        "unit": "g/dL"
    },
    "WBC": {
        "pattern": r"(wbc|white blood)[^\d]*([\d,]+)",
        "unit": "cells/mm3"
    },
    "Platelet Count": {
        "pattern": r"(platelet)[^\d]*([\d\.]+)\s*(lakh|lakhs)?",
        "unit": "cells/mm3"
    }

}

def extract_parameters(text: str) -> Dict:
    extracted = {}

    text = text.lower()

    for param, config in PARAMETER_PATTERNS.items():
        match = re.search(config["pattern"], text, re.IGNORECASE)
        if match:
            value = match.group(2).replace(",", "")
            extracted[param] = {
                "value": float(value),
                "unit": config["unit"]
            }
        if match:
            value = float(match.group(2))
            unit = match.group(3)

            if param == "Platelet Count" and unit:
                value = value * 100000  # convert lakh to absolute count

            extracted[param] = {
                "value": value,
                "unit": config["unit"]
        }


    return extracted
