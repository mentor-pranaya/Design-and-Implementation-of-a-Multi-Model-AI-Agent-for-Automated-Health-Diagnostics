
"""
Phase 1 Input Processing - File extraction and OCR cleaning.

Handles extraction of text from various file formats (PDF, images, JSON)
and applies OCR cleaning to improve downstream processing.
"""

import os
import logging
from input_handlers.image_handlers import extract_text_from_image
from input_handlers.pdf_handlers import extract_text_from_pdf
from input_handlers.json_handlers import extract_text_from_json

logger = logging.getLogger(__name__)


def process_input(file_path: str, apply_ocr_cleaning: bool = True) -> str:
    """
    Extract text from file and optionally apply OCR cleaning.
    
    Supports:
    - Images: PNG, JPG, JPEG (via EasyOCR)
    - PDF: Text extraction via pdfplumber
    - JSON: Structured data extraction
    
    Args:
        file_path: Path to input file
        apply_ocr_cleaning: Whether to apply OCR text cleaning (default: True)
    
    Returns:
        Extracted and optionally cleaned text
    """
    if not file_path or not os.path.exists(file_path):
        logger.warning(f"File not found: {file_path}")
        return ""

    file_path_lower = file_path.lower()
    raw_text = ""

    try:
        if file_path_lower.endswith((".png", ".jpg", ".jpeg")):
            logger.info(f"Extracting text from image: {file_path}")
            raw_text = extract_text_from_image(file_path)
        elif file_path_lower.endswith(".pdf"):
            logger.info(f"Extracting text from PDF: {file_path}")
            raw_text = extract_text_from_pdf(file_path)
        elif file_path_lower.endswith(".json"):
            logger.info(f"Extracting text from JSON: {file_path}")
            raw_text = extract_text_from_json(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            return ""
        
        if not raw_text:
            logger.warning(f"No text extracted from file: {file_path}")
            return ""
        
        # Apply OCR cleaning if requested
        if apply_ocr_cleaning:
            logger.info("Applying OCR cleaning")
            from structuring_layers.ocr_cleaner import clean_and_standardize
            try:
                cleaned_text = clean_and_standardize(raw_text)
                logger.info(f"OCR cleaning completed: {len(raw_text)} → {len(cleaned_text)} chars")
                return cleaned_text
            except Exception as e:
                logger.warning(f"OCR cleaning failed: {e}. Using raw text.")
                return raw_text
        
        return raw_text
        
    except Exception as e:
        logger.error(f"Error processing input file {file_path}: {e}", exc_info=True)
        return ""
