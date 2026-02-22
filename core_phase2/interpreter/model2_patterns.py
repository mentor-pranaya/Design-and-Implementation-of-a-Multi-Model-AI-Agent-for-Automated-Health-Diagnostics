"""
Model 2: Pattern Recognition & Risk Assessment - Phase 2
Identifies clinical patterns from parameter combinations.

NO HARDCODING - All thresholds loaded from config/pattern_thresholds.json
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List


# Load pattern thresholds from configuration
def load_pattern_thresholds() -> Dict[str, Any]:
    """Load pattern detection thresholds from JSON configuration."""
    config_path = Path(__file__).parent.parent.parent / "config" / "pattern_thresholds.json"
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Pattern thresholds configuration not found: {config_path}\n"
            "Please ensure config/pattern_thresholds.json exists."
        )
    
    with open(config_path, 'r') as f:
        data = json.load(f)
    
    # Remove metadata
    if '_metadata' in data:
        data.pop('_metadata')
    
    return data


# Load thresholds once at module import
THRESHOLDS = load_pattern_thresholds()


def cholesterol_hdl_risk(parameters: dict) -> dict | None:
    """
    Calculate cholesterol/HDL ratio for cardiovascular risk assessment.
    
    Thresholds from: config/pattern_thresholds.json
    Source: AHA/ACC Guidelines 2019
    """
    total = parameters.get("Total Cholesterol", {}).get("value")
    hdl = parameters.get("HDL Cholesterol", {}).get("value")
    
    # Also check alternate names
    if not hdl:
        hdl = parameters.get("HDL", {}).get("value")

    if total and hdl and hdl > 0:
        ratio = total / hdl
        
        # Load thresholds from config
        config = THRESHOLDS["cholesterol_hdl_ratio"]
        high_threshold = config["high"]
        moderate_threshold = config["moderate"]

        if ratio > high_threshold:
            risk = "High"
        elif ratio > moderate_threshold:
            risk = "Moderate"
        else:
            risk = "Low"

        return {
            "metric": "Cholesterol/HDL Ratio",
            "value": round(ratio, 2),
            "risk": risk,
            "source": config["source"],
            "thresholds": {
                "high": high_threshold,
                "moderate": moderate_threshold
            }
        }
    return None


def diabetes_indicator(parameters: dict) -> dict | None:
    """
    Identify diabetes risk based on glucose and HbA1c levels.
    
    Thresholds from: config/pattern_thresholds.json
    Source: ADA Standards of Care 2024
    """
    fbs = parameters.get("Fasting Blood Sugar", {}).get("value")
    if not fbs:
        fbs = parameters.get("Glucose", {}).get("value")
    
    hba1c = parameters.get("HbA1c", {}).get("value")

    indicators = []
    
    # Load thresholds from config
    glucose_config = THRESHOLDS["diabetes_fasting_glucose"]
    hba1c_config = THRESHOLDS["diabetes_hba1c"]
    
    diabetes_glucose = glucose_config["diabetes"]
    diabetes_hba1c = hba1c_config["diabetes"]

    if fbs and fbs >= diabetes_glucose:
        indicators.append(f"Elevated fasting glucose (≥{diabetes_glucose} {glucose_config['unit']})")
    if hba1c and hba1c >= diabetes_hba1c:
        indicators.append(f"Elevated HbA1c (≥{diabetes_hba1c}{hba1c_config['unit']})")

    if indicators:
        return {
            "pattern": "Diabetes Risk",
            "indicators": indicators,
            "source": glucose_config["source"],
            "thresholds": {
                "glucose": diabetes_glucose,
                "hba1c": diabetes_hba1c
            }
        }
    return None


def prediabetes_indicator(parameters: dict) -> dict | None:
    """
    Identify prediabetes risk based on glucose and HbA1c levels.
    
    Thresholds from: config/pattern_thresholds.json
    Source: ADA Standards of Care 2024
    """
    fbs = parameters.get("Fasting Blood Sugar", {}).get("value")
    if not fbs:
        fbs = parameters.get("Glucose", {}).get("value")
    
    hba1c = parameters.get("HbA1c", {}).get("value")

    indicators = []
    
    # Load thresholds from config
    glucose_config = THRESHOLDS["diabetes_fasting_glucose"]
    hba1c_config = THRESHOLDS["diabetes_hba1c"]
    
    prediabetes_glucose = glucose_config["prediabetes"]
    diabetes_glucose = glucose_config["diabetes"]
    prediabetes_hba1c_min = hba1c_config["prediabetes_min"]
    prediabetes_hba1c_max = hba1c_config["prediabetes_max"]

    if fbs and prediabetes_glucose <= fbs < diabetes_glucose:
        indicators.append(
            f"Prediabetes glucose range ({prediabetes_glucose}-{diabetes_glucose-1} {glucose_config['unit']})"
        )
    if hba1c and prediabetes_hba1c_min <= hba1c <= prediabetes_hba1c_max:
        indicators.append(
            f"Prediabetes HbA1c range ({prediabetes_hba1c_min}-{prediabetes_hba1c_max}{hba1c_config['unit']})"
        )

    if indicators:
        return {
            "pattern": "Prediabetes Risk",
            "indicators": indicators,
            "source": glucose_config["source"]
        }
    return None


def metabolic_syndrome_indicators(parameters: dict) -> dict | None:
    """
    Identify metabolic syndrome risk factors.
    
    Thresholds from: config/pattern_thresholds.json
    Source: NCEP ATP III Guidelines
    """
    indicators = []
    risk_score = 0
    
    # Load thresholds from config
    config = THRESHOLDS["metabolic_syndrome"]
    trig_threshold = config["triglycerides_threshold"]
    hdl_threshold_male = config["hdl_threshold_male"]
    hdl_threshold_female = config["hdl_threshold_female"]
    glucose_threshold = config["fasting_glucose_threshold"]
    
    # Check triglycerides
    trig = parameters.get("Triglyceride", {}).get("value")
    if not trig:
        trig = parameters.get("Triglycerides", {}).get("value")
    
    if trig and trig > trig_threshold:
        indicators.append(f"Elevated triglycerides (>{trig_threshold} {config['unit_triglycerides']})")
        risk_score += 1
    
    # Check HDL (use lower threshold if sex unknown)
    hdl = parameters.get("HDL Cholesterol", {}).get("value")
    if not hdl:
        hdl = parameters.get("HDL", {}).get("value")
    
    if hdl and hdl < hdl_threshold_male:  # Most conservative threshold
        indicators.append(f"Low HDL cholesterol (<{hdl_threshold_male} {config['unit_hdl']})")
        risk_score += 1
    
    # Check fasting glucose
    fbs = parameters.get("Fasting Blood Sugar", {}).get("value")
    if not fbs:
        fbs = parameters.get("Glucose", {}).get("value")
    
    if fbs and fbs > glucose_threshold:
        indicators.append(f"Elevated fasting glucose (>{glucose_threshold} {config['unit_glucose']})")
        risk_score += 1
    
    moderate_threshold = config["risk_score_moderate"]
    high_threshold = config["risk_score_high"]
    
    if risk_score >= moderate_threshold:
        return {
            "pattern": "Metabolic Syndrome Risk",
            "indicators": indicators,
            "risk_level": "High" if risk_score >= high_threshold else "Moderate",
            "risk_score": risk_score,
            "recommendation": "Consult physician for comprehensive metabolic panel",
            "source": config["source"]
        }
    
    return None


def kidney_function_assessment(parameters: dict) -> dict | None:
    """
    Assess kidney function based on creatinine.
    
    Thresholds from: config/pattern_thresholds.json
    Source: KDIGO Guidelines
    
    Note: Should be adjusted for age, sex, and race using eGFR calculation
    """
    creatinine = parameters.get("Creatinine", {}).get("value")
    
    if creatinine:
        # Load thresholds from config
        config = THRESHOLDS["kidney_function"]
        moderate_threshold = config["creatinine_moderate"]
        high_threshold = config["creatinine_high"]
        
        if creatinine > moderate_threshold:
            return {
                "pattern": "Reduced Kidney Function",
                "creatinine": creatinine,
                "unit": config["unit"],
                "risk_level": "High" if creatinine > high_threshold else "Moderate",
                "recommendation": "Kidney function evaluation recommended (eGFR calculation)",
                "source": config["source"],
                "note": config["note"]
            }
    
    return None


def thyroid_function_assessment(parameters: dict) -> dict | None:
    """
    Assess thyroid function based on TSH levels.
    
    Thresholds from: config/pattern_thresholds.json
    Source: ATA Guidelines
    """
    tsh = parameters.get("TSH", {}).get("value")
    
    if tsh:
        # Load thresholds from config
        config = THRESHOLDS["thyroid_function"]
        hypothyroid_threshold = config["tsh_hypothyroid"]
        hyperthyroid_threshold = config["tsh_hyperthyroid"]
        
        if tsh > hypothyroid_threshold:
            return {
                "pattern": "Hypothyroidism Indicator",
                "tsh": tsh,
                "unit": config["unit"],
                "risk_level": "Moderate",
                "recommendation": "Thyroid function evaluation recommended",
                "source": config["source"]
            }
        elif tsh < hyperthyroid_threshold:
            return {
                "pattern": "Hyperthyroidism Indicator",
                "tsh": tsh,
                "unit": config["unit"],
                "risk_level": "Moderate",
                "recommendation": "Thyroid function evaluation recommended",
                "source": config["source"]
            }
    
    return None


def anemia_assessment(parameters: dict) -> dict | None:
    """
    Check for anemia indicators based on hemoglobin.
    
    Thresholds from: config/pattern_thresholds.json
    Source: WHO Guidelines
    
    Note: Sex-specific thresholds should be used when patient sex is available
    """
    hb = parameters.get("Hemoglobin", {}).get("value")
    
    if hb:
        # Load thresholds from config
        config = THRESHOLDS["anemia"]
        threshold = config["hemoglobin_threshold_simplified"]
        severe_threshold = config["severity_severe"]
        moderate_threshold = config["severity_moderate"]
        
        if hb < threshold:
            if hb < severe_threshold:
                severity = "Severe"
            elif hb < moderate_threshold:
                severity = "Moderate"
            else:
                severity = "Mild"
            
            return {
                "pattern": "Anemia Indicator",
                "hemoglobin": hb,
                "unit": config["unit"],
                "severity": severity,
                "recommendation": "Iron studies and further evaluation recommended",
                "source": config["source"],
                "note": config["note"]
            }
    
    return None


def detect_all_patterns(parameters: dict) -> List[Dict[str, Any]]:
    """
    Run all pattern detection functions and return detected patterns.
    
    Args:
        parameters: Dictionary of validated parameters
    
    Returns:
        List of detected patterns
    """
    patterns = []
    
    # Run all pattern detection functions
    pattern_functions = [
        cholesterol_hdl_risk,
        diabetes_indicator,
        prediabetes_indicator,
        metabolic_syndrome_indicators,
        kidney_function_assessment,
        thyroid_function_assessment,
        anemia_assessment
    ]
    
    for func in pattern_functions:
        try:
            result = func(parameters)
            if result:
                patterns.append(result)
        except Exception as e:
            # Log error but continue with other patterns
            print(f"Warning: Pattern detection failed for {func.__name__}: {str(e)}")
    
    return patterns

