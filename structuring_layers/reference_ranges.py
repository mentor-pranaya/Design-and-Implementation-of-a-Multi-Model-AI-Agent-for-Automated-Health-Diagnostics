"""
Medical Reference Ranges and Risk Classification.

Defines normal, abnormal, and risk thresholds for common blood tests.
Used for intelligent risk detection and findings generation.
"""

from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass

logger = None  # Will be set in init


@dataclass
class ReferenceRange:
    """Medical reference range with risk thresholds."""
    test_name: str
    unit: str
    normal_min: float
    normal_max: float
    warning_min: Optional[float] = None  # Below this is concerning
    warning_max: Optional[float] = None  # Above this is concerning
    critical_min: Optional[float] = None  # Below this is critical
    critical_max: Optional[float] = None  # Above this is critical
    
    def classify_risk(self, value: float) -> Tuple[str, str]:
        """
        Classify value into risk category.
        
        Returns:
            (risk_level, description) where risk_level is 'normal', 'low', 'moderate', or 'high'
        """
        if self.critical_min is not None and value < self.critical_min:
            return 'high', f'critically low (< {self.critical_min})'
        if self.critical_max is not None and value > self.critical_max:
            return 'high', f'critically high (> {self.critical_max})'
        
        if self.warning_min is not None and value < self.warning_min:
            return 'moderate', f'low (< {self.warning_min})'
        if self.warning_max is not None and value > self.warning_max:
            return 'moderate', f'high (> {self.warning_max})'
        
        if self.normal_min <= value <= self.normal_max:
            return 'normal', 'within normal range'
        
        if value < self.normal_min:
            return 'low', f'below normal range (< {self.normal_min})'
        if value > self.normal_max:
            return 'low', f'above normal range (> {self.normal_max})'
        
        return 'normal', 'within acceptable range'


# Comprehensive reference ranges for common blood tests
# These are general reference ranges; actual ranges may vary by lab
REFERENCE_RANGES: Dict[str, ReferenceRange] = {
    # ========== GLUCOSE TESTS ==========
    'glucose_fasting': ReferenceRange(
        test_name='Fasting Blood Sugar',
        unit='mg/dL',
        normal_min=70,
        normal_max=100,
        warning_min=60,
        warning_max=126,
        critical_min=50,
        critical_max=300,
    ),
    'glucose_random': ReferenceRange(
        test_name='Random Blood Sugar',
        unit='mg/dL',
        normal_min=80,
        normal_max=140,
        warning_min=70,
        warning_max=180,
        critical_min=50,
        critical_max=400,
    ),
    
    # ========== CHOLESTEROL TESTS ==========
    'total_cholesterol': ReferenceRange(
        test_name='Total Cholesterol',
        unit='mg/dL',
        normal_min=0,
        normal_max=200,
        warning_min=150,
        warning_max=240,
        critical_max=300,
    ),
    'hdl': ReferenceRange(
        test_name='HDL Cholesterol',
        unit='mg/dL',
        normal_min=40,
        normal_max=100,
        warning_min=30,
        warning_max=200,
        critical_min=20,
    ),
    'ldl': ReferenceRange(
        test_name='LDL Cholesterol',
        unit='mg/dL',
        normal_min=0,
        normal_max=100,
        warning_min=50,
        warning_max=160,
        critical_max=250,
    ),
    'triglycerides': ReferenceRange(
        test_name='Triglycerides',
        unit='mg/dL',
        normal_min=0,
        normal_max=150,
        warning_min=100,
        warning_max=200,
        critical_max=500,
    ),
    
    # ========== HEMOGLOBIN & RBC ==========
    'hemoglobin': ReferenceRange(
        test_name='Hemoglobin',
        unit='g/dL',
        normal_min=12.0,  # Female
        normal_max=16.0,  # Female
        warning_min=10.0,
        warning_max=18.0,
        critical_min=7.0,
        critical_max=20.0,
    ),
    'rbc': ReferenceRange(
        test_name='Red Blood Cells',
        unit='million/µL',
        normal_min=4.5,  # Female
        normal_max=5.5,  # Female
        warning_min=4.0,
        warning_max=6.0,
        critical_min=3.0,
        critical_max=7.0,
    ),
    
    # ========== WBC & PLATELETS ==========
    'wbc': ReferenceRange(
        test_name='White Blood Cells',
        unit='thousand/µL',
        normal_min=4.5,
        normal_max=11.0,
        warning_min=3.5,
        warning_max=12.0,
        critical_min=2.0,
        critical_max=30.0,
    ),
    'platelets': ReferenceRange(
        test_name='Platelets',
        unit='thousand/µL',
        normal_min=150,
        normal_max=400,
        warning_min=100,
        warning_max=450,
        critical_min=50,
        critical_max=1000,
    ),
    
    # ========== KIDNEY FUNCTION ==========
    'creatinine': ReferenceRange(
        test_name='Creatinine',
        unit='mg/dL',
        normal_min=0.7,  # Female
        normal_max=1.3,  # Female
        warning_min=0.5,
        warning_max=1.5,
        critical_min=0.4,
        critical_max=10.0,
    ),
    'bun': ReferenceRange(
        test_name='Blood Urea Nitrogen',
        unit='mg/dL',
        normal_min=7,
        normal_max=20,
        warning_min=5,
        warning_max=25,
        critical_min=3,
        critical_max=100,
    ),
    
    # ========== LIVER FUNCTION ==========
    'sodium': ReferenceRange(
        test_name='Sodium',
        unit='mEq/L',
        normal_min=136,
        normal_max=145,
        warning_min=130,
        warning_max=150,
        critical_min=125,
        critical_max=160,
    ),
    'potassium': ReferenceRange(
        test_name='Potassium',
        unit='mEq/L',
        normal_min=3.5,
        normal_max=5.0,
        warning_min=3.0,
        warning_max=5.5,
        critical_min=2.5,
        critical_max=6.5,
    ),
    'albumin': ReferenceRange(
        test_name='Albumin',
        unit='g/dL',
        normal_min=3.5,
        normal_max=5.5,
        warning_min=3.0,
        warning_max=6.0,
        critical_min=2.0,
        critical_max=7.0,
    ),
}


def get_reference_range(test_name: str) -> Optional[ReferenceRange]:
    """
    Get reference range for a test.
    
    Args:
        test_name: Test name (e.g., 'hemoglobin', 'glucose_fasting')
    
    Returns:
        ReferenceRange object or None if not found
    """
    return REFERENCE_RANGES.get(test_name.lower())


def classify_value(test_name: str, value: float) -> Optional[Tuple[str, str]]:
    """
    Classify a test value as normal/low/moderate/high risk.
    
    Args:
        test_name: Test name
        value: Numeric value
    
    Returns:
        (risk_level, description) or None if test not found
    """
    ref_range = get_reference_range(test_name)
    if not ref_range:
        return None
    
    return ref_range.classify_risk(value)


def get_abnormal_findings(
    test_results: Dict[str, Dict[str, any]],
) -> List[Dict[str, any]]:
    """
    Extract abnormal findings from test results.
    
    Args:
        test_results: Dictionary of test results with structure:
                     {test_name: {'value': float, 'unit': str, ...}}
    
    Returns:
        List of abnormal finding dicts with test name, value, and risk info
    """
    abnormalities = []
    
    for test_name, result in test_results.items():
        if not isinstance(result, dict):
            continue
        
        value = result.get('value')
        if value is None:
            continue
        
        try:
            value = float(value)
        except (ValueError, TypeError):
            continue
        
        risk_info = classify_value(test_name, value)
        if risk_info and risk_info[0] != 'normal':
            abnormalities.append({
                'test_name': test_name,
                'value': value,
                'unit': result.get('unit', ''),
                'risk_level': risk_info[0],
                'description': risk_info[1],
            })
    
    return abnormalities


# Mapping of test names to risk domains
TEST_TO_DOMAIN = {
    # Glucose tests → Diabetes risk
    'glucose_fasting': 'diabetes',
    'glucose_random': 'diabetes',
    
    # Lipid tests → Cardiac risk
    'total_cholesterol': 'cardiac',
    'hdl': 'cardiac',
    'ldl': 'cardiac',
    'triglycerides': 'cardiac',
    
    # CBC tests → CBC risk
    'hemoglobin': 'cbc',
    'rbc': 'cbc',
    'wbc': 'cbc',
    'platelets': 'cbc',
    
    # Kidney tests → Renal risk
    'creatinine': 'renal',
    'bun': 'renal',
    
    # Electrolytes → Metabolic risk
    'sodium': 'metabolic',
    'potassium': 'metabolic',
}


def get_risk_domain(test_name: str) -> Optional[str]:
    """
    Get the medical domain/category for a test.
    
    Args:
        test_name: Test name
    
    Returns:
        Domain name (cardiac, diabetes, cbc, etc.) or None
    """
    return TEST_TO_DOMAIN.get(test_name.lower())


__all__ = [
    'ReferenceRange',
    'REFERENCE_RANGES',
    'get_reference_range',
    'classify_value',
    'get_abnormal_findings',
    'get_risk_domain',
]
