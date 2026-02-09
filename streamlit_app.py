import streamlit as st
from PIL import Image
import pytesseract
import cv2
import numpy as np
import os
import json
import sys

import supabase

from utils.supabase_client import supabase_client
from models.borderline_analysis import detect_borderline_parameters
from extraction.parameter_extractor import extract_parameters
from models.model1_parameter_interpretation import interpret_parameters
from models.model2_pattern_recognition import detect_health_patterns
from models.risk_score import calculate_risk_score
from models.model3_contextual_analysis import apply_contextual_adjustment
from models.findings_synthesis import synthesize_findings
from models.recommendation_generator import generate_recommendations



# ---------------- DEBUG ----------------
st.write("Python executable:", sys.executable)

# ---------------- TESSERACT SETUP ----------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

st.title("🩺 AI Health Diagnostic – OCR, Model-1 & Model-2")

st.subheader("👤 Patient Information")

age = st.number_input("Age", min_value=0, max_value=120, value=30)
gender = st.selectbox("Gender", ["Male", "Female"])

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

    # ---------- IMAGE ----------
    if file_type in ["image/png", "image/jpeg"]:
        image = Image.open(uploaded_file)

    # ---------- PDF ----------
    elif file_type == "application/pdf":
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(uploaded_file.read())
        image = images[0]

    # ---------- JSON ----------
    elif file_type == "application/json":
        params = json.load(uploaded_file)

    # ---------- OCR ----------
    if file_type != "application/json":
        st.image(image, caption="Uploaded Image", width=600)

        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        text = pytesseract.image_to_string(gray, lang="eng", config="--oem 3 --psm 6")

        st.subheader("📝 Extracted Text (OCR Output)")
        st.text_area("Raw OCR Text", text, height=300)

        params = extract_parameters(text)

        if not params:
            st.warning("No blood parameters detected from OCR text.")
            st.stop()

    # ---------- MODEL-1 ----------
    st.subheader("🧪 Parameter Interpretation (Model-1)")
    model1_results = interpret_parameters(params)

    for p, r in model1_results.items():
        st.write(f"{p.upper()} : {r['value']} → {r['status']}")

    # ---------- MODEL-2 ----------
    st.subheader("🧠 Health Pattern Analysis (Model-2)")
    
    patterns = detect_health_patterns(model1_results)
    patterns = apply_contextual_adjustment(patterns, age, gender)


    if patterns:
        for p in patterns:
            st.write(f"{p['pattern']} – {p['risk_level']}")
    else:
        st.write("No significant health risk patterns detected.")

    # ---------- RISK SCORE ----------
    st.subheader("📊 Overall Risk Score")
    risk_score = calculate_risk_score(model1_results, patterns)
    st.progress(risk_score / 100)
    st.write(f"Risk Score: {risk_score}/100")

    # ---------- BORDERLINE ----------
    st.subheader("🟡 Borderline Observations")
    borderline_notes = detect_borderline_parameters(model1_results)

    if borderline_notes:
        for note in borderline_notes:
            st.write(f"• {note}")
    else:
        st.write("No borderline observations detected.")

# ---------- FINDINGS SYNTHESIS ----------
    st.subheader("📋 Summary of Findings")
    summary = synthesize_findings(
    model1_results, patterns, risk_score, age, gender)
    st.write(summary)

# ---------- RECOMMENDATIONS ----------
    from models.recommendation_generator import generate_recommendations
    st.subheader("✅ Personalized Recommendations")
    recommendations = generate_recommendations(patterns, model1_results, risk_score)
    for rec in recommendations:
        st.write("•", rec)

        # ---------- SAVE TO SUPABASE ----------
if st.button("💾 Save Report to Database"):
    record = {
        "age": age,
        "gender": gender,
        "parameters": params,
        "model1_results": model1_results,
        "model_patterns": patterns,
        "risk_score": risk_score
    }

    response = supabase.table("reports").insert(record).execute()

    if response.data:
        st.success("Report saved successfully to Supabase ✅")
    else:
        st.error("Failed to save report ❌")


