import streamlit as st
from PIL import Image
import pytesseract
import cv2
import numpy as np
import os
import json
import sys
st.write("Python executable:", sys.executable)

from extraction.parameter_extractor import extract_parameters
from models.model1_parameter_interpretation import classify_parameter

# Tesseract setup
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

st.title("🩺 AI Health Diagnostic – OCR, Extraction & Model-1")


uploaded_file = st.file_uploader(
    "Upload a blood report (Image / PDF / JSON)",
    type=["png", "jpg", "jpeg", "pdf", "json"]
)

if uploaded_file is not None:
    st.success("File uploaded successfully")

    file_type = uploaded_file.type

    # ---------------- IMAGE ----------------
    if file_type in ["image/png", "image/jpeg"]:
        image = Image.open(uploaded_file)

    # ---------------- PDF ----------------
    elif file_type == "application/pdf":
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(uploaded_file.read())
        image = images[0]  # first page only

    # ---------------- JSON (NO OCR) ----------------
    elif file_type == "application/json":
        data = json.load(uploaded_file)

        st.subheader("🧪 Extracted Blood Parameters & Diagnosis (Model-1)")
        for key, value in data.items():
            try:
                status = classify_parameter(key, float(value))
                st.write(
                    f"**{key.replace('_', ' ').upper()}** : {value} → {status}"
                )
            except:
                st.write(
                    f"**{key.replace('_', ' ').upper()}** : {value} (No reference range)"
                )
        st.stop()

    # ---------------- COMMON OCR PIPELINE ----------------
    st.image(image, caption="Uploaded Image", width=600)

    # Convert to OpenCV format
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Preprocessing
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    # OCR
    text = pytesseract.image_to_string(
        gray,
        lang="eng",
        config="--oem 3 --psm 6"
    )

    st.subheader("📝 Extracted Text (OCR Output)")
    st.text_area("Raw OCR Text (Debug)", text, height=300)

    # Parameter extraction
    params = extract_parameters(text)

    st.subheader("🧪 Extracted Blood Parameters & Diagnosis (Model-1)")

    if params:
        for key, value in params.items():
            try:
                status = classify_parameter(key, value)
                st.write(
                    f"**{key.replace('_', ' ').upper()}** : {value} → {status}"
                )
            except:
                st.write(
                    f"**{key.replace('_', ' ').upper()}** : {value} (No reference range)"
                )
    else:
        st.warning("No blood parameters detected from OCR text.")
