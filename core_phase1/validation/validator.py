class ValidationError(Exception):
    """Custom exception for validation-related issues."""
    pass


# Allowed units (expandable)
ALLOWED_UNITS = {
    "g/dL",
    "mg/dL",
    "%",
    "cells/mm3",
}


# Medical reference ranges for plausibility checks
REFERENCE_RANGES = {
    "Hemoglobin": (5.0, 20.0),
    "WBC": (1000, 50000),
    "Platelet Count": (50000, 1500000),
    "Fasting Blood Sugar": (40, 600),
    "HbA1c": (3.0, 15.0),
    "Total Cholesterol": (50, 400),
    "Triglyceride": (30, 1000),
    "HDL Cholesterol": (10, 150),
    "LDL Cholesterol": (20, 300),
    "Creatinine": (0.2, 15.0),
    "Urea": (5, 300),
    "SGPT": (5, 1000),
    "SGOT": (5, 1000),
}

# Clinical normal ranges for classification
CLINICAL_NORMAL_RANGES = {
    "Hemoglobin": (13.0, 17.5),
    "WBC": (4000, 11000),
    "Platelet Count": (150000, 450000),
    "Fasting Blood Sugar": (70, 100),
    "HbA1c": (4.0, 5.6),
    "Total Cholesterol": (0, 200),
    "Triglyceride": (0, 150),
    "HDL Cholesterol": (40, 100),
    "LDL Cholesterol": (0, 100),
    "Creatinine": (0.7, 1.3),
    "Urea": (7, 20),
    "SGPT": (0, 40),
    "SGOT": (0, 40),
    "TSH": (0.4, 4.0),
    "T3": (0.80, 2.00),
    "T4": (5.0, 12.0),
}


def validate_parameters(extracted_data: dict) -> dict:
    """
    Validate extracted parameters using lab-specific reference ranges (GOLD STANDARD).
    Falls back to hardcoded ranges only if lab ranges are not available.

    Args:
        extracted_data (dict): Output from extraction stage with optional reference_range

    Returns:
        dict: Validated parameters with flags, warnings, and severity
    """
    validated = {}

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
            "range_source": "external" if not lab_range else "lab_report"
        }

        # Missing value
        if value is None:
            param_result["valid"] = False
            param_result["severity"] = "Unknown"
            param_result["warnings"].append("Missing numeric value")

        # Negative values (biologically implausible)
        elif value < 0:
            param_result["valid"] = False
            param_result["severity"] = "Critical"
            param_result["warnings"].append("Negative value detected")

        # Medical plausibility range check (always check for critical errors)
        elif parameter in REFERENCE_RANGES:
            low, high = REFERENCE_RANGES[parameter]

            if value < low or value > high:
                param_result["valid"] = False
                param_result["severity"] = "Critical"
                param_result["warnings"].append("Value outside plausible range")
        
        # GOLD STANDARD: Use lab-specific reference range if available
        if lab_range and lab_range.get('source') == 'lab_report' and value is not None and value >= 0:
            lab_min = lab_range.get('min')
            lab_max = lab_range.get('max')
            
            if lab_min is not None and lab_max is not None:
                param_result["reference_range"] = {
                    "min": lab_min,
                    "max": lab_max,
                    "unit": lab_range.get('unit')
                }
                
                # Use lab range for classification (GROUND TRUTH)
                if value < lab_min:
                    param_result["severity"] = "Low"
                    param_result["warnings"].append(f"Below lab reference range ({lab_min}-{lab_max})")
                elif value > lab_max:
                    param_result["severity"] = "High"
                    param_result["warnings"].append(f"Above lab reference range ({lab_min}-{lab_max})")
                elif param_result["severity"] not in ["Critical", "Unknown"]:
                    param_result["severity"] = "Normal"
        
        # FALLBACK: Use static clinical ranges only if lab range not found
        elif parameter in CLINICAL_NORMAL_RANGES and value is not None and value >= 0:
            clin_low, clin_high = CLINICAL_NORMAL_RANGES[parameter]
            
            param_result["warnings"].append("Using external reference ranges (lab range not found)")
            
            if value < clin_low:
                param_result["severity"] = "Low"
            elif value > clin_high:
                param_result["severity"] = "High"
            elif param_result["severity"] not in ["Critical", "Unknown"]:
                param_result["severity"] = "Normal"

        # Unit validation
        if unit and unit not in ALLOWED_UNITS:
            param_result["warnings"].append(f"Unrecognized unit '{unit}'")

        validated[parameter] = param_result

    return validated
