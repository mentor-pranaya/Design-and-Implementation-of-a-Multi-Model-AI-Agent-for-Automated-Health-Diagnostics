def cholesterol_hdl_risk(parameters: dict) -> dict | None:
    total = parameters.get("Total Cholesterol", {}).get("value")
    hdl = parameters.get("HDL Cholesterol", {}).get("value")

    if total and hdl and hdl > 0:
        ratio = total / hdl

        if ratio > 5:
            risk = "High"
        elif ratio > 3.5:
            risk = "Moderate"
        else:
            risk = "Low"

        return {
            "metric": "Cholesterol/HDL Ratio",
            "value": round(ratio, 2),
            "risk": risk
        }
    return None

def diabetes_indicator(parameters: dict) -> dict | None:
    fbs = parameters.get("Fasting Blood Sugar", {}).get("value")
    hba1c = parameters.get("HbA1c", {}).get("value")

    indicators = []

    if fbs and fbs >= 126:
        indicators.append("Elevated fasting glucose")
    if hba1c and hba1c >= 6.5:
        indicators.append("Elevated HbA1c")

    if indicators:
        return {
            "pattern": "Diabetes Risk",
            "indicators": indicators
        }
    return None


def metabolic_syndrome_indicators(parameters: dict) -> dict | None:
    """Identify metabolic syndrome risk factors."""
    indicators = []
    risk_score = 0
    
    # Check triglycerides
    trig = parameters.get("Triglyceride", {}).get("value")
    if trig and trig > 150:
        indicators.append("Elevated triglycerides (>150 mg/dL)")
        risk_score += 1
    
    # Check HDL
    hdl = parameters.get("HDL Cholesterol", {}).get("value")
    if hdl and hdl < 40:
        indicators.append("Low HDL cholesterol (<40 mg/dL)")
        risk_score += 1
    
    # Check fasting glucose
    fbs = parameters.get("Fasting Blood Sugar", {}).get("value")
    if fbs and fbs > 100:
        indicators.append("Elevated fasting glucose (>100 mg/dL)")
        risk_score += 1
    
    if risk_score >= 2:
        return {
            "pattern": "Metabolic Syndrome Risk",
            "indicators": indicators,
            "risk_level": "High" if risk_score >= 3 else "Moderate",
            "recommendation": "Consult physician for comprehensive metabolic panel"
        }
    
    return None


def kidney_function_assessment(parameters: dict) -> dict | None:
    """Assess kidney function based on creatinine."""
    creatinine = parameters.get("Creatinine", {}).get("value")
    
    if creatinine:
        if creatinine > 1.3:
            return {
                "pattern": "Reduced Kidney Function",
                "creatinine": creatinine,
                "risk_level": "High" if creatinine > 2.0 else "Moderate",
                "recommendation": "Kidney function evaluation recommended"
            }
    
    return None


def thyroid_function_assessment(parameters: dict) -> dict | None:
    """Assess thyroid function."""
    tsh = parameters.get("TSH", {}).get("value")
    
    if tsh:
        if tsh > 4.5:
            return {
                "pattern": "Hypothyroidism Indicator",
                "tsh": tsh,
                "risk_level": "Moderate",
                "recommendation": "Thyroid function evaluation recommended"
            }
        elif tsh < 0.4:
            return {
                "pattern": "Hyperthyroidism Indicator",
                "tsh": tsh,
                "risk_level": "Moderate",
                "recommendation": "Thyroid function evaluation recommended"
            }
    
    return None


def anemia_assessment(parameters: dict) -> dict | None:
    """Check for anemia indicators."""
    hb = parameters.get("Hemoglobin", {}).get("value")
    
    if hb:
        if hb < 12.0:  # Simplified threshold
            severity = "Severe" if hb < 8.0 else "Moderate" if hb < 10.0 else "Mild"
            return {
                "pattern": "Anemia Indicator",
                "hemoglobin": hb,
                "severity": severity,
                "recommendation": "Iron studies and further evaluation recommended"
            }
    
    return None

