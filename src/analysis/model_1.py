from typing import Dict, Any, Optional

# Reference Ranges (simplified for adult)
# Format: (min, max) or (min, max, "unit")
REFERENCE_RANGES = {
    "hemoglobin": {"min": 12.0, "max": 17.5, "unit": "g/dL"}, # Combined range
    "glucose": {"min": 70, "max": 100, "unit": "mg/dL"}, # Fasting
    "cholesterol": {"max": 200, "unit": "mg/dL"},
    "hdl": {"min": 40, "unit": "mg/dL"}, # Higher is better
    "ldl": {"max": 100, "unit": "mg/dL"},
    "triglycerides": {"max": 150, "unit": "mg/dL"},
    "wbc": {"min": 4500, "max": 11000, "unit": "/µL"},
    "platelets": {"min": 150000, "max": 450000, "unit": "/µL"},
    "creatinine": {"min": 0.6, "max": 1.2, "unit": "mg/dL"},
    "sodium": {"min": 135, "max": 145, "unit": "mmol/L"},
    "potassium": {"min": 3.5, "max": 5.0, "unit": "mmol/L"},
    "calcium": {"min": 8.5, "max": 10.5, "unit": "mg/dL"},
}

def analyze_parameter(param: str, value: float, unit: Optional[str] = None, gender: str = "unknown") -> Dict[str, Any]:
    """
    Analyze a single parameter against reference ranges.
    Returns a dictionary with status (normal, high, low, borderline) and reference range.
    """
    param = param.lower()
    ref = REFERENCE_RANGES.get(param)
    
    if not ref:
        return {"status": "unknown", "message": "No reference range available"}
    
    # Note: Value conversion should happen before this step if units mismatch. 
    # For Milestone 1, we assume units are standardized or we ignore them if mismatch (risky but starting point).
    
    status = "normal"
    
    if "min" in ref and value < ref["min"]:
        status = "low"
    elif "max" in ref and value > ref["max"]:
        status = "high"
    
    # Special handling for HDL (High is good, Low is bad)
    if param == "hdl":
        if value < ref["min"]:
            status = "low" # Risk
        else:
            status = "normal" # Good
            
    return {
        "status": status,
        "value": value,
        "ref_range": f"{ref.get('min', '')} - {ref.get('max', '')} {ref.get('unit', '')}".strip()
    }

def analyze_report(parameters: Dict[str, Dict[str, Any]], gender: str = "unknown") -> Dict[str, Any]:
    """
    Analyze all parameters in a report.
    """
    analysis = {}
    
    for param, data in parameters.items():
        value = data.get("value")
        unit = data.get("unit")
        
        if isinstance(value, (int, float)):
            result = analyze_parameter(param, value, unit, gender)
            analysis[param] = result
            
    return analysis
