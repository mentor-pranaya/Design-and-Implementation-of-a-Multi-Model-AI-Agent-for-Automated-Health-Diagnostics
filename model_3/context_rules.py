# model_3/context_rules.py

AGE_RULES = [
    {"min_age": 50, "severity_boost": 0.15, "reason": "Age above 50"},
    {"min_age": 65, "severity_boost": 0.25, "reason": "Age above 65"}
]

LIFESTYLE_RULES = {
    "smoking": {
        "severity_boost": 0.2,
        "reason": "Smoking history increases cardiovascular risk"
    },
    "alcohol": {
        "severity_boost": 0.1,
        "reason": "Regular alcohol intake"
    },
    "sedentary": {
        "severity_boost": 0.15,
        "reason": "Sedentary lifestyle"
    }
}

MEDICAL_HISTORY_RULES = {
    "diabetes": {
        "risk_domains": ["cardiac", "kidney"],
        "severity_boost": 0.2,
        "reason": "Existing diabetes"
    },
    "hypertension": {
        "risk_domains": ["cardiac"],
        "severity_boost": 0.2,
        "reason": "History of hypertension"
    }
}
