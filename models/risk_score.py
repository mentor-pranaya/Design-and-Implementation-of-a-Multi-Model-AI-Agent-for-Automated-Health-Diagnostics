def calculate_risk_score(model1_results, patterns):
    score = 0

    # Score from abnormal parameters (Model-1)
    for param, result in model1_results.items():
        if result["status"] in ["Low", "High"]:
            score += 20

    # Score from detected patterns (Model-2)
    for p in patterns:
        if p["pattern"] in [
            "Anemia Risk",
            "Leukopenia Risk",
            "Bleeding Risk (Thrombocytopenia)",
            "Thrombocytosis Risk"
        ]:
            score += 30

    return min(score, 100)
