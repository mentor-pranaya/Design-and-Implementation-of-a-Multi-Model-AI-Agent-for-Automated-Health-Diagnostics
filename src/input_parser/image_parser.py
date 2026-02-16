open web
import easyocr
from PIL import Image, ImageFilter, ImageEnhance
import tempfile
import os
import numpy as np
from fastapi import UploadFile, HTTPException
import logging
import cv2
import ssl

# Fix SSL certificate verification issues on some systems
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Initialize EasyOCR reader (English language)
# Use local model storage to avoid permission issues and ensuring clean downloads
model_dir = os.path.join(os.getcwd(), "data", "easyocr_models")
os.makedirs(model_dir, exist_ok=True)

try:
    reader = easyocr.Reader(['en'], gpu=False, model_storage_directory=model_dir)
except Exception as e:
    logger.warning(f"Failed to initialize EasyOCR reader: {str(e)}. OCR functionality may be limited.")
    reader = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_image(upload_file: UploadFile) -> str:
    """
    Extract text from uploaded image using EasyOCR.
    EasyOCR is a pure Python solution that doesn't require external dependencies.
    """
    if reader is None:
        logger.error("EasyOCR reader not initialized")
        return ""

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(upload_file.file.read())
        tmp_path = tmp.name

    try:
        # Open and preprocess image
        image = Image.open(tmp_path)

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Apply preprocessing for better OCR results
        image = image.filter(ImageFilter.SHARPEN)

        # Convert PIL image to numpy array for EasyOCR
        image_np = np.array(image)

        # Extract text using EasyOCR
        results = reader.readtext(image_np, detail=0)  # detail=0 returns only text

        # Join all detected text
        text = ' '.join(results)

        return text.strip()

    except Exception as e:
        logger.error(f"OCR failed: {str(e)}")
        return ""
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def extract_text_with_opencv(upload_file: UploadFile) -> str:
    """
    Alternative implementation using OpenCV for preprocessing and EasyOCR for OCR.
    This provides better image preprocessing capabilities for medical documents.
    """
    if reader is None:
        logger.error("EasyOCR reader not initialized")
        return ""

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(upload_file.file.read())
        tmp_path = tmp.name

    try:
        # Read image with OpenCV
        image = cv2.imread(tmp_path)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply noise reduction
        gray = cv2.medianBlur(gray, 3)

        # Apply thresholding to get better contrast
        _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Morphological operations to clean up the image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        threshold = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)

        # Extract text using EasyOCR
        results = reader.readtext(threshold, detail=0)
        text = ' '.join(results)
        return text.strip()

    except Exception as e:
        logger.error(f"OpenCV OCR failed: {str(e)}")
        return ""
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def preprocess_image_advanced(image_path: str) -> list:
    """
    Apply multiple preprocessing techniques to improve OCR accuracy.
    Returns a list of preprocessed images for OCR processing.
    """
    original = Image.open(image_path)

    # Ensure RGB mode
    if original.mode != 'RGB':
        original = original.convert('RGB')

    preprocessed_images = []

    # 1. Original image
    preprocessed_images.append(original)

    # 2. Enhanced contrast
    enhancer = ImageEnhance.Contrast(original)
    contrast_enhanced = enhancer.enhance(2.0)
    preprocessed_images.append(contrast_enhanced)

    # 3. Sharpened
    sharpened = original.filter(ImageFilter.SHARPEN)
    preprocessed_images.append(sharpened)

    # 4. Enhanced brightness
    brightness_enhancer = ImageEnhance.Brightness(original)
    brightness_enhanced = brightness_enhancer.enhance(1.2)
    preprocessed_images.append(brightness_enhanced)

    # 5. Combined enhancement
    combined = ImageEnhance.Contrast(ImageEnhance.Brightness(original).enhance(1.1)).enhance(1.5)
    combined = combined.filter(ImageFilter.SHARPEN)
    preprocessed_images.append(combined)

    return preprocessed_images


def extract_text_automated(upload_file: UploadFile) -> str:
    """
    Automated image processing with multiple preprocessing techniques using EasyOCR.
    Tries different combinations and selects the best result.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(upload_file.file.read())
        tmp_path = tmp.name

    try:
        logger.info("Starting automated EasyOCR image processing...")

        # Get multiple preprocessed versions
        preprocessed_images = preprocess_image_advanced(tmp_path)

        best_text = ""
        best_score = 0

        # Try each preprocessing technique with EasyOCR
        for i, img in enumerate(preprocessed_images):
            try:
                # Convert to numpy array
                img_np = np.array(img)

                # Extract text with EasyOCR
                results = reader.readtext(img_np, detail=0)
                text = ' '.join(results).strip()

                # Score based on text length and word count
                words = len(text.split())
                score = len(text) * 0.7 + words * 0.3

                logger.info(f"Preprocessing {i+1}: {len(text)} chars, {words} words, score: {score:.1f}")

                if score > best_score:
                    best_score = score
                    best_text = text

            except Exception as e:
                logger.warning(f"Preprocessing {i+1} failed: {str(e)}")
                continue

        if not isinstance(best_text, str) or not best_text.strip():
            logger.warning("Automated OCR produced no readable text")
            return ""

        logger.info(f"Final result: {len(best_text)} characters, {len(str(best_text).split())} words")
        return best_text

    except Exception as e:
        logger.error(f"Automated OCR failed: {str(e)}")
        return ""
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def extract_text_with_fallback(upload_file: UploadFile) -> str:
    """
    Extract text from image using EasyOCR with multiple preprocessing fallbacks.
    Provides robust OCR processing with error handling.
    """
    if reader is None:
        logger.error("EasyOCR reader not initialized due to SSL certificate issues")
        raise HTTPException(
            status_code=500,
            detail="OCR service unavailable due to SSL certificate verification issues. Please contact administrator."
        )

    # Reset file pointer in case it was read before
    upload_file.file.seek(0)

    try:
        # Try automated processing with multiple preprocessing techniques
        logger.info("Attempting automated EasyOCR processing with multiple preprocessing...")
        text = extract_text_automated(upload_file)

        if text.strip():
            logger.info("Automated EasyOCR processing successful")
            return text

    except Exception as e:
        logger.warning(f"Automated processing failed: {str(e)}, trying basic methods...")

    # Reset file pointer
    upload_file.file.seek(0)

    try:
        # Try OpenCV preprocessing + EasyOCR
        logger.info("Attempting OCR with OpenCV preprocessing...")
        text = extract_text_with_opencv(upload_file)

        if text.strip():
            logger.info("OpenCV + EasyOCR successful")
            return text
        else:
            logger.warning("OpenCV preprocessing returned empty text, trying basic EasyOCR...")

    except Exception as e:
        logger.warning(f"OpenCV preprocessing failed: {str(e)}, trying basic EasyOCR...")

    try:
        # Reset file pointer for basic attempt
        upload_file.file.seek(0)

        # Try basic EasyOCR
        logger.info("Attempting basic EasyOCR...")
        text = extract_text_from_image(upload_file)

        if text.strip():
            logger.info("Basic EasyOCR successful")
            return text
        else:
            logger.error("All EasyOCR methods returned empty text")
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from image. Please ensure the image contains readable text."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"All OCR methods failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}. Please try a clearer image."
        )
