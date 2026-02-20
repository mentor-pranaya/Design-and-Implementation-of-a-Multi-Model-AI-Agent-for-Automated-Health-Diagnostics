from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def _safe_lower(value: Any) -> str:
    if value is None:
        return ""
    return str(value).lower().strip()


def _has_keyword(text: str, keywords: List[str]) -> bool:
    lowered = _safe_lower(text)
    return any(keyword in lowered for keyword in keywords)


def _dedupe_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _get_risk_level_by_domain(risk_summary: List[Dict[str, Any]], domain: str) -> str:
    for risk in risk_summary:
        if _safe_lower(risk.get("domain")) == domain:
            return _safe_lower(risk.get("risk_level"))
    return ""


def _extract_abnormality_test_names(abnormalities: List[Dict[str, Any]]) -> List[str]:
    """Extract test names from abnormalities, handling both old and new formats."""
    test_names = []
    for abnorm in abnormalities:
        # New format: test_name key
        if 'test_name' in abnorm:
            test_names.append(_safe_lower(abnorm.get('test_name', '')))
        # Old format: parameter key
        elif 'parameter' in abnorm:
            test_names.append(_safe_lower(abnorm.get('parameter', '')))
    return test_names


def generate_recommendations(
    synthesized_findings: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate rule-based recommendations from risks, abnormalities, and context.
    
    Enhanced to use reference range abnormalities directly if available.
    Falls back to model-based risk levels.
    """
    user_context = user_context or {}
    recommendations: List[str] = []

    key_abnormalities = synthesized_findings.get("key_abnormalities", []) or []
    risk_summary = synthesized_findings.get("risk_summary", []) or []

    # Extract test names from abnormalities for pattern matching
    abnormal_tests = _extract_abnormality_test_names(key_abnormalities)
    
    logger.info(f"Generating recommendations for {len(key_abnormalities)} abnormalities, "
               f"{len(risk_summary)} risk domains")

    # Get risk levels by domain
    cardiac_risk = _get_risk_level_by_domain(risk_summary, "cardiac")
    diabetes_risk = _get_risk_level_by_domain(risk_summary, "diabetes")
    cbc_risk = _get_risk_level_by_domain(risk_summary, "cbc")
    bp_risk = _get_risk_level_by_domain(risk_summary, "bp")
    renal_risk = _get_risk_level_by_domain(risk_summary, "renal")

    # Cardiac recommendations
    if cardiac_risk == "high":
        recommendations.append("Consult a cardiologist for further evaluation.")
        recommendations.append("Adopt a heart-healthy diet and regular aerobic exercise.")
    elif cardiac_risk == "moderate":
        recommendations.append("Consider lifestyle changes to reduce cardiac risk.")
    
    # Check for specific abnormal lipid markers even if risk model didn't fire
    if any(keyword in abnormal_tests for keyword in ["total_cholesterol", "ldl", "triglycerides", "hdl"]):
        if cardiac_risk != "high":
            recommendations.append("Consider lipid management and dietary modification.")

    # Diabetes recommendations
    if diabetes_risk == "high":
        recommendations.append("Consult an endocrinologist for diabetes evaluation.")
        recommendations.append("Monitor blood glucose regularly.")
    elif diabetes_risk == "moderate":
        recommendations.append("Reduce refined sugar intake and manage body weight.")
    
    # Check for elevated glucose directly
    if any(keyword in abnormal_tests for keyword in ["glucose_fasting", "glucose_random"]):
        if diabetes_risk != "high" and not any("Monitor blood glucose" in r for r in recommendations):
            recommendations.append("Monitor and track blood glucose levels regularly.")

    # CBC recommendations
    if cbc_risk in ("high", "moderate"):
        recommendations.append("Discuss abnormal blood counts with a physician.")
    
    # Check for specific CBC abnormalities
    if any(keyword in abnormal_tests for keyword in ["hemoglobin", "rbc", "wbc", "platelets"]):
        if cbc_risk not in ("high", "moderate") and not any("blood count" in r.lower() for r in recommendations):
            recommendations.append("Recheck blood count values and consult if abnormalities persist.")

    # Blood pressure recommendations
    if bp_risk in ("high", "moderate"):
        recommendations.append("Monitor blood pressure and limit excess salt intake.")
    
    if any(keyword == "blood_pressure" for keyword in abnormal_tests):
        if bp_risk not in ("high", "moderate") and not any("blood pressure" in r.lower() for r in recommendations):
            recommendations.append("Monitor blood pressure regularly and maintain a healthy lifestyle.")

    # Renal recommendations
    if renal_risk in ("high", "moderate"):
        recommendations.append("Consult a nephrologist and monitor kidney function regularly.")
    
    if any(keyword in abnormal_tests for keyword in ["creatinine", "bun"]):
        if renal_risk not in ("high", "moderate"):
            recommendations.append("Monitor kidney function and discuss with your physician.")

    # Process additional abnormality-specific recommendations
    for abnormal in key_abnormalities:
        # Support both old and new abnormality formats
        param_name = _safe_lower(abnormal.get("test_name") or abnormal.get("parameter", ""))
        risk_level = _safe_lower(abnormal.get("risk_level", ""))
        
        # Glucose-related
        if "glucose" in param_name and "high" in risk_level:
            if not any("glucose" in r.lower() for r in recommendations):
                recommendations.append(
                    "Follow a low-glycemic diet and recheck glucose levels in 2-3 months."
                )
        
        # Lipid-related
        if any(keyword in param_name for keyword in ["ldl", "cholesterol", "triglycer"]):
            if not any("cholesterol" in r.lower() or "lipid" in r.lower() for r in recommendations):
                recommendations.append("Limit saturated fats and review lipid levels.")
        
        # Blood pressure
        if "pressure" in param_name or "systolic" in param_name or "diastolic" in param_name:
            if not any("blood pressure" in r.lower() for r in recommendations):
                recommendations.append("Track blood pressure and prioritize sleep and stress control.")

    # Lifestyle and context-based recommendations
    lifestyle = _safe_lower(user_context.get("lifestyle"))
    if lifestyle in ("sedentary", "inactive"):
        recommendations.append("Increase physical activity to at least 150 minutes per week.")

    smoker = user_context.get("smoker")
    if smoker in (True, "yes", "true", "y"):
        recommendations.append("Enroll in a smoking cessation program.")

    # Age-based recommendations
    age = user_context.get("age") or user_context.get("age_years")
    try:
        age_value = int(age) if age is not None else None
    except (TypeError, ValueError):
        age_value = None

    if age_value is not None and age_value > 50:
        if cardiac_risk in ("high", "moderate"):
            recommendations.append("Schedule a cardiology consultation due to age and risk level.")
        if diabetes_risk in ("high", "moderate"):
            recommendations.append("Increase diabetes screening frequency given age and risk.")

    # Medical history recommendations
    history = _safe_lower(user_context.get("history"))
    if history and any(keyword in history for keyword in ["diabetes", "cardiac", "heart", "hypertension"]):
        recommendations.append("Share your medical history with your clinician during follow-up.")

    # Ensure we have at least some recommendations
    if not recommendations and key_abnormalities:
        recommendations.append("Discuss test results with your healthcare provider.")
    elif not recommendations:
        recommendations.append("Maintain current healthy habits and recheck periodically.")

    # Deduplicate and preserve order
    recommendations = _dedupe_preserve_order(recommendations)

    # Determine urgency level
    urgency_level = "low"
    # Check for any high-risk findings
    if any(_safe_lower(risk.get("risk_level")) == "high" for risk in risk_summary):
        urgency_level = "high"
    # Check for high-risk abnormalities
    elif any(_safe_lower(abnorm.get("risk_level")) == "high" for abnorm in key_abnormalities):
        urgency_level = "high"
    # Check for moderate risks
    elif any(_safe_lower(risk.get("risk_level")) == "moderate" for risk in risk_summary):
        urgency_level = "moderate"
    elif any(_safe_lower(abnorm.get("risk_level")) == "moderate" for abnorm in key_abnormalities):
        urgency_level = "moderate"

    logger.info(f"Generated {len(recommendations)} recommendations, urgency: {urgency_level}")

    return {
        "recommendations": recommendations,
        "urgency_level": urgency_level,
    }
