"""
OCR Text Cleaning and Normalization Module.

Handles common OCR mistakes, unit normalization, and text cleaning
to improve downstream parameter extraction accuracy.
"""

import re
import logging
from typing import Tuple, Dict, List, Optional

logger = logging.getLogger(__name__)


# Common OCR character misrecognitions
OCR_CORRECTIONS = {
    # O→0 (letter O to digit 0)
    'O': '0',  # Will be applied selectively in context
    # l→1 (lowercase L to digit 1)
    '|': '1',  # pipe to 1
    'l': '1',  # lowercase L to 1 (context-sensitive)
    # S→5
    'S': '5',  # Will be applied selectively
    # I→1 (capital I to 1)
    'I': '1',  # Capital I to 1 (context-sensitive)
    # Z→2
    'Z': '2',
    # B→8
    'B': '8',  # Will be applied selectively
}

# Common unit variations and normalization mappings
UNIT_NORMALIZATIONS = {
    # Glucose/Sugar units
    'mg/dl': 'mg/dL',
    'mg/dL': 'mg/dL',
    'mg/	dl': 'mg/dL',  # Tab character
    'mg dl': 'mg/dL',
    'mgdl': 'mg/dL',
    'mg/100ml': 'mg/dL',
    
    # Hemoglobin units
    'g/dl': 'g/dL',
    'g/dL': 'g/dL',
    'gm/dl': 'g/dL',
    'gm/dL': 'g/dL',
    'g%': 'g/dL',
    'gm%': 'g/dL',
    
    # Red Blood Cells
    '10^6/ul': 'million/µL',
    '10^6/µl': 'million/µL',
    'million/ul': 'million/µL',
    'million/µl': 'million/µL',
    'm/ul': 'million/µL',
    'm/µl': 'million/µL',
    
    # White Blood Cells
    '10^3/ul': 'thousand/µL',
    '10^3/µl': 'thousand/µL',
    'thousand/ul': 'thousand/µL',
    'thousand/µl': 'thousand/µL',
    'k/ul': 'thousand/µL',
    'k/µl': 'thousand/µL',
    
    # Platelets
    '10^3/ul': 'thousand/µL',
    '10^3/µl': 'thousand/µL',
    
    # Cholesterol/Triglycerides
    'mg/dL': 'mg/dL',
    'mg/dl': 'mg/dL',
    
    # Creatinine
    'mg/dl': 'mg/dL',
    'mg/dL': 'mg/dL',
    'mg/100ml': 'mg/dL',
    
    # BUN (Blood Urea Nitrogen)
    'mg/dl': 'mg/dL',
    'mg/dL': 'mg/dL',
    
    # Electrolytes (mEq/L or mmol/L)
    'meq/l': 'mEq/L',
    'meq/L': 'mEq/L',
    'mmol/l': 'mmol/L',
    'mmol/L': 'mmol/L',
    
    # Blood Pressure
    'mmhg': 'mmHg',
    'mmHg': 'mmHg',
    'mm hg': 'mmHg',
    
    # Albumin/Protein
    'g/dl': 'g/dL',
    'gm/dl': 'g/dL',
}

# Unwanted symbols that should be removed
UNWANTED_SYMBOLS = [
    r'[•·‣◦▪▸]',  # Bullet points
    r'[©®™]',     # Copyright/trademark symbols
    r'[""„"‟]',   # Fancy quotes
    r'[—–−]',     # Dashes beyond hyphen
    r'[\x00-\x08\x0B\x0C\x0E-\x1F]',  # Control characters
]


def _correct_ocr_character(char: str, context: str = "") -> str:
    """
    Correct a single OCR character based on context.
    
    Args:
        char: Character to correct
        context: Surrounding context for intelligent correction
    
    Returns:
        Corrected character or original if uncertain
    """
    if char == '|':
        return '1'
    if char == 'l' and context.isdigit():
        # Convert lowercase L to 1 only if surrounded by digits
        return '1'
    if char == 'O' and context.replace('.', '').isdigit():
        # Convert O to 0 only if surrounded by digits
        return '0'
    if char == 'S' and context.replace('.', '').isdigit():
        # Convert S to 5 only if surrounded by digits
        return '5'
    if char == 'I' and context.replace('.', '').isdigit():
        # Convert I to 1 only if surrounded by digits
        return '1'
    if char == 'Z' and context.replace('.', '').isdigit():
        return '2'
    if char == 'B' and context.replace('.', '').isdigit():
        # Convert B to 8 only if surrounded by digits
        return '8'
    return char


def fix_ocr_mistakes(text: str) -> str:
    """
    Fix common OCR mistakes in text using context-aware corrections.
    
    Args:
        text: Raw OCR-extracted text
    
    Returns:
        Text with corrected spellings
    
    Examples:
        >>> fix_ocr_mistakes("Hemoglobin: l2.5 g/dl")
        "Hemoglobin: 12.5 g/dl"
    """
    # Find numeric patterns and fix OCR mistakes within them
    # Pattern: optional +/-, digits, optional decimal and more digits
    numeric_pattern = re.compile(r'[-+]?[\d\s.]+')
    
    result = []
    last_end = 0
    
    for match in numeric_pattern.finditer(text):
        # Add text before the match
        result.append(text[last_end:match.start()])
        
        # Process the numeric match
        numeric_text = match.group()
        corrected = ""
        for i, char in enumerate(numeric_text):
            # Get surrounding context
            context = numeric_text[max(0, i-1):i+2]
            corrected += _correct_ocr_character(char, context)
        
        result.append(corrected)
        last_end = match.end()
    
    result.append(text[last_end:])
    return "".join(result)


def normalize_units(text: str) -> str:
    """
    Normalize medical units to standard formats.
    
    Handles variations like mg/dl → mg/dL, mm hg → mmHg, etc.
    
    Args:
        text: Text potentially containing medical units
    
    Returns:
        Text with normalized units
    
    Examples:
        >>> normalize_units("Glucose: 110 mg/dl")
        "Glucose: 110 mg/dL"
    """
    result = text
    
    # Sort by length (longest first) to match longer patterns first
    for raw_unit, standard_unit in sorted(
        UNIT_NORMALIZATIONS.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):
        # Case-insensitive replacement
        pattern = re.compile(re.escape(raw_unit), re.IGNORECASE)
        result = pattern.sub(standard_unit, result)
    
    return result


def convert_to_lowercase(text: str) -> str:
    """
    Convert text to lowercase while preserving structure.
    
    Args:
        text: Input text
    
    Returns:
        Lowercase text
    """
    return text.lower()


def remove_unwanted_symbols(text: str) -> str:
    """
    Remove unwanted symbols (bullets, control chars, etc).
    
    Args:
        text: Input text
    
    Returns:
        Text with unwanted symbols removed
    """
    result = text
    for pattern in UNWANTED_SYMBOLS:
        result = re.sub(pattern, '', result)
    return result


def clean_whitespace(text: str) -> str:
    """
    Clean excessive whitespace but preserve line breaks.
    
    Args:
        text: Input text
    
    Returns:
        Text with normalized whitespace
    """
    # Replace tabs with spaces
    result = text.replace('\t', ' ')
    
    # Replace multiple spaces with single space
    result = re.sub(r' {2,}', ' ', result)
    
    # Remove leading/trailing whitespace from each line
    lines = result.split('\n')
    lines = [line.strip() for line in lines]
    
    # Remove empty lines
    lines = [line for line in lines if line]
    
    return '\n'.join(lines)


def extract_unit_from_value(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract numeric value and unit from text.
    
    Args:
        text: Text containing value and optional unit
    
    Returns:
        Tuple of (numeric_value_str, unit_str) or (None, None) if no match
    
    Examples:
        >>> extract_unit_from_value("8.5 g/dL")
        ('8.5', 'g/dL')
        >>> extract_unit_from_value("110mg/dL")
        ('110', 'mg/dL')
    """
    # Pattern: number followed by optional unit
    # e.g., "8.5 g/dL", "110mg/dL", "12.5", "7.8 g%"
    pattern = re.compile(
        r'([-+]?\d+\.?\d*)\s*([a-zA-Z%/°µ]+)?',
        re.IGNORECASE
    )
    
    match = pattern.search(text)
    if match:
        value = match.group(1)
        unit = match.group(2) if match.group(2) else None
        return value, unit
    
    return None, None


def clean_and_standardize(text: str) -> str:
    """
    Complete OCR cleaning and standardization pipeline.
    
    Applies all cleaning steps in optimal order:
    1. Fix common OCR mistakes
    2. Normalize units
    3. Remove unwanted symbols
    4. Clean whitespace
    5. Convert to lowercase
    
    Args:
        text: Raw OCR-extracted text
    
    Returns:
        Cleaned and standardized text
    
    Examples:
        >>> clean_and_standardize("Hemoglobin: l2.5 g/dl•")
        "hemoglobin: 12.5 g/dl"
    """
    logger.debug(f"Starting OCR cleaning. Original length: {len(text)}")
    
    # Step 1: Fix OCR mistakes
    text = fix_ocr_mistakes(text)
    logger.debug("Fixed OCR mistakes")
    
    # Step 2: Normalize units
    text = normalize_units(text)
    logger.debug("Normalized units")
    
    # Step 3: Remove unwanted symbols
    text = remove_unwanted_symbols(text)
    logger.debug("Removed unwanted symbols")
    
    # Step 4: Clean whitespace
    text = clean_whitespace(text)
    logger.debug("Cleaned whitespace")
    
    # Step 5: Convert to lowercase
    text = convert_to_lowercase(text)
    logger.debug(f"Converted to lowercase. Final length: {len(text)}")
    
    return text


# Public API
__all__ = [
    'clean_and_standardize',
    'fix_ocr_mistakes',
    'normalize_units',
    'extract_unit_from_value',
    'remove_unwanted_symbols',
    'clean_whitespace',
]
