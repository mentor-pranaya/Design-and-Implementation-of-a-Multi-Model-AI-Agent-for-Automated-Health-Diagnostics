def interpret_parameters(parameters: dict, context: dict = None):
    """
    Interpret blood parameters with basic rule-based thresholds.
    Context can include age, gender for more personalized thresholds.
    """
    findings = []
    context = context or {}

    # Hemoglobin (gender-specific thresholds)
    hb = parameters.get("hemoglobin")
    gender = context.get("gender", "unknown").lower()
    if hb is not None:
        if gender == "female" and hb < 12:
            findings.append("Low Hemoglobin (Anemia risk for females)")
        elif gender == "male" and hb < 13.5:
            findings.append("Low Hemoglobin (Anemia risk for males)")
        elif gender == "unknown" and hb < 12:
            findings.append("Low Hemoglobin")

    # Glucose and HbA1c (Diabetes indicators)
    glucose = parameters.get("glucose")
    if glucose is not None and glucose > 126:
        findings.append("High Blood Glucose (Diabetes risk)")

    hba1c = parameters.get("hba1c")
    if hba1c is not None and hba1c > 6.5:
        findings.append("High HbA1c (Poor diabetes control)")

    # White Blood Cells
    wbc = parameters.get("wbc")
    if wbc is not None:
        if wbc > 11000:
            findings.append("High WBC (Possible infection)")
        elif wbc < 4000:
            findings.append("Low WBC (Immunodeficiency risk)")

    # Platelets
    platelets = parameters.get("platelets")
    if platelets is not None:
        if platelets < 150000:
            findings.append("Low Platelet Count (Bleeding risk)")
        elif platelets > 450000:
            findings.append("High Platelet Count (Thrombosis risk)")

    # Liver Enzymes
    alt = parameters.get("alt")
    if alt is not None and alt > 40:
        findings.append("Elevated ALT (Liver damage possible)")

    ast = parameters.get("ast")
    if ast is not None and ast > 40:
        findings.append("Elevated AST (Liver damage possible)")

    alp = parameters.get("alp")
    if alp is not None and alp > 120:
        findings.append("Elevated ALP (Liver/bone issues)")

    # Bilirubin
    bilirubin_total = parameters.get("bilirubin_total")
    if bilirubin_total is not None and bilirubin_total > 1.2:
        findings.append("High Bilirubin (Jaundice risk)")

    # Lipids
    cholesterol = parameters.get("cholesterol")
    if cholesterol is not None and cholesterol > 200:
        findings.append("High Cholesterol")

    hdl = parameters.get("hdl")
    if hdl is not None and hdl < 40:
        findings.append("Low HDL (Good cholesterol)")

    ldl = parameters.get("ldl")
    if ldl is not None and ldl > 100:
        findings.append("High LDL (Bad cholesterol)")

    triglycerides = parameters.get("triglycerides")
    if triglycerides is not None and triglycerides > 150:
        findings.append("High Triglycerides")

    # Electrolytes
    sodium = parameters.get("sodium")
    if sodium is not None:
        if sodium > 145:
            findings.append("High Sodium")
        elif sodium < 135:
            findings.append("Low Sodium")

    potassium = parameters.get("potassium")
    if potassium is not None:
        if potassium > 5.0:
            findings.append("High Potassium")
        elif potassium < 3.5:
            findings.append("Low Potassium")

    calcium = parameters.get("calcium")
    if calcium is not None and calcium < 8.5:
        findings.append("Low Calcium")

    # Kidney Function
    creatinine = parameters.get("creatinine")
    if creatinine is not None and creatinine > 1.2:
        findings.append("High Creatinine (Kidney function concern)")

    urea = parameters.get("urea")
    if urea is not None and urea > 50:
        findings.append("High Urea (Kidney function concern)")

    # Thyroid
    tsh = parameters.get("tsh")
    if tsh is not None:
        if tsh > 4.0:
            findings.append("High TSH (Hypothyroidism)")
        elif tsh < 0.4:
            findings.append("Low TSH (Hyperthyroidism)")

    # Vitamins and Minerals
    iron = parameters.get("iron")
    if iron is not None and iron < 60:
        findings.append("Low Iron (Anemia risk)")

    vitamin_d = parameters.get("vitamin_d")
    if vitamin_d is not None and vitamin_d < 20:
        findings.append("Low Vitamin D")

    vitamin_b12 = parameters.get("vitamin_b12")
    if vitamin_b12 is not None and vitamin_b12 < 200:
        findings.append("Low Vitamin B12")

    return findings
