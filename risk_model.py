def assess_risk(parameters):
    risk = {
        "Cardiovascular Risk": "LOW",
        "Diabetes Risk": "LOW",
        "Anemia Risk": "LOW"
    }

    glucose = parameters.get("Glucose", 0)
    cholesterol = parameters.get("Cholesterol", 0)
    hemoglobin = parameters.get("Hemoglobin", 20)

    if cholesterol > 240:
        risk["Cardiovascular Risk"] = "HIGH"
    elif cholesterol > 200:
        risk["Cardiovascular Risk"] = "MODERATE"

    if glucose >= 126:
        risk["Diabetes Risk"] = "HIGH"
    elif glucose >= 110:
        risk["Diabetes Risk"] = "MODERATE"

    if hemoglobin < 12:
        risk["Anemia Risk"] = "HIGH"

    return risk
