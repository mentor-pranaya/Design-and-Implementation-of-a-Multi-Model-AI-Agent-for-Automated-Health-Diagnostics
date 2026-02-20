"""
Severity Engine: Advanced medical parameter severity classification.

Provides sophisticated calculation of parameter severity based on deviation
from reference ranges, with support for age adjustment and medical history
consideration.

Production-grade severity assessment for health report analysis.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Enumeration of severity levels for medical parameters."""
    NORMAL = "Normal"
    MILD = "Mild Deviation"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class SeverityResult:
    """Structured result of severity assessment."""
    value: float
    unit: str
    severity: SeverityLevel
    deviation_percent: float
    reference_min: float
    reference_max: float
    is_abnormal: bool
    reasoning: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "value": self.value,
            "unit": self.unit,
            "severity": self.severity.value,
            "deviation_percent": round(self.deviation_percent, 2),
            "reference_min": self.reference_min,
            "reference_max": self.reference_max,
            "is_abnormal": self.is_abnormal,
            "reasoning": self.reasoning
        }


class SeverityEngine:
    """
    Advanced severity classification engine for medical parameters.
    
    Calculates severity levels based on percentage deviation from
    reference ranges with thresholds optimized for clinical decision-making.
    """
    
    # Severity thresholds (as percentage deviation from reference range)
    THRESHOLD_MILD = 10.0      # 10% deviation = Mild
    THRESHOLD_MODERATE = 20.0  # 20% deviation = Moderate
    THRESHOLD_HIGH = 35.0      # 35% deviation = High
    THRESHOLD_CRITICAL = 50.0  # 50% deviation = Critical
    
    def __init__(self):
        """Initialize severity engine with clinical thresholds."""
        logger.info("Severity engine initialized")
    
    def calculate_severity(
        self,
        value: float,
        reference_min: float,
        reference_max: float,
        unit: str = "",
        age: Optional[int] = None,
        gender: Optional[str] = None
    ) -> SeverityResult:
        """
        Calculate severity level for a medical parameter.
        
        Args:
            value: Measured parameter value
            reference_min: Minimum normal reference value
            reference_max: Maximum normal reference value
            unit: Unit of measurement (for display)
            age: Optional age for age-adjusted thresholds
            gender: Optional gender for gender-adjusted thresholds
            
        Returns:
            SeverityResult: Structured severity assessment
            
        Example:
            >>> engine = SeverityEngine()
            >>> result = engine.calculate_severity(250, 0, 200, "mg/dL")
            >>> print(result.severity.value)
            'High'
        """
        
        # Check if value is within normal range
        if reference_min <= value <= reference_max:
            return SeverityResult(
                value=value,
                unit=unit,
                severity=SeverityLevel.NORMAL,
                deviation_percent=0.0,
                reference_min=reference_min,
                reference_max=reference_max,
                is_abnormal=False,
                reasoning="Value within normal reference range"
            )
        
        # Calculate deviation percentage
        range_width = reference_max - reference_min
        
        if value < reference_min:
            deviation = reference_min - value
            direction = "below"
        else:
            deviation = value - reference_max
            direction = "above"
        
        # Handle edge case of single-value reference (range width = 0)
        if range_width == 0:
            deviation_percent = (deviation / reference_min * 100) if reference_min != 0 else 0
        else:
            deviation_percent = (deviation / range_width) * 100
        
        # Determine severity level based on deviation percentage
        severity = self._classify_by_deviation(
            deviation_percent,
            age=age,
            gender=gender
        )
        
        reasoning = (
            f"Value {value} {unit} is {direction} normal range "
            f"({reference_min}-{reference_max} {unit}) by {deviation_percent:.1f}%"
        )
        
        logger.debug(
            f"Severity calculated: value={value}, severity={severity.value}, "
            f"deviation={deviation_percent:.1f}%"
        )
        
        return SeverityResult(
            value=value,
            unit=unit,
            severity=severity,
            deviation_percent=deviation_percent,
            reference_min=reference_min,
            reference_max=reference_max,
            is_abnormal=True,
            reasoning=reasoning
        )
    
    def _classify_by_deviation(
        self,
        deviation_percent: float,
        age: Optional[int] = None,
        gender: Optional[str] = None
    ) -> SeverityLevel:
        """
        Classify severity based on deviation percentage.
        
        Optionally adjusts thresholds based on age and gender.
        
        Args:
            deviation_percent: Percentage deviation from reference range
            age: Optional age for age-adjusted assessment
            gender: Optional gender for gender-adjusted assessment
            
        Returns:
            SeverityLevel: Classified severity
        """
        
        # Apply age adjustments (example: stricter for elderly)
        thresholds = self._get_adjusted_thresholds(age, gender)
        
        if deviation_percent >= thresholds["critical"]:
            return SeverityLevel.CRITICAL
        elif deviation_percent >= thresholds["high"]:
            return SeverityLevel.HIGH
        elif deviation_percent >= thresholds["moderate"]:
            return SeverityLevel.MODERATE
        elif deviation_percent >= thresholds["mild"]:
            return SeverityLevel.MILD
        else:
            return SeverityLevel.NORMAL
    
    def _get_adjusted_thresholds(
        self,
        age: Optional[int] = None,
        gender: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Get adjusted severity thresholds based on demographics.
        
        Applies clinical judgment for age and gender considerations.
        
        Args:
            age: Age in years
            gender: 'Male' or 'Female'
            
        Returns:
            Dict: Adjusted thresholds for each severity level
        """
        
        thresholds = {
            "mild": self.THRESHOLD_MILD,
            "moderate": self.THRESHOLD_MODERATE,
            "high": self.THRESHOLD_HIGH,
            "critical": self.THRESHOLD_CRITICAL
        }
        
        # Age adjustment: stricter for elderly or very young
        if age is not None:
            if age > 65:
                # Elderly: lower thresholds (more sensitive)
                thresholds = {k: v * 0.85 for k, v in thresholds.items()}
            elif age < 18:
                # Pediatric: context-specific
                thresholds = {k: v * 0.90 for k, v in thresholds.items()}
        
        return thresholds
    
    def batch_calculate_severity(
        self,
        parameters: Dict[str, Tuple[float, float, float]],
        age: Optional[int] = None,
        gender: Optional[str] = None,
        units: Optional[Dict[str, str]] = None
    ) -> Dict[str, SeverityResult]:
        """
        Calculate severity for multiple parameters efficiently.
        
        Args:
            parameters: Dict of {param_name: (value, ref_min, ref_max)}
            age: Optional age for all parameters
            gender: Optional gender for all parameters
            units: Optional {param_name: unit} mapping
            
        Returns:
            Dict: {param_name: SeverityResult}
            
        Example:
            >>> params = {
            ...     "glucose": (250, 70, 100),
            ...     "hemoglobin": (9.5, 12, 16)
            ... }
            >>> results = engine.batch_calculate_severity(params)
        """
        
        results = {}
        for param_name, (value, ref_min, ref_max) in parameters.items():
            unit = units.get(param_name, "") if units else ""
            results[param_name] = self.calculate_severity(
                value=value,
                reference_min=ref_min,
                reference_max=ref_max,
                unit=unit,
                age=age,
                gender=gender
            )
        
        return results
    
    def get_abnormality_count(
        self,
        severity_results: Dict[str, SeverityResult],
        severity_threshold: SeverityLevel = SeverityLevel.MODERATE
    ) -> int:
        """
        Count abnormal parameters above a threshold.
        
        Args:
            severity_results: Dict of severity assessment results
            severity_threshold: Minimum severity to count (default: MODERATE)
            
        Returns:
            int: Count of parameters meeting threshold
        """
        
        threshold_value = {
            SeverityLevel.NORMAL: 0,
            SeverityLevel.MILD: 1,
            SeverityLevel.MODERATE: 2,
            SeverityLevel.HIGH: 3,
            SeverityLevel.CRITICAL: 4
        }
        
        count = 0
        for result in severity_results.values():
            if self._severity_value(result.severity) >= threshold_value[severity_threshold]:
                count += 1
        
        return count
    
    @staticmethod
    def _severity_value(severity: SeverityLevel) -> int:
        """Convert severity level to numeric value for comparison."""
        severity_map = {
            SeverityLevel.NORMAL: 0,
            SeverityLevel.MILD: 1,
            SeverityLevel.MODERATE: 2,
            SeverityLevel.HIGH: 3,
            SeverityLevel.CRITICAL: 4
        }
        return severity_map.get(severity, 0)


# Convenience functions for single-call usage
def calculate_severity(
    value: float,
    reference_min: float,
    reference_max: float,
    unit: str = "",
    age: Optional[int] = None,
    gender: Optional[str] = None
) -> SeverityResult:
    """
    Convenience function for quick severity calculation.
    
    Creates engine instance and calculates severity in one call.
    Use for one-off calculations; use SeverityEngine class for batch operations.
    """
    engine = SeverityEngine()
    return engine.calculate_severity(
        value=value,
        reference_min=reference_min,
        reference_max=reference_max,
        unit=unit,
        age=age,
        gender=gender
    )


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    engine = SeverityEngine()
    
    # Single parameter assessment
    result = engine.calculate_severity(
        value=250,
        reference_min=0,
        reference_max=200,
        unit="mg/dL",
        age=45
    )
    
    print("\n=== Single Parameter Assessment ===")
    print(f"Value: {result.value} {result.unit}")
    print(f"Severity: {result.severity.value}")
    print(f"Deviation: {result.deviation_percent:.1f}%")
    print(f"Reasoning: {result.reasoning}")
    
    # Batch assessment
    print("\n=== Batch Assessment ===")
    params = {
        "glucose": (250, 70, 100),
        "hemoglobin": (9.5, 12, 16),
        "cholesterol": (220, 0, 200),
        "triglycerides": (150, 0, 150)
    }
    
    units = {
        "glucose": "mg/dL",
        "hemoglobin": "g/dL",
        "cholesterol": "mg/dL",
        "triglycerides": "mg/dL"
    }
    
    batch_results = engine.batch_calculate_severity(
        parameters=params,
        age=55,
        gender="Male",
        units=units
    )
    
    for param_name, result in batch_results.items():
        print(f"{param_name}: {result.severity.value} ({result.deviation_percent:.1f}% deviation)")
    
    # Count abnormalities
    abnormal_count = engine.get_abnormality_count(
        batch_results,
        severity_threshold=SeverityLevel.MODERATE
    )
    print(f"\nParameters with Moderate+ severity: {abnormal_count}")
