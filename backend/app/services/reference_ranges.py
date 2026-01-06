"""
Reference ranges for common blood test parameters
Based on standard clinical guidelines
"""

from typing import Dict, Optional, Tuple
from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class ParameterStatus(str, Enum):
    NORMAL = "normal"
    LOW = "low"
    HIGH = "high"
    BORDERLINE_LOW = "borderline_low"
    BORDERLINE_HIGH = "borderline_high"
    CRITICAL_LOW = "critical_low"
    CRITICAL_HIGH = "critical_high"

# Standard reference ranges (adult)
REFERENCE_RANGES = {
    # Complete Blood Count (CBC)
    "hemoglobin": {
        "unit": "g/dL",
        "male": {"critical_low": 7.0, "low": 13.5, "normal_min": 13.5, "normal_max": 17.5, "high": 17.5, "critical_high": 20.0},
        "female": {"critical_low": 7.0, "low": 12.0, "normal_min": 12.0, "normal_max": 15.5, "high": 15.5, "critical_high": 18.0},
        "aliases": ["hb", "hgb", "haemoglobin"]
    },
    "rbc": {
        "unit": "million cells/μL",
        "male": {"critical_low": 3.0, "low": 4.7, "normal_min": 4.7, "normal_max": 6.1, "high": 6.1, "critical_high": 7.0},
        "female": {"critical_low": 3.0, "low": 4.2, "normal_min": 4.2, "normal_max": 5.4, "high": 5.4, "critical_high": 6.5},
        "aliases": ["red blood cells", "erythrocytes"]
    },
    "wbc": {
        "unit": "cells/μL",
        "general": {"critical_low": 2000, "low": 4000, "normal_min": 4000, "normal_max": 11000, "high": 11000, "critical_high": 30000},
        "aliases": ["white blood cells", "leukocytes"]
    },
    "platelets": {
        "unit": "cells/μL",
        "general": {"critical_low": 20000, "low": 150000, "normal_min": 150000, "normal_max": 400000, "high": 400000, "critical_high": 1000000},
        "aliases": ["plt", "thrombocytes"]
    },
    "hematocrit": {
        "unit": "%",
        "male": {"critical_low": 25.0, "low": 38.3, "normal_min": 38.3, "normal_max": 48.6, "high": 48.6, "critical_high": 60.0},
        "female": {"critical_low": 25.0, "low": 35.5, "normal_min": 35.5, "normal_max": 44.9, "high": 44.9, "critical_high": 55.0},
        "aliases": ["hct", "pcv"]
    },
    "mcv": {
        "unit": "fL",
        "general": {"critical_low": 70.0, "low": 80.0, "normal_min": 80.0, "normal_max": 100.0, "high": 100.0, "critical_high": 120.0},
        "aliases": ["mean corpuscular volume"]
    },
    
    # Metabolic Panel
    "glucose": {
        "unit": "mg/dL",
        "general": {"critical_low": 40.0, "low": 70.0, "normal_min": 70.0, "normal_max": 100.0, "high": 126.0, "critical_high": 400.0},
        "aliases": ["blood sugar", "fasting glucose", "fbs"]
    },
    "creatinine": {
        "unit": "mg/dL",
        "male": {"critical_low": 0.4, "low": 0.7, "normal_min": 0.7, "normal_max": 1.3, "high": 1.3, "critical_high": 5.0},
        "female": {"critical_low": 0.4, "low": 0.6, "normal_min": 0.6, "normal_max": 1.1, "high": 1.1, "critical_high": 5.0},
        "aliases": ["serum creatinine"]
    },
    "bun": {
        "unit": "mg/dL",
        "general": {"critical_low": 5.0, "low": 7.0, "normal_min": 7.0, "normal_max": 20.0, "high": 20.0, "critical_high": 100.0},
        "aliases": ["blood urea nitrogen", "urea"]
    },
    "sodium": {
        "unit": "mEq/L",
        "general": {"critical_low": 120.0, "low": 136.0, "normal_min": 136.0, "normal_max": 145.0, "high": 145.0, "critical_high": 160.0},
        "aliases": ["na", "serum sodium"]
    },
    "potassium": {
        "unit": "mEq/L",
        "general": {"critical_low": 2.5, "low": 3.5, "normal_min": 3.5, "normal_max": 5.0, "high": 5.0, "critical_high": 6.5},
        "aliases": ["k", "serum potassium"]
    },
    
    # Lipid Panel
    "total_cholesterol": {
        "unit": "mg/dL",
        "general": {"critical_low": 100.0, "low": 125.0, "normal_min": 125.0, "normal_max": 200.0, "high": 240.0, "critical_high": 400.0},
        "aliases": ["cholesterol", "total chol"]
    },
    "hdl": {
        "unit": "mg/dL",
        "male": {"critical_low": 20.0, "low": 40.0, "normal_min": 40.0, "normal_max": 100.0, "high": 100.0, "critical_high": 150.0},
        "female": {"critical_low": 20.0, "low": 50.0, "normal_min": 50.0, "normal_max": 100.0, "high": 100.0, "critical_high": 150.0},
        "aliases": ["hdl cholesterol", "good cholesterol"]
    },
    "ldl": {
        "unit": "mg/dL",
        "general": {"critical_low": 40.0, "low": 50.0, "normal_min": 50.0, "normal_max": 100.0, "high": 160.0, "critical_high": 300.0},
        "aliases": ["ldl cholesterol", "bad cholesterol"]
    },
    "triglycerides": {
        "unit": "mg/dL",
        "general": {"critical_low": 40.0, "low": 50.0, "normal_min": 50.0, "normal_max": 150.0, "high": 200.0, "critical_high": 500.0},
        "aliases": ["tg", "trigs"]
    },
    
    # Liver Function
    "alt": {
        "unit": "U/L",
        "general": {"critical_low": 5.0, "low": 7.0, "normal_min": 7.0, "normal_max": 56.0, "high": 56.0, "critical_high": 1000.0},
        "aliases": ["sgpt", "alanine aminotransferase"]
    },
    "ast": {
        "unit": "U/L",
        "general": {"critical_low": 5.0, "low": 10.0, "normal_min": 10.0, "normal_max": 40.0, "high": 40.0, "critical_high": 1000.0},
        "aliases": ["sgot", "aspartate aminotransferase"]
    },
    "bilirubin_total": {
        "unit": "mg/dL",
        "general": {"critical_low": 0.1, "low": 0.1, "normal_min": 0.1, "normal_max": 1.2, "high": 1.2, "critical_high": 20.0},
        "aliases": ["total bilirubin", "bilirubin"]
    },
    
    # Thyroid
    "tsh": {
        "unit": "mIU/L",
        "general": {"critical_low": 0.1, "low": 0.4, "normal_min": 0.4, "normal_max": 4.0, "high": 4.0, "critical_high": 10.0},
        "aliases": ["thyroid stimulating hormone"]
    },
    
    # Diabetes
    "hba1c": {
        "unit": "%",
        "general": {"critical_low": 4.0, "low": 4.0, "normal_min": 4.0, "normal_max": 5.7, "high": 6.5, "critical_high": 14.0},
        "aliases": ["glycated hemoglobin", "glycohemoglobin", "a1c"]
    },
}

class ReferenceRangeService:
    """Service for managing reference ranges and parameter classification"""
    
    def __init__(self):
        self.ranges = REFERENCE_RANGES
    
    def normalize_parameter_name(self, name: str) -> Optional[str]:
        """Normalize parameter name to standard form"""
        name_lower = name.lower().strip()
        
        # Direct match
        if name_lower in self.ranges:
            return name_lower
        
        # Check aliases
        for param, data in self.ranges.items():
            if "aliases" in data:
                if name_lower in [alias.lower() for alias in data["aliases"]]:
                    return param
        
        return None
    
    def get_reference_range(
        self, 
        parameter: str, 
        gender: Optional[Gender] = None,
        age: Optional[int] = None
    ) -> Optional[Dict]:
        """Get reference range for a parameter"""
        param_name = self.normalize_parameter_name(parameter)
        
        if not param_name or param_name not in self.ranges:
            return None
        
        range_data = self.ranges[param_name]
        
        # Get gender-specific range if available
        if gender and gender.value in range_data:
            return {
                "parameter": param_name,
                "unit": range_data["unit"],
                **range_data[gender.value]
            }
        
        # Fallback to general range
        if "general" in range_data:
            return {
                "parameter": param_name,
                "unit": range_data["unit"],
                **range_data["general"]
            }
        
        return None
    
    def classify_value(
        self,
        parameter: str,
        value: float,
        gender: Optional[Gender] = None,
        age: Optional[int] = None
    ) -> Tuple[ParameterStatus, str]:
        """
        Classify a parameter value against reference ranges
        Returns: (status, explanation)
        """
        ref_range = self.get_reference_range(parameter, gender, age)
        
        if not ref_range:
            return ParameterStatus.NORMAL, "Reference range not available"
        
        critical_low = ref_range.get("critical_low", float('-inf'))
        low = ref_range.get("low", ref_range.get("normal_min"))
        normal_min = ref_range["normal_min"]
        normal_max = ref_range["normal_max"]
        high = ref_range.get("high", normal_max)
        critical_high = ref_range.get("critical_high", float('inf'))
        
        # Critical values
        if value <= critical_low:
            return ParameterStatus.CRITICAL_LOW, f"Critically low (≤{critical_low} {ref_range['unit']})"
        if value >= critical_high:
            return ParameterStatus.CRITICAL_HIGH, f"Critically high (≥{critical_high} {ref_range['unit']})"
        
        # Low values
        if value < normal_min:
            if value < low:
                return ParameterStatus.LOW, f"Low (below {normal_min} {ref_range['unit']})"
            else:
                return ParameterStatus.BORDERLINE_LOW, f"Borderline low ({low}-{normal_min} {ref_range['unit']})"
        
        # High values
        if value > normal_max:
            if value > high:
                return ParameterStatus.HIGH, f"High (above {normal_max} {ref_range['unit']})"
            else:
                return ParameterStatus.BORDERLINE_HIGH, f"Borderline high ({normal_max}-{high} {ref_range['unit']})"
        
        # Normal range
        return ParameterStatus.NORMAL, f"Normal ({normal_min}-{normal_max} {ref_range['unit']})"
    
    def get_clinical_significance(self, parameter: str, status: ParameterStatus) -> str:
        """Get clinical significance explanation for a parameter status"""
        
        clinical_notes = {
            "hemoglobin": {
                ParameterStatus.LOW: "May indicate anemia, blood loss, or nutritional deficiency",
                ParameterStatus.HIGH: "May indicate dehydration, lung disease, or polycythemia",
                ParameterStatus.CRITICAL_LOW: "Severe anemia requiring immediate medical attention",
                ParameterStatus.CRITICAL_HIGH: "Severe polycythemia requiring immediate evaluation"
            },
            "glucose": {
                ParameterStatus.LOW: "May indicate hypoglycemia - check for diabetes medication issues",
                ParameterStatus.HIGH: "May indicate prediabetes or diabetes",
                ParameterStatus.CRITICAL_LOW: "Severe hypoglycemia - risk of unconsciousness",
                ParameterStatus.CRITICAL_HIGH: "Severe hyperglycemia - risk of diabetic complications"
            },
            "creatinine": {
                ParameterStatus.HIGH: "May indicate kidney dysfunction or dehydration",
                ParameterStatus.CRITICAL_HIGH: "Severe kidney impairment requiring immediate attention"
            },
            "ldl": {
                ParameterStatus.HIGH: "Increased risk of cardiovascular disease",
                ParameterStatus.CRITICAL_HIGH: "Very high cardiovascular risk - consider medication"
            },
            "hdl": {
                ParameterStatus.LOW: "Low protective cholesterol - increased cardiovascular risk"
            },
            "triglycerides": {
                ParameterStatus.HIGH: "Increased cardiovascular risk and risk of pancreatitis",
                ParameterStatus.CRITICAL_HIGH: "Very high risk of pancreatitis"
            },
            "wbc": {
                ParameterStatus.LOW: "May indicate infection, bone marrow disorder, or autoimmune disease",
                ParameterStatus.HIGH: "May indicate infection, inflammation, or blood disorder"
            },
            "platelets": {
                ParameterStatus.LOW: "Increased bleeding risk",
                ParameterStatus.CRITICAL_LOW: "Severe bleeding risk requiring immediate attention"
            }
        }
        
        param = self.normalize_parameter_name(parameter)
        
        if param in clinical_notes and status in clinical_notes[param]:
            return clinical_notes[param][status]
        
        return "Consult with healthcare provider for interpretation"

# Global instance
reference_range_service = ReferenceRangeService()
