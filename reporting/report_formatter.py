from typing import Any, Dict


def format_report(synthesized: Dict[str, Any], recommendations: Dict[str, Any]) -> Dict[str, Any]:
    """Format a frontend-ready report JSON payload."""
    summary = synthesized.get("overall_assessment", "")
    key_findings = synthesized.get("key_abnormalities", [])
    risks = synthesized.get("risk_summary", [])
    recs = recommendations.get("recommendations", [])
    urgency_level = recommendations.get("urgency_level", "low")

    confidence_summary = "No elevated risks detected with high confidence."
    if risks:
        top_risk = risks[0]
        domain = top_risk.get("domain", "unknown")
        level = top_risk.get("risk_level", "")
        confidence = top_risk.get("confidence")
        if confidence not in (None, ""):
            confidence_summary = f"Top risk: {domain} ({level}, confidence {confidence})."
        else:
            confidence_summary = f"Top risk: {domain} ({level})."

    return {
        "summary": summary,
        "key_findings": key_findings,
        "risks": risks,
        "recommendations": recs,
        "urgency_level": urgency_level,
        "confidence_summary": confidence_summary,
        "disclaimer": (
            "This AI-generated report is for informational purposes only and is not "
            "a substitute for professional medical advice."
        ),
    }
