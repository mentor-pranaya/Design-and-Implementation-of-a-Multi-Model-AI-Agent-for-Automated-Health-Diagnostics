import streamlit as st
from PIL import Image
import pytesseract
import cv2
import numpy as np
import os
import json
import sys

from models.borderline_analysis import detect_borderline_parameters
from extraction.parameter_extractor import extract_parameters
from models.model1_parameter_interpretation import interpret_parameters
from models.model2_pattern_recognition import detect_health_patterns

# ---------------- DEBUG (OPTIONAL) ----------------
st.write("Python executable:", sys.executable)

# ---------------- TESSERACT SETUP ----------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

# ---------------- UI TITLE ----------------
st.title("🩺 AI Health Diagnostic – OCR, Model-1 & Model-2")

# ---------------- FILE UPLOADER ----------------
uploaded_file = st.file_uploader(
    "Upload a blood report (Image / PDF / JSON)",
    type=["png", "jpg", "jpeg", "pdf", "json"]
)

# =================================================
# MAIN PIPELINE
# =================================================
if uploaded_file is not None:
    st.success("File uploaded successfully")

    file_type = uploaded_file.type

    # ---------------- IMAGE ----------------
    if file_type in ["image/png", "image/jpeg"]:
        image = Image.open(uploaded_file)

    # ---------------- PDF ----------------
    elif file_type == "application/pdf":
        try:
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(uploaded_file.read())
            image = images[0]  # first page only
        except ImportError:
            st.error("pdf2image is not installed in this Python environment.")
            st.stop()

    # ---------------- JSON (NO OCR) ----------------
    elif file_type == "application/json":
        data = json.load(uploaded_file)

        # -------- MODEL-1 --------
        st.subheader("🧪 Parameter Interpretation (Model-1)")
        model1_results = interpret_parameters(data)

        for param, result in model1_results.items():
            st.write(
                f"**{param.replace('_', ' ').upper()}** : "
                f"{result['value']} → {result['status']}"
            )

        # -------- MODEL-2 --------
        st.subheader("🧠 Health Pattern Analysis (Model-2)")
        patterns = detect_health_patterns(model1_results)

        if patterns:
            for p in patterns:
                st.markdown(
                    f"""
                    **{p['pattern']}**
                    - Risk Level: {p['risk_level']}
                    - Reason: {p['reason']}
                    """
                )
        else:
            st.write("No significant health risk patterns detected.")

        # -------- BORDERLINE --------
        st.subheader("🟡 Borderline Observations (Optional)")
        borderline_notes = detect_borderline_parameters(model1_results)

        if borderline_notes:
            for note in borderline_notes:
                st.write(f"• {note}")
        else:
            st.write("No borderline observations detected.")

        st.stop()

    # ---------------- OCR PIPELINE (IMAGE / PDF) ----------------
    st.image(image, caption="Uploaded Image", width=600)

    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    text = pytesseract.image_to_string(
        gray,
        lang="eng",
        config="--oem 3 --psm 6"
    )

    st.subheader("📝 Extracted Text (OCR Output)")
    st.text_area("Raw OCR Text (Debug)", text, height=300)

    # ---------------- PARAMETER EXTRACTION ----------------
    params = extract_parameters(text)

    if not params:
        st.warning("No blood parameters detected from OCR text.")
        st.stop()

    # ---------------- MODEL-1 ----------------
    st.subheader("🧪 Parameter Interpretation (Model-1)")
    model1_results = interpret_parameters(params)

    for param, result in model1_results.items():
        st.write(
            f"**{param.replace('_', ' ').upper()}** : "
            f"{result['value']} → {result['status']}"
        )

    # ---------------- MODEL-2 ----------------
    st.subheader("🧠 Health Pattern Analysis (Model-2)")
    patterns = detect_health_patterns(model1_results)

    if patterns:
        for p in patterns:
            st.markdown(
                f"""
                **{p['pattern']}**
                - Risk Level: {p['risk_level']}
                - Reason: {p['reason']}
                """
            )
    else:
        st.write("No significant health risk patterns detected.")

    # ---------------- BORDERLINE ----------------
    st.subheader("🟡 Borderline Observations (Optional)")
    borderline_notes = detect_borderline_parameters(model1_results)

    if borderline_notes:
        for note in borderline_notes:
            st.write(f"• {note}")
    else:
        st.write("No borderline observations detected.")
