"""
Robust Medical Parameter Extraction with Fuzzy Matching.

Extracts medical test parameters from raw text with flexible matching,
fallback strategies, and comprehensive error handling.
"""

import re
import logging
from typing import Dict, Tuple, Optional, List, Any
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


def fuzzy_match(text: str, candidates: List[str], threshold: float = 0.7) -> Optional[str]:
    """
    Find best fuzzy match from candidates.
    
    Uses SequenceMatcher from difflib for flexible string matching.
    Useful for matching test names with OCR errors or spacing variations.
    
    Args:
        text: Text to match
        candidates: List of candidate strings to match against
        threshold: Minimum similarity ratio (0.0 to 1.0)
    
    Returns:
        Best matching candidate or None if no match above threshold
    
    Examples:
        >>> fuzzy_match("hemoglobin", ["hemoglobin", "wbc", "rbc"])
        'hemoglobin'
        >>> fuzzy_match("hmogobin", ["hemoglobin", "wbc"], threshold=0.7)
        'hemoglobin'
    """
    text_lower = text.lower().strip()
    best_match = None
    best_ratio = threshold
    
    for candidate in candidates:
        candidate_lower = candidate.lower().strip()
        ratio = SequenceMatcher(None, text_lower, candidate_lower).ratio()
        
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = candidate
    
    if best_match:
        logger.debug(f"Fuzzy matched '{text}' to '{best_match}' (ratio: {best_ratio:.2f})")
    
    return best_match


def extract_numeric_value_safe(text: str) -> Optional[float]:
    """
    Safely extract first numeric value from text.
    
    Handles:
    - Integers: 110
    - Decimals: 8.5, 12.75
    - Signed: -5, +120 (for edge cases)
    - Whitespace variations
    
    Args:
        text: Text potentially containing numeric value
    
    Returns:
        Numeric value as float or None if not found
    
    Examples:
        >>> extract_numeric_value_safe("Hb: 8.5 g/dL")
        8.5
        >>> extract_numeric_value_safe("WBC - 7.2 thousand")
        7.2
    """
    # Pattern: optional sign, digits, optional decimal and more digits
    pattern = re.compile(r'[-+]?\d+\.?\d*')
    match = pattern.search(text)
    
    if match:
        try:
            value = float(match.group())
            logger.debug(f"Extracted value {value} from '{text}'")
            return value
        except ValueError:
            logger.warning(f"Failed to convert '{match.group()}' to float")
            return None
    
    logger.debug(f"No numeric value found in '{text}'")
    return None


def extract_unit_safe(text: str) -> Optional[str]:
    """
    Safely extract unit designation from text.
    
    Handles:
    - Standard units: g/dL, mg/dL, mmHg, mEq/L
    - With/without spaces: "g/dL", "g /dL", "g/ dL"
    - Abbreviated: g%, gm%, mg/100ml
    
    Args:
        text: Text potentially containing unit
    
    Returns:
        Unit string or None if not found
    
    Examples:
        >>> extract_unit_safe("8.5 g/dL")
        'g/dL'
        >>> extract_unit_safe("110mg/dL")
        'mg/dL'
    """
    # Remove numeric values first to avoid confusion
    text_no_nums = re.sub(r'[-+]?\d+\.?\d*', '', text)
    
    # Pattern for unit: letters, %, /, superscripts, µ, etc.
    unit_pattern = re.compile(
        r'([a-zA-Z%/°µ]+(?:\s*[/°]\s*[a-zA-Z%]+)*)',
        re.IGNORECASE
    )
    
    match = unit_pattern.search(text_no_nums)
    if match:
        unit = match.group(1).strip()
        # Normalize internal spaces
        unit = re.sub(r'\s+', '', unit)
        if unit:
            logger.debug(f"Extracted unit '{unit}' from '{text}'")
            return unit
    
    logger.debug(f"No unit found in '{text}'")
    return None


def parse_test_line(
    line: str,
    test_aliases: Dict[str, List[str]],
) -> Tuple[Optional[str], Optional[float], Optional[str]]:
    """
    Parse a single line to extract test name, value, and unit.
    
    Strategy:
    1. Try exact alias match
    2. If fails, try fuzzy match against all aliases
    3. Extract numeric value
    4. Extract unit
    
    Args:
        line: Raw text line from OCR
        test_aliases: {test_name: [alias1, alias2, ...]}
    
    Returns:
        (test_name, value, unit) with None for missing components
    
    Examples:
        >>> aliases = {'hemoglobin': ['hemoglobin', 'hb', 'hgb']}
        >>> parse_test_line("Hb: 8.5 g/dL", aliases)
        ('hemoglobin', 8.5, 'g/dL')
    """
    line_lower = line.lower()
    
    # Strategy 1: Exact alias match
    matched_test = None
    for test_name, aliases in test_aliases.items():
        if any(alias in line_lower for alias in aliases):
            matched_test = test_name
            break
    
    # Strategy 2: Fuzzy match if exact failed
    if not matched_test:
        all_aliases = []
        for aliases in test_aliases.values():
            all_aliases.extend(aliases)
        
        # Try to find any word in the line that matches an alias
        words = re.findall(r'\b\w+\b', line_lower)
        for word in words:
            fuzzy = fuzzy_match(word, all_aliases, threshold=0.7)
            if fuzzy:
                # Find which test this alias belongs to
                for test_name, aliases in test_aliases.items():
                    if fuzzy in aliases:
                        matched_test = test_name
                        break
            if matched_test:
                break
    
    # Extract numeric value
    value = extract_numeric_value_safe(line)
    
    # Extract unit
    unit = extract_unit_safe(line)
    
    if matched_test:
        logger.debug(f"Parsed line: test='{matched_test}', value={value}, unit='{unit}'")
    
    return matched_test, value, unit


def extract_all_parameters(
    text: str,
    test_aliases: Dict[str, List[str]],
) -> Dict[str, Dict[str, Any]]:
    """
    Extract all medical parameters from text.
    
    Process:
    1. Split text into lines
    2. Parse each line with fallback strategies
    3. Group by test category (biochemistry, hematology, vitals, etc.)
    
    Args:
        text: Raw OCR text
        test_aliases: Test name aliases mapping
    
    Returns:
        Dictionary structure: {test_name: {value, unit, raw_text, ...}}
    """
    results = {}
    lines = text.split('\n')
    
    logger.info(f"Starting parameter extraction from {len(lines)} lines")
    
    for line in lines:
        if not line.strip():
            continue
        
        test_name, value, unit = parse_test_line(line, test_aliases)
        
        if test_name and value is not None:
            results[test_name] = {
                'value': value,
                'unit': unit,
                'raw_text': line.strip(),
                'extraction_method': 'regex'
            }
            logger.info(f"Extracted: {test_name}={value} {unit or '(no unit)'}")
        elif test_name and value is None:
            # Test name matched but value extraction failed
            logger.warning(
                f"Test '{test_name}' matched but no value found in: '{line}'"
            )
    
    logger.info(f"Extracted {len(results)} parameters total")
    return results


def validate_extracted_parameters(
    parameters: Dict[str, Dict[str, Any]],
    valid_ranges: Optional[Dict[str, Tuple[float, float]]] = None,
) -> Dict[str, Any]:
    """
    Validate extracted parameters for sanity and medical plausibility.
    
    Args:
        parameters: Extracted parameters
        valid_ranges: Optional {test_name: (min, max)} for validation
    
    Returns:
        Validation report with counts and any issues found
    """
    valid_ranges = valid_ranges or {}
    report = {
        'total_extracted': len(parameters),
        'valid': 0,
        'warnings': [],
        'parameters': {}
    }
    
    for test_name, data in parameters.items():
        value = data.get('value')
        status = 'valid'
        warning = None
        
        if value is not None:
            # Check if value is in plausible range
            if test_name in valid_ranges:
                min_val, max_val = valid_ranges[test_name]
                if not (min_val <= value <= max_val):
                    status = 'warning'
                    warning = f"Value {value} outside expected range ({min_val}-{max_val})"
            
            # Check for obviously impossible values
            if value < 0:
                status = 'warning'
                warning = "Negative value"
            elif value > 10000:
                status = 'warning'
                warning = "Suspiciously high value"
        
        if status == 'valid':
            report['valid'] += 1
        else:
            if warning:
                report['warnings'].append({
                    'test': test_name,
                    'value': value,
                    'issue': warning
                })
        
        report['parameters'][test_name] = {
            'status': status,
            **data
        }
    
    return report


# Public API
__all__ = [
    'fuzzy_match',
    'extract_numeric_value_safe',
    'extract_unit_safe',
    'parse_test_line',
    'extract_all_parameters',
    'validate_extracted_parameters',
]
