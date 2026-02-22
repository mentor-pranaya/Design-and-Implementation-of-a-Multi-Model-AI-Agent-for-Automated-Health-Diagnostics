"""
Risk Scoring Engine - Quantified Clinical Risk Assessment

This module transforms qualitative clinical interpretation into quantified,
structured risk scores using guideline-inspired algorithms.

NO HARDCODING - All thresholds and weights loaded from config/risk_scoring_config.json

Architecture Position:
Phase 2 (Extraction) -> 
Phase 3A (Evaluation - Model 1) -> 
Phase 3B (Pattern Detection - Model 2) -> 
Phase 3D (Contextual Refinement - Model 3) -> 
Phase 3E (Risk Scoring - NEW LAYER) ->
Phase 3C (Recommendations)

Design Philosophy:
- Deterministic: Same inputs always produce same outputs
- Explainable: Every point contribution is tracked and reported
- Context-aware: Uses age, sex, conditions, lifestyle
- Clinically grounded: Inspired by established guidelines (ASCVD, ADA)
- Research-ready: Produces structured, defensible risk estimates
- Configuration-driven: All parameters externalized to JSON

This is NOT a black-box ML model. This is structured clinical logic that can be:
- Validated against clinical guidelines
- Explained to healthcare providers
- Published in academic papers
- Used in clinical decision support systems
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


# Load risk scoring configuration
def load_risk_scoring_config() -> Dict[str, Any]:
    """Load risk scoring configuration from JSON file."""
    config_path = Path(__file__).parent.parent / "config" / "risk_scoring_config.json"
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Risk scoring configuration not found: {config_path}\n"
            "Please ensure config/risk_scoring_config.json exists."
        )
    
    with open(config_path, 'r') as f:
        data = json.load(f)
    
    # Remove metadata
    if '_metadata' in data:
        data.pop('_metadata')
    
    return data


# Load configuration once at module import
RISK_CONFIG = load_risk_scoring_config()


def extract_points_from_trigger(trigger: str) -> int:
    """Extract point value from trigger string using regex.
    
    Args:
        trigger: String like "Age 72 (70+) contributes +12 points"
                 or "diabetes (CVD risk multiplier): +4 points)"
    
    Returns:
        Integer point value, or 0 if no match found
    """
    match = re.search(r'\+(\d+)', trigger)
    return int(match.group(1)) if match else 0


class CardiovascularRiskScorer:
    """
    ASCVD-inspired structured cardiovascular risk scoring engine.
    
    Produces quantified 10-year cardiovascular risk estimates based on:
    - Age and sex
    - Lipid profile (Total Cholesterol, LDL, HDL)
    - Clinical risk factors (smoking, hypertension, diabetes)
    
    This is a structured, rule-based model (not the proprietary ASCVD calculator)
    designed for transparency, explainability, and research validation.
    
    Risk Categories:
    - Low: <5% 10-year risk
    - Borderline: 5-7.5% 10-year risk
    - Intermediate: 7.5-20% 10-year risk
    - High: >20% 10-year risk
    """
    
    def __init__(
        self, 
        patient_info: Dict[str, Any], 
        evaluated_params: Dict[str, Any]
    ):
        """
        Initialize cardiovascular risk scorer.
        
        Args:
            patient_info: Patient demographics and context
                {
                    "age": 45,
                    "sex": "male",
                    "known_conditions": ["diabetes", "hypertension"],
                    "lifestyle": {"smoker": True, "exercise_level": "low"}
                }
            evaluated_params: Evaluated laboratory parameters
                Dictionary of parameter evaluations from Phase 3A
        """
        self.patient_info = patient_info or {}
        self.params = evaluated_params or {}
        
        # Extract patient context
        self.age = self.patient_info.get("age", 0)
        self.sex = self.patient_info.get("sex", "").lower()
        self.conditions = [c.lower() for c in self.patient_info.get("known_conditions", [])]
        self.lifestyle = self.patient_info.get("lifestyle", {})
        
        # Scoring state
        self.triggers = []
        self.points = 0
        
        print(f"  Calculating CV risk for {self.sex or 'unknown'} patient, age {self.age}")
    
    # =========================================================================
    # PUBLIC API
    # =========================================================================
    
    def calculate(self) -> Dict[str, Any]:
        """
        Calculate comprehensive cardiovascular risk score.
        
        Returns:
            Dictionary containing:
            - model: Scoring model name
            - total_points: Raw point score
            - estimated_10_year_risk_percent: Quantified risk estimate
            - risk_category: Low/Borderline/Intermediate/High
            - criteria_triggers: List of contributing factors
            - confidence: Confidence in the estimate (0-1)
            - recommendations: Risk-specific guidance
        """
        # Score components
        self._age_score()
        self._sex_modifier()
        self._lipid_contribution()
        self._clinical_factors()
        
        # Convert to risk percentage and category
        risk_percent, category = self._convert_to_risk()
        
        # Generate risk-specific recommendations
        recommendations = self._get_recommendations(category, risk_percent)
        
        return {
            "model": "ASCVD-inspired structured scoring model",
            "version": "1.0",
            "total_points": self.points,
            "estimated_10_year_risk_percent": risk_percent,
            "risk_category": category,
            "criteria_triggers": self.triggers,
            "confidence": self._calculate_confidence(),
            "recommendations": recommendations,
            "scoring_breakdown": {
                "age_sex_contribution": self._get_age_sex_points(),
                "lipid_contribution": self._get_lipid_points(),
                "clinical_factors_contribution": self._get_clinical_points()
            }
        }
    
    # =========================================================================
    # SCORING COMPONENTS
    # =========================================================================
    
    def _age_score(self) -> None:
        """
        Assign points based on age.
        
        Age stratification loaded from config/risk_scoring_config.json
        """
        config = RISK_CONFIG["cardiovascular_risk"]["age_stratification"]
        
        if self.age < 40:
            age_data = config["under_40"]
        elif 40 <= self.age <= 49:
            age_data = config["40_to_49"]
        elif 50 <= self.age <= 59:
            age_data = config["50_to_59"]
        elif 60 <= self.age <= 69:
            age_data = config["60_to_69"]
        else:
            age_data = config["70_plus"]
        
        age_points = age_data["points"]
        age_category = age_data["category"]
        
        self.points += age_points
        self.triggers.append(f"Age {self.age} ({age_category}) contributes {age_points} points")
    
    def _sex_modifier(self) -> None:
        """
        Apply sex-based risk modifier.
        
        Sex modifiers loaded from config/risk_scoring_config.json
        """
        config = RISK_CONFIG["cardiovascular_risk"]["sex_modifier"]
        
        if self.sex == "male":
            points = config["male"]
            self.points += points
            self.triggers.append(f"Male sex risk modifier: +{points} points")
        elif self.sex == "female":
            points = config["female"]
            if points > 0:
                self.points += points
                self.triggers.append(f"Female sex risk modifier: +{points} points")
    
    def _lipid_contribution(self) -> None:
        """
        Score lipid profile contributions.
        
        Thresholds and points loaded from config/risk_scoring_config.json
        """
        thresholds = RISK_CONFIG["cardiovascular_risk"]["lipid_thresholds"]
        points_config = RISK_CONFIG["cardiovascular_risk"]["lipid_points"]
        
        # Total Cholesterol
        total_chol = self._get_param_value("Total Cholesterol")
        if total_chol and total_chol > thresholds["total_cholesterol_high"]:
            points = points_config["total_cholesterol_high"]
            self.points += points
            self.triggers.append(
                f"Total Cholesterol {total_chol} {thresholds['unit']} "
                f"(>{thresholds['total_cholesterol_high']}): +{points} points"
            )
        
        # LDL Cholesterol
        ldl = self._get_param_value("LDL")
        if ldl:
            if ldl > thresholds["ldl_very_high"]:
                points = points_config["ldl_very_high"]
                self.points += points
                self.triggers.append(
                    f"LDL {ldl} {thresholds['unit']} "
                    f"(>{thresholds['ldl_very_high']}, very high): +{points} points"
                )
            elif ldl > thresholds["ldl_high"]:
                points = points_config["ldl_high"]
                self.points += points
                self.triggers.append(
                    f"LDL {ldl} {thresholds['unit']} "
                    f"(>{thresholds['ldl_high']}, high): +{points} points"
                )
        
        # HDL Cholesterol (protective factor)
        hdl = self._get_param_value("HDL")
        if hdl and hdl < thresholds["hdl_low"]:
            points = points_config["hdl_low"]
            self.points += points
            self.triggers.append(
                f"HDL {hdl} {thresholds['unit']} "
                f"(<{thresholds['hdl_low']}, low protective factor): +{points} points"
            )
    
    def _clinical_factors(self) -> None:
        """
        Score clinical risk factors.
        
        Factor weights loaded from config/risk_scoring_config.json
        """
        factors = RISK_CONFIG["cardiovascular_risk"]["clinical_factors"]
        
        # Smoking
        if self.lifestyle.get("smoker"):
            points = factors["smoking"]
            self.points += points
            self.triggers.append(f"Current smoker: +{points} points")
        
        # Hypertension
        if "hypertension" in self.conditions or "htn" in self.conditions:
            points = factors["hypertension"]
            self.points += points
            self.triggers.append(f"Known hypertension: +{points} points")
        
        # Diabetes
        if "diabetes" in self.conditions or "dm" in self.conditions:
            points = factors["diabetes"]
            self.points += points
            self.triggers.append(f"Known diabetes (CVD risk multiplier): +{points} points")
    
    # =========================================================================
    # RISK CONVERSION
    # =========================================================================
    
    def _convert_to_risk(self) -> tuple[float, str]:
        """
        Convert total points to estimated 10-year risk percentage and category.
        
        Risk categories loaded from config/risk_scoring_config.json
        
        Returns:
            Tuple of (risk_percent, category)
        """
        categories = RISK_CONFIG["cardiovascular_risk"]["risk_categories"]
        
        if self.points <= categories["low"]["max_points"]:
            return categories["low"]["risk_percent"], "Low"
        elif self.points <= categories["borderline"]["max_points"]:
            return categories["borderline"]["risk_percent"], "Borderline"
        elif self.points <= categories["intermediate"]["max_points"]:
            return categories["intermediate"]["risk_percent"], "Intermediate"
        else:
            return categories["high"]["risk_percent"], "High"
    
    def _calculate_confidence(self) -> float:
        """
        Calculate confidence in the risk estimate.
        
        Confidence increases with:
        - More data points available
        - Presence of major risk factors
        - Age in validated range (40-75)
        
        Returns:
            Confidence score between 0.6 and 0.95
        """
        base_confidence = 0.6
        
        # Increase confidence with data completeness
        if self.age and 40 <= self.age <= 75:
            base_confidence += 0.1
        
        if self._get_param_value("LDL") is not None:
            base_confidence += 0.05
        
        if self._get_param_value("HDL") is not None:
            base_confidence += 0.05
        
        if self.conditions:
            base_confidence += 0.05
        
        # Cap at 0.95 (clinical judgment always needed)
        return round(min(0.95, base_confidence + (self.points * 0.01)), 2)
    
    # =========================================================================
    # RECOMMENDATIONS
    # =========================================================================
    
    def _get_recommendations(self, category: str, risk_percent: float) -> List[str]:
        """
        Generate risk-category-specific recommendations.
        
        Args:
            category: Risk category (Low/Borderline/Intermediate/High)
            risk_percent: Estimated 10-year risk percentage
        
        Returns:
            List of clinical recommendations
        """
        recommendations = []
        
        if category == "High":
            recommendations.extend([
                "URGENT: Immediate cardiology consultation recommended",
                "Consider statin therapy initiation or intensification",
                "Aggressive lifestyle modification required",
                "Blood pressure control critical (target <130/80 mmHg)",
                "Smoking cessation mandatory if applicable",
                "Consider aspirin therapy (discuss with physician)",
                "Close monitoring: repeat lipid panel in 3 months"
            ])
        
        elif category == "Intermediate":
            recommendations.extend([
                "Moderate-to-high CVD risk: Medical evaluation recommended",
                "Consider statin therapy (discuss with physician)",
                "Lifestyle modifications strongly encouraged",
                "Target LDL <100 mg/dL",
                "Blood pressure monitoring and control",
                "Smoking cessation if applicable",
                "Repeat lipid panel in 6 months"
            ])
        
        elif category == "Borderline":
            recommendations.extend([
                "Borderline CVD risk: Lifestyle modification priority",
                "Therapeutic lifestyle changes (TLC) recommended",
                "Target LDL <130 mg/dL through diet and exercise",
                "Regular cardiovascular exercise (150 min/week)",
                "Heart-healthy diet (Mediterranean or DASH)",
                "Annual lipid panel monitoring"
            ])
        
        else:  # Low
            recommendations.extend([
                "Low CVD risk: Continue healthy lifestyle",
                "Maintain healthy diet and regular exercise",
                "Periodic screening (lipid panel every 3-5 years)",
                "Avoid smoking and limit alcohol",
                "Maintain healthy weight"
            ])
        
        return recommendations
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _get_param_value(self, param_name: str) -> Optional[float]:
        """
        Extract parameter value from evaluated parameters.
        
        Args:
            param_name: Parameter name (e.g., "LDL", "HDL")
        
        Returns:
            Parameter value or None if not found
        """
        # Check in evaluations list
        if 'evaluations' in self.params:
            for eval_item in self.params['evaluations']:
                if eval_item.get('parameter') == param_name:
                    return eval_item.get('value')
        
        # Check direct key access
        if param_name in self.params:
            param_data = self.params[param_name]
            if isinstance(param_data, dict):
                return param_data.get('value')
            return param_data
        
        return None
    
    def _get_age_sex_points(self) -> int:
        """Get total points from age and sex contributions."""
        points = 0
        for trigger in self.triggers:
            if 'Age' in trigger or 'sex' in trigger.lower():
                points += extract_points_from_trigger(trigger)
        return points
    
    def _get_lipid_points(self) -> int:
        """Get total points from lipid contributions."""
        points = 0
        for trigger in self.triggers:
            if any(word in trigger for word in ['Cholesterol', 'LDL', 'HDL']):
                points += extract_points_from_trigger(trigger)
        return points
    
    def _get_clinical_points(self) -> int:
        """Get total points from clinical factor contributions."""
        points = 0
        for trigger in self.triggers:
            if any(word in trigger for word in ['smoker', 'hypertension', 'diabetes']):
                points += extract_points_from_trigger(trigger)
        return points


class DiabetesRiskScorer:
    """
    Diabetes risk scoring engine based on ADA guidelines and risk factors.
    
    Future implementation for comprehensive metabolic risk assessment.
    """
    
    def __init__(self, patient_info: Dict[str, Any], evaluated_params: Dict[str, Any]):
        """Initialize diabetes risk scorer."""
        self.patient_info = patient_info
        self.params = evaluated_params
    
    def calculate(self) -> Dict[str, Any]:
        """
        Calculate diabetes risk score.
        
        Placeholder for future implementation.
        """
        return {
            "model": "Diabetes Risk Score (ADA-inspired)",
            "status": "Not yet implemented",
            "note": "Future enhancement for comprehensive metabolic risk assessment"
        }


class CKDRiskScorer:
    """
    Chronic Kidney Disease staging based on GFR estimation.
    
    Future implementation for renal function assessment.
    """
    
    def __init__(self, patient_info: Dict[str, Any], evaluated_params: Dict[str, Any]):
        """Initialize CKD risk scorer."""
        self.patient_info = patient_info
        self.params = evaluated_params
    
    def calculate(self) -> Dict[str, Any]:
        """
        Calculate CKD stage and risk.
        
        Placeholder for future implementation.
        """
        return {
            "model": "CKD Staging (KDIGO guidelines)",
            "status": "Not yet implemented",
            "note": "Future enhancement for renal function risk assessment"
        }


# =========================================================================
# CONVENIENCE FUNCTIONS
# =========================================================================

def calculate_cardiovascular_risk(
    patient_info: Dict[str, Any],
    evaluated_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function to calculate cardiovascular risk.
    
    Args:
        patient_info: Patient demographics and context
        evaluated_params: Evaluated laboratory parameters
    
    Returns:
        Cardiovascular risk assessment
    """
    scorer = CardiovascularRiskScorer(patient_info, evaluated_params)
    return scorer.calculate()
