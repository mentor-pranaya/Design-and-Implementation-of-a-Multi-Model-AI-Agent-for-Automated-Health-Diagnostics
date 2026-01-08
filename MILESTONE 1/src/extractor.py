import re

def extract_data(raw_text):
    # Pattern: Parameter Name | Value | Unit | Range
    # Example: Hemoglobin 14.5 g/dL (13.5-17.5)
    pattern = r"([a-zA-Z\s]+)\s+(\d+\.?\d*)\s+([a-zA-Z/]+)\s+\(?(\d+\.?\d*\s*-\s*\d+\.?\d*)\)?"
    
    matches = re.finditer(pattern, raw_text)
    extracted = []
    
    for match in matches:
        extracted.append({
            "parameter": match.group(1).strip(),
            "value": float(match.group(2)),
            "unit": match.group(3),
            "range": match.group(4)
        })
    return extracted
  
