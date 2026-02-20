import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import json
import os

pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'

def parse_input(uploaded_file):
    """
    Extracts content from uploaded files (JSON, PDF, or Images).
    Returns (content, type)
    """
    file_type = uploaded_file.type
    
    try:
        # Handle JSON files
        if file_type == "application/json":
            return json.load(uploaded_file), "json"
        
        # Handle PDF files
        elif file_type == "application/pdf":
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            # If PDF has no text layer, you would usually need to OCR the pages.
            # For now, we return what we found.
            return text.strip(), "text"
        
        # Handle Image files (PNG, JPG, JPEG)
        elif "image" in file_type:
            img = Image.open(uploaded_file)
            text = pytesseract.image_to_string(img)
            return text.strip(), "text"
        
        else:
            return None, "unsupported_error"

    except Exception as e:
        # Return the error message to be handled by app.py
        return str(e), "error"
