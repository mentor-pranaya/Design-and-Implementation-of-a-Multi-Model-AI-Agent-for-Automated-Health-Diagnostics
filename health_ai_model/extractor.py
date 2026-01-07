import pandas as pd
import json
import re
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes

# Set Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract(file, file_type):
    if file_type == "csv":
        return extract_from_csv(file)

    elif file_type == "json":
        return extract_from_json(file)

    elif file_type == "pdf":
        text = ocr_pdf(file)
        return parse_cbc(text)

    elif file_type in ["png", "jpg", "jpeg"]:
        text = pytesseract.image_to_string(Image.open(file), config="--psm 6")
        return parse_cbc(text)

    return []


# -------- CSV --------
def extract_from_csv(file):
    df = pd.read_csv(file)
    df.columns = [c.strip().lower() for c in df.columns]

    test_col = None
    value_col = None

    for c in df.columns:
        if c in ["test", "test_name", "parameter", "name"]:
            test_col = c
        if c in ["value", "result", "reading"]:
            value_col = c

    if test_col is None or value_col is None:
        return []

    return [
        {"Test": str(row[test_col]).strip(), "Value": float(row[value_col])}
        for _, row in df.iterrows()
    ]


# -------- JSON --------
def extract_from_json(file):
    data = json.load(file)
    results = []

    for k, v in data.items():
        try:
            results.append({"Test": k, "Value": float(v)})
        except:
            pass

    return results


# -------- PDF OCR --------
def ocr_pdf(file):
    images = convert_from_bytes(file.getvalue(), dpi=300)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, config="--psm 6") + "\n"
    return text


# -------- CBC PARSER --------
def parse_cbc(text):
    results = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines:
        u = line.upper()

        def get_val():
            nums = re.findall(r"\d+\.?\d*", line)
            return float(nums[0]) if nums else None

        if u.startswith("HEMOGLOBIN"):
            results.append({"Test": "Hemoglobin", "Value": get_val()})

        elif "TOTAL LEUKOCYTE" in u or u.startswith("WBC") or u.startswith("TLC"):
            results.append({"Test": "Total WBC Count", "Value": get_val()})

        elif u.startswith("PLATELET"):
            results.append({"Test": "Platelet Count", "Value": get_val()})

        elif u.startswith("TOTAL RBC") or u.startswith("RBC"):
            results.append({"Test": "RBC Count", "Value": get_val()})

        elif u.startswith("MCV"):
            results.append({"Test": "MCV", "Value": get_val()})

        elif u.startswith("MCHC"):
            results.append({"Test": "MCHC", "Value": get_val()})

    return results
