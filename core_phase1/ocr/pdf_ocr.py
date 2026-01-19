import pytesseract
from pdf2image import convert_from_path
from pathlib import Path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class OCRError(Exception):
    """Custom exception for OCR-related failures."""
    pass


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract raw text from a PDF using OCR.

    Args:
        pdf_path (str): Path to PDF file

    Returns:
        str: Extracted raw text
    """
    path = Path(pdf_path)

    if not path.exists():
        raise OCRError(f"PDF not found: {pdf_path}")

    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        raise OCRError(f"Failed to convert PDF to images: {e}")

    full_text = []

    for idx, image in enumerate(images):
        try:
            text = pytesseract.image_to_string(image)
            full_text.append(text)
        except Exception as e:
            raise OCRError(f"OCR failed on page {idx + 1}: {e}")

    return "\n".join(full_text)
