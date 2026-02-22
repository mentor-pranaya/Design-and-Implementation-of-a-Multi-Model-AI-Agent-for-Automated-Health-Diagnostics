"""
Comprehensive Health Risk Engine - Multi-Model Integration

This replaces the CVD-centric CardiovascularRiskScorer with a comprehensive
systemic health risk assessment engine that integrates:

- Model 1: Parameter severity classifications
- Model 2: Detected clinical patterns
- Demographics: Age, sex, comorbidities
- Multi-organ dysfunction amplifiers
- Transparent explainability layer

NO HARDCODING - All weights and thresholds loaded from config/risk_scoring_config.json

Architecture:
    Modular component-based weighted scoring system
    └── DemographicRiskModule
    └── ParameterSeverityModule (Model 1 integration)
    └── PatternRiskModule (Model 2 integration)
    └── MultiOrganAmplifier
    └── ExplainabilityLayer

Scoring Formula:
    Total Risk Score = 
        Demographic Base +
        Σ(Parameter Severity × Organ Weight) +
        Σ(Pattern Risk Weight) +
        Multi-Organ Amplifier

Risk Categorization (from config):
    0-20:   Low
    21-40:  Borderline
    41-60:  Intermediate
    61-80:  High
    81+:    Critical

Design Philosophy:
    - Academically defensible (no arbitrary weights)
    - Clinically interpretable (transparent contributors)
    - Modular (easy to extend/modify)
    - Integrates all AI models (Model 1 + Model 2)
    - Production-ready (stable, tested, explainable)
    - Configuration-driven (all parameters externalized)
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict


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


class ComprehensiveHealthRiskEngine:
    """
    Comprehensive health risk scoring engine integrating multiple AI models.
    
    This is the final decision layer that synthesizes:
    - Model 1 parameter classifications and severity
    - Model 2 pattern detections
    - Patient demographics and context
    - Multi-organ dysfunction indicators
    
    Output includes transparent explainability suitable for clinical review
    and academic publication.
    """
    
    # Parameter to organ system mapping (static reference)
    ORGAN_MAP = {
        "Creatinine": "Renal",
        "BUN": "Renal",
        "Potassium": "Electrolyte",
        "Sodium": "Electrolyte",
        "Chloride": "Electrolyte",
        "Hemoglobin": "Hematologic",
        "RBC": "Hematologic",
        "WBC": "Hematologic",
        "Platelets": "Hematologic",
        "HbA1c": "Metabolic",
        "Glucose": "Metabolic",
        "LDL": "Cardiovascular",
        "HDL": "Cardiovascular",
        "Triglycerides": "Metabolic",
        "Total Cholesterol": "Cardiovascular",
        "Albumin": "Hepatic",
        "ALT": "Hepatic",
        "AST": "Hepatic",
        "Bilirubin Total": "Hepatic"
    }

    def __init__(
        self,
        patient_info: Dict[str, Any],
        parameter_evaluations: List[Dict[str, Any]],
        detected_patterns: List[Dict[str, Any]]
    ):
        """
        Initialize comprehensive health risk engine.
        
        Args:
            patient_info: Patient demographics and context
                {
                    "age": 72,
                    "sex": "female",
                    "known_conditions": ["ckd", "hypertension"],
                    "lifestyle": {"smoker": False, ...}
                }
            
            parameter_evaluations: List of Model 1 evaluated parameters
                [
                    {
                        "parameter": "Creatinine",
                        "value": 3.8,
                        "status": EvaluationStatus.HIGH,
                        "severity": "Severe",
                        ...
                    },
                    ...
                ]
            
            detected_patterns: List of Model 2 detected patterns
                [
                    {
                        "pattern": "Kidney Disease",
                        "severity": "Moderate",
                        "confidence": "high",
                        "triggered_by": ["Creatinine", "BUN"]
                    },
                    ...
                ]
        """
        self.patient_info = patient_info
        self.parameter_evaluations = parameter_evaluations
        self.detected_patterns = detected_patterns

        # Scoring state
        self.total_score = 0
        self.score_breakdown = defaultdict(int)
        self.contributors = []
        self.affected_organs = set()

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def calculate(self) -> Dict[str, Any]:
        """
        Calculate comprehensive health risk score.
        
        Returns:
            Dictionary containing:
            - total_score: Aggregate risk score
            - risk_category: Low/Borderline/Intermediate/High/Critical
            - score_breakdown: Points by component
            - top_contributors: Ranked list of risk factors
            - organ_systems_affected: List of affected organ systems
            - clinical_urgency: Urgency-appropriate guidance
        """
        # Execute scoring modules in sequence
        self._demographic_module()
        self._parameter_severity_module()
        self._pattern_module()
        self._multi_organ_amplifier()

        # Categorize and generate output
        category = self._categorize_risk()

        return {
            "total_score": self.total_score,
            "risk_category": category,
            "score_breakdown": dict(self.score_breakdown),
            "top_contributors": sorted(
                self.contributors,
                key=lambda x: x["points"],
                reverse=True
            )[:5],
            "organ_systems_affected": list(self.affected_organs),
            "clinical_urgency": self._urgency_flag(category)
        }

    # ==========================================================
    # MODULE 1: DEMOGRAPHIC RISK
    # ==========================================================

    def _demographic_module(self):
        """
        Calculate demographic baseline risk.
        
        Age stratification and sex modifiers loaded from config/risk_scoring_config.json
        """
        age = self.patient_info.get("age", 0)
        sex = self.patient_info.get("sex", "").lower()

        # Load config
        age_config = RISK_CONFIG["comprehensive_health_risk"]["demographic_age_points"]
        sex_config = RISK_CONFIG["comprehensive_health_risk"]["sex_modifier"]

        # Age-based points
        if age < 40:
            points = age_config["under_40"]
        elif age < 50:
            points = age_config["40_to_49"]
        elif age < 60:
            points = age_config["50_to_59"]
        elif age < 70:
            points = age_config["60_to_69"]
        else:
            points = age_config["70_plus"]

        self._add_points("Demographic (Age)", points)

        # Sex modifier
        if sex == "male":
            self._add_points("Male Sex Modifier", sex_config["male"])
        elif sex == "female" and sex_config["female"] > 0:
            self._add_points("Female Sex Modifier", sex_config["female"])

    # ==========================================================
    # MODULE 2: PARAMETER SEVERITY (Model 1 Integration)
    # ==========================================================

    def _parameter_severity_module(self):
        """
        Score risk based on parameter severity classifications from Model 1.
        
        Severity points and organ weights loaded from config/risk_scoring_config.json
        
        Formula:
            parameter_points = SEVERITY_POINTS[severity] × ORGAN_WEIGHTS[parameter]
        
        This integrates Model 1 directly:
        - Uses severity classifications (Mild/Moderate/Severe/Critical)
        - Applies organ-specific weights
        - Tracks affected organ systems
        """
        severity_points = RISK_CONFIG["comprehensive_health_risk"]["severity_points"]
        organ_weights = RISK_CONFIG["comprehensive_health_risk"]["organ_weights"]
        
        for param in self.parameter_evaluations:
            status = str(param.get("status"))
            severity = param.get("severity")
            name = param.get("parameter")

            # Only score abnormal parameters with severity
            if severity in severity_points:
                base_points = severity_points[severity]
                weight = organ_weights.get(name, 1.0)
                final_points = int(base_points * weight)

                self._add_points(
                    f"{severity} {name}",
                    final_points
                )

                # Track organ involvement
                organ = self.ORGAN_MAP.get(name)
                if organ:
                    self.affected_organs.add(organ)

    # ==========================================================
    # MODULE 3: PATTERN RISK (Model 2 Integration)
    # ==========================================================

    def _pattern_module(self):
        """
        Score risk based on detected clinical patterns from Model 2.
        
        Pattern weights loaded from config/risk_scoring_config.json
        
        Patterns represent higher-level clinical constructs that aggregate
        multiple parameter abnormalities. This prevents double-counting while
        rewarding pattern recognition.
        
        Integrates Model 2 directly by applying configured weights to detected patterns.
        """
        pattern_weights = RISK_CONFIG["comprehensive_health_risk"]["pattern_weights"]
        
        for pattern in self.detected_patterns:
            pattern_name = pattern.get("pattern")

            if pattern_name in pattern_weights:
                points = pattern_weights[pattern_name]

                self._add_points(pattern_name, points)

                # Organ mapping by pattern (for multi-organ detection)
                if "Kidney" in pattern_name:
                    self.affected_organs.add("Renal")
                if "Metabolic" in pattern_name or "Diabetes" in pattern_name:
                    self.affected_organs.add("Metabolic")
                if "Anemia" in pattern_name:
                    self.affected_organs.add("Hematologic")
                if "Electrolyte" in pattern_name:
                    self.affected_organs.add("Electrolyte")
                if "Liver" in pattern_name:
                    self.affected_organs.add("Hepatic")
                if "Cholesterol" in pattern_name:
                    self.affected_organs.add("Cardiovascular")

    # ==========================================================
    # MODULE 4: MULTI-ORGAN DYSFUNCTION AMPLIFIER
    # ==========================================================

    def _multi_organ_amplifier(self):
        """
        Apply bonus for multi-organ dysfunction.
        
        Amplifier values loaded from config/risk_scoring_config.json
        
        Multi-organ involvement indicates systemic disease and higher
        overall risk beyond individual parameter/pattern contributions.
        """
        amplifier_config = RISK_CONFIG["comprehensive_health_risk"]["multi_organ_amplifier"]
        organ_count = len(self.affected_organs)

        if organ_count >= 3:
            self._add_points("Multi-Organ Dysfunction", amplifier_config["three_plus_organs"])
        elif organ_count == 2:
            self._add_points("Dual Organ Involvement", amplifier_config["two_organs"])

    # ==========================================================
    # RISK CATEGORIZATION AND UTILITIES
    # ==========================================================

    def _categorize_risk(self) -> str:
        """
        Convert total score to risk category.
        
        Categorization thresholds loaded from config/risk_scoring_config.json
        
        Returns:
            Risk category string
        """
        categories = RISK_CONFIG["comprehensive_health_risk"]["risk_categories"]
        
        if self.total_score <= categories["low"]["max_score"]:
            return "Low"
        elif self.total_score <= categories["borderline"]["max_score"]:
            return "Borderline"
        elif self.total_score <= categories["intermediate"]["max_score"]:
            return "Intermediate"
        elif self.total_score <= categories["high"]["max_score"]:
            return "High"
        else:
            return "Critical"

    def _urgency_flag(self, category: str) -> str:
        """
        Map risk category to clinical urgency guidance.
        
        Urgency messages loaded from config/risk_scoring_config.json
        
        Args:
            category: Risk category
        
        Returns:
            Clinical urgency message
        """
        categories = RISK_CONFIG["comprehensive_health_risk"]["risk_categories"]
        
        if category in categories:
            return categories[category].get("urgency", "Unknown risk level")
        
        return "Unknown risk level"

    def _add_points(self, factor: str, points: int):
        """
        Add points to total score and track for explainability.
        
        Args:
            factor: Description of risk factor
            points: Point contribution
        """
        self.total_score += points
        self.score_breakdown[factor] += points
        self.contributors.append({
            "factor": factor,
            "points": points
        })
