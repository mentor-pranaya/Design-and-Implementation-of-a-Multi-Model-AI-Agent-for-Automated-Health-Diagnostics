"""
Quick test of improved extraction on test report 11
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core_phase1.ocr.pdf_ocr import extract_text_from_pdf
from improved_extraction_patterns import extract_parameters_comprehensive

def test_report_11():
    """Test extraction on report 11 which has T3, T4, TSH"""
    
    report_path = r"C:\Users\mi\Downloads\infosys project\data\test_reports\test report (11).pdf"
    
    print("=" * 80)
    print("TESTING IMPROVED EXTRACTION ON REPORT 11")
    print("=" * 80)
    
    # Extract OCR text
    print("\n1. Extracting OCR text...")
    text = extract_text_from_pdf(report_path)
    print(f"   Text length: {len(text)} characters")
    
    # Show relevant section
    print("\n2. Relevant section from report:")
    print("-" * 80)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if 't3' in line.lower() or 't4' in line.lower() or 'tsh' in line.lower():
            # Show context
            start = max(0, i-2)
            end = min(len(lines), i+3)
            for j in range(start, end):
                print(lines[j])
            break
    print("-" * 80)
    
    # Extract parameters
    print("\n3. Extracting parameters with improved patterns...")
    extracted = extract_parameters_comprehensive(text)
    
    print(f"\n4. RESULTS:")
    print("=" * 80)
    if extracted:
        print(f"✅ Extracted {len(extracted)} parameters:")
        for param, data in extracted.items():
            print(f"   {param:20} = {data['value']:8.2f} {data['unit']}")
    else:
        print("❌ No parameters extracted")
    
    # Expected parameters
    print("\n5. EXPECTED PARAMETERS:")
    print("   T3  = 151.9 ng/dL")
    print("   T4  = 10.14 µg/dL")
    print("   TSH = 8.480 µIU/mL")
    
    # Validation
    print("\n6. VALIDATION:")
    expected = {'t3': 151.9, 't4': 10.14, 'tsh': 8.480}
    for param, expected_value in expected.items():
        if param in extracted:
            actual_value = extracted[param]['value']
            if abs(actual_value - expected_value) < 0.01:
                print(f"   ✅ {param.upper()}: CORRECT ({actual_value})")
            else:
                print(f"   ⚠️  {param.upper()}: MISMATCH (expected {expected_value}, got {actual_value})")
        else:
            print(f"   ❌ {param.upper()}: NOT EXTRACTED")
    
    return extracted

if __name__ == "__main__":
    test_report_11()
