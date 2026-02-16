import re
from typing import Dict, Any, Union, cast
from src.extraction.medical_schema import MEDICAL_SCHEMA

def extract_parameters_from_text(text: str) -> Dict[str, Dict[str, Any]]:
    """
    Extract medical parameters from text using improved regex patterns.
    Returns a dictionary where keys are parameter names and values are dicts with 'value' and 'unit'.
    """
    print(f"DEBUG: Extraction Input Text ({len(text)} chars)")
    # Fix slicing issue by ensuring integer indices
    sample_text = str(text)[:200] if len(str(text)) > 200 else str(text)
    print(f"DEBUG: Sample: {sample_text}...")

    text = str(text).lower()
    # Explicitly allow Any to silence strict type checkers
    extracted: Dict[str, Dict[str, Any]] = {}

    for parameter, aliases in MEDICAL_SCHEMA.items():
        for alias in aliases:
            # Flexible pattern:
            # 1. Alias (start of line or word boundary)
            # 2. Optional separator (colon, equals, hyphen) with optional whitespace
            # 3. Value: 
            #    - "1,000.50" format
            #    - "1000.50" format
            # 4. Optional Unit (whitespace separator optional but likely)
            
            # \s* allows for missing spaces (OCR error) or newlines
            pattern = rf"(?:\b|^){re.escape(alias)}\s*[:=\-]?\s*([0-9]{{1,3}}(?:,[0-9]{{3}})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)(?:\s+([a-z/%^3\u00B5\u03BC]+))?"
            
            match = re.search(pattern, text)
            
            if match:
                try:
                    value_str = match.group(1)
                    unit_str = match.group(2) if match.group(2) else None
                    
                    # Remove commas
                    value_str = value_str.replace(',', '')
                    value = float(value_str)
                    
                    extracted[parameter] = {
                        "value": value,
                        "unit": unit_str,
                        "original_text": match.group(0)
                    }
                    print(f"DEBUG: Extracted {parameter}: {value} {unit_str}")
                    break # Found a match for this parameter, stop checking other aliases
                except ValueError:
                    continue

    print(f"DEBUG: Total extracted parameters: {len(extracted)}")
    return extracted

def extract_parameters_from_json(data: Union[Dict, list]) -> Dict[str, Dict[str, Any]]:
    """
    Extract parameters from a JSON object (dict or list of dicts).
    Tries to map keys to known parameters in MEDICAL_SCHEMA.
    """
    extracted = {}
    
    # helper to process a single dict
    def process_dict(d: Dict):
        for key, value in d.items():
            key_lower = key.lower()
            # Check if key matches any known parameter alias
            matched_param = None
            for param, aliases in MEDICAL_SCHEMA.items():
                if key_lower == param or key_lower in aliases:
                    matched_param = param
                    break
            
            if matched_param:
                # If value is simple number
                if isinstance(value, (int, float)):
                    extracted[matched_param] = {
                        "value": float(value),
                        "unit": None # Unit might be in a separate field or implicit
                    }
                # If value is string, try to parse number and unit
                elif isinstance(value, str):
                    # Try to separate value and unit
                     match = re.match(r"([0-9.]+)\s*([a-z/%]+)?", value.strip())
                     if match:
                         try:
                             extracted[matched_param] = {
                                 "value": float(match.group(1)),
                                 "unit": str(match.group(2)) if match.group(2) else None
                             }
                         except ValueError:
                             pass
    
    if isinstance(data, dict):
        process_dict(data)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                process_dict(item)
                
    return extracted

