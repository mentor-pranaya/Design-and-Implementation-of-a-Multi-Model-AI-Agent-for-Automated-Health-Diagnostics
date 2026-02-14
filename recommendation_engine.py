# model_3/recommendation_engine.py

RECOMMENDATIONS = {
    "cardiac": {
        "high": [
            "Consult a cardiologist",
            "Adopt heart-healthy diet and regular exercise",
            "Monitor blood pressure and cholesterol regularly"
        ],
        "moderate": [
            "Consider lifestyle modifications",
            "Periodic lipid profile monitoring"
        ]
    },
    "diabetes": {
        "high": [
            "Consult an endocrinologist",
            "Monitor blood glucose regularly"
        ],
        "moderate": [
            "Reduce sugar intake",
            "Maintain healthy body weight"
        ]
    },
    "cbc": {
        "high": [
            "Consult a physician for further blood investigations"
        ]
    }
}


def generate_recommendations(adjusted_risks):
    advice = []

    for domain, risk_data in adjusted_risks.items():
        level = risk_data.get("risk_level")
        domain_recs = RECOMMENDATIONS.get(domain, {})
        advice.extend(domain_recs.get(level, []))

    return list(set(advice))
