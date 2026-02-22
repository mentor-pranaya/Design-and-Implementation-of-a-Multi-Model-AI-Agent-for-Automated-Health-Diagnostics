"""
Image OCR support for PNG/JPG blood reports.
"""

import pytesseract
from PIL import Image
import os

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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
