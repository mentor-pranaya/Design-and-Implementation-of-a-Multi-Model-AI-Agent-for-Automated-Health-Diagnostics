def analyze_health_patterns(data):
    patterns = []
    recommendations = []
    score = 0

    if data.get("Hemoglobin", 99) < 12 and data.get("RBC", 99) < 4.5:
        patterns.append("Anemia pattern detected")
        recommendations.append("Increase iron-rich foods and consult a physician.")
        score += 2

    if data.get("WBC", 0) > 11000:
        patterns.append("Possible infection pattern")
        recommendations.append("Consult doctor for infection screening.")
        score += 2

    if data.get("Glucose", 0) > 126:
        patterns.append("Diabetic risk pattern detected")
        recommendations.append("Reduce sugar intake and exercise regularly.")
        score += 3

    if data.get("LDL", 0) > 130 and data.get("HDL", 100) < 40:
        patterns.append("Cardiovascular risk pattern detected")
        recommendations.append("Avoid fatty foods and monitor cholesterol.")
        score += 3

    if score >= 6:
        risk = "High Risk"
    elif score >= 3:
        risk = "Moderate Risk"
    else:
        risk = "Low Risk"

    if not patterns:
        patterns.append("No significant health risk patterns detected")
        recommendations.append("Maintain a healthy lifestyle.")

    return patterns, risk, recommendations
