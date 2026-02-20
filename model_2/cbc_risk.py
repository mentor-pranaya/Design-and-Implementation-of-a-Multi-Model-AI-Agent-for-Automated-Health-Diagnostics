def assess_cbc_risk(model1_output, pattern_summary=None):
    score = 0
    findings = []

    wbc = model1_output.get("wbc")
    hb = model1_output.get("hemoglobin")
    rbc = model1_output.get("rbc")

    if wbc and wbc["status"] == "high":
        score += 2
        findings.append("Elevated WBC count")

    if hb and hb["status"] == "low":
        score += 1
        findings.append("Low hemoglobin")

    if rbc and rbc["status"] == "low":
        score += 1
        findings.append("Low RBC count")

    if score >= 3:
        risk, severity, confidence = "MODERATE", "MODERATE", 0.75
    elif score >= 1:
        risk, severity, confidence = "LOW", "MILD", 0.5
    else:
        risk, severity, confidence = "NORMAL", "NONE", 0.9
    if pattern_summary:
        rel = pattern_summary.get("relative_freq", 0.0)
        if rel > 0:
            confidence = min(0.99, max(confidence, confidence + rel * 0.5))
            if rel > 0.1:
                if risk == "NORMAL":
                    risk = "LOW"
                elif risk == "LOW":
                    risk = "MODERATE"

    return {
        "risk_level": risk,
        "severity": severity,
        "confidence": confidence,
        "pattern_score": score,
        "findings": findings,
        "reason": "CBC pattern-based abnormality detection",
        "pattern_summary": pattern_summary
    }

