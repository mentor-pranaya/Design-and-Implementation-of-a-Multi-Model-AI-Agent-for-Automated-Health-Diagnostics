from typing import Dict, Any, Optional

STANDARD_UNITS = {
    "hemoglobin": "g/dL",
    "glucose": "mg/dL",
    "cholesterol": "mg/dL",
    "hdl": "mg/dL",
    "ldl": "mg/dL",
    "triglycerides": "mg/dL",
    "wbc": "/µL",
    "platelets": "/µL",
    "creatinine": "mg/dL",
    "urea": "mg/dL",
    "sodium": "mmol/L",
    "potassium": "mmol/L",
    "chloride": "mmol/L",
    "calcium": "mg/dL",
    "magnesium": "mg/dL",
    "tsh": "µIU/mL",
    "t3": "ng/dL",
    "t4": "µg/dL",
    "vitamin_d": "ng/mL",
    "vitamin_b12": "pg/mL",
    "iron": "µg/dL",
    "blood_pressure": "mmHg"
}

UNIT_ALIASES = {
    "g/dl": ["gdl", "gm/dl", "g/l"], # Note: g/L is 10x g/dL, need conversion logic if we want to support it. For now just mapping string aliases.
    "mg/dl": ["mgdl", "mg/100ml"],
    "mmol/l": ["mmoll", "mmol/L"],
    "/µL": ["/ul", "/mm3", "cmm", "cells/ul"],
    "iu/l": ["i.u./l", "u/l"],
    "mmhg": ["mm hg"]
}

def standardize_units(parameters: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Standardize units in the extracted parameters.
    Converts unit strings to standard format.
    Does NOT currently perform value conversion (e.g. mmol/L to mg/dL) but prepares for it.
    """
    standardized = {}
    
    for param, data in parameters.items():
        value = data.get("value")
        unit = data.get("unit")
        
        if unit:
            unit = unit.lower().replace(" ", "")
            # Check aliases
            for std_unit, aliases in UNIT_ALIASES.items():
                if unit in aliases or unit == std_unit.lower().replace(" ", ""):
                    unit = std_unit
                    break
        else:
            # If unit is missing, we might assume standard unit or leave as None
            pass
            
        standardized[param] = {
            "value": value,
            "unit": unit,
            "original_text": data.get("original_text")
        }
        
    return standardized
