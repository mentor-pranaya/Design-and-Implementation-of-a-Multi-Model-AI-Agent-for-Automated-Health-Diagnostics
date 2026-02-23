def generate_summary(interpretations, patterns, risk, recommendations):
    text = "AI HEALTH DIAGNOSTIC REPORT\n\n"

    text += "Parameter Interpretation:\n"
    for k, v in interpretations.items():
        text += f"- {k}: {v}\n"

    text += "\nDetected Patterns:\n"
    for p in patterns:
        text += f"- {p}\n"

    text += f"\nOverall Risk Level: {risk}\n"

    text += "\nPersonalized Recommendations:\n"
    for r in recommendations:
        text += f"- {r}\n"

    text += "\nDisclaimer: This is AI-generated and not a medical diagnosis."
    return text
