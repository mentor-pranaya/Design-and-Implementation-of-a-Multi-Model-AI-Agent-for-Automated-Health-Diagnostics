def explain_health_risks(parameters, risk_scores):
    risks = []

    glucose = parameters.get("Glucose", 0)
    cholesterol = parameters.get("Cholesterol", 0)
    hemoglobin = parameters.get("Hemoglobin", 0)

    if cholesterol > 200:
        risks.append(
            "High cholesterol increases the risk of heart disease, stroke, and artery blockage."
        )

    if glucose >= 126:
        risks.append(
            "High blood glucose may indicate diabetes, which can damage kidneys, nerves, and eyes."
        )
    elif glucose >= 110:
        risks.append(
            "Slightly elevated glucose may indicate prediabetes and increased future diabetes risk."
        )

    if hemoglobin < 12:
        risks.append(
            "Low hemoglobin suggests anemia, which can cause fatigue, dizziness, and weakness."
        )

    if glucose > 110 and cholesterol > 200:
        risks.append(
            "Combined high glucose and cholesterol suggest metabolic syndrome and higher cardiovascular risk."
        )

    if not risks:
        risks.append("No significant health risks detected based on current parameters.")

    return risks
