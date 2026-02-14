EXPLANATIONS = {
    ("glucose_fasting", "pre_high"): "Fasting glucose is borderline high and may indicate impaired glucose tolerance.",
    ("glucose_fasting", "high"): "Fasting glucose is high and may indicate diabetes; consider repeat testing and clinical correlation.",
    ("ldl", "high"): "LDL cholesterol is high and associated with increased cardiovascular risk.",
    ("hdl", "low"): "HDL cholesterol is low; low HDL is a risk factor for cardiovascular disease.",
    ("hemoglobin", "low"): "Hemoglobin is below the expected range for the reported sex/age and may indicate anemia.",
    ("rbc", "low"): "Red blood cell count is low which can be associated with anemia or recent bleeding.",
    ("bp_systolic", "high"): "Systolic blood pressure is elevated; consider evaluation for hypertension.",
    ("bp_diastolic", "high"): "Diastolic blood pressure is elevated; consider evaluation for hypertension.",
}


def get_explanation(parameter: str, status: str) -> str:
    return EXPLANATIONS.get((parameter, status), "")
