import cv2
import pytesseract
import numpy as np
import re


def normalize_ocr_text(text):
    """Normalize OCR output to fix common mistakes"""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    # Character fixes
    text = text.replace("°", ".").replace("|", "1")
    text = text.replace("'", "").replace("`", "").replace("~", "-")

    # Unit fixes
    replacements = {
        "gid.": "g/dl", "g id": "g/dl", "qml": "g/dl", "idl": "g/dl",
        "g/d1": "g/dl", "10+ 6": "10^6", "10*e": "10^6", "10*ev": "10^6",
        "10*3": "10^3", "10%3": "10^3", "10^6/ul": "10^6",
        "10^3/ul": "10^3", "aul": "10^3", "evul": "10^6"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    text = re.sub(r"(\d)\s+\.(\d)", r"\1.\2", text)
    text = re.sub(r"[ft](\d)", r"\1", text)

    return text


def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at {image_path}")

    img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    h, w = img.shape[:2]
    crop = img[int(h * 0.10):int(h * 0.95), int(w * 0.01):int(w * 0.99)]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    bilateral = cv2.bilateralFilter(denoised, 9, 75, 75)

    thresh = cv2.adaptiveThreshold(
        bilateral, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    kernel = np.ones((1, 1), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    return thresh


def read_image(image_path):
    processed = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed, config="--oem 3 --psm 6")
    # print("=== RAW OCR TEXT ===")
    # print(text)
    # print("=== END OCR TEXT ===")
    return normalize_ocr_text(text)
