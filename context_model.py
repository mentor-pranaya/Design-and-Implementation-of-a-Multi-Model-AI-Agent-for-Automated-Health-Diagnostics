def apply_context(risk, age, gender):
    adjusted = risk.copy()

    if age > 45 and risk["Cardiovascular Risk"] == "MODERATE":
        adjusted["Cardiovascular Risk"] = "HIGH"

    if gender.lower() == "female" and risk["Anemia Risk"] == "LOW":
        adjusted["Anemia Risk"] = "MODERATE"

    return adjusted
