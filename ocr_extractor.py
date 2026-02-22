import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os

# Optional: Set tesseract path if not in environment
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_with_ocr(pdf_path):
    """
    Extracts text from a scanned PDF using OCR.
    Iterates through each page, converts it to an image, and runs Tesseract OCR.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file {pdf_path} not found.")
        return ""

    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Increase resolution for better OCR
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Run OCR on the image
            page_text = pytesseract.image_to_string(img)
            text += f"--- Page {page_num + 1} ---\n"
            text += page_text + "\n"
        doc.close()
    except Exception as e:
        print(f"OCR Error: {e}")
        return "ERROR: OCR failed."

    return text
