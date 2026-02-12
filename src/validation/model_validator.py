."""
Model validation utilities to compare AI predictions with rule-based interpretations.
"""
import numpy as np
from typing import Dict, List, Tuple
from src.analysis.predictor import predict_risk
from src.models.model_1_parameter_interpretation import interpret_parameters
from src.models.model_2_pattern_analysis import analyze_risks


def validate_prediction_consistency(params: Dict[str, float], context: Dict = None) -> Dict:
    """
    Validate that AI predictions are consistent with rule-based interpretations.

    Args:
        params: Dictionary of medical parameters
        context: Additional context (age, gender, etc.)

    Returns:
        Dictionary with validation results
    """
    # Get AI prediction
    ai_prediction = predict_risk(params)

    # Get rule-based interpretations
    interpretations = interpret_parameters(params, context)
    risks = analyze_risks(params, interpretations)

    # Determine rule-based risk level
    rule_based_risk = _calculate_rule_based_risk_score(interpretations, risks)

    # Compare predictions
    consistency_score = _calculate_consistency_score(ai_prediction, rule_based_risk)

    return {
        "ai_prediction": ai_prediction,
        "rule_based_risk": rule_based_risk,
        "interpretations": interpretations,
        "risks": risks,
        "consistency_score": consistency_score,
        "is_consistent": consistency_score >= 0.7,  # 70% threshold
        "discrepancy_reason": _analyze_discrepancy(ai_prediction, rule_based_risk, interpretations, risks)
    }


def _calculate_rule_based_risk_score(interpretations: List[str], risks: List[str]) -> float:
    """
    Calculate a risk score based on rule-based findings.
    """
    base_score = 0.0

    # Count different types of findings
    severe_findings = sum(1 for risk in risks if any(word in risk.lower() for word in
                      ['severe', 'critical', 'acute', 'failure', 'hyperkalemia', 'hyponatremia']))
    high_findings = sum(1 for risk in risks if 'high' in risk.lower() or 'low' in risk.lower())
    moderate_findings = len(interpretations)

    # Weight the findings
    base_score += severe_findings * 0.3
    base_score += high_findings * 0.15
    base_score += moderate_findings * 0.05

    # Cap at 1.0
    return min(base_score, 1.0)


def _calculate_consistency_score(ai_pred: Dict, rule_score: float) -> float:
    """
    Calculate how consistent AI and rule-based predictions are.
    """
    ai_score = ai_pred['risk_score']

    # Convert AI risk labels to numeric scores for comparison
    label_to_score = {
        'low': 0.1,
        'low_moderate': 0.25,
        'moderate': 0.5,
        'high': 0.75,
        'very_high': 0.9
    }

    ai_numeric = label_to_score.get(ai_pred['risk_label'], ai_score)

    # Calculate consistency (1.0 = perfect match, 0.0 = complete opposite)
    score_diff = abs(ai_numeric - rule_score)
    consistency = 1.0 - score_diff

    return max(0.0, consistency)


def _analyze_discrepancy(ai_pred: Dict, rule_score: float,
                        interpretations: List[str], risks: List[str]) -> str:
    """
    Analyze why AI and rule-based predictions might differ.
    """
    ai_score = ai_pred['risk_score']

    if abs(ai_score - rule_score) < 0.2:
        return "Predictions are well-aligned"

    if ai_score > rule_score + 0.3:
        return "AI predicts higher risk - may detect subtle patterns not captured by rules"

    if rule_score > ai_score + 0.3:
        return "Rules indicate higher risk - AI may be underestimating known risk factors"

    # Check for specific patterns
    if any('anemia' in interp.lower() for interp in interpretations) and ai_score < 0.3:
        return "AI may not be weighting anemia risk appropriately"

    if any('diabetes' in interp.lower() for interp in interpretations) and ai_score < 0.4:
        return "AI may not be weighting diabetes risk appropriately"

    return "Minor discrepancy - predictions are reasonably aligned"


def validate_on_synthetic_data(n_samples: int = 1000) -> Dict:
    """
    Validate model consistency on synthetic data.
    """
    from src.analysis.predictor import generate_synthetic_data

    X, y = generate_synthetic_data(n_samples)
    feature_names = ["glucose", "cholesterol", "hemoglobin", "blood_pressure",
                    "wbc", "platelets", "creatinine", "alt", "ast", "ldl", "hdl"]

    consistency_scores = []
    discrepancies = []

    for i in range(min(n_samples, 100)):  # Test on subset for speed
        params = {feature_names[j]: X[i, j] for j in range(len(feature_names))}

        try:
            validation = validate_prediction_consistency(params)
            consistency_scores.append(validation['consistency_score'])

            if not validation['is_consistent']:
                discrepancies.append({
                    'params': params,
                    'ai_pred': validation['ai_prediction'],
                    'rule_risk': validation['rule_based_risk'],
                    'reason': validation['discrepancy_reason']
                })

        except Exception as e:
            print(f"Error validating sample {i}: {e}")
            continue

    return {
        "average_consistency": np.mean(consistency_scores) if consistency_scores else 0,
        "consistency_std": np.std(consistency_scores) if consistency_scores else 0,
        "total_validated": len(consistency_scores),
        "consistent_predictions": sum(1 for s in consistency_scores if s >= 0.7),
        "discrepancies": discrepancies[:10]  # Show first 10 discrepancies
    }


def generate_validation_report() -> str:
    """
    Generate a comprehensive validation report.
    """
    print("Running model validation...")
    results = validate_on_synthetic_data(500)

    report = f"""
# AI Model Validation Report

## Overall Consistency
- Average consistency score: {results['average_consistency']:.3f}
- Consistency standard deviation: {results['consistency_std']:.3f}
- Total samples validated: {results['total_validated']}
- Consistent predictions: {results['consistent_predictions']} ({results['consistent_predictions']/results['total_validated']*100:.1f}%)

## Key Findings
"""

    if results['average_consistency'] > 0.8:
        report += "- ✅ Excellent alignment between AI and rule-based predictions\n"
    elif results['average_consistency'] > 0.7:
        report += "- ⚠️ Good alignment with some minor discrepancies\n"
    else:
        report += "- ❌ Significant discrepancies requiring investigation\n"

    if results['discrepancies']:
        report += "\n## Notable Discrepancies\n"
        for i, disc in enumerate(results['discrepancies'][:5]):
            report += f"### Discrepancy {i+1}\n"
            report += f"- AI Risk: {disc['ai_pred']['risk_label']} ({disc['ai_pred']['risk_score']:.3f})\n"
            report += f"- Rule-based Risk: {disc['rule_risk']:.3f}\n"
            report += f"- Reason: {disc['reason']}\n\n"

    return report


if __name__ == "__main__":
    print(generate_validation_report())
