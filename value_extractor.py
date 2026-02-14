import re

# Matches numbers like: 110, 12.5, 7.8
VALUE_PATTERN = re.compile(r"(-?\d+(\.\d+)?)")

def extract_numeric_value(text: str):
    """
    Extracts the first numeric value found in a line.
    Returns (value, unit_text) — unit_text may be None.
    """
    match = VALUE_PATTERN.search(text)
    if not match:
        return None, None

    value = float(match.group(1))
    return value, None
