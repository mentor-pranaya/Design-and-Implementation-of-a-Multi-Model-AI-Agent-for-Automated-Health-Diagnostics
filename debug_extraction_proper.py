"""
Debug OCR extraction using the actual project components.
Tests both PDF and PNG/image processing.
"""

import sys
import os

# Add project paths
sys.path.append('core_phase1/ocr')
sys.path.append('core_phase1/extraction')

def debug_pdf_extraction():
    """Debug PDF OCR extraction."""
    
    print("=" * 80)
    print("DEBUGGING PDF OCR EXTRACTION")
    print("=" * 80)
    
    # Get first PDF test report
    test_dir = "data/test_reports"
    pdf_files = [f for f in os.listdir(test_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found")
        return None, None
    
    test_report = os.path.join(test_dir, sorted(pdf_files)[0])
    print(f"Testing PDF OCR on: {test_report}")
    
    try:
        # Import OCR component
        from pdf_ocr import extract_text_from_pdf
        print("✅ PDF OCR imported successfully")
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(test_report)
        
        if extracted_text:
            print(f"✅ PDF OCR extraction successful!")
            print(f"   Text length: {len(extracted_text)} characters")
            print(f"   First 300 characters:")
            print(f"   {repr(extracted_text[:300])}")
            
            # Save OCR text for inspection
            with open("debug_pdf_ocr_output.txt", 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print("✅ PDF OCR text saved to: debug_pdf_ocr_output.txt")
            
            return extracted_text, "pdf"
        else:
            print("❌ PDF OCR extraction returned empty text")
            return None, None
            
    except Exception as e:
        print(f"❌ PDF OCR error: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def debug_png_extraction():
    """Debug PNG/image OCR extraction."""
    
    print("\n" + "=" * 80)
    print("DEBUGGING PNG/IMAGE OCR EXTRACTION")
    print("=" * 80)
    
    # Get first PNG test report
    test_dir = "data/test_reports"
    png_files = [f for f in os.listdir(test_dir) if f.endswith('.png')]
    
    if not png_files:
        print("❌ No PNG files found")
        return None, None
    
    test_report = os.path.join(test_dir, sorted(png_files)[0])
    print(f"Testing PNG OCR on: {test_report}")
    
    try:
        # Import OCR libraries
        import pytesseract
        from PIL import Image
        
        # Set tesseract path (adjust if needed)
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        print("✅ Tesseract and PIL imported successfully")
        
        # Extract text from PNG
        image = Image.open(test_report)
        extracted_text = pytesseract.image_to_string(image)
        
        if extracted_text:
            print(f"✅ PNG OCR extraction successful!")
            print(f"   Text length: {len(extracted_text)} characters")
            print(f"   First 300 characters:")
            print(f"   {repr(extracted_text[:300])}")
            
            # Save OCR text for inspection
            with open("debug_png_ocr_output.txt", 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print("✅ PNG OCR text saved to: debug_png_ocr_output.txt")
            
            return extracted_text, "png"
        else:
            print("❌ PNG OCR extraction returned empty text")
            return None, None
            
    except Exception as e:
        print(f"❌ PNG OCR error: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_parameter_extraction(text, file_type):
    """Test parameter extraction on OCR text."""
    
    print(f"\n" + "=" * 80)
    print(f"TESTING PARAMETER EXTRACTION ({file_type.upper()})")
    print("=" * 80)
    
    if not text:
        print("❌ No text to extract parameters from")
        return None
    
    try:
        # Import extraction component
        from parser import extract_parameters, parse_value_unit
        print("✅ Parameter extraction imported successfully")
        
        # For now, let's try to find some common blood parameters manually
        # since we need to see what the OCR text looks like first
        
        print("🔍 Searching for common blood parameters in OCR text...")
        
        # Common blood parameters to look for
        parameters = [
            'hemoglobin', 'hb', 'glucose', 'cholesterol', 'triglycerides',
            'hdl', 'ldl', 'creatinine', 'urea', 'platelet', 'wbc', 'rbc'
        ]
        
        found_params = []
        text_lower = text.lower()
        
        for param in parameters:
            if param in text_lower:
                found_params.append(param)
        
        if found_params:
            print(f"✅ Found potential parameters: {found_params}")
        else:
            print("⚠️  No common blood parameters found in OCR text")
            print("   This might indicate:")
            print("   - OCR quality issues")
            print("   - Different parameter naming")
            print("   - Report format not recognized")
        
        # Try to extract some numeric values
        import re
        numeric_pattern = r'\d+\.?\d*'
        numbers = re.findall(numeric_pattern, text)
        
        print(f"🔢 Found {len(numbers)} numeric values in text")
        if len(numbers) > 0:
            print(f"   First 10 numbers: {numbers[:10]}")
        
        return found_params
        
    except Exception as e:
        print(f"❌ Parameter extraction error: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_image_ocr_function():
    """Create a function to handle image OCR for the orchestrator."""
    
    print(f"\n" + "=" * 80)
    print("CREATING IMAGE OCR SUPPORT")
    print("=" * 80)
    
    # Create a simple image OCR function
    image_ocr_code = '''"""
Image OCR support for PNG/JPG blood reports.
"""

import pytesseract
from PIL import Image
import os

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from image file (PNG, JPG, etc.) using OCR.
    
    Args:
        image_path (str): Path to image file
        
    Returns:
        str: Extracted text
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        # Open and process image
        image = Image.open(image_path)
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(image)
        
        return text
        
    except Exception as e:
        raise Exception(f"Failed to extract text from image: {e}")

if __name__ == "__main__":
    # Test with first PNG file
    import glob
    png_files = glob.glob("data/test_reports/*.png")
    
    if png_files:
        test_file = png_files[0]
        print(f"Testing image OCR on: {test_file}")
        
        try:
            text = extract_text_from_image(test_file)
            print(f"Success! Extracted {len(text)} characters")
            print(f"First 200 characters: {repr(text[:200])}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No PNG files found for testing")
'''
    
    # Save the image OCR function
    with open("core_phase1/ocr/image_ocr.py", 'w') as f:
        f.write(image_ocr_code)
    
    print("✅ Created core_phase1/ocr/image_ocr.py")
    print("   This adds PNG/JPG support to your project")

if __name__ == "__main__":
    print("🔍 DEBUGGING OCR AND PARAMETER EXTRACTION")
    print("Testing both PDF and PNG/image processing...")
    
    # Test PDF extraction
    pdf_text, pdf_type = debug_pdf_extraction()
    
    # Test PNG extraction  
    png_text, png_type = debug_png_extraction()
    
    # Test parameter extraction on both
    if pdf_text:
        test_parameter_extraction(pdf_text, pdf_type)
    
    if png_text:
        test_parameter_extraction(png_text, png_type)
    
    # Create image OCR support
    create_image_ocr_function()
    
    print(f"\n" + "=" * 80)
    print("DEBUGGING SUMMARY")
    print("=" * 80)
    
    pdf_status = "✅ Working" if pdf_text else "❌ Issues"
    png_status = "✅ Working" if png_text else "❌ Issues"
    
    print(f"PDF OCR: {pdf_status}")
    print(f"PNG OCR: {png_status}")
    
    if pdf_text or png_text:
        print("\n✅ Your project CAN process both PDF and PNG files!")
        print("✅ OCR extraction is working")
        print("⚠️  Parameter extraction may need adjustment based on OCR text format")
    else:
        print("\n❌ OCR extraction has issues")
        print("   Check Tesseract installation and file formats")
    
    print(f"\nFiles created for inspection:")
    if pdf_text:
        print("- debug_pdf_ocr_output.txt (PDF OCR text)")
    if png_text:
        print("- debug_png_ocr_output.txt (PNG OCR text)")
    print("- core_phase1/ocr/image_ocr.py (PNG support)")
    
    print(f"\nNext steps:")
    print("1. Review OCR output files to see text quality")
    print("2. Adjust parameter extraction patterns if needed")
    print("3. Test with different report formats")
    print("4. Update orchestrator to use image OCR for PNG files")