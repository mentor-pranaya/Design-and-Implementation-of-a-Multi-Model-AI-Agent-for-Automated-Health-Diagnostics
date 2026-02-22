"""
Findings Synthesis Engine (Milestone 3)
Aggregates and synthesizes outputs from all analysis models (Model 1, Model 2, Model 3)
into a coherent, comprehensive summary of the blood report findings.
"""


def synthesize_findings(parameters, interpretation, risk_assessment, contextual_risk, age=None, gender=None):
    """
    Synthesize all model outputs into a coherent, comprehensive summary.
    
    Args:
        parameters: dict - Raw extracted blood parameters with values
        interpretation: dict - Model 1 output (param classification: HIGH/LOW/NORMAL)
        risk_assessment: dict - Model 2 output (risk scores from parameter combinations)
        contextual_risk: dict - Model 3 output (context-adjusted risk scores)
        age: int - User age (optional)
        gender: str - User gender (optional)
    
    Returns:
        dict - Comprehensive synthesis with structured findings
    """
    
    synthesis = {
        "summary": "",
        "critical_findings": [],
        "abnormal_parameters": [],
        "normal_parameters": [],
        "risk_patterns": [],
        "contextual_insights": [],
        "overall_health_status": "",
        "priority_areas": []
    }
    
    # ===== PART 1: Identify Abnormal and Normal Parameters =====
    abnormal_count = 0
    for param, status in interpretation.items():
        if status != "NORMAL":
            abnormal_count += 1
            value = parameters.get(param, "N/A")
            synthesis["abnormal_parameters"].append({
                "parameter": param,
                "value": value,
                "status": status,
                "reference_range": _get_reference_range(param, age, gender)
            })
        else:
            value = parameters.get(param, "N/A")
            synthesis["normal_parameters"].append({
                "parameter": param,
                "value": value,
                "status": "NORMAL",
                "reference_range": _get_reference_range(param, age, gender)
            })
    
    # ===== PART 2: Identify Critical Findings (High/Low Parameters) =====
    for param, status in interpretation.items():
        if status == "HIGH":
            synthesis["critical_findings"].append(
                f"{param} is significantly ELEVATED ({parameters.get(param, 'N/A')})"
            )
        elif status == "LOW":
            synthesis["critical_findings"].append(
                f"{param} is significantly DECREASED ({parameters.get(param, 'N/A')})"
            )
    
    # ===== PART 3: Analyze Risk Patterns =====
    high_risk_count = 0
    moderate_risk_count = 0
    
    for risk_category, risk_level in risk_assessment.items():
        risk_pattern = {
            "category": risk_category,
            "level": risk_level,
            "contributing_factors": _get_contributing_factors(risk_category, parameters, interpretation),
            "clinical_significance": _get_clinical_significance(risk_category, risk_level)
        }
        synthesis["risk_patterns"].append(risk_pattern)
        
        if risk_level == "HIGH":
            high_risk_count += 1
        elif risk_level == "MODERATE":
            moderate_risk_count += 1
    
    # ===== PART 4: Contextual Insights =====
    if contextual_risk:
        for risk_category, adjusted_level in contextual_risk.items():
            original_level = risk_assessment.get(risk_category, "N/A")
            if adjusted_level != original_level:
                insight = {
                    "risk_area": risk_category,
                    "adjustment_reason": _get_adjustment_reason(risk_category, age, gender),
                    "original_level": original_level,
                    "adjusted_level": adjusted_level,
                    "demographic_factor": "Age" if age and age > 45 else "Gender" if gender else "Other"
                }
                synthesis["contextual_insights"].append(insight)
    
    # ===== PART 5: Determine Overall Health Status =====
    if high_risk_count >= 2 or abnormal_count >= 5:
        synthesis["overall_health_status"] = "CONCERNING - Multiple abnormalities detected"
        status_code = "CONCERNING"
    elif high_risk_count == 1 or moderate_risk_count >= 2 or abnormal_count >= 3:
        synthesis["overall_health_status"] = "ATTENTION REQUIRED - Several elevated risk factors"
        status_code = "ATTENTION_REQUIRED"
    elif abnormal_count >= 1:
        synthesis["overall_health_status"] = "MONITOR - Some parameters are outside normal range"
        status_code = "MONITOR"
    else:
        synthesis["overall_health_status"] = "HEALTHY - Most parameters within normal range"
        status_code = "HEALTHY"
    
    # ===== PART 6: Prioritize Areas Requiring Attention =====
    priority_mapping = _get_priority_areas(interpretation, risk_assessment, contextual_risk, parameters)
    synthesis["priority_areas"] = priority_mapping
    
    # ===== PART 7: Generate Executive Summary =====
    synthesis["summary"] = _generate_executive_summary(
        abnormal_count,
        high_risk_count,
        moderate_risk_count,
        synthesis["critical_findings"],
        synthesis["priority_areas"],
        age,
        gender,
        status_code
    )
    
    return synthesis


def _get_reference_range(parameter, age=None, gender=None):
    """Get standard reference range for a parameter with optional age/gender adjustment."""
    ranges = {
        "Hemoglobin": "(12-17 g/dL)",
        "Glucose": "(70-110 mg/dL)",
        "Cholesterol": "(0-200 mg/dL)",
        "LDL": "(0-100 mg/dL)",
        "HDL": "(>40 mg/dL for men, >50 mg/dL for women)",
        "Triglycerides": "(0-150 mg/dL)",
        "Creatinine": "(0.7-1.3 mg/dL)",
        "BUN": "(7-20 mg/dL)",
        "ALT": "(7-56 U/L)",
        "AST": "(10-40 U/L)",
        "Bilirubin": "(0.1-1.2 mg/dL)",
        "Protein": "(6.0-8.3 g/dL)",
        "Albumin": "(3.4-5.4 g/dL)",
        "Platelet Count": "(150-400 K/uL)",
        "WBC": "(4.5-11.0 K/uL)",
        "RBC": "(4.5-5.5 M/uL for men, 4.0-5.0 M/uL for women)"
    }
    return ranges.get(parameter, "Standard range not available")


def _get_contributing_factors(risk_category, parameters, interpretation):
    """Identify which parameters contribute to a specific risk category."""
    factors = []
    
    if risk_category == "Cardiovascular Risk":
        if interpretation.get("Cholesterol") == "HIGH":
            factors.append(f"Elevated Cholesterol ({parameters.get('Cholesterol', 'N/A')} mg/dL)")
        if interpretation.get("Glucose") == "HIGH":
            factors.append(f"High Glucose ({parameters.get('Glucose', 'N/A')} mg/dL)")
        if parameters.get("LDL", 0) > 100:
            factors.append(f"Elevated LDL ({parameters.get('LDL', 'N/A')} mg/dL)")
        if parameters.get("HDL", 0) < 40:
            factors.append(f"Low HDL ({parameters.get('HDL', 'N/A')} mg/dL)")
    
    elif risk_category == "Diabetes Risk":
        if interpretation.get("Glucose") in ["HIGH", "BORDERLINE"]:
            factors.append(f"Elevated Glucose ({parameters.get('Glucose', 'N/A')} mg/dL)")
        if parameters.get("Triglycerides", 0) > 150:
            factors.append(f"High Triglycerides ({parameters.get('Triglycerides', 'N/A')} mg/dL)")
    
    elif risk_category == "Anemia Risk":
        if interpretation.get("Hemoglobin") == "LOW":
            factors.append(f"Low Hemoglobin ({parameters.get('Hemoglobin', 'N/A')} g/dL)")
        if parameters.get("RBC", 0) < 4.5:
            factors.append(f"Low RBC ({parameters.get('RBC', 'N/A')} M/uL)")
    
    elif risk_category == "Liver Risk":
        if interpretation.get("ALT") == "HIGH":
            factors.append(f"Elevated ALT ({parameters.get('ALT', 'N/A')} U/L)")
        if interpretation.get("AST") == "HIGH":
            factors.append(f"Elevated AST ({parameters.get('AST', 'N/A')} U/L)")
    
    elif risk_category == "Kidney Risk":
        if interpretation.get("Creatinine") == "HIGH":
            factors.append(f"Elevated Creatinine ({parameters.get('Creatinine', 'N/A')} mg/dL)")
        if interpretation.get("BUN") == "HIGH":
            factors.append(f"Elevated BUN ({parameters.get('BUN', 'N/A')} mg/dL)")
    
    return factors if factors else ["Multiple contributing factors"]


def _get_clinical_significance(risk_category, risk_level):
    """Explain the clinical significance of a risk level."""
    significance_map = {
        "Cardiovascular Risk": {
            "HIGH": "Elevated risk of heart disease, stroke, and arterial damage. Immediate lifestyle modification and medical consultation recommended.",
            "MODERATE": "Moderate risk of cardiovascular complications. Lifestyle changes and monitoring are advisable.",
            "LOW": "Low risk for cardiovascular complications. Continue healthy lifestyle practices."
        },
        "Diabetes Risk": {
            "HIGH": "Strong indicator of diabetes or prediabetes. Urgent medical evaluation and lifestyle intervention needed.",
            "MODERATE": "Elevated diabetes risk. Dietary management and regular monitoring essential.",
            "LOW": "Low risk for diabetes. Maintain current healthy practices."
        },
        "Anemia Risk": {
            "HIGH": "Significant anemia present. Medical evaluation and treatment may be necessary.",
            "MODERATE": "Mild to moderate anemia. Dietary changes and monitoring recommended.",
            "LOW": "No significant anemia risk detected."
        },
        "Liver Risk": {
            "HIGH": "Liver function is compromised. Immediate medical consultation required.",
            "MODERATE": "Liver stress detected. Medical evaluation and lifestyle changes recommended.",
            "LOW": "Liver function appears normal."
        },
        "Kidney Risk": {
            "HIGH": "Kidney function is compromised. Urgent medical evaluation needed.",
            "MODERATE": "Kidney stress detected. Medical monitoring and management needed.",
            "LOW": "Kidney function appears normal."
        }
    }
    return significance_map.get(risk_category, {}).get(risk_level, "Unable to determine significance")


def _get_adjustment_reason(risk_category, age=None, gender=None):
    """Explain why a risk level was adjusted based on context."""
    reasons = []
    
    if age and age > 45:
        reasons.append(f"Age ({age} years) increases baseline risk")
    
    if gender:
        if gender.lower() == "female":
            reasons.append("Female gender-specific health considerations applied")
        elif gender.lower() == "male":
            reasons.append("Male gender-specific health considerations applied")
    
    return "; ".join(reasons) if reasons else "Contextual adjustment applied"


def _get_priority_areas(interpretation, risk_assessment, contextual_risk, parameters):
    """Determine priority areas requiring immediate attention."""
    priorities = []
    
    # High risk areas get highest priority
    for category, level in risk_assessment.items():
        if level == "HIGH":
            contextual_level = contextual_risk.get(category, level) if contextual_risk else level
            priorities.append({
                "priority": 1,
                "area": category,
                "risk_level": contextual_level,
                "action_needed": "URGENT - Medical consultation recommended"
            })
    
    # Moderate risk areas
    for category, level in risk_assessment.items():
        if level == "MODERATE":
            contextual_level = contextual_risk.get(category, level) if contextual_risk else level
            priorities.append({
                "priority": 2,
                "area": category,
                "risk_level": contextual_level,
                "action_needed": "Recommended - Lifestyle modifications and monitoring"
            })
    
    # Abnormal parameters that don't fall into high/moderate risk
    for param, status in interpretation.items():
        if status != "NORMAL" and param not in [p.get("parameter") for p in priorities]:
            priorities.append({
                "priority": 3,
                "area": f"{param} ({status})",
                "risk_level": status,
                "action_needed": "Monitor and track changes"
            })
    
    # Sort by priority
    priorities.sort(key=lambda x: x["priority"])
    
    return priorities


def _generate_executive_summary(abnormal_count, high_risk_count, moderate_risk_count, 
                                critical_findings, priority_areas, age=None, gender=None, status_code="MONITOR"):
    """Generate a comprehensive executive summary of findings."""
    
    summary_parts = []
    
    # Overview
    if status_code == "HEALTHY":
        summary_parts.append(
            "Your blood report shows overall healthy results with parameters within normal ranges. "
            "Continue your current healthy lifestyle and regular health check-ups."
        )
    elif status_code == "MONITOR":
        summary_parts.append(
            f"Your blood report shows {abnormal_count} parameter(s) outside normal range(s). "
            "While not immediately concerning, these areas should be monitored."
        )
    elif status_code == "ATTENTION_REQUIRED":
        summary_parts.append(
            f"Your blood report shows {abnormal_count} parameter(s) outside normal range(s) with "
            f"{moderate_risk_count} moderate risk factor(s). Attention to lifestyle and medical follow-up is recommended."
        )
    else:  # CONCERNING
        summary_parts.append(
            f"Your blood report shows {abnormal_count} parameter(s) outside normal range(s) with "
            f"{high_risk_count} high-risk area(s). Immediate consultation with a healthcare professional is strongly advised."
        )
    
    # Critical findings
    if critical_findings:
        summary_parts.append(
            f"Critical findings identified: {'; '.join(critical_findings[:3])}." +
            (f" Plus {len(critical_findings) - 3} additional concern(s)." if len(critical_findings) > 3 else "")
        )
    
    # Demographic context
    if age or gender:
        demo_info = []
        if age:
            demo_info.append(f"age {age}")
        if gender:
            demo_info.append(f"gender {gender}")
        summary_parts.append(
            f"Given your {', '.join(demo_info)}, certain risk profiles have been adjusted accordingly."
        )
    
    # Next steps
    if high_risk_count > 0:
        summary_parts.append(
            "Next steps: Schedule an appointment with your healthcare provider for professional evaluation and guidance."
        )
    elif moderate_risk_count > 0:
        summary_parts.append(
            "Next steps: Consider lifestyle modifications and schedule a follow-up appointment within the next month."
        )
    else:
        summary_parts.append(
            "Next steps: Continue regular check-ups and maintain your current healthy practices."
        )
    
    return " ".join(summary_parts)
