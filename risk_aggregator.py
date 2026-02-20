"""
Risk Aggregator: Intelligent aggregation of multiple abnormalities.

Synthesizes multiple parameter abnormalities into a global urgency assessment
considering medical history, age, and clinical decision rules.

Production-grade risk escalation and aggregation engine.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set

from severity_engine import SeverityLevel, SeverityResult

logger = logging.getLogger(__name__)


class UrgencyLevel(Enum):
    """Enumeration of global urgency levels."""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class RiskAggregation:
    """Structured result of risk aggregation."""
    global_urgency: UrgencyLevel
    severity_distribution: Dict[str, int]  # Count by severity level
    critical_parameters: List[str] = field(default_factory=list)
    high_risk_parameters: List[str] = field(default_factory=list)
    moderate_parameters: List[str] = field(default_factory=list)
    escalation_reasons: List[str] = field(default_factory=list)
    num_abnormal_parameters: int = 0
    max_deviation_percent: float = 0.0
    age_adjusted: bool = False
    medical_history_considered: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "global_urgency": self.global_urgency.value,
            "severity_distribution": self.severity_distribution,
            "critical_parameters": self.critical_parameters,
            "high_risk_parameters": self.high_risk_parameters,
            "moderate_parameters": self.moderate_parameters,
            "escalation_reasons": self.escalation_reasons,
            "num_abnormal_parameters": self.num_abnormal_parameters,
            "max_deviation_percent": round(self.max_deviation_percent, 2),
            "age_adjusted": self.age_adjusted,
            "medical_history_considered": self.medical_history_considered
        }


class RiskAggregator:
    """
    Aggregates multiple abnormal parameters into clinical urgency assessment.
    
    Uses decision rules based on:
    - Number of abnormalities
    - Severity distribution
    - Patient age
    - Medical history
    - Parameter interactions
    """
    
    # Escalation decision rules
    CRITICAL_ESCALATION_RULE = {
        "critical_count": 1  # 1+ Critical = Escalate to Critical
    }
    
    HIGH_ESCALATION_RULE = {
        "high_count": 1,  # 1+ High
        "moderate_count_threshold": 2  # OR 2+ Moderate
    }
    
    MODERATE_ESCALATION_RULE = {
        "mild_count": 3,  # 3+ Mild
        "moderate_count": 1  # OR 1+ Moderate
    }
    
    # Risk domains for categorization
    CARDIOVASCULAR_MARKERS = {
        "total_cholesterol", "ldl", "hdl", "triglycerides",
        "blood_pressure_systolic", "blood_pressure_diastolic"
    }
    
    METABOLIC_MARKERS = {
        "glucose", "glucose_fasting", "hemoglobin_a1c", "fasting_glucose",
        "insulin", "triglycerides"
    }
    
    HEMATOLOGY_MARKERS = {
        "hemoglobin", "hematocrit", "wbc", "platelets", "rbc",
        "white_blood_cells", "red_blood_cells"
    }
    
    RENAL_MARKERS = {
        "creatinine", "bun", "gfr", "potassium", "sodium"
    }
    
    HEPATIC_MARKERS = {
        "alt", "ast", "bilirubin", "albumin", "alkaline_phosphatase",
        "alanine_aminotransferase", "aspartate_aminotransferase"
    }
    
    def __init__(self):
        """Initialize risk aggregator with clinical decision rules."""
        logger.info("Risk aggregator initialized")
    
    def aggregate_risks(
        self,
        severity_results: Dict[str, SeverityResult],
        age: Optional[int] = None,
        gender: Optional[str] = None,
        medical_history: Optional[List[str]] = None
    ) -> RiskAggregation:
        """
        Aggregate multiple parameter severities into global urgency.
        
        Args:
            severity_results: Dict of {param_name: SeverityResult}
            age: Optional age in years
            gender: Optional gender
            medical_history: Optional list of conditions
            
        Returns:
            RiskAggregation: Structured risk assessment
            
        Example:
            >>> aggregator = RiskAggregator()
            >>> severity_results = {
            ...     "glucose": SeverityResult(..., severity=SeverityLevel.HIGH),
            ...     "hemoglobin": SeverityResult(..., severity=SeverityLevel.MODERATE)
            ... }
            >>> risk = aggregator.aggregate_risks(severity_results, age=55)
            >>> print(risk.global_urgency.value)
            'High'
        """
        
        # Categorize severe parameters
        critical_params, high_params, moderate_params, mild_params = \
            self._categorize_parameters(severity_results)
        
        # Build severity distribution
        severity_dist = {
            "critical": len(critical_params),
            "high": len(high_params),
            "moderate": len(moderate_params),
            "mild": len(mild_params),
            "normal": len(severity_results) - len(critical_params) - len(high_params) - len(moderate_params) - len(mild_params)
        }
        
        # Calculate statistics
        num_abnormal = len(critical_params) + len(high_params) + len(moderate_params) + len(mild_params)
        max_deviation = self._get_max_deviation(severity_results)
        
        # Apply decision rules
        urgency, escalation_reasons = self._apply_decision_rules(
            critical_count=len(critical_params),
            high_count=len(high_params),
            moderate_count=len(moderate_params),
            mild_count=len(mild_params),
            num_abnormal=num_abnormal,
            age=age,
            medical_history=medical_history
        )
        
        # Consider medical history risk factors
        age_adjusted = age is not None
        history_considered = medical_history is not None and len(medical_history) > 0
        
        if history_considered:
            urgency, history_escalation = self._apply_medical_history_adjustment(
                urgency,
                medical_history,
                critical_params + high_params
            )
            escalation_reasons.extend(history_escalation)
        
        logger.info(
            f"Risk aggregation complete: urgency={urgency.value}, "
            f"abnormal_params={num_abnormal}, critical={len(critical_params)}"
        )
        
        return RiskAggregation(
            global_urgency=urgency,
            severity_distribution=severity_dist,
            critical_parameters=critical_params,
            high_risk_parameters=high_params,
            moderate_parameters=moderate_params,
            escalation_reasons=escalation_reasons,
            num_abnormal_parameters=num_abnormal,
            max_deviation_percent=max_deviation,
            age_adjusted=age_adjusted,
            medical_history_considered=history_considered
        )
    
    def _categorize_parameters(
        self,
        severity_results: Dict[str, SeverityResult]
    ) -> tuple[List[str], List[str], List[str], List[str]]:
        """Categorize parameters by severity level."""
        
        critical = []
        high = []
        moderate = []
        mild = []
        
        for param_name, result in severity_results.items():
            if result.severity == SeverityLevel.CRITICAL:
                critical.append(param_name)
            elif result.severity == SeverityLevel.HIGH:
                high.append(param_name)
            elif result.severity == SeverityLevel.MODERATE:
                moderate.append(param_name)
            elif result.severity == SeverityLevel.MILD:
                mild.append(param_name)
        
        return critical, high, moderate, mild
    
    def _apply_decision_rules(
        self,
        critical_count: int,
        high_count: int,
        moderate_count: int,
        mild_count: int,
        num_abnormal: int,
        age: Optional[int] = None,
        medical_history: Optional[List[str]] = None
    ) -> tuple[UrgencyLevel, List[str]]:
        """
        Apply clinical decision rules for urgency escalation.
        
        Rules:
        - 1+ Critical → CRITICAL
        - 1+ High OR 2+ Moderate → HIGH
        - 3+ Mild OR 1+ Moderate → MODERATE
        - Else → LOW
        """
        
        reasons = []
        
        # Check Critical escalation
        if critical_count >= self.CRITICAL_ESCALATION_RULE["critical_count"]:
            reasons.append(f"{critical_count} critical abnormality detected")
            return UrgencyLevel.CRITICAL, reasons
        
        # Check High escalation
        if high_count >= self.HIGH_ESCALATION_RULE["high_count"]:
            reasons.append(f"{high_count} high-severity abnormality detected")
            return UrgencyLevel.HIGH, reasons
        
        if moderate_count >= self.HIGH_ESCALATION_RULE["moderate_count_threshold"]:
            reasons.append(f"{moderate_count} moderate abnormalities detected")
            return UrgencyLevel.HIGH, reasons
        
        # Check Moderate escalation
        if moderate_count >= self.MODERATE_ESCALATION_RULE["moderate_count"]:
            reasons.append(f"{moderate_count} moderate abnormality detected")
            return UrgencyLevel.MODERATE, reasons
        
        if mild_count >= self.MODERATE_ESCALATION_RULE["mild_count"]:
            reasons.append(f"{mild_count} mild abnormalities detected")
            return UrgencyLevel.MODERATE, reasons
        
        # Default to Low if any abnormalities exist
        if num_abnormal > 0:
            reasons.append("Mild abnormalities detected")
            return UrgencyLevel.MODERATE, reasons  # Conservative: err on side of caution
        
        reasons.append("No significant abnormalities detected")
        return UrgencyLevel.LOW, reasons
    
    def _apply_medical_history_adjustment(
        self,
        current_urgency: UrgencyLevel,
        medical_history: List[str],
        abnormal_parameters: List[str]
    ) -> tuple[UrgencyLevel, List[str]]:
        """
        Adjust urgency based on medical history.
        
        High-risk conditions warrant escalation.
        """
        
        reasons = []
        new_urgency = current_urgency
        
        # High-risk conditions for escalation
        high_risk_conditions = {
            "diabetes", "hypertension", "cardiac", "heart disease",
            "stroke", "kidney disease", "liver disease", "cancer"
        }
        
        is_high_risk = any(
            condition.lower() in " ".join(medical_history).lower()
            for condition in high_risk_conditions
        )
        
        if is_high_risk:
            # Escalate one level for known high-risk conditions
            urgency_levels = [UrgencyLevel.LOW, UrgencyLevel.MODERATE, UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]
            current_idx = urgency_levels.index(current_urgency)
            
            if current_idx < len(urgency_levels) - 1:
                new_urgency = urgency_levels[current_idx + 1]
                reasons.append(f"Medical history includes high-risk condition(s)")
            
            if not reasons:
                reasons.append("Pre-existing high-risk condition requires careful monitoring")
        
        return new_urgency, reasons
    
    def _get_max_deviation(self, severity_results: Dict[str, SeverityResult]) -> float:
        """Get maximum deviation percentage across all parameters."""
        deviations = [result.deviation_percent for result in severity_results.values()]
        return max(deviations) if deviations else 0.0
    
    def identify_risk_domains(
        self,
        critical_parameters: List[str],
        high_parameters: List[str]
    ) -> Dict[str, List[str]]:
        """
        Identify which medical domains are affected.
        
        Returns:
            Dict: {domain: [affected_parameters]}
        """
        
        affected_params = critical_parameters + high_parameters
        domains = {}
        
        if any(p in self.CARDIOVASCULAR_MARKERS for p in affected_params):
            domains["Cardiovascular"] = [p for p in affected_params if p in self.CARDIOVASCULAR_MARKERS]
        
        if any(p in self.METABOLIC_MARKERS for p in affected_params):
            domains["Metabolic"] = [p for p in affected_params if p in self.METABOLIC_MARKERS]
        
        if any(p in self.HEMATOLOGY_MARKERS for p in affected_params):
            domains["Hematology"] = [p for p in affected_params if p in self.HEMATOLOGY_MARKERS]
        
        if any(p in self.RENAL_MARKERS for p in affected_params):
            domains["Renal"] = [p for p in affected_params if p in self.RENAL_MARKERS]
        
        if any(p in self.HEPATIC_MARKERS for p in affected_params):
            domains["Hepatic"] = [p for p in affected_params if p in self.HEPATIC_MARKERS]
        
        return domains
    
    def get_action_items(self, urgency: UrgencyLevel) -> List[str]:
        """
        Get recommended action items based on urgency level.
        
        Args:
            urgency: Global urgency level
            
        Returns:
            List: Recommended immediate actions
        """
        
        actions = {
            UrgencyLevel.CRITICAL: [
                "🔴 SEEK IMMEDIATE MEDICAL ATTENTION",
                "Contact emergency services or visit ER immediately",
                "Inform physician of critical findings",
                "Do not delay professional medical evaluation"
            ],
            UrgencyLevel.HIGH: [
                "🟠 Schedule medical appointment within 1-3 days",
                "Do not delay - discuss findings with physician promptly",
                "Consider urgent care if appointment not available",
                "Monitor symptoms closely"
            ],
            UrgencyLevel.MODERATE: [
                "🟡 Schedule routine medical appointment within 1-2 weeks",
                "Discuss results with healthcare provider",
                "Consider lifestyle modifications",
                "Monitor parameters regularly"
            ],
            UrgencyLevel.LOW: [
                "🟢 No immediate action required",
                "Routine follow-up during normal appointments",
                "Maintain healthy lifestyle",
                "Annual check-ups recommended"
            ]
        }
        
        return actions.get(urgency, [])


def aggregate_risks(
    severity_results: Dict[str, SeverityResult],
    age: Optional[int] = None,
    gender: Optional[str] = None,
    medical_history: Optional[List[str]] = None
) -> RiskAggregation:
    """Convenience function for quick risk aggregation."""
    aggregator = RiskAggregator()
    return aggregator.aggregate_risks(
        severity_results=severity_results,
        age=age,
        gender=gender,
        medical_history=medical_history
    )


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    from severity_engine import SeverityEngine
    
    engine = SeverityEngine()
    
    # Simulate severity results
    severity_results = {
        "glucose": engine.calculate_severity(250, 70, 100, "mg/dL"),
        "hemoglobin": engine.calculate_severity(9.5, 12, 16, "g/dL"),
        "cholesterol": engine.calculate_severity(220, 0, 200, "mg/dL"),
        "hdl": engine.calculate_severity(30, 40, 999, "mg/dL"),
    }
    
    aggregator = RiskAggregator()
    risk = aggregator.aggregate_risks(
        severity_results=severity_results,
        age=58,
        gender="Male",
        medical_history=["Type 2 Diabetes", "Hypertension"]
    )
    
    print("\n=== Risk Aggregation ===")
    print(f"Global Urgency: {risk.global_urgency.value}")
    print(f"Critical Parameters: {risk.critical_parameters}")
    print(f"High Risk Parameters: {risk.high_risk_parameters}")
    print(f"Escalation Reasons: {risk.escalation_reasons}")
    
    # Identify affected domains
    domains = aggregator.identify_risk_domains(
        risk.critical_parameters,
        risk.high_risk_parameters
    )
    print(f"\nAffected Medical Domains: {list(domains.keys())}")
    
    # Get action items
    actions = aggregator.get_action_items(risk.global_urgency)
    print(f"\nRecommended Actions:")
    for action in actions:
        print(f"  - {action}")
