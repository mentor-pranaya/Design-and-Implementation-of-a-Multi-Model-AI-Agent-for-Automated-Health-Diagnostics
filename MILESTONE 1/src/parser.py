import pytesseract
from PIL import Image
import fitz
import json

pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'

def parse_input(uploaded_file):
    file_type = uploaded_file.type
    
    if file_type == "application/json":
        return json.load(uploaded_file), "json"
    
    elif file_type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text, "text"
    
    else: # Images (JPG, PNG)
        # Convert image to text using OCR
        img = Image.open(uploaded_file)
        text = pytesseract.image_to_string(img)
        return text, "text" # Change this to "text" so app.py processes it
