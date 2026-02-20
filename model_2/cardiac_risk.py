def assess_cardiac_risk(model1_output, pattern_summary=None):
    score = 0
    findings = []

    ldl = model1_output.get("ldl")
    hdl = model1_output.get("hdl")
    bp = model1_output.get("blood_pressure")
    glucose = model1_output.get("glucose_fasting")

    if ldl and ldl["status"] == "high":
        score += 2
        findings.append("High LDL cholesterol")

    if hdl and hdl["status"] == "low":
        score += 1
        findings.append("Low HDL cholesterol")

    if bp and bp["status"] == "high":
        score += 2
        findings.append("Hypertension")

    if glucose and glucose["status"] == "high":
        score += 1
        findings.append("Elevated glucose")

    if score >= 5:
        risk, severity, confidence = "HIGH", "SEVERE", 0.9
    elif score >= 3:
        risk, severity, confidence = "MODERATE", "MODERATE", 0.7
    elif score >= 1:
        risk, severity, confidence = "LOW", "MILD", 0.5
    else:
        risk, severity, confidence = "NORMAL", "NONE", 0.9
    if pattern_summary:
        rel = pattern_summary.get("relative_freq", 0.0)
        if rel > 0:
            confidence = min(0.99, max(confidence, confidence + rel * 0.6))
            if rel > 0.12:
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
        "reason": "Multi-parameter cardiovascular risk pattern detected",
        "pattern_summary": pattern_summary
    }
