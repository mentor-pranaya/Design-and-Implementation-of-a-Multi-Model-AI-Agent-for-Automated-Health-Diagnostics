SYNONYMS = {
    "fasting blood sugar": "glucose_fasting",
    "fbs": "glucose_fasting",
    "blood sugar fasting": "glucose_fasting",
    "hdl cholesterol": "hdl",
    "ldl cholesterol": "ldl",
    "total cholesterol": "total_cholesterol",
    "hemoglobin": "hemoglobin",
    "hb": "hemoglobin",
    "red blood cell": "rbc",
    "rbc": "rbc",
    "systolic": "bp_systolic",
    "diastolic": "bp_diastolic",
}


def normalize_name(raw_name: str) -> str:
    if not raw_name:
        return raw_name
    key = raw_name.strip().lower()
    return SYNONYMS.get(key, raw_name)
