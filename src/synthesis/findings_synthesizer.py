def synthesize_findings(interpretation: dict, risks: list):
    """
    Combines model outputs into a human-readable summary.
    """

    summary = []

    # Summarize abnormal parameters
    abnormal = [
        f"{param} is {status}"
        for param, status in interpretation.items()
        if status != "Normal"
    ]

    if abnormal:
        summary.append(
            "Some blood parameters are outside the normal range: "
            + ", ".join(abnormal) + "."
        )
    else:
        summary.append("All measured blood parameters are within normal range.")

    # Summarize risks
    if risks and "No major risk patterns detected" not in risks:
        summary.append(
            "Risk pattern analysis indicates the following concerns: "
            + ", ".join(risks) + "."
        )
    else:
        summary.append("No significant health risk patterns were detected.")

    return " ".join(summary)
