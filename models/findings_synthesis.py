def synthesize_findings(model1_results, patterns, risk_score, age, gender):
    summary = []

    summary.append(
        f"This blood report has been reviewed for a {age}-year-old {gender.lower()} individual."
    )

    abnormal_params = [
        p.replace("_", " ").upper()
        for p, r in model1_results.items()
        if r["status"] != "Normal"
    ]

    if abnormal_params:
        summary.append(
            f"Some values in the report are outside the usual range, particularly "
            f"{', '.join(abnormal_params)}."
        )
    else:
        summary.append(
            "All major blood parameters are within the expected healthy range."
        )

    if patterns:
        pattern_names = [p["pattern"] for p in patterns]
        summary.append(
            "When these values are looked at together, the analysis suggests "
            f"{', '.join(pattern_names)}."
        )
    else:
        summary.append(
            "No concerning health patterns were identified based on the available data."
        )

    if risk_score < 30:
        risk_text = "overall health risk appears to be low"
    elif risk_score < 60:
        risk_text = "overall health risk appears to be moderate"
    else:
        risk_text = "overall health risk appears to be higher than normal"

    summary.append(
        f"The overall risk score is {risk_score}/100, which means your {risk_text}."
    )

    summary.append(
        "This interpretation is meant to help you understand your report better and should "
        "always be considered alongside advice from a healthcare professional."
    )

    return " ".join(summary)
