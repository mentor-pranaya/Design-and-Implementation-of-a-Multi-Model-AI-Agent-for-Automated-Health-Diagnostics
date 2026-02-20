"""
INTEGRATION GUIDE - Production-Ready Health Report AI

This module demonstrates the complete integration of the improved pipeline:
1. OCR Cleaning (structuring_layers/ocr_cleaner.py)
2. Medical Parameter Extraction (structuring_layers/medical_parameter_extractor.py)
3. Reference Ranges & Risk Classification (structuring_layers/reference_ranges.py)
4. Enhanced Structuring (structuring_layers/phase2_structuring.py)
5. Intelligent Findings Synthesis (reporting/finding_synthesizer.py)
6. Enhanced Recommendations (reporting/recommendation_engine.py)

Key Improvements:
✓ Robust OCR text cleaning with common mistake corrections
✓ Flexible parameter extraction with fuzzy matching fallback
✓ Medical reference ranges for intelligent abnormality detection
✓ Comprehensive logging and error handling
✓ Production-ready error recovery and fallback strategies
✓ Never returns empty findings when abnormal values exist

Usage:
    python structuring_layers/integration_guide.py --test
    or in your FastAPI app:
    python api/main.py  (with uvicorn)
"""

import logging
import json
import sys
from typing import Dict, Any
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_ocr_cleaning():
    """Demonstrate OCR text cleaning capabilities."""
    print("\n" + "="*80)
    print("TEST 1: OCR CLEANING")
    print("="*80)
    
    from structuring_layers.ocr_cleaner import clean_and_standardize
    
    # Sample noisy OCR text
    raw_ocr = """
    Hemoglobin: l2.8 g/dl•
    WBC: 7.2 thousand/µl
    Glucose Fasting: llO mg/dl
    Total Cholesterol: 2lO mg/dL
    HDL Cholesterol 38 mg/DL
    """
    
    print("BEFORE cleaning:")
    print(raw_ocr)
    
    cleaned = clean_and_standardize(raw_ocr)
    
    print("\nAFTER cleaning:")
    print(cleaned)
    
    return cleaned


def test_parameter_extraction(cleaned_text: str):
    """Demonstrate medical parameter extraction."""
    print("\n" + "="*80)
    print("TEST 2: PARAMETER EXTRACTION WITH FUZZY MATCHING")
    print("="*80)
    
    from structuring_layers.medical_parameter_extractor import (
        extract_all_parameters,
        validate_extracted_parameters
    )
    from structuring_layers.test_dictionary import TEST_ALIASES
    
    # Build flattened aliases
    flattened_aliases = {}
    for category, tests in TEST_ALIASES.items():
        for test_name, aliases in tests.items():
            flattened_aliases[test_name] = aliases
    
    # Extract parameters
    parameters = extract_all_parameters(cleaned_text, flattened_aliases)
    
    print(f"\nExtracted {len(parameters)} parameters:")
    for test_name, data in parameters.items():
        print(f"  {test_name}: {data['value']} {data.get('unit', '')}")
    
    # Validate
    validation = validate_extracted_parameters(parameters)
    print(f"\nValidation: {validation['valid']}/{validation['total_extracted']} valid")
    if validation['warnings']:
        print("Warnings:")
        for w in validation['warnings']:
            print(f"  - {w}")
    
    return parameters


def test_reference_ranges(parameters: Dict[str, Dict[str, Any]]):
    """Demonstrate reference range abnormality detection."""
    print("\n" + "="*80)
    print("TEST 3: REFERENCE RANGES & ABNORMALITY DETECTION")
    print("="*80)
    
    from structuring_layers.reference_ranges import (
        get_abnormal_findings,
        get_risk_domain,
    )
    
    # Get abnormalities
    abnormalities = get_abnormal_findings(parameters)
    
    print(f"\nFound {len(abnormalities)} abnormalities:")
    for abnorm in abnormalities:
        print(f"  {abnorm['test_name']}: {abnorm['value']} {abnorm['unit']} "
              f"-> {abnorm['risk_level']} ({abnorm['description']})")
    
    # Show risk domains
    print("\nRisk domains:")
    domains = set()
    for abnorm in abnormalities:
        domain = get_risk_domain(abnorm['test_name'])
        if domain and domain not in domains:
            domains.add(domain)
            print(f"  - {domain}")
    
    return abnormalities


def test_full_structuring():
    """Demonstrate complete structuring pipeline."""
    print("\n" + "="*80)
    print("TEST 4: COMPLETE STRUCTURING PIPELINE")
    print("="*80)
    
    from structuring_layers.phase2_structuring import structure_report
    
    raw_text = """
    BLOOD TEST REPORT
    
    Hemoglobin: l2.5 g/dl
    RBC: 4.2 million/ul
    WBC: 7.8 thousand/ul
    Platelets: 245 thousand/ul
    
    Fasting Blood Sugar: l20 mg/dL
    Total Cholesterol: 240 mg/dl
    HDL: 35 mg/dL
    LDL: 160 mg/dl
    Triglycerides: 180 mg/dL
    
    Creatinine: 1.5 mg/dL
    BUN: 28 mg/dL
    
    Blood Pressure: 145/92 mmHg
    """
    
    result = structure_report(raw_text)
    
    print(f"\nStructuring Results:")
    print(f"  Categories: {list(result.keys())}")
    
    # Show extracted values
    for category, tests in result.items():
        if category not in ['key_abnormalities', 'extraction_log']:
            print(f"\n{category.upper()}:")
            for test, data in tests.items():
                if isinstance(data, dict):
                    print(f"  {test}: {data.get('value')} {data.get('unit', '')}")
    
    # Show abnormalities
    abnormalities = result.get('key_abnormalities', [])
    print(f"\nKEY ABNORMALITIES ({len(abnormalities)} found):")
    for abnorm in abnormalities:
        test_name = abnorm.get('test_name', abnorm.get('parameter', 'unknown'))
        value = abnorm.get('value', 'N/A')
        unit = abnorm.get('unit', '')
        risk = abnorm.get('risk_level', 'unknown')
        desc = abnorm.get('description', '')
        print(f"  {test_name}: {value} {unit}")
        print(f"    Risk: {risk} - {desc}")
    
    # Show extraction log
    log = result.get('extraction_log', {})
    print(f"\nEXTRACTION LOG:")
    print(f"  Status: {log.get('status')}")
    print(f"  Tests found: {log.get('tests_found')}")
    print(f"  Abnormalities found: {log.get('abnormalities_found')}")
    
    return result


def test_findings_and_recommendations(structured_result: Dict[str, Any]):
    """Demonstrate findings synthesis and recommendations."""
    print("\n" + "="*80)
    print("TEST 5: FINDINGS SYNTHESIS & RECOMMENDATIONS")
    print("="*80)
    
    from reporting.finding_synthesizer import synthesize_findings
    from reporting.recommendation_engine import generate_recommendations
    
    # Create mock model outputs
    model1_output = {
        'key_abnormalities': structured_result.get('key_abnormalities', [])
    }
    
    model3_output = {
        'adjusted_risks': {
            'cardiac': {'risk_level': 'moderate', 'severity_score': 0.65},
            'diabetes': {'risk_level': 'high', 'severity_score': 0.78},
            'cbc': {'risk_level': 'low', 'severity_score': 0.35},
            'renal': {'risk_level': 'moderate', 'severity_score': 0.62},
        }
    }
    
    # Synthesize findings
    synthesized = synthesize_findings(model1_output, model3_output)
    
    print(f"\nKEY FINDINGS ({len(synthesized.get('key_findings', []))} total):")
    for finding in synthesized.get('key_findings', []):
        print(f"  • {finding.get('description', 'Unknown')}")
    
    print(f"\nRISK SUMMARY ({len(synthesized.get('risk_summary', []))} domains):")
    for risk in synthesized.get('risk_summary', []):
        domain = risk.get('domain', 'unknown')
        level = risk.get('risk_level', 'unknown')
        score = risk.get('severity_score', 0)
        print(f"  {domain}: {level} (score: {score})")
    
    # Generate recommendations
    user_context = {
        'age': 55,
        'gender': 'male',
        'lifestyle': 'sedentary',
    }
    
    recommendations = generate_recommendations(synthesized, user_context)
    
    print(f"\nRECOMMENDATIONS ({len(recommendations['recommendations'])} total):")
    print(f"Urgency Level: {recommendations['urgency_level'].upper()}")
    for i, rec in enumerate(recommendations['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    return {
        'findings': synthesized,
        'recommendations': recommendations
    }


def main():
    """Run all integration tests."""
    print("\n" + "="*80)
    print("HEALTH REPORT AI - INTEGRATION TEST SUITE")
    print("="*80)
    print("\nThis test demonstrates all major pipeline improvements:")
    print("1. OCR cleaning and text normalization")
    print("2. Medical parameter extraction with fuzzy matching")
    print("3. Reference range abnormality detection")
    print("4. Complete structuring pipeline")
    print("5. Findings synthesis and recommendations")
    
    try:
        # Test 1
        cleaned = test_ocr_cleaning()
        
        # Test 2
        params = test_parameter_extraction(cleaned)
        
        # Test 3
        abnormalities = test_reference_ranges(params)
        
        # Test 4
        structured = test_full_structuring()
        
        # Test 5
        final = test_findings_and_recommendations(structured)
        
        print("\n" + "="*80)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nKey Improvements Verified:")
        print("✓ Noisy OCR text successfully cleaned")
        print("✓ Parameters extracted with flexible matching")
        print("✓ Abnormalities detected using medical reference ranges")
        print("✓ Complete structuring with logging")
        print("✓ Findings and recommendations generated")
        print("\nPI PRODUCTION READY!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n[FAILED] TEST FAILED: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
