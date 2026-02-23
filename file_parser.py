import re
import json
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image


def parse_uploaded_file(uploaded_file):
    """
    Detect file type and parse blood report.
    Supports: PDF, Image, CSV, JSON
    """

    name = uploaded_file.name.lower()

    if name.endswith(".json"):
        return parse_json(uploaded_file)

    elif name.endswith(".csv"):
        return parse_csv(uploaded_file)

    elif name.endswith(".pdf"):
        return parse_pdf(uploaded_file)

    elif name.endswith((".png", ".jpg", ".jpeg")):
        return parse_image(uploaded_file)

    else:
        raise ValueError("Unsupported file format. Upload PDF/Image/CSV/JSON only.")


# ---------------- JSON PARSER ----------------

def parse_json(file):
    """
    Expected JSON format:
    {
      "Glucose": {"value":145, "low":70, "high":99},
      "Hemoglobin": {"value":11.2, "low":13, "high":17}
    }
    """
    return json.load(file)


# ---------------- CSV PARSER ----------------

def parse_csv(file):
    """
    Expected CSV format:
    Parameter,Value,Low,High
    Glucose,145,70,99
    Hemoglobin,11.2,13,17
    """

    df = pd.read_csv(file)
    result = {}

    for _, row in df.iterrows():
        param = str(row["Parameter"]).strip()

        result[param] = {
            "value": float(row["Value"]),
            "low": float(row["Low"]),
            "high": float(row["High"])
        }

    return result


# ---------------- PDF PARSER ----------------

def parse_pdf(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    return extract_from_text(text)


# ---------------- IMAGE PARSER ----------------

def parse_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return extract_from_text(text)


# ---------------- TEXT EXTRACTION ----------------

def extract_from_text(text):
    """
    Extracts parameter, tested value, and reference range from raw text.

    Supports patterns like:
    Glucose 145 mg/dL 70 - 99
    Hemoglobin 11.2 g/dL 13-17
    Cholesterol 220 125 – 200
    """

    data = {}

    # flexible pattern for most lab reports
    pattern = re.compile(
        r"([A-Za-z][A-Za-z \(\)\/%]+?)\s+(\d+\.?\d*)\s*[A-Za-z\/%]*\s+(\d+\.?\d*)\s*[-–to]+\s*(\d+\.?\d*)",
        re.IGNORECASE
    )

    for line in text.split("\n"):
        line = line.strip()

        match = pattern.search(line)

        if match:
            param = match.group(1).strip()
            value = float(match.group(2))
            low = float(match.group(3))
            high = float(match.group(4))

            # clean param name
            param = re.sub(r"\s+", " ", param)

            data[param] = {
                "value": value,
                "low": low,
                "high": high
            }

    return data
