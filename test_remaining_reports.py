"""Test the remaining problematic reports"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core_phase1.ocr.pdf_ocr import extract_text_from_pdf
from core_phase1.ocr.image_ocr import extract_text_from_image
from core_phase1.extraction.comprehensive_extractor import extract_parameters_comprehensive

def test_report(filepath):
    """Test a single report"""
    filename = filepath.name
    
    print(f"\n{'='*80}")
    print(f"Testing: {filename}")
    print(f"{'='*80}")
    
    try:
        # Extract OCR text
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(str(filepath))
        else:
            text = extract_text_from_image(str(filepath))
        
        print(f"OCR text length: {len(text)} characters")
        
        if len(text) == 0:
            print("❌ OCR FAILED - No text extracted")
            return False
        
        # Show first 500 chars
        print(f"\nFirst 500 characters:")
        print("-" * 80)
        print(text[:500])
        print("-" * 80)
        
        # Extract parameters
        extracted = extract_parameters_comprehensive(text)
        
        if not extracted:
            print(f"\n⚠️  NO PARAMETERS EXTRACTED")
            print("This report may contain:")
            print("  - Non-standard parameter names")
            print("  - Different format/layout")
            print("  - Poor OCR quality")
            return False
        
        print(f"\n✅ EXTRACTED {len(extracted)} PARAMETERS:")
        for param, data in extracted.items():
            print(f"   {param:20} = {data['value']:8.2f} {data['unit']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Test remaining problematic reports"""
    test_dir = Path(r"C:\Users\mi\Downloads\infosys project\data\test_reports")
    
    # Reports that need checking
    problem_reports = [
        "test report (4).png",
        "test report (5).pdf",
        "test report (6).pdf",
        "test report (7).pdf"
    ]
    
    print("="*80)
    print("TESTING REMAINING PROBLEMATIC REPORTS")
    print("="*80)
    
    results = {}
    for report_name in problem_reports:
        filepath = test_dir / report_name
        if filepath.exists():
            success = test_report(filepath)
            results[report_name] = success
        else:
            print(f"\n❌ File not found: {report_name}")
            results[report_name] = False
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    success_count = sum(1 for v in results.values() if v)
    total = len(results)
    
    for report, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{report:30} - {status}")
    
    print(f"\nSuccess rate: {success_count}/{total} ({success_count/total*100:.1f}%)")
    
    if success_count == total:
        print("\n🎉 ALL REPORTS NOW WORKING!")
    elif success_count > 0:
        print(f"\n✅ Improved {success_count} reports")
    else:
        print("\n⚠️  These reports need manual investigation")

if __name__ == "__main__":
    main()
