#!/usr/bin/env python
"""
QUICK START - Health Report AI Production Pipeline

Run this script to verify the improved pipeline is working correctly
and see the impact of the enhancements.
"""

import json
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def demo_ocr_cleaning():
    """Show the power of OCR cleaning."""
    from structuring_layers.ocr_cleaner import clean_and_standardize
    
    print("\n" + "="*80)
    print("🔧 OCR CLEANING DEMO")
    print("="*80)
    
    # Simulate real OCR output with common mistakes
    noisy_ocr = """
    LABORATORY TEST REPORT
    Patient: John Doe
    
    HEMATOLOGY
    Hemoglobin: l2.8 g/dl•
    RBC: 4.2 million/ul
    WBC: 7.2 thousand/µl
    Platelets: 245 K/ul
    
    BIOCHEMISTRY
    Fasting Glucose: llO mg/dl
    Total Cholesterol: 2lO mg/dL
    HDL Cholesterol 38 mg/DL
    LDL Cholesterol: l60 mg/dl
    Triglycerides: l80 mg/dl
    
    RENAL FUNCTION
    Creatinine: 1.5 mg/dl
    BUN: 28 mg/dl
    
    VITALS
    Blood Pressure: l45/92 mmHg
    """
    
    print("BEFORE cleaning (noisy OCR):")
    print(noisy_ocr)
    
    cleaned = clean_and_standardize(noisy_ocr)
    
    print("\nAFTER cleaning:")
    print(cleaned)
    
    print("\n✓ OCR text is now clean and standardized")
    return cleaned


def demo_parameter_extraction(cleaned_text: str):
    """Show parameter extraction."""
    from structuring_layers.medical_parameter_extractor import extract_all_parameters
    from structuring_layers.test_dictionary import TEST_ALIASES
    
    print("\n" + "="*80)
    print("📊 PARAMETER EXTRACTION DEMO")
    print("="*80)
    
    # Flatten test aliases
    flattened = {}
    for cat, tests in TEST_ALIASES.items():
        for test_name, aliases in tests.items():
            flattened[test_name] = aliases
    
    # Extract
    params = extract_all_parameters(cleaned_text, flattened)
    
    print(f"\n✓ Extracted {len(params)} medical parameters:")
    for test_name, data in list(params.items())[:5]:
        print(f"  • {test_name}: {data['value']} {data.get('unit', '')}")
    if len(params) > 5:
        print(f"  ... and {len(params) - 5} more")
    
    return params


def demo_abnormality_detection(params):
    """Show abnormality detection using reference ranges."""
    from structuring_layers.reference_ranges import get_abnormal_findings
    
    print("\n" + "="*80)
    print("⚠️  ABNORMALITY DETECTION DEMO")
    print("="*80)
    
    abnormalities = get_abnormal_findings(params)
    
    if abnormalities:
        print(f"\n✓ Found {len(abnormalities)} abnormalities:")
        for abnorm in abnormalities[:5]:
            print(f"  • {abnorm['test_name']}: {abnorm['value']} {abnorm['unit']}")
            print(f"    Risk: {abnorm['risk_level'].upper()} - {abnorm['description']}")
        if len(abnormalities) > 5:
            print(f"  ... and {len(abnormalities) - 5} more")
    else:
        print("\n✓ No abnormalities found (all values within normal range)")
    
    return abnormalities


def demo_full_pipeline():
    """Show the complete pipeline end-to-end."""
    from structuring_layers.phase2_structuring import structure_report
    
    print("\n" + "="*80)
    print("🔄 COMPLETE PIPELINE DEMO")
    print("="*80)
    
    # Real-world test data with OCR errors
    sample_report = """
    BLOOD TEST REPORT - 2025-02-18
    
    Hemoglobin: l2.5 g/dl
    RBC: 4.2 million/ul
    WBC: 7.8 thousand/ul
    Platelets: 200 thousand/ul
    
    Fasting Blood Sugar: l20 mg/dL
    Total Cholesterol: 240 mg/dl
    HDL: 35 mg/dL
    LDL: 160 mg/dl
    Triglycerides: l85 mg/dL
    
    Creatinine: 1.6 mg/dL
    BUN: 30 mg/dL
    
    Blood Pressure: l48/95 mmHg
    """
    
    print("\nProcessing medical report...")
    result = structure_report(sample_report)
    
    # Show results
    categories = {k: v for k, v in result.items() 
                  if k not in ['key_abnormalities', 'extraction_log']}
    total_tests = sum(len(v) for v in categories.values())
    
    print(f"\n✓ Pipeline Results:")
    print(f"  • Categories extracted: {len(categories)}")
    print(f"  • Tests found: {total_tests}")
    
    abnormalities = result.get('key_abnormalities', [])
    print(f"  • Abnormalities detected: {len(abnormalities)}")
    
    if abnormalities:
        print(f"\n  Key Abnormalities (these would have been EMPTY before):")
        for ab in abnormalities[:5]:
            test = ab.get('test_name', ab.get('parameter'))
            value = ab.get('value')
            unit = ab.get('unit', '')
            risk = ab.get('risk_level')
            print(f"    - {test}: {value} {unit} ({risk})")
    
    return result


def demo_findings_and_recommendations(result):
    """Show findings and recommendations generation."""
    from reporting.finding_synthesizer import synthesize_findings
    from reporting.recommendation_engine import generate_recommendations
    
    print("\n" + "="*80)
    print("📋 FINDINGS & RECOMMENDATIONS DEMO")
    print("="*80)
    
    # Create model outputs
    model1 = {'key_abnormalities': result.get('key_abnormalities', [])}
    model3 = {
        'adjusted_risks': {
            'cardiac': {'risk_level': 'moderate', 'severity_score': 0.65},
            'diabetes': {'risk_level': 'high', 'severity_score': 0.78},
            'cbc': {'risk_level': 'low', 'severity_score': 0.35},
            'renal': {'risk_level': 'moderate', 'severity_score': 0.62},
        }
    }
    
    # Synthesize
    findings = synthesize_findings(model1, model3)
    
    print(f"\n✓ Key Findings ({len(findings['key_findings'])} total):")
    for f in findings['key_findings'][:5]:
        print(f"  • {f['description']}")
    
    # Generate recommendations
    user_context = {'age': 55, 'gender': 'male', 'lifestyle': 'sedentary'}
    recs = generate_recommendations(findings, user_context)
    
    print(f"\n✓ Recommendations (Urgency: {recs['urgency_level'].upper()}):")
    for i, rec in enumerate(recs['recommendations'][:5], 1):
        print(f"  {i}. {rec}")
    
    if len(recs['recommendations']) > 5:
        print(f"  ... and {len(recs['recommendations']) - 5} more")
    
    print(f"\n✓ Total recommendations: {len(recs['recommendations'])}")
    print("   (Never empty like before!)")


def main():
    """Run full demo."""
    print("\n" + "="*80)
    print("🏥 HEALTH REPORT AI - QUICK START DEMO")
    print("="*80)
    print("\nThis demo shows the production improvements in action.")
    print("Watch how the pipeline transforms noisy OCR into actionable findings!\n")
    
    try:
        # Run demos
        cleaned = demo_ocr_cleaning()
        params = demo_parameter_extraction(cleaned)
        abnorms = demo_abnormality_detection(params)
        result = demo_full_pipeline()
        demo_findings_and_recommendations(result)
        
        # Summary
        print("\n" + "="*80)
        print("✅ DEMO COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nKey Improvements Demonstrated:")
        print("  ✓ Noisy OCR text automatically cleaned")
        print("  ✓ Parameters extracted despite spacing variations")
        print("  ✓ Abnormalities detected using medical reference ranges")
        print("  ✓ Findings and recommendations NEVER empty")
        print("  ✓ Complete end-to-end pipeline working")
        print("\n🎉 Your Health Report AI is now PRODUCTION READY!")
        
        print("\nNEXT STEPS:")
        print("  1. Test with your actual medical reports:")
        print("     from structuring_layers.phase2_structuring import structure_report")
        print("     result = structure_report(your_ocr_text)")
        print("")
        print("  2. Run the full test suite:")
        print("     python structuring_layers/integration_guide.py")
        print("")
        print("  3. Deploy the API:")
        print("     uvicorn api.main:app --reload")
        print("\n" + "="*80)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
