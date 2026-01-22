import re
from typing import Dict, Optional, Tuple

def extract_reference_range(text: str, parameter_name: str) -> Optional[Dict]:
    """
    Extract lab-specific reference range for a parameter from the report.
    This is the GOLD STANDARD - labs are legally required to print validated ranges.
    
    Args:
        text: The OCR text from the lab report
        parameter_name: The parameter to find the range for
    
    Returns:
        dict with 'min', 'max', 'unit', 'source' if found, None otherwise
    
    Example patterns:
    - "Hemoglobin: 13.5 g/dL | Reference: 13.0-17.0 g/dL"
    - "WBC Count: 7500 /cmm (Normal: 4000-11000)"
    - "Platelet Count 250000 /cmm 150000 - 450000"
    """
    text_lower = text.lower()
    param_lower = parameter_name.lower()
    
    # Common reference range patterns in lab reports
    patterns = [
        # Pattern: "Parameter: value unit (Reference: min-max unit)"
        rf"{param_lower}[:\s]+[\d\.,]+\s*[\w/]+\s*\(?(?:reference|normal|range)[:\s]*([\d\.]+)\s*[-–—]\s*([\d\.]+)\s*([\w/µ]+)?\)?",
        
        # Pattern: "Parameter value unit (min - max unit)"
        rf"{param_lower}[:\s]+[\d\.,]+\s*[\w/µ]+\s*\([\s]*([\d\.]+)\s*[-–—]\s*([\d\.]+)[\s]*([\w/µ]+)?\)",
        
        # Pattern: "Parameter value unit min - max" (range on same line)
        rf"{param_lower}[:\s]+[\d\.,]+\s*[\w/µ]+[\s]+([\d\.]+)\s*[-–—]\s*([\d\.]+)",
        
        # Pattern: "Parameter value (min-max)" (simple parentheses)
        rf"{param_lower}[:\s]+[\d\.,]+.*?\([\s]*([\d\.]+)\s*[-–—]\s*([\d\.]+)[\s]*\)",
        
        # Pattern with "biological reference interval"
        rf"{param_lower}.*?(?:biological|reference).*?interval[:\s]*([\d\.]+)\s*[-–—]\s*([\d\.]+)\s*([\w/µ]+)?",
        
        # Pattern: "Parameter...Normal Range: min-max"
        rf"{param_lower}.*?normal\s+range[:\s]*([\d\.]+)\s*[-–—]\s*([\d\.]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        if match:
            groups = match.groups()
            
            # Handle different group arrangements
            if len(groups) == 3 and groups[2] and not groups[2].replace('.', '').isdigit():
                # Pattern with unit at end: (min, max, unit)
                return {
                    'min': float(groups[0]),
                    'max': float(groups[1]),
                    'unit': groups[2],
                    'source': 'lab_report'
                }
            elif len(groups) >= 2:
                # Extract unit from earlier in the line if present
                try:
                    min_val = float(groups[0] if not groups[0].replace('.', '').replace('/', '').isalpha() else groups[1])
                    max_val = float(groups[1] if not groups[0].replace('.', '').replace('/', '').isalpha() else groups[2])
                    
                    # Try to find unit near the parameter
                    unit_match = re.search(rf"{param_lower}[:\s]+[\d\.,]+\s*([\w/µ]+)", text_lower)
                    unit = unit_match.group(1) if unit_match else None
                    
                    return {
                        'min': min_val,
                        'max': max_val,
                        'unit': unit,
                        'source': 'lab_report'
                    }
                except (ValueError, IndexError):
                    continue
    
    return None


PARAMETER_PATTERNS = {
    "Hemoglobin": {
        "pattern": r"hemoglobin\s+[^\d]*([\d\.]+)\s*g/dl",
        "unit": "g/dL"
    },
    "WBC": {
        "pattern": r"wbc\s+count[^\d]*([\d,]+)\s*/cmm",
        "unit": "cells/mm3"
    },
    "Platelet Count": {
        "pattern": r"platelet\s+count[^\d]*([\d]+)\s*/",
        "unit": "cells/mm3"
    },
    "Fasting Blood Sugar": {
        "pattern": r"fasting\s+blood\s+sugar[^\d]+h?\s*([\d\.]+)\s*mg/dl",
        "unit": "mg/dL"
    },
    "HbA1c": {
        "pattern": r"result\s+unit[^\d]+h?\s*([\d\.]+)\s*%",
        "unit": "%"
    },
    "Total Cholesterol": {
        "pattern": r"total\s+cholesterol[^\d]*([\d\.]+)\s*mg/dl",
        "unit": "mg/dL"
    },
    "Triglyceride": {
        "pattern": r"triglyceride[^\d]+result[^\d]*([\d\.]+)\s*mg/dl",
        "unit": "mg/dL"
    },
    "HDL Cholesterol": {
        "pattern": r"hdl\s+cholesterol[^\d]+result[^\d]*([\d\.]+)\s*mg/dl",
        "unit": "mg/dL"
    },
    "LDL Cholesterol": {
        "pattern": r"(?:direct\s+)?ldl[^\d]+result[^\d]*([\d\.]+)\s*mg/dl",
        "unit": "mg/dL"
    },
    "Creatinine": {
        "pattern": r"creatinine[^\d]+result[^\d]*([\d\.]+)\s*mg/dl",
        "unit": "mg/dL"
    },
    "TSH": {
        "pattern": r"tsh[^\d]+([\d\.]+)\s*microiu/ml",
        "unit": "µIU/mL"
    },
    "T3": {
        "pattern": r"t3[^\d]+([\d\.]+)\s*ng/ml",
        "unit": "ng/mL"
    },
    "T4": {
        "pattern": r"t4[^\d]+([\d\.]+)\s*mg/ml",
        "unit": "µg/dL"
    }
}

def extract_parameters(text: str) -> Dict:
    """
    Extract parameters and their lab-specific reference ranges from report text.
    Implements GOLD STANDARD approach: prioritize lab-printed ranges.
    """
    extracted = {}
    original_text = text  # Keep original for reference range extraction
    text_lower = text.lower()

    for param, config in PARAMETER_PATTERNS.items():
        match = re.search(config["pattern"], text_lower, re.IGNORECASE | re.DOTALL)
        if not match:
            continue

        value_str = match.group(1).replace(",", "")
        value = float(value_str)

        if param == "Platelet Count":
            # Platelet values are often large numbers
            if value < 10000:  # Likely in lakhs
                value *= 100000

        # Extract lab-specific reference range (GOLD STANDARD)
        reference_range = extract_reference_range(original_text, param)

        extracted[param] = {
            "value": value,
            "unit": config["unit"],
            "reference_range": reference_range  # Lab-specific range or None
        }

    return extracted
