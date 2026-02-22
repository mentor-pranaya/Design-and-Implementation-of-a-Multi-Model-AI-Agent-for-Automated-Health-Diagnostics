"""
Data Validation Module - Phase 1
Validates extracted parameters using intelligent multi-source reference ranges.

NO HARDCODING - Uses UnifiedReferenceManager for data-driven validation.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core_phase3.knowledge_base.unified_reference_manager import UnifiedReferenceManager


class ValidationError(Exception):
    """Custom exception for validation-related issues."""
    pass


# Allowed units (expandable)
ALLOWED_UNITS = {
    "g/dL",
    "mg/dL",
    "%",
    "cells/mm3",
    "mU/L",
    "ng/mL",
    "mmol/L",
    "U/L",
}


# Medical plausibility ranges (extreme bounds for sanity checks)
# These are NOT clinical ranges - just biological plausibility checks
PLAUSIBILITY_RANGES = {
    "Hemoglobin": (5.0, 20.0),
    "WBC": (1000, 50000),
    "Platelet Count": (50000, 1500000),
    "Fasting Blood Sugar": (40, 600),
    "Glucose": (40, 600),
    "HbA1c": (3.0, 15.0),
    "Total Cholesterol": (50, 400),
    "Triglyceride": (30, 1000),
    "Triglycerides": (30, 1000),
    "HDL Cholesterol": (10, 150),
    "HDL": (10, 150),
    "LDL Cholesterol": (20, 300),
    "LDL": (20, 300),
    "Creatinine": (0.2, 15.0),
    "Urea": (5, 300),
    "BUN": (5, 300),
    "SGPT": (5, 1000),
    "ALT": (5, 1000),
    "SGOT": (5, 1000),
    "AST": (5, 1000),
    "TSH": (0.01, 100.0),
    "T3": (0.5, 5.0),
    "T4": (2.0, 20.0),
}


# Initialize unified reference manager (singleton pattern)
_reference_manager = None

def get_reference_manager():
    """Get or create unified reference manager instance."""
    global _reference_manager
    if _reference_manager is None:
        _reference_manager = UnifiedReferenceManager()
    return _reference_manager


def validate_parameters(
    extracted_data: dict,
    patient_age: int = None,
    patient_sex: str = None
) -> dict:
    """
    Validate extracted parameters using intelligent multi-source reference ranges.
    
    Uses UnifiedReferenceManager with intelligent fallback:
    1. Lab-provided range (from report) - HIGHEST PRIORITY
    2. NHANES age/sex-specific ranges - POPULATION-BASED
    3. NHANES overall ranges - POPULATION-BASED
    4. ABIM clinical guidelines - CLINICAL STANDARD
    
    NO HARDCODING - All ranges from data sources.

    Args:
        extracted_data (dict): Output from extraction stage with optional reference_range
        patient_age (int): Patient age for age-specific ranges (optional)
        patient_sex (str): Patient sex ("male" or "female") for sex-specific ranges (optional)

    Returns:
        dict: Validated parameters with flags, warnings, severity, and source attribution
    """
    validated = {}
    manager = get_reference_manager()

    for parameter, details in extracted_data.items():
        value = details.get("value")
        unit = details.get("unit")
        lab_range = details.get("reference_range")  # Lab-specific range (GOLD STANDARD)

        param_result = {
            "value": value,
            "unit": unit,
            "valid": True,
            "severity": "Normal",
            "warnings": [],
        }

        # Missing value
        if value is None:
            param_result["valid"] = False
            param_result["severity"] = "Unknown"
            param_result["warnings"].append("Missing numeric value")
            validated[parameter] = param_result
            continue

        # Negative values (biologically implausible)
        if value < 0:
            param_result["valid"] = False
            param_result["severity"] = "Critical"
            param_result["warnings"].append("Negative value detected")
            validated[parameter] = param_result
            continue

        # Medical plausibility range check (sanity check for extreme values)
        if parameter in PLAUSIBILITY_RANGES:
            low, high = PLAUSIBILITY_RANGES[parameter]
            if value < low or value > high:
                param_result["valid"] = False
                param_result["severity"] = "Critical"
                param_result["warnings"].append(f"Value outside plausible range ({low}-{high})")
                validated[parameter] = param_result
                continue
        
        # Prepare lab-provided range for UnifiedReferenceManager
        lab_provided_range = None
        if lab_range and lab_range.get('source') == 'lab_report':
            lab_min = lab_range.get('min')
            lab_max = lab_range.get('max')
            if lab_min is not None and lab_max is not None:
                lab_provided_range = {
                    'min': lab_min,
                    'max': lab_max,
                    'unit': lab_range.get('unit')
                }
        
        # Use UnifiedReferenceManager for intelligent evaluation
        try:
            evaluation = manager.evaluate_value(
                parameter=parameter,
                value=value,
                age=patient_age,
                sex=patient_sex,
                lab_provided_range=lab_provided_range
            )
            
            # Check if reference range is available
            if not evaluation.get('reference_available', True):
                param_result["warnings"].append(f"No reference range available for {parameter}")
                param_result["severity"] = "Unknown"
                param_result["range_source"] = "none"
            else:
                # Use evaluation results
                param_result["severity"] = evaluation['status']
                param_result["reference_range"] = evaluation['reference_range']
                param_result["range_source"] = evaluation['source']
                param_result["confidence"] = evaluation['confidence']
                param_result["source_detail"] = evaluation['source_detail']
                
                # Add age/sex specificity info
                if evaluation.get('age_specific'):
                    param_result["age_specific"] = True
                if evaluation.get('sex_specific'):
                    param_result["sex_specific"] = True
                
                # Add percentile context if available
                if evaluation.get('percentiles'):
                    param_result["percentiles"] = evaluation['percentiles']
                
                # Add clinical significance if available
                if evaluation.get('clinical_significance'):
                    param_result["clinical_significance"] = evaluation['clinical_significance']
                
                # Add deviation info for abnormal values
                if evaluation['status'] != 'Normal':
                    if evaluation.get('severity'):
                        param_result["severity"] = evaluation['severity']
                    if evaluation.get('deviation_percent'):
                        param_result["deviation_percent"] = evaluation['deviation_percent']
                    
                    # Add warning message
                    if evaluation['status'] == 'Low':
                        param_result["warnings"].append(
                            f"Below reference range ({evaluation['reference_range']})"
                        )
                    elif evaluation['status'] == 'High':
                        param_result["warnings"].append(
                            f"Above reference range ({evaluation['reference_range']})"
                        )
        
        except Exception as e:
            # Fallback if UnifiedReferenceManager fails
            param_result["warnings"].append(f"Reference evaluation error: {str(e)}")
            param_result["severity"] = "Unknown"
            param_result["range_source"] = "error"

        # Unit validation
        if unit and unit not in ALLOWED_UNITS:
            param_result["warnings"].append(f"Unrecognized unit '{unit}'")

        validated[parameter] = param_result

    return validated
