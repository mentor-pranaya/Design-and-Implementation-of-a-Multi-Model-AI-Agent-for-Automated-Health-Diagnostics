import re

def extract_data(raw_text):
    """
    Identifies and extracts medical parameters, values, units, and ranges 
    from raw OCR text using robust pattern matching.
    """
    # Updated Regex breakdown:
    # 1. ([a-zA-Z\s\(\)]+?): Matches parameter names (non-greedy)
    # 2. [: \t]*: Optional colon or tab separators
    # 3. (\d*\.?\d+): Matches the numerical value (integer or decimal)
    # 4. \s*([a-zA-Z/%10\^/]+)?: Matches units (optional, handles %, 10^3, etc.)
    # 5. [^0-9]*: Skip any non-numeric brackets or separators
    # 6. (\d+\.?\d*\s*[-–—]\s*\d+\.?\d*): Matches the reference range
    
    pattern = r"([a-zA-Z\s\(\)]+?)[: \t]*(\d*\.?\d+)\s*([a-zA-Z/%10\^/]+)?\s*[\(\[]?(\d+\.?\d*\s*[-–—]\s*\d+\.?\d*)[\)\]]?"
    
    matches = re.finditer(pattern, raw_text)
    extracted = []
    
    for match in matches:
        try:
            # Clean up the extracted strings
            parameter_name = match.group(1).strip()
            
            # Basic validation: ensure the parameter isn't just whitespace or a single char
            if len(parameter_name) < 2:
                continue
                
            extracted.append({
                "parameter": parameter_name,
                "value": float(match.group(2)),
                "unit": match.group(3).strip() if match.group(3) else "unit",
                "range": match.group(4).replace(" ", "") if match.group(4) else "N/A"
            })
        except (ValueError, IndexError):
            # Skip any matches that fail float conversion or grouping
            continue
            
    return extracted
