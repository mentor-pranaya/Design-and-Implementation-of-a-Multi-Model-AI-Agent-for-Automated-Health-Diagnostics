"""
Improved Parameter Extraction Patterns
Handles multiple lab report formats and variations
"""
import re
from typing import Dict, List, Tuple, Optional

# Comprehensive parameter name variations
PARAMETER_ALIASES = {
    "hemoglobin": ["hemoglobin", "hb", "hgb", "haemoglobin"],
    "glucose": ["glucose", "sugar", "fbs", "rbs", "fasting blood sugar", "random blood sugar", "blood sugar"],
    "creatinine": ["creatinine", "creat", "serum creatinine"],
    "cholesterol": ["cholesterol", "chol", "total cholesterol"],
    "triglycerides": ["triglyceride", "triglycerides", "trig", "tg"],
    "hdl": ["hdl", "hdl cholesterol", "hdl-c"],
    "ldl": ["ldl", "ldl cholesterol", "ldl-c", "direct ldl"],
    "wbc": ["wbc", "white blood cell", "leucocyte", "leukocyte", "total leukocyte count", "tlc"],
    "rbc": ["rbc", "red blood cell", "erythrocyte", "red cell count"],
    "platelet": ["platelet", "plt", "platelet count"],
    "hematocrit": ["hematocrit", "hct", "pcv", "packed cell volume"],
    "mcv": ["mcv", "mean corpuscular volume"],
    "mch": ["mch", "mean corpuscular hemoglobin"],
    "mchc": ["mchc", "mean corpuscular hemoglobin concentration"],
    "rdw": ["rdw", "red cell distribution width"],
    "alt": ["alt", "sgpt", "alanine aminotransferase", "alanine transaminase"],
    "ast": ["ast", "sgot", "aspartate aminotransferase", "aspartate transaminase"],
    "alp": ["alp", "alkaline phosphatase"],
    "ggt": ["ggt", "gamma gt", "gamma glutamyl transferase"],
    "bilirubin_total": ["bilirubin total", "total bilirubin", "bilirubin"],
    "bilirubin_direct": ["bilirubin direct", "direct bilirubin"],
    "bilirubin_indirect": ["bilirubin indirect", "indirect bilirubin"],
    "albumin": ["albumin", "alb", "serum albumin"],
    "protein_total": ["total protein", "protein total", "serum protein"],
    "globulin": ["globulin", "serum globulin"],
    "urea": ["urea", "blood urea"],
    "bun": ["bun", "blood urea nitrogen"],
    "sodium": ["sodium", "na", "serum sodium"],
    "potassium": ["potassium", "k", "serum potassium"],
    "chloride": ["chloride", "cl", "serum chloride"],
    "calcium": ["calcium", "ca", "serum calcium"],
    "phosphorus": ["phosphorus", "phosphate", "po4"],
    "magnesium": ["magnesium", "mg"],
    "tsh": ["tsh", "thyroid stimulating hormone"],
    "t3": ["t3", "triiodothyronine"],
    "t4": ["t4", "thyroxine"],
    "hba1c": ["hba1c", "hb a1c", "glycated hemoglobin", "glycosylated hemoglobin"],
    "neutrophils": ["neutrophil", "neutrophils", "segmented neutrophils", "polymorphs"],
    "lymphocytes": ["lymphocyte", "lymphocytes"],
    "monocytes": ["monocyte", "monocytes"],
    "eosinophils": ["eosinophil", "eosinophils"],
    "basophils": ["basophil", "basophils"],
}

def build_flexible_pattern(param_aliases: List[str]) -> str:
    """
    Build a flexible regex pattern that matches parameter name followed by value.
    
    Handles formats like:
    - "Hemoglobin 13.5 g/dL"
    - "HB: 13.5"
    - "Hemoglobin (HB) 13.5 g/dL"
    - "Test Name: Hemoglobin Result: 13.5"
    - "TSH 3RD GENERATION 8.480" (skips "3RD GENERATION")
    """
    # Create alternation of all aliases
    aliases_pattern = "|".join(re.escape(alias) for alias in param_aliases)
    
    # Pattern that captures value after parameter name
    # Allows for various separators and formats
    # Handles "TSH 3RD GENERATION 8.480" by skipping non-numeric words
    pattern = rf"""
        (?:{aliases_pattern})           # Parameter name (any alias)
        \s*                              # Optional whitespace
        (?:\([^\)]*\))?                  # Optional parenthetical (like "(HB)")
        \s*                              # Optional whitespace
        (?:\d+(?:st|nd|rd|th)\s+[A-Z]+\s+)?  # Optional ordinal + word (like "3RD GENERATION")
        (?::|=|result)?                  # Optional separator
        \s*                              # Optional whitespace
        (?:result)?                      # Optional "result" keyword
        \s*                              # Optional whitespace
        (?P<value>-?\d+(?:\.\d+)?)      # Numeric value (int or float)
        \s*                              # Optional whitespace
        (?P<unit>[a-zA-Z/%µ]+)?         # Optional unit
    """
    
    return pattern

def extract_parameters_flexible(text: str) -> Dict:
    """
    Extract parameters using flexible patterns that handle multiple formats.
    
    Args:
        text: OCR text from lab report
        
    Returns:
        dict: {parameter_name: {"value": float, "unit": str, "raw_match": tuple}}
    """
    extracted = {}
    text_lower = text.lower()
    
    for canonical_name, aliases in PARAMETER_ALIASES.items():
        pattern = build_flexible_pattern(aliases)
        
        # Find all matches (some reports have multiple occurrences)
        matches = list(re.finditer(pattern, text_lower, re.VERBOSE | re.IGNORECASE))
        
        if not matches:
            continue
            
        # Use the first match (usually the actual result, not reference range)
        match = matches[0]
        
        try:
            value = float(match.group("value"))
            unit = match.group("unit") or "unknown"
            
            extracted[canonical_name] = {
                "value": value,
                "unit": unit,
                "raw_match": (match.group("value"), unit)
            }
        except (ValueError, AttributeError):
            continue
    
    return extracted

def extract_with_table_format(text: str) -> Dict:
    """
    Extract parameters from table-formatted reports.
    
    Common table formats:
    - "Test Name | Result | Unit | Reference Range"
    - "Parameter  Value  Unit  Range"
    - "T3  151.9  Adult : 80-200  ng/dL"
    """
    extracted = {}
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Check if line contains a parameter name
        for canonical_name, aliases in PARAMETER_ALIASES.items():
            for alias in aliases:
                if alias in line_lower:
                    # Try to extract value from this line or next few lines
                    # Look for numeric values in the same line
                    value_pattern = r'\b(\d+(?:\.\d+)?)\b'
                    values = re.findall(value_pattern, line)
                    
                    if values:
                        # First numeric value is usually the result
                        # Skip if it looks like a reference range (e.g., "80-200")
                        try:
                            value = float(values[0])
                            
                            # Skip values that are clearly part of reference ranges
                            # Check if there's a dash/hyphen near this value
                            context = line[max(0, line.find(values[0])-5):min(len(line), line.find(values[0])+20)]
                            if '-' in context and len(values) > 1:
                                # This might be a reference range, use first value before range
                                value = float(values[0])
                            
                            # Try to find unit
                            unit_pattern = r'(\d+(?:\.\d+)?)\s*([a-zA-Zµ/%]+)'
                            unit_match = re.search(unit_pattern, line)
                            unit = unit_match.group(2) if unit_match else "unknown"
                            
                            if canonical_name not in extracted:  # Avoid duplicates
                                extracted[canonical_name] = {
                                    "value": value,
                                    "unit": unit,
                                    "raw_match": (values[0], unit)
                                }
                                break
                        except ValueError:
                            continue
    
    return extracted

def extract_parameters_comprehensive(text: str) -> Dict:
    """
    Comprehensive extraction using multiple strategies.
    
    Args:
        text: OCR text from lab report
        
    Returns:
        dict: Extracted parameters with values and units
    """
    # Strategy 1: Flexible pattern matching
    results1 = extract_parameters_flexible(text)
    
    # Strategy 2: Table format extraction
    results2 = extract_with_table_format(text)
    
    # Merge results (prefer strategy 1 if both found same parameter)
    merged = {**results2, **results1}
    
    # Filter out false positives
    filtered = {}
    for param, data in merged.items():
        value = data['value']
        
        # Filter out unrealistic values that are likely from patient IDs or dates
        # Patient IDs often have large numbers like 10344, 772782820
        # Dates have numbers like 04, 08, 2025
        
        # Skip if value is too large (likely patient ID or accession number)
        if value > 10000 and param not in ['wbc', 'rbc', 'platelet']:
            continue
            
        # Skip very small values that are likely from dates (01-31)
        if value < 1 and param not in ['creatinine', 'bilirubin_total', 'bilirubin_direct', 'bilirubin_indirect']:
            continue
            
        # Skip if unit looks like it's from metadata (jaccession, rd, etc.)
        unit = data['unit'].lower()
        if any(word in unit for word in ['jaccession', 'patient', 'drawn', 'received', 'reported', 'code', 'address']):
            continue
            
        filtered[param] = data
    
    return filtered

if __name__ == "__main__":
    # Test with sample text
    test_text = """
    COMPLETE BLOOD COUNT (CBC)
    Hemoglobin 12.00 g/dL 13.00 - 17.00
    Packed Cell Volume (PCV) 37.70 % 40.00 - 50.00
    Total Leukocyte Count (TLC) 4.20 thou/mm3 4.00 - 10.00
    Platelet Count 150 thou/mm3 150.00 - 450.00
    
    LIVER FUNCTION TEST
    Bilirubin Total 2.00 mg/dL 0.30-1.20
    ALT (SGPT), SERUM 45 U/L 0-40
    """
    
    print("Testing Comprehensive Extraction:")
    print("=" * 80)
    results = extract_parameters_comprehensive(test_text)
    
    for param, data in results.items():
        print(f"{param:20} = {data['value']:8.2f} {data['unit']}")
    
    print(f"\nTotal parameters extracted: {len(results)}")
