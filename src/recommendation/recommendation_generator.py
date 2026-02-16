from typing import List, Dict, Any

class RecommendationGenerator:
    """
    Generates rule-based recommendations linked to specific findings.
    """
    
    def generate(self, interpretations: List[str], risks: List[str], extracted_params: Dict[str, Any], derived_metrics: Dict[str, Any] = {}) -> List[Dict[str, str]]:
        """
        Generate recommendations linked to findings.
        Returns: List of dicts { "finding", "recommendation", "severity" }
        """
        recommendations = []

        # 1. Parameter-based Recommendations (Model 1)
        for param, data in extracted_params.items():
            value = data.get("value")
            
            # Simple rules (expand as needed)
            if "glucose" in param.lower():
                if value > 100:
                    recommendations.append({
                        "finding": f"High Glucose ({value})",
                        "recommendation": "Reduce intake of sugary foods and refined carbohydrates. Monitor blood sugar regularly.",
                        "severity": "High" if value > 125 else "Moderate"
                    })
            
            if "cholesterol" in param.lower() and "ratio" not in param.lower():
                if value > 200:
                    recommendations.append({
                        "finding": f"High Total Cholesterol ({value})",
                        "recommendation": "Adopt a heart-healthy diet low in saturated fats. Increase physical activity.",
                        "severity": "Moderate"
                    })

        # 2. Risk-based Recommendations (Model 2)
        for risk in risks:
            req = {
                "finding": risk,
                "recommendation": "Consult a healthcare provider for a detailed risk assessment.",
                "severity": "High"
            }
            
            if "Cardiovascular" in risk:
                req["recommendation"] = "Prioritize cardio exercises (walking, swimming) 30 mins/day. Limit sodium and red meat."
            elif "Metabolic" in risk:
                req["recommendation"] = "Focus on weight management and a balanced diet rich in whole grains and vegetables."
            elif "Kidney" in risk:
                req["recommendation"] = "Ensure adequate hydration. Limit protein intake if advised by a doctor."
                
            recommendations.append(req)

        # 3. Derived Metrics (Model 2)
        chol_hdl = derived_metrics.get("Cholesterol/HDL Ratio")
        if chol_hdl and chol_hdl > 5.0:
             recommendations.append({
                "finding": f"High Cholesterol/HDL Ratio ({chol_hdl})",
                "recommendation": "Increase HDL (good cholesterol) by consuming healthy fats (olive oil, avocado) and aerobic exercise.",
                "severity": "High"
            })

        return recommendations

def generate_prescriptions(interpretations: List[str], risks: List[str], extracted_params: Dict[str, Any]) -> List[str]:
    """
    Generate prescriptions based on analysis.
    This is a placeholder/mock function as AI agents usually don't prescribe meds directly.
    """
    prescriptions = []
    
    # Mock logic
    for risk in risks:
        if "Diabetes" in risk:
            prescriptions.append("Consult Doctor for Metformin (if HBA1C > 7%)")
        if "Cholesterol" in risk:
            prescriptions.append("Consult Doctor for Atorvastatin")
            
    return prescriptions
