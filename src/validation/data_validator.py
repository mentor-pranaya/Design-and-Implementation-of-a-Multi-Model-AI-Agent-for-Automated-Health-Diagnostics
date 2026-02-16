from typing import Dict, Any, Tuple, List

def validate_parameters(parameters: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    """
    Validates extracted blood parameters.
    Checks value types, ranges, and structure.
    """
    validated = {}
    issues = []

    for param, data in parameters.items():
        if not isinstance(data, dict):
            issues.append(f"{param}: Invalid data structure")
            continue
            
        value = data.get("value")
        unit = data.get("unit")
        
        # Check value type
        if not isinstance(value, (int, float)):
             issues.append(f"{param}: Invalid value type ({type(value)})")
             continue

        # Check value range (basic sanity)
        if value < 0:
            issues.append(f"{param}: Negative value ({value})")
            continue
            
        # We could add specific range checks per parameter here
        # e.g. Glucose > 1000 is unlikely (except hyperosmolar state)
        if value > 5000 and param != "wbc" and param != "platelets": # simplistic check
             issues.append(f"{param}: Value suspicously high ({value})")
             # We might still include it but flag it
        
        validated[param] = data

    if not validated:
        issues.append("No valid parameters found")

    return validated, issues

