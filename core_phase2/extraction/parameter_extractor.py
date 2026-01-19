import re
from typing import Dict

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
        if not match:
            continue

        value = float(match.group(2).replace(",", ""))
        unit_suffix = match.group(3) if match.lastindex and match.lastindex >= 3 else None

        if param == "Platelet Count":
            if unit_suffix:
                value *= 100000
            if value > 1_000_000:
                value /= 10

        extracted[param] = {
            "value": value,
            "unit": config["unit"]
        }

    return extracted
