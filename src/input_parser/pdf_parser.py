import fitz  # PyMuPDF
import tempfile
import os
from fastapi import UploadFile
import numpy as np
import io
from PIL import Image
from src.input_parser.image_parser import reader

def extract_text_from_pdf(upload_file: UploadFile) -> str:
    """
    Extract text from an uploaded PDF file (FastAPI UploadFile).
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(upload_file.file.read())
        tmp_path = tmp.name

    try:
        doc = fitz.open(tmp_path)
        text = ""
        for page in doc:
            page_text = page.get_text()
            if not page_text.strip():  # If no text, try OCR on images
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes()))
                
                # Convert PIL image to numpy array for EasyOCR
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img_np = np.array(img)
                
                # Extract text using EasyOCR
                results = reader.readtext(img_np, detail=0)
                page_text = ' '.join(results)
                
            text += page_text + "\n"
        doc.close()
        return text
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
