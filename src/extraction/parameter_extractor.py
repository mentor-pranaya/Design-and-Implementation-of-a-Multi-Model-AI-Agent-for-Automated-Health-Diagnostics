import re
from src.extraction.medical_schema import MEDICAL_SCHEMA

def extract_parameters_from_text(text: str) -> dict:
    """
    Extract medical parameters from text using improved regex patterns.
    Handles various number formats and units.
    """
    text = text.lower()
    extracted = {}

    for parameter, aliases in MEDICAL_SCHEMA.items():
        for alias in aliases:
            # Improved regex: matches numbers with optional decimal places
            # Supports formats like: 12.5, 12, 12.50, 1,234.56
            # Improved regex: matches numbers with optional decimal places
            # Supports formats like: 12.5, 12, 12.50, 1,234.56
            # Handles optional colon, spaces, tabs
            # Try specific pattern with colon first
            pattern_strict = rf"(?:\b|^){alias}\s*[:=\-]\s*([0-9]{{1,3}}(?:,[0-9]{{3}})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)"
            match = re.search(pattern_strict, text)
            
            if not match:
                # Try lax pattern without colon (but ensure boundary)
                pattern_lax = rf"(?:\b|^){alias}\s+([0-9]{{1,3}}(?:,[0-9]{{3}})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)(?:\s|$)"
                match = re.search(pattern_lax, text)
            if match:
                try:
                    value_str = match.group(1)
                    # Remove commas from numbers like 1,234
                    value_str = value_str.replace(',', '')
                    extracted[parameter] = float(value_str)
                    break
                except ValueError:
                    # Skip invalid number formats
                    continue

    return extracted
