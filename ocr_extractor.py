import pytesseract
from pdf2image import convert_from_path
import os
from PIL import Image, ImageEnhance

# Configure Tesseract path for Windows
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure Poppler path for Windows
poppler_path = r'C:\Users\subis\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin'

def preprocess_image(image):
    """Enhance image for better OCR recognition"""
    # Convert to grayscale if needed
    if image.mode != 'L':
        image = image.convert('L')
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2)
    
    return image

def extract_text_with_ocr(pdf_path):
    """Extract text from PDF using OCR (Tesseract)"""
    try:
        # Convert PDF to images with higher DPI for better OCR
        images = convert_from_path(pdf_path, poppler_path=poppler_path, dpi=300)
        
        text = ""
        for i, image in enumerate(images):
            # Preprocess image for better OCR
            processed_image = preprocess_image(image)
            
            # Extract text from each image using Tesseract with config
            page_text = pytesseract.image_to_string(processed_image, lang='eng', config='--psm 6')
            if page_text.strip():
                text += page_text + "\n"
        
        return text
    except Exception as e:
        print(f"Error during OCR extraction: {e}")
        import traceback
        traceback.print_exc()
        return ""
