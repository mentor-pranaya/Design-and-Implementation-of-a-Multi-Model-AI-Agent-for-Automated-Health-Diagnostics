"""
PDF Text Parser
Extracts structured blood parameters from OCR text
"""
import re
from typing import Dict


def parse_pdf_text(raw_text: str) -> Dict[str, str]:
    """
    Parse OCR text from PDF to extract blood parameters.
    
    Args:
        raw_text: Raw OCR text from PDF
        
    Returns:
        Dictionary of parameter names to values with units
    """
    parameters = {}
    
    print(f"\n{'='*70}")
    print("DEBUG: PDF Parsing Started")
    print(f"{'='*70}")
    
    # Split into lines
    lines = raw_text.split('\n')
    print(f"DEBUG: Total lines in PDF: {len(lines)}")
    
    # Parameter mapping with their expected patterns
    # Updated patterns to be more precise
    param_patterns = {
        'Free T4': r'FREE\s+T4.*?(\d+\.?\d*)\s+(ng/d[lL])',
        'TSH': r'TSH.*?(\d+\.?\d*)\s+(u?[IiLl]U/m[lL])',
        'FSH': r'FSH.*?(\d+\.?\d*)\s+(m[IiLl]U/m[lL])',
        'LH': r'LH.*?(\d+\.?\d*)\s+(m[IiLl]U/m[lL])',
        'Prolactin': r'PROLACTIN.*?(\d+\.?\d*)\s+(ng/m[lL])',
        'Testosterone Total': r'Testosterone.*?Total.*?(\d+\.?\d*)\s+(ng/m[lL])',
    }
    
    # Join all lines for easier pattern matching
    full_text = ' '.join(lines)
    
    # Also try line-by-line parsing for better accuracy
    for line in lines:
        # Try to match FREE T4 with more precision
        if 'FREE T4' in line.upper() or 'FREE-T4' in line.upper():
            # Look for pattern: FREE T4 <value> ng/dL
            # More specific: look for decimal number followed by ng/dL
            match = re.search(r'FREE[\s\-]*T4.*?(\d+\.\d+)\s*(ng/d[lL])', line, re.IGNORECASE)
            if match:
                value = match.group(1)
                unit = match.group(2)
                parameters['Free T4'] = f"{value} {unit}"
                print(f"DEBUG: Extracted Free T4 from line: {line.strip()}")
                print(f"DEBUG: Free T4 = {value} {unit}")
                continue
        
        # Try to match TSH
        if 'TSH' in line.upper() and 'FREE' not in line.upper():
            match = re.search(r'(\d+\.?\d*)\s+(u?[IiLl]U/m[lL])', line)
            if match:
                value = match.group(1)
                unit = match.group(2)
                parameters['TSH'] = f"{value} {unit}"
                continue
        
        # Try to match FSH
        if 'FSH' in line.upper() and 'TSH' not in line.upper():
            match = re.search(r'(\d+\.?\d*)\s+(m[IiLl]U/m[lL])', line)
            if match:
                value = match.group(1)
                unit = match.group(2)
                parameters['FSH'] = f"{value} {unit}"
                continue
        
        # Try to match LH
        if 'LH' in line.upper() and 'FSH' not in line.upper():
            match = re.search(r'(\d+\.?\d*)\s+(m[IiLl]U/m[lL])', line)
            if match:
                value = match.group(1)
                unit = match.group(2)
                parameters['LH'] = f"{value} {unit}"
                continue
        
        # Try to match Prolactin
        if 'PROLACTIN' in line.upper():
            match = re.search(r'(\d+\.?\d*)\s+(ng/m[lL])', line)
            if match:
                value = match.group(1)
                unit = match.group(2)
                parameters['Prolactin'] = f"{value} {unit}"
                continue
        
        # Try to match Testosterone Total
        if 'TESTOSTERONE' in line.upper() and 'TOTAL' in line.upper():
            match = re.search(r'(\d+\.?\d*)\s+(ng/m[lL])', line)
            if match:
                value = match.group(1)
                unit = match.group(2)
                parameters['Testosterone Total'] = f"{value} {unit}"
                continue
    
    # Fallback to full text patterns if line-by-line didn't work
    for param_name, pattern in param_patterns.items():
        if param_name not in parameters:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                value = match.group(1)
                unit = match.group(2)
                
                # Standardize unit format
                unit = unit.replace('d', 'd').replace('L', 'L').replace('l', 'L')
                
                parameters[param_name] = f"{value} {unit}"
    
    print(f"\n{'='*70}")
    print(f"DEBUG: Extracted {len(parameters)} parameters:")
    for param, val in parameters.items():
        print(f"  {param}: {val}")
    print(f"{'='*70}\n")
    
    return parameters


def clean_parameter_name(name: str) -> str:
    """Clean up parameter name."""
    # Standardize common variations
    name = name.upper().strip()
    
    # Map variations to standard names (matching ABIM reference ranges)
    mappings = {
        'FREE T4': 'Free T4',
        'FREE-T4': 'Free T4',
        'T4': 'Free T4',
        'TSH': 'TSH',
        'FSH': 'FSH',
        'LH': 'LH',
        'PROLACTIN': 'Prolactin',
        'TESTOSTERONE': 'Testosterone Total',
        'TESTOSTERONE TOTAL': 'Testosterone Total',
        'TESTOSTERONE, TOTAL': 'Testosterone Total',
        'HEMOGLOBIN': 'Hemoglobin',
        'GLUCOSE': 'Glucose',
        'HBA1C': 'HbA1c',
        'CHOLESTEROL': 'Total Cholesterol',
        'TOTAL CHOLESTEROL': 'Total Cholesterol',
        'LDL': 'LDL',
        'HDL': 'HDL',
        'TRIGLYCERIDES': 'Triglycerides',
        'CREATININE': 'Creatinine',
        'BUN': 'BUN',
        'ALT': 'ALT',
        'AST': 'AST',
        'PLATELET COUNT': 'Platelets',
        'PLATELETS': 'Platelets',
        'WBC': 'WBC',
        'RBC': 'RBC'
    }
    
    return mappings.get(name, name.title())


def extract_patient_info(raw_text: str) -> Dict[str, str]:
    """Extract patient information from OCR text."""
    info = {}
    
    # Extract age and sex
    age_match = re.search(r'Age\s*[:/]?\s*(\d+)\s*Y', raw_text, re.IGNORECASE)
    if age_match:
        info['age'] = age_match.group(1)
    
    sex_match = re.search(r'Sex\s*[:/]?\s*(Male|Female|M|F)', raw_text, re.IGNORECASE)
    if sex_match:
        sex = sex_match.group(1).upper()
        info['sex'] = 'M' if sex.startswith('M') else 'F'
    
    # Extract dates
    date_match = re.search(r'Collected Date\s*[:/]?\s*(\d{2}/\d{2}/\d{4})', raw_text)
    if date_match:
        info['collected_date'] = date_match.group(1)
    
    return info
