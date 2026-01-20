import pdfplumber
import easyocr
import numpy as np
import cv2
from PIL import Image


# Initialize OCR reader (English)
reader = easyocr.Reader(['en'], gpu=False)


def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF.
    Uses normal extraction first.
    If empty, falls back to OCR (for scanned PDFs).
    """

    extracted_text = ""

    # -------- STEP 1: TRY NORMAL PDF TEXT EXTRACTION --------
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
    except Exception as e:
        print("PDF read error:", e)

    # -------- STEP 2: IF TEXT FOUND, RETURN IT --------
    if extracted_text.strip():
        print("✅ Text extracted using pdfplumber")
        return extracted_text

    # -------- STEP 3: FALLBACK TO OCR (SCANNED PDF) --------
    print("⚠️ No text found. Using OCR...")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                image = page.to_image(resolution=300).original
                image_np = np.array(image)

                # Convert to grayscale
                gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

                # OCR
                ocr_result = reader.readtext(gray)

                for detection in ocr_result:
                    extracted_text += detection[1] + " "

    except Exception as e:
        print("OCR error:", e)

    return extracted_text
