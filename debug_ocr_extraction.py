"""
Debug OCR extraction to see what's happening with parameter extraction.
"""

import sys
import os

# Add project paths
sys.path.append('core_phase1')

def debug_ocr_extraction():
    """Debug OCR extraction on a test report."""
    
    print("=" * 80)
    print("DEBUGGING OCR EXTRACTION")
    print("=" * 80)
    
    # Get first test report
    test_dir = "data/test_reports"
    pdf_files = [f for f in os.listdir(test_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found")
        return
    
    test_report = os.path.join(test_dir, sorted(pdf_files)[0])
    print(f"Testing OCR on: {test_report}")
    
    try:
        # Try to import OCR components
        print("\n1. Testing OCR imports...")
        
        try:
            from ocr.pdf_processor import PDFProcessor
            print("✅ PDFProcessor imported successfully")
        except ImportError as e:
            print(f"❌ PDFProcessor import failed: {e}")
            
            # Try alternative import paths
            try:
                import sys
                sys.path.append('core_phase1/ocr')
                from pdf_processor import PDFProcessor
                print("✅ PDFProcessor imported with alternative path")
            except ImportError as e2:
                print(f"❌ Alternative import also failed: {e2}")
                return
        
        # Try OCR processing
        print("\n2. Testing OCR processing...")
        processor = PDFProcessor()
        
        # Extract text
        extracted_text = processor.extract_text_from_pdf(test_report)
        
        if extracted_text:
            print(f"✅ OCR extraction successful!")
            print(f"   Text length: {len(extracted_text)} characters")
            print(f"   First 200 characters:")
            print(f"   {repr(extracted_text[:200])}")
        else:
            print("❌ OCR extraction returned empty text")
            return
        
        # Try parameter extraction
        print("\n3. Testing parameter extraction...")
        
        try:
            from extraction.parameter_extractor import ParameterExtractor
            print("✅ ParameterExtractor imported successfully")
            
            extractor = ParameterExtractor()
            extracted_params = extractor.extract_parameters(extracted_text)
            
            print(f"✅ Parameter extraction completed")
            print(f"   Parameters found: {len(extracted_params)}")
            
            if extracted_params:
                print("   Extracted parameters:")
                for param, value in extracted_params.items():
                    print(f"     {param}: {value}")
            else:
                print("   ⚠️  No parameters extracted")
                print("   This might indicate:")
                print("     - OCR text doesn't match extraction patterns")
                print("     - Extraction regex needs adjustment")
                print("     - Report format not supported")
        
        except ImportError as e:
            print(f"❌ ParameterExtractor import failed: {e}")
            return
        
        # Save OCR text for manual inspection
        ocr_file = "debug_ocr_output.txt"
        with open(ocr_file, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        print(f"\n✅ OCR text saved to: {ocr_file}")
        print("   You can manually inspect this file to see what OCR extracted")
        
        return extracted_text, extracted_params
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def check_extraction_patterns():
    """Check what extraction patterns are being used."""
    
    print("\n" + "=" * 80)
    print("CHECKING EXTRACTION PATTERNS")
    print("=" * 80)
    
    try:
        sys.path.append('core_phase1/extraction')
        from parameter_extractor import ParameterExtractor
        
        extractor = ParameterExtractor()
        
        # Check if extractor has pattern information
        if hasattr(extractor, 'patterns') or hasattr(extractor, 'parameter_patterns'):
            print("✅ Extractor has pattern definitions")
            
            # Try to show patterns (this depends on your implementation)
            patterns = getattr(extractor, 'patterns', None) or getattr(extractor, 'parameter_patterns', None)
            
            if patterns:
                print(f"   Number of patterns: {len(patterns)}")
                print("   Pattern keys:")
                for key in patterns.keys():
                    print(f"     - {key}")
            else:
                print("   ⚠️  Patterns attribute exists but is empty")
        else:
            print("⚠️  Extractor doesn't have visible pattern definitions")
            print("   Patterns might be hardcoded in methods")
        
    except Exception as e:
        print(f"❌ Error checking patterns: {e}")

if __name__ == "__main__":
    # Debug OCR extraction
    text, params = debug_ocr_extraction()
    
    # Check extraction patterns
    check_extraction_patterns()
    
    print("\n" + "=" * 80)
    print("DEBUGGING SUMMARY")
    print("=" * 80)
    
    if text and params is not None:
        if len(params) > 0:
            print("✅ OCR and extraction working correctly")
            print(f"   Extracted {len(params)} parameters")
        else:
            print("⚠️  OCR working but no parameters extracted")
            print("   Check extraction patterns and OCR text format")
    else:
        print("❌ OCR or extraction has issues")
        print("   Check component imports and dependencies")
    
    print("\nNext steps:")
    print("1. Review debug_ocr_output.txt to see OCR text")
    print("2. Check if extraction patterns match the OCR text format")
    print("3. Adjust extraction patterns if needed")
    print("4. Test with different report formats")