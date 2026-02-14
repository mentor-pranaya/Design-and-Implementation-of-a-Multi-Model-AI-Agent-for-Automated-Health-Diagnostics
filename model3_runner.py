# model_3/model3_runner.py

from model_3.risk_adjuster import adjust_risk
from model_3.recommendation_engine import generate_recommendations


def run_model_3(model1_output, model2_output, user_context):
    """
    model1_output: dict (unused now but future-proof)
    model2_output: dict of domain risks
    user_context: age, gender, lifestyle, medical history
    """

    adjusted_risks = {}
    context_reasons = []

    for domain, domain_risk in model2_output.items():
        adjusted = adjust_risk(
            domain_risk,
            user_context,
            domain
        )
        adjusted["matched_patterns"] = domain_risk.get("matched_patterns", [])
        adjusted_risks[domain] = adjusted
        context_reasons.extend(adjusted.get("context_adjustments", []))

    recommendations = generate_recommendations(adjusted_risks)

    if context_reasons:
        context_summary = "Risk adjusted due to " + ", ".join(sorted(set(context_reasons)))
    else:
        context_summary = "Risk unchanged by contextual factors"

    return {
        "adjusted_risks": adjusted_risks,
        "recommendations": recommendations,
        "context_summary": context_summary,
        "confidence_summary": "Risk interpretation refined using personal context"
    }
