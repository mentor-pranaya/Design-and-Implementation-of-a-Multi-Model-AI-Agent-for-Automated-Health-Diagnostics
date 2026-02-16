from typing import Dict, Any

def clean_and_structure_data(params: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Clean and structure the extracted data.
    Handles both flat {key: value} and nested {key: {value: v, unit: u}}
    """
    cleaned = {}
    for key, data in params.items():
        key = key.lower().strip()
        
        if isinstance(data, dict):
            value = data.get("value")
            structured_data = data
        else:
            value = data
            structured_data = {"value": value, "unit": "unknown"}
            
        # Coerce to float if possible
        if not isinstance(value, (int, float)):
             try:
                 if isinstance(value, str):
                     import re
                     # Find first number in string
                     num_match = re.search(r"[-+]?\d*\.?\d+", value)
                     if num_match:
                         value = float(num_match.group())
                         structured_data["value"] = value
                     else:
                         continue
                 else:
                     continue
             except (ValueError, TypeError):
                 continue
                 
        if isinstance(value, (int, float)):
             # Basic sanity cleaning
             if 0 <= value <= 1000000: # WBC/Platelets can be high
                 cleaned[key] = structured_data
                 
    return cleaned