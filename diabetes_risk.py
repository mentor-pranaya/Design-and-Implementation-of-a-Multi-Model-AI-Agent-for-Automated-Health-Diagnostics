def assess_diabetes_risk(model1_output, pattern_summary=None):
    score = 0
    findings = []

    glucose = model1_output.get("glucose_fasting")
    bp = model1_output.get("blood_pressure")
    hdl = model1_output.get("hdl")
    ldl = model1_output.get("ldl")

    if glucose and glucose["status"] == "high":
        score += 2
        findings.append("Elevated fasting glucose")

    if bp and bp["status"] == "high":
        score += 1
        findings.append("High blood pressure")

    if hdl and hdl["status"] == "low":
        score += 1
        findings.append("Low HDL cholesterol")

    if ldl and ldl["status"] == "high":
        score += 1
        findings.append("High LDL cholesterol")

    if score >= 4:
        risk, severity, confidence = "HIGH", "SEVERE", 0.85
    elif score >= 2:
        risk, severity, confidence = "MODERATE", "MODERATE", 0.65
    elif score == 1:
        risk, severity, confidence = "LOW", "MILD", 0.45
    else:
        risk, severity, confidence = "NORMAL", "NONE", 0.9
    # If pattern_summary indicates correlated patterns, boost confidence/severity
    if pattern_summary:
        rel = pattern_summary.get("relative_freq", 0.0)
        if rel > 0:
            # boost confidence proportionally to dataset-derived relative frequency
            confidence = min(0.99, max(confidence, confidence + rel * 0.5))
            if rel > 0.15:
                # promote risk by one level when a strong historical pattern matches
                if risk == "NORMAL":
                    risk = "LOW"
                elif risk == "LOW":
                    risk = "MODERATE"
                elif risk == "MODERATE":
                    risk = "HIGH"

    return {
        "risk_level": risk,
        "severity": severity,
        "confidence": confidence,
        "pattern_score": score,
        "findings": findings,
        "reason": "Pattern-based diabetes risk assessment",
        "pattern_summary": pattern_summary
    }
