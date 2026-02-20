"""
Production-Ready Phase 2 Structuring with Intelligent Parameter Detection.

Replaces the previous simple structuring with a robust pipeline that:
- Cleans OCR text
- Extracts parameters with fallback strategies
- Detects abnormalities
- Provides comprehensive logging
"""

import logging
import re
from typing import Dict, Any, Optional, List

# Import our new modules
from structuring_layers.ocr_cleaner import clean_and_standardize
from structuring_layers.medical_parameter_extractor import (
    extract_all_parameters,
    validate_extracted_parameters,
)
from structuring_layers.reference_ranges import (
    get_abnormal_findings,
)

# Import existing dependencies
from structuring_layers.test_dictionary import TEST_ALIASES
from structuring_layers.unit_normalizer import normalize_unit
from structuring_layers.bp_extractor import extract_blood_pressure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def structure_report(plain_text: str) -> Dict[str, Any]:
    """
    Production-ready structuring pipeline with intelligent parameter detection.
    
    Process:
    1. Clean and standardize OCR text
    2. Extract parameters with fallback logic
    3. Detect abnormalities using reference ranges
    4. Structure output consistently
    
    Args:
        plain_text: Raw OCR-extracted text
    
    Returns:
        Structured output with:
        - categories: biochemistry, hematology, vitals (preserved for compatibility)
        - test results structured by category
        - key_abnormalities: List of abnormal findings
        - extraction_log: Metadata about extraction process
    """
    
    if not plain_text or not plain_text.strip():
        logger.warning("Empty input text provided to structuring")
        return {
            'vitals': {},
            'biochemistry': {},
            'hematology': {},
            'key_abnormalities': [],
        }
    
    extraction_log = {
        'status': 'success',
        'tests_found': 0,
        'abnormalities_found': 0,
    }
    
    try:
        # Step 1: Clean OCR text
        logger.info("Step 1: Cleaning OCR text")
        cleaned_text = clean_and_standardize(plain_text)
        logger.debug(f"Cleaned text length: {len(cleaned_text)}")
        
        # Step 2: Build flattened alias dictionary for parameter extraction
        flattened_aliases = {}
        for category, tests in TEST_ALIASES.items():
            for test_name, aliases in tests.items():
                flattened_aliases[test_name] = aliases
        
        # Step 3: Extract parameters with our new extractor
        logger.info("Step 2: Extracting medical parameters")
        raw_parameters = extract_all_parameters(cleaned_text, flattened_aliases)
        extraction_log['tests_found'] = len(raw_parameters)
        
        # Step 4: Structure output by category
        logger.info("Step 3: Organizing parameters by category")
        structured_output = {}
        normalized_params = {}
        
        for test_name, param_data in raw_parameters.items():
            # Find category for this test
            category = None
            for cat, tests in TEST_ALIASES.items():
                if test_name in tests:
                    category = cat
                    break
            
            if not category:
                logger.warning(f"Test '{test_name}' not found in TEST_ALIASES categories")
                continue
            
            # Normalize unit
            value = param_data.get('value')
            raw_unit = param_data.get('unit')
            normalized_unit = normalize_unit(test_name, raw_unit)
            
            # Store in structured format
            if category not in structured_output:
                structured_output[category] = {}
            
            structured_output[category][test_name] = {
                'value': value,
                'unit': normalized_unit,
                'raw_text': param_data.get('raw_text', ''),
            }
            
            normalized_params[test_name] = {
                'value': value,
                'unit': normalized_unit,
            }
        
        # Step 5: Detect abnormalities using reference ranges
        logger.info("Step 4: Detecting abnormalities")
        key_abnormalities = get_abnormal_findings(normalized_params)
        extraction_log['abnormalities_found'] = len(key_abnormalities)
        
        if key_abnormalities:
            logger.info(f"Found {len(key_abnormalities)} abnormalities")
            for abnormality in key_abnormalities:
                logger.info(
                    f"  - {abnormality['test_name']}: {abnormality['value']} "
                    f"({abnormality['risk_level']})"
                )
        
        # Step 6: Handle special case - Blood Pressure
        logger.info("Step 5: Extracting special parameters (blood pressure)")
        bp_data = _extract_blood_pressure_with_fallback(cleaned_text)
        if bp_data:
            if 'vitals' not in structured_output:
                structured_output['vitals'] = {}
            structured_output['vitals']['blood_pressure'] = bp_data
            logger.info(f"Extracted blood pressure: {bp_data}")
        
        # Ensure all categories exist
        for category in ['vitals', 'biochemistry', 'hematology']:
            if category not in structured_output:
                structured_output[category] = {}
        
        result = {
            **structured_output,
            'key_abnormalities': key_abnormalities,
            'extraction_log': extraction_log,
        }
        
        logger.info(f"Extraction completed: {extraction_log['tests_found']} tests, "
                   f"{extraction_log['abnormalities_found']} abnormalities")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during structuring: {str(e)}", exc_info=True)
        return {
            'vitals': {},
            'biochemistry': {},
            'hematology': {},
            'key_abnormalities': [],
            'extraction_log': {'status': 'error', 'error': str(e)},
        }


def _extract_blood_pressure_with_fallback(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract blood pressure with fallback strategies.
    
    Strategy:
    1. Try the existing extract_blood_pressure function
    2. If fails, attempt manual regex extraction
    """
    try:
        # Strategy 1: Use existing function
        bp_data = extract_blood_pressure(text)
        if bp_data:
            return bp_data
    except Exception as e:
        logger.debug(f"extract_blood_pressure raised: {e}, trying manual extraction")
    
    try:
        # Strategy 2: Manual fallback
        bp_pattern = re.compile(
            r'(\d{2,3})\s*[/\-]\s*(\d{2,3})',
            re.IGNORECASE
        )
        
        match = bp_pattern.search(text.lower())
        if match:
            systolic = int(match.group(1))
            diastolic = int(match.group(2))
            
            # Sanity check
            if 70 <= systolic <= 250 and 30 <= diastolic <= 150:
                return {
                    'systolic': systolic,
                    'diastolic': diastolic,
                    'unit': 'mmHg',
                    'raw_text': match.group(0),
                }
    except Exception as e:
        logger.debug(f"Manual blood pressure extraction failed: {e}")
    
    return None


# Test and demonstration
if __name__ == "__main__":
    sample_text = """
    Hemoglobin: 12.8 g/dL
    WBC: 7.2 thousand/µL
    RBC: 4.8 million/µL
    Platelets: 245 thousand/µL
    
    Fasting Blood Sugar: 110 mg/dL
    Total Cholesterol: 210 mg/dL
    HDL: 38 mg/dL
    LDL: 140 mg/dL
    Triglycerides: 150 mg/dL
    
    Creatinine: 1.2 mg/dL
    
    Blood Pressure: 128/82 mmHg
    """
    
    print("=== Structuring Report v2 ===\n")
    result = structure_report(sample_text)
    
    import json
    print(json.dumps(result, indent=2, default=str))
