def synthesize_findings(model1_results, patterns, risk_score, age, gender):
    summary = []

    abnormal_params = [
        p for p, r in model1_results.items()
        if r["status"] != "Normal"
    ]

    if abnormal_params:
        summary.append(
            f"Abnormal parameters detected: {', '.join(abnormal_params)}."
        )
    else:
        summary.append("All major blood parameters are within normal limits.")

    if patterns:
        pattern_names = [p["pattern"] for p in patterns]
        summary.append(
            f"Identified health risk patterns: {', '.join(pattern_names)}."
        )

    summary.append(
        f"Overall calculated risk score is {risk_score}/100."
    )

    summary.append(
        f"Interpretation adjusted for a {age}-year-old {gender.lower()}."
    )

    return " ".join(summary)
