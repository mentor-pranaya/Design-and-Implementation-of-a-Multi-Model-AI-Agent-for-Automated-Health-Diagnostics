# input_handlers/image_handler.py

import easyocr
import os

reader = easyocr.Reader(['en'])

def extract_text_from_image(image_path):
    if not os.path.exists(image_path):
        return ""

    try:
        results = reader.readtext(image_path)

        extracted_text = []
        for (bbox, text, confidence) in results:
            extracted_text.append(text)

        return "\n".join(extracted_text)

    except Exception:
        return ""

