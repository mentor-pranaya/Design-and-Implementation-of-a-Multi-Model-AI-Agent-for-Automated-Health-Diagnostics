from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class Model2:
    """
    Model 2: Pattern Recognition & Advanced Analytics.
    Calculates derived metrics, ratios, and risk indicators based on extracted parameters.
    """

    def analyze(self, parameters: Dict[str, Any], patient_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform advanced analysis on the parameters.
        Returns a dictionary containing derived metrics and risk flags.
        """
        results = {
            "derived_metrics": {},
            "risk_indicators": []
        }

        # 1. Calculate Derived Metrics (Ratios)
        results["derived_metrics"] = self._calculate_ratios(parameters)

        # 2. Identify Risk Patterns
        risk_flags = self._identify_risk_patterns(parameters, results["derived_metrics"], patient_context)
        results["risk_indicators"] = risk_flags

        return results

    def _calculate_ratios(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate clinical ratios like Cholesterol/HDL, LDL/HDL, etc."""
        ratios = {}

        # Safe helper to get value
        def get_val(key):
            item = params.get(key)
            if isinstance(item, dict):
                return item.get("value")
            return item

        # Lipid Panel Ratios
        total_chol = get_val("Total Cholesterol")
        hdl = get_val("HDL Cholesterol")
        ldl = get_val("LDL Cholesterol")
        triglycerides = get_val("Triglycerides")

        if total_chol and hdl and hdl > 0:
            ratios["Cholesterol/HDL Ratio"] = round(total_chol / hdl, 2)
        
        if ldl and hdl and hdl > 0:
            ratios["LDL/HDL Ratio"] = round(ldl / hdl, 2)

        if triglycerides and hdl and hdl > 0:
            ratios["Triglycerides/HDL Ratio"] = round(triglycerides / hdl, 2)

        # Kidney Function Ratios
        bun = get_val("Urea") or get_val("Blood Urea Nitrogen")
        creatinine = get_val("Creatinine")

        if bun and creatinine and creatinine > 0:
            ratios["BUN/Creatinine Ratio"] = round(bun / creatinine, 2)

        # Liver Function Ratios
        ast = get_val("AST") or get_val("SGOT")
        alt = get_val("ALT") or get_val("SGPT")

        if ast and alt and alt > 0:
             ratios["AST/ALT Ratio"] = round(ast / alt, 2)

        return ratios

    def _identify_risk_patterns(self, params: Dict[str, Any], ratios: Dict[str, Any], context: Optional[Dict] = None) -> List[str]:
        """Identify potential health risks based on combinations of factors."""
        risks = []

        # Helper to check if a value is high/low (simplified logic, ideally relies on Model 1 flags)
        # For now, we'll re-check robust thresholds or rely on calculated ratios
        
        # Cardiovascular Risk Indicators
        chol_hdl_ratio = ratios.get("Cholesterol/HDL Ratio")
        if chol_hdl_ratio and chol_hdl_ratio > 5.0:
            risks.append("High Cardiovascular Risk (Cholesterol/HDL Ratio > 5.0)")
        
        ldl_hdl_ratio = ratios.get("LDL/HDL Ratio")
        if ldl_hdl_ratio and ldl_hdl_ratio > 3.5:
             risks.append("Elevated Atherogenic Risk (LDL/HDL Ratio > 3.5)")

        # Metabolic Syndrome (Draft Logic - requires 3 of 5, checking available ones)
        metabolic_signs = 0
        
        def get_val(key):
            item = params.get(key)
            if isinstance(item, dict):
                return item.get("value")
            return item

        trigs = get_val("Triglycerides")
        hdl = get_val("HDL Cholesterol")
        glucose = get_val("Glucose Fasting") or get_val("Glucose") # Fallback
        
        if trigs and trigs > 150:
            metabolic_signs += 1
        if hdl and hdl < 40: # Male threshold as baseline, context needed for female (<50)
            metabolic_signs += 1
        if glucose and glucose > 100:
            metabolic_signs += 1
            
        if metabolic_signs >= 2:
             risks.append(f"Potential Metabolic Syndrome Signs Identified ({metabolic_signs} markers present)")

        # Kidney Issues
        bun_creat_ratio = ratios.get("BUN/Creatinine Ratio")
        if bun_creat_ratio:
            if bun_creat_ratio > 20:
                risks.append("Prerenal Azotemia indicator (High BUN/Creatinine Ratio)")
            elif bun_creat_ratio < 10:
                risks.append("Intrarenal pathology indicator (Low BUN/Creatinine Ratio)")

        return risks
