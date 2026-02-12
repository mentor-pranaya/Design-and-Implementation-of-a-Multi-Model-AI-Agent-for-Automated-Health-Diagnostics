def synthesize_findings(parameters, interpretation, patterns, recommendations):
    """
    Combines outputs from multiple AI models
    into a single human-readable summary.
    """

    summary = []

    if not parameters:
        return "No clinical data could be extracted from the report."

    summary.append("📋 Report Summary")

    summary.append("\n🔬 Extracted Parameters:")
    for k, v in parameters.items():
        summary.append(f"- {k}: {v}")

    if interpretation:
        summary.append("\n🧠 Interpretation:")
        for i in interpretation:
            summary.append(f"- {i}")

    if patterns:
        summary.append("\n📊 Patterns Identified:")
        for p in patterns:
            summary.append(f"- {p}")

    if recommendations:
        summary.append("\n💡 Recommendations:")
        for r in recommendations:
            summary.append(f"- {r}")

    return "\n".join(summary)
