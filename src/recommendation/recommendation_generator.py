def generate_recommendations(interpretation: dict, risks: list):
    """
    Generates basic health recommendations based on findings.
    """

    recommendations = []

    # Diabetes-related advice
    if "High risk of Diabetes" in risks:
        recommendations.append(
            "Maintain a balanced diet with reduced sugar and refined carbohydrates. "
            "Engage in regular physical activity and consult a healthcare professional "
            "for further evaluation."
        )

    # Cardiovascular advice
    if "Elevated Cardiovascular Risk" in risks:
        recommendations.append(
            "Limit intake of fried and fatty foods, increase fiber-rich foods, "
            "and consider regular cardiovascular exercise after medical advice."
        )

    # High triglycerides
    if interpretation.get("Triglyceride") == "High":
        recommendations.append(
            "Reduce intake of sugary foods and alcohol, and include healthy fats "
            "such as nuts and omega-3 rich foods."
        )

    # General advice
    if not recommendations:
        recommendations.append(
            "Continue maintaining a healthy lifestyle with balanced nutrition, "
            "regular exercise, and periodic health check-ups."
        )

    # Medical disclaimer (MANDATORY)
    recommendations.append(
        "Disclaimer: This AI-generated information is for educational purposes only "
        "and is not a substitute for professional medical advice, diagnosis, or treatment."
    )

    return recommendations
