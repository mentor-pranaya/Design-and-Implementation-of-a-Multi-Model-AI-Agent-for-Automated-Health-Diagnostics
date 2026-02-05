import json
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image
import io
import re


def parse_uploaded_file(uploaded_file):
    """
    Detect file type and extract key-value pairs
    Returns dictionary {parameter: value}
    """

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".json"):
        return parse_json(uploaded_file)

    elif file_name.endswith(".csv"):
        return parse_csv(uploaded_file)

    elif file_name.endswith(".pdf"):
        return parse_pdf(uploaded_file)

    elif file_name.endswith((".png", ".jpg", ".jpeg")):
        return parse_image(uploaded_file)

    else:
        raise ValueError("Unsupported file format")


# ---------- Parsers ----------

def parse_json(uploaded_file):
    data = json.load(uploaded_file)
    return data


def parse_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)

    # Expect columns: Parameter, Value
    result = {}
    for _, row in df.iterrows():
        result[str(row[0])] = float(row[1])
    return result


def parse_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    return extract_parameters_from_text(text)


def parse_image(uploaded_file):
    image = Image.open(uploaded_file)
    text = pytesseract.image_to_string(image)
    return extract_parameters_from_text(text)


# ---------- Text Extraction ----------

def extract_parameters_from_text(text):
    """
    Extract lines like:
    Glucose : 120
    Hemoglobin 13.5
    """

    result = {}

    patterns = [
        r"([A-Za-z ]+)\s*[:\-]?\s*(\d+\.?\d*)"
    ]

    for line in text.split("\n"):
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                param = match.group(1).strip()
                value = float(match.group(2))
                result[param] = value

    return result
