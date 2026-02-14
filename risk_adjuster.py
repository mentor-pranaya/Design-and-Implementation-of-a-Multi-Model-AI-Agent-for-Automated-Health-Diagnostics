# model_3/risk_adjuster.py

def clamp(value, min_v=0.0, max_v=1.0):
    return max(min_v, min(max_v, value))


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [k for k, v in value.items() if v]
    return [value]


def _risk_level_from_severity(severity):
    if severity <= 0.3:
        return "low"
    if severity <= 0.6:
        return "moderate"
    return "high"


def adjust_risk(domain_risk, user_context, domain_name):
    """
    domain_risk: output from Model 2 for one domain
    user_context: dict with age, gender, lifestyle, medical_history
    """
    severity = float(domain_risk.get("severity_score", 0.0) or 0.0)
    confidence = float(domain_risk.get("confidence", 0.0) or 0.0)

    adjustments = []
    multiplier = 1.0

    age = user_context.get("age")
    gender = user_context.get("gender")
    lifestyle = _as_list(user_context.get("lifestyle"))
    medical_history = _as_list(user_context.get("medical_history"))

    # Context multipliers
    if age and age > 50 and domain_name == "cardiac":
        multiplier *= 1.15
        adjustments.append("Age above 50 increases cardiac risk")

    if age and age > 65 and domain_name == "cardiac":
        multiplier *= 1.1
        adjustments.append("Age above 65 increases cardiac risk")

    if "smoker" in lifestyle and domain_name == "cardiac":
        multiplier *= 1.2
        adjustments.append("Smoking history increases cardiac risk")

    if "family_history_diabetes" in medical_history and domain_name == "diabetes":
        multiplier *= 1.25
        adjustments.append("Family history of diabetes")

    if "physically_active" in lifestyle:
        multiplier *= 0.9
        adjustments.append("Physical activity reduces risk")

    if gender and domain_name == "cardiac" and str(gender).lower() in ("male", "m"):
        multiplier *= 1.05
        adjustments.append("Male gender slightly increases cardiac risk")

    severity *= multiplier
    severity = clamp(severity)

    # Slightly increase confidence if multiple contextual factors align
    if len(adjustments) >= 2:
        confidence = clamp(confidence + 0.05)

    risk_level = _risk_level_from_severity(severity)

    return {
        "risk_level": risk_level,
        "severity_score": round(severity, 3),
        "confidence": round(confidence, 3),
        "context_adjustments": adjustments,
    }
