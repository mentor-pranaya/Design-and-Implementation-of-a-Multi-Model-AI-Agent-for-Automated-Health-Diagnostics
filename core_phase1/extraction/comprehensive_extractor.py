"""
Comprehensive Parameter Extraction Module
Handles multiple lab report formats with flexible pattern matching
"""
import re
from typing import Dict, List, Optional

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
    "tsh": ["tsh", "thyroid stimulating hormone", "tsh 3rd generation"],
    "t3": ["t3", "triiodothyronine"],
    "t4": ["t4", "thyroxine"],
    "hba1c": ["hba1c", "hb a1c", "glycated hemoglobin", "glycosylated hemoglobin"],
    "neutrophils": ["neutrophil", "neutrophils", "segmented neutrophils", "polymorphs"],
    "lymphocytes": ["lymphocyte", "lymphocytes"],
    "monocytes": ["monocyte", "monocytes"],
    "eosinophils": ["eosinophil", "eosinophils"],
    "basophils": ["basophil", "basophils"],
}

# Value ranges for validation (to filter false positives)
VALUE_RANGES = {
    "hemoglobin": (3.0, 25.0),
    "glucose": (30.0, 600.0),
    "creatinine": (0.1, 15.0),
    "cholesterol": (50.0, 500.0),
    "triglycerides": (20.0, 1000.0),
    "hdl": (10.0, 150.0),
    "ldl": (10.0, 300.0),
    "wbc": (0.5, 50.0),
    "rbc": (1.0, 10.0),
    "platelet": (10.0, 1000.0),
    "hematocrit": (10.0, 70.0),
    "mcv": (50.0, 120.0),
    "mch": (15.0, 50.0),
    "mchc": (20.0, 40.0),
    "rdw": (10.0, 25.0),
    "alt": (0.0, 1000.0),
    "ast": (0.0, 1000.0),
    "alp": (0.0, 1000.0),
    "ggt": (0.0, 500.0),
    "bilirubin_total": (0.0, 30.0),
    "bilirubin_direct": (0.0, 15.0),
    "bilirubin_indirect": (0.0, 20.0),
    "albumin": (1.0, 6.0),
    "protein_total": (3.0, 10.0),
    "globulin": (1.0, 6.0),
    "urea": (5.0, 200.0),
    "bun": (2.0, 100.0),
    "sodium": (100.0, 200.0),
    "potassium": (2.0, 8.0),
    "chloride": (70.0, 130.0),
    "calcium": (5.0, 15.0),
    "phosphorus": (1.0, 10.0),
    "magnesium": (0.5, 5.0),
    "tsh": (0.01, 100.0),
    "t3": (0.5, 500.0),
    "t4": (0.5, 30.0),
    "hba1c": (3.0, 20.0),
    "neutrophils": (0.0, 100.0),
    "lymphocytes": (0.0, 100.0),
    "monocytes": (0.0, 100.0),
    "eosinophils": (0.0, 100.0),
    "basophils": (0.0, 100.0),
}

def build_flexible_pattern(param_aliases: List[str]) -> str:
    """Build a flexible regex pattern for parameter extraction."""
    aliases_pattern = "|".join(re.escape(alias) for alias in param_aliases)
    
    pattern = rf"""
        (?:{aliases_pattern})           # Parameter name
        \s*                              # Optional whitespace
        (?:\([^\)]*\))?                  # Optional parenthetical
        \s*                              # Optional whitespace
        (?::|=|result)?                  # Optional separator
        \s*                              # Optional whitespace
        (?:result)?                      # Optional "result" keyword
        \s*                              # Optional whitespace
        (?P<value>-?\d+(?:\.\d+)?)      # Numeric value
        \s*                              # Optional whitespace
        (?P<unit>[a-zA-Z/%µ]+)?         # Optional unit
    """
    
    return pattern

def is_valid_value(param_name: str, value: float) -> bool:
    """Check if extracted value is within reasonable range for the parameter."""
    if param_name not in VALUE_RANGES:
        return True  # No range defined, accept it
    
    min_val, max_val = VALUE_RANGES[param_name]
    return min_val <= value <= max_val

def extract_parameters_flexible(text: str) -> Dict:
    """
    Extract parameters using flexible patterns.
    
    Args:
        text: OCR text from lab report
        
    Returns:
        dict: {parameter_name: {"value": float, "unit": str, "raw_match": tuple}}
    """
    extracted = {}
    text_lower = text.lower()
    
    for canonical_name, aliases in PARAMETER_ALIASES.items():
        pattern = build_flexible_pattern(aliases)
        
        # Find all matches
        matches = list(re.finditer(pattern, text_lower, re.VERBOSE | re.IGNORECASE))
        
        if not matches:
            continue
        
        # Use the first match
        match = matches[0]
        
        try:
            value = float(match.group("value"))
            
            # Validate value is in reasonable range
            if not is_valid_value(canonical_name, value):
                continue
            
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
    """Extract parameters from table-formatted reports."""
    extracted = {}
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        for canonical_name, aliases in PARAMETER_ALIASES.items():
            for alias in aliases:
                if alias in line_lower:
                    # Extract numeric values from line
                    value_pattern = r'\b(\d+(?:\.\d+)?)\b'
                    values = re.findall(value_pattern, line)
                    
                    if values:
                        try:
                            value = float(values[0])
                            
                            # Validate value
                            if not is_valid_value(canonical_name, value):
                                continue
                            
                            # Extract unit
                            unit_pattern = r'(\d+(?:\.\d+)?)\s*([a-zA-Z/%µ]+)'
                            unit_match = re.search(unit_pattern, line)
                            unit = unit_match.group(2) if unit_match else "unknown"
                            
                            if canonical_name not in extracted:
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
    
    # Merge results (prefer strategy 1)
    merged = {**results2, **results1}
    
    return merged
