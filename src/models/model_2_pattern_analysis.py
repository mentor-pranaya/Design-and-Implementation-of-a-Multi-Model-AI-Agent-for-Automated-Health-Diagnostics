import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Placeholder for ML model - in production, this would be trained on real data
MODEL_PATH = "models/risk_predictor.pkl"
SCALER_PATH = "models/scaler.pkl"

def analyze_risks(parameters: dict, interpretation: list = None):
    """
    Analyze patterns and risks from parameters and interpretations.
    Includes basic ML prediction for overall risk score.
    """
    risks = []
    interpretation = interpretation or []

    # Severe conditions
    hb = parameters.get("hemoglobin")
    if hb is not None and hb < 10:
        risks.append("Severe anemia risk")

    wbc = parameters.get("wbc")
    if wbc is not None:
        if wbc > 15000:
            risks.append("Possible acute infection")
        elif wbc < 2000:
            risks.append("Critical leukopenia (severe infection risk)")

    hba1c = parameters.get("hba1c")
    if hba1c is not None and hba1c > 8:
        risks.append("Poor diabetes control")

    platelets = parameters.get("platelets")
    if platelets is not None and platelets < 100000:
        risks.append("Bleeding risk due to low platelets")

    # Liver disease patterns
    alt = parameters.get("alt")
    ast = parameters.get("ast")
    if alt and ast:
        if alt > 100 and ast > 100:
            risks.append("Possible acute liver injury")
        elif alt > ast * 2:
            risks.append("Possible drug-induced liver injury")

    # Kidney disease patterns
    creatinine = parameters.get("creatinine")
    urea = parameters.get("urea")
    if creatinine and urea:
        if creatinine > 2.0 or urea > 100:
            risks.append("Possible kidney failure")

    # Electrolyte imbalances
    potassium = parameters.get("potassium")
    if potassium:
        if potassium > 6.0:
            risks.append("Hyperkalemia (cardiac risk)")
        elif potassium < 2.5:
            risks.append("Hypokalemia (arrhythmia risk)")

    sodium = parameters.get("sodium")
    if sodium:
        if sodium > 160:
            risks.append("Hypernatremia (neurological risk)")
        elif sodium < 120:
            risks.append("Hyponatremia (seizure risk)")

    # Cardiovascular risk patterns
    cholesterol = parameters.get("cholesterol")
    ldl = parameters.get("ldl")
    hdl = parameters.get("hdl")
    if cholesterol and ldl and hdl:
        if cholesterol > 240 or ldl > 160:
            risks.append("High cardiovascular risk")
        if hdl < 35:
            risks.append("Very low HDL (increased CVD risk)")

    # Thyroid disorders
    tsh = parameters.get("tsh")
    if tsh:
        if tsh > 10:
            risks.append("Severe hypothyroidism")
        elif tsh < 0.1:
            risks.append("Severe hyperthyroidism")

    # Combined risk assessment
    risk_score = calculate_risk_score(parameters, interpretation)
    if risk_score > 0.7:
        risks.append("High overall health risk - immediate medical attention recommended")
    elif risk_score > 0.4:
        risks.append("Moderate health risk - follow-up recommended")

    return risks

def calculate_risk_score(parameters: dict, interpretation: list):
    """
    Calculate an overall risk score based on parameters and findings.
    Uses simple weighted scoring for now; can be replaced with ML model.
    """
    score = 0.0
    total_weight = 0.0

    # Define weights for different parameters
    weights = {
        "hemoglobin": 0.1,
        "glucose": 0.15,
        "hba1c": 0.15,
        "cholesterol": 0.1,
        "ldl": 0.1,
        "creatinine": 0.1,
        "alt": 0.08,
        "ast": 0.08,
        "platelets": 0.07,
        "wbc": 0.07
    }

    # Calculate abnormality scores
    for param, weight in weights.items():
        value = parameters.get(param)
        if value is not None:
            abnormality = get_abnormality_score(param, value)
            score += abnormality * weight
            total_weight += weight

    # Add interpretation-based risk
    interpretation_risk = len(interpretation) * 0.05  # Each finding adds 5% risk
    score += min(interpretation_risk, 0.3)  # Cap at 30%

    # Normalize
    if total_weight > 0:
        score = score / total_weight

    return min(score, 1.0)  # Cap at 100%

def get_abnormality_score(param: str, value: float):
    """
    Calculate how abnormal a parameter value is (0-1 scale).
    """
    normal_ranges = {
        "hemoglobin": (12, 16),
        "glucose": (70, 140),
        "hba1c": (4, 6.5),
        "cholesterol": (125, 200),
        "ldl": (50, 100),
        "creatinine": (0.6, 1.2),
        "alt": (7, 40),
        "ast": (10, 40),
        "platelets": (150000, 450000),
        "wbc": (4000, 11000)
    }

    if param not in normal_ranges:
        return 0.0

    min_val, max_val = normal_ranges[param]
    if value < min_val:
        return min((min_val - value) / min_val, 1.0)
    elif value > max_val:
        return min((value - max_val) / max_val, 1.0)
    else:
        return 0.0

# Placeholder for ML model integration
def predict_risk_with_ml(parameters: dict):
    """
    Placeholder for ML-based risk prediction.
    In production, load a trained model and make predictions.
    """
    # This would load a trained model and predict risk
    # For now, return None to use rule-based approach
    return None
