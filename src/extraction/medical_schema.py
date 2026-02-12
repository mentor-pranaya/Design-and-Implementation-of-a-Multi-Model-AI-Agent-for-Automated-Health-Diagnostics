MEDICAL_SCHEMA = {
    # Existing parameters
    "glucose": ["glucose", "blood sugar", "sugar level"],
    "cholesterol": ["cholesterol", "total cholesterol"],
    "hemoglobin": ["hemoglobin", "hb", "hgb"],
    "blood_pressure": ["blood pressure", "bp"],

    # Additional parameters from models
    "hba1c": ["hba1c", "glycated hemoglobin", "a1c"],
    "wbc": ["wbc", "white blood cell", "leukocytes"],
    "platelets": ["platelets", "plt", "thrombocytes"],

    # Liver enzymes
    "alt": ["alt", "alanine aminotransferase", "sgpt"],
    "ast": ["ast", "aspartate aminotransferase", "sgot"],
    "alp": ["alp", "alkaline phosphatase"],
    "bilirubin_total": ["total bilirubin", "bilirubin total"],
    "bilirubin_direct": ["direct bilirubin", "bilirubin direct"],

    # Lipids
    "hdl": ["hdl", "hdl cholesterol"],
    "ldl": ["ldl", "ldl cholesterol"],
    "triglycerides": ["triglycerides", "tg"],

    # Electrolytes
    "sodium": ["sodium", "na"],
    "potassium": ["potassium", "k"],
    "chloride": ["chloride", "cl"],
    "calcium": ["calcium", "ca"],
    "magnesium": ["magnesium", "mg"],

    # Kidney function
    "creatinine": ["creatinine", "crea"],
    "urea": ["urea", "bun", "blood urea nitrogen"],
    "uric_acid": ["uric acid", "ua"],

    # Thyroid
    "tsh": ["tsh", "thyroid stimulating hormone"],
    "t3": ["t3", "triiodothyronine"],
    "t4": ["t4", "thyroxine"],

    # Other common markers
    "iron": ["iron", "serum iron"],
    "vitamin_d": ["vitamin d", "25-hydroxyvitamin d"],
    "vitamin_b12": ["vitamin b12", "b12"]
}
