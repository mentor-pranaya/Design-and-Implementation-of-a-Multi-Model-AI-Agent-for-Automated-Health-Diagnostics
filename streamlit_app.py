
import streamlit as st
from PIL import Image
import pytesseract
import cv2
import numpy as np
import os
import json
import sys

import supabase

from fpdf import FPDF
from datetime import datetime
from utils.supabase_client import supabase_client
from models.borderline_analysis import detect_borderline_parameters
from extraction.parameter_extractor import extract_parameters
from models.model1_parameter_interpretation import interpret_parameters
from models.model2_pattern_recognition import detect_health_patterns
from models.risk_score import calculate_risk_score
from models.model3_contextual_analysis import apply_contextual_adjustment
from models.findings_synthesis import synthesize_findings
from models.recommendation_generator import generate_recommendations

from fpdf import FPDF

from fpdf import FPDF

def generate_pdf_report(name,age, gender, model1_results, patterns, risk_score, borderline_notes):

    pdf = FPDF()
    pdf.add_page()

    # ---------- HEADER ----------
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "AI HEALTH DIAGNOSTICS ", ln=True, align="C")

    pdf.set_font("Arial", size=11)
    pdf.cell(200, 8, "Automated Blood Report Analysis", ln=True, align="C")

    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 8, "------------------------------------------------------------", ln=True)

    # ---------- PATIENT INFO ----------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Patient Information", ln=True)

    pdf.set_font("Arial", size=11)
    pdf.cell(200, 8, f"Name: {name}", ln=True)
    pdf.cell(200, 8, f"Age: {age}", ln=True)
    pdf.cell(200, 8, f"Gender: {gender}", ln=True)

    pdf.ln(3)
    pdf.cell(200, 8, "------------------------------------------------------------", ln=True)

    # ---------- PARAMETER TABLE ----------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "CBC Parameter Interpretation", ln=True)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 8, "Parameter", 1)
    pdf.cell(40, 8, "Value", 1)
    pdf.cell(40, 8, "Status", 1)
    pdf.ln()

    pdf.set_font("Arial", size=10)
    for p, r in model1_results.items():
        pdf.cell(60, 8, p.upper(), 1)
        pdf.cell(40, 8, str(r["value"]), 1)
        pdf.cell(40, 8, r["status"], 1)
        pdf.ln()

    # ---------- HEALTH PATTERNS ----------
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Detected Health Patterns", ln=True)

    pdf.set_font("Arial", size=11)
    if patterns:
        for p in patterns:
            pdf.multi_cell(0, 8, f"{p['pattern']} ({p['risk_level']}) - {p['reason']}")
    else:
        pdf.cell(200, 8, "No significant health risk patterns detected.", ln=True)

    # ---------- RISK SCORE ----------
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Overall Risk Score", ln=True)

    pdf.set_font("Arial", size=11)
    pdf.cell(200, 8, f"Risk Score: {risk_score}/100", ln=True)

    if risk_score < 30:
        pdf.cell(200, 8, "Risk Level: Low", ln=True)
    elif risk_score < 60:
        pdf.cell(200, 8, "Risk Level: Moderate", ln=True)
    else:
        pdf.cell(200, 8, "Risk Level: High", ln=True)

    # ---------- BORDERLINE ----------
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Borderline Observations", ln=True)

    pdf.set_font("Arial", size=11)
    if borderline_notes:
        for note in borderline_notes:
            pdf.multi_cell(0, 8, f"- {note}")
    else:
        pdf.cell(200, 8, "No borderline observations detected.", ln=True)

    # ---------- SUMMARY ----------
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Summary", ln=True)

    pdf.set_font("Arial", size=11)
    if patterns:
        pdf.multi_cell(
            0,
            8,
            "Your report indicates certain blood parameter variations that may require medical attention. "
            "This is not a diagnosis. Please consult a healthcare professional for further evaluation."
        )
    else:
        pdf.multi_cell(
            0,
            8,
            "Your blood parameters are within acceptable limits. Maintain a healthy lifestyle and schedule regular check-ups."
        )

    # ---------- RECOMMENDATIONS ----------
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Personalized Recommendations", ln=True)

    pdf.set_font("Arial", size=11)

    recommendations = []

    if "hemoglobin" in model1_results and model1_results["hemoglobin"]["status"] == "Low":
        recommendations.append("Increase intake of iron-rich foods such as spinach, legumes, and dates.")
        recommendations.append("Consider clinical screening for anemia.")

    if "wbc_count" in model1_results and model1_results["wbc_count"]["status"] == "Low":
        recommendations.append("Maintain hygiene and monitor for frequent infections.")

    if "platelet_count" in model1_results:
        if model1_results["platelet_count"]["status"] == "Low":
            recommendations.append("Avoid injury-prone activities and consult a doctor.")
        elif model1_results["platelet_count"]["status"] == "High":
            recommendations.append("Stay hydrated and seek medical advice for further evaluation.")

    recommendations.append("Follow a balanced diet and regular physical activity.")
    recommendations.append("Consult a healthcare professional for proper diagnosis.")

    for rec in recommendations:
        pdf.multi_cell(0, 8, f"- {rec}")

    # ---------- FOOTER ----------
    pdf.ln(10)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(
        0,
        6,
        "Disclaimer: This report is generated by an AI system for screening purposes only and does not replace professional medical advice."
    )

    file_path = "AI_Health_Report.pdf"
    pdf.output(file_path)

    return file_path

# ---------------- DEBUG ----------------
st.write("Python executable:", sys.executable)

# ---------------- TESSERACT SETUP ----------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

st.title(" AI Agent for Automated Health Diagnostics")

st.subheader("👤 Patient Information")

name = st.text_input("Patient Name", "Enter name")
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
    st.subheader("🧪 Parameter Interpretation")
    model1_results = interpret_parameters(params)

    for p, r in model1_results.items():
        st.write(f"{p.upper()} : {r['value']} → {r['status']}")

    # ---------- MODEL-2 ----------
    st.subheader(" Health Pattern Analysis")
    
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
    
   
   # ---------- DOWNLOAD REPORT ----------
    st.subheader("📄 Download Report")
    borderline_notes = detect_borderline_parameters(model1_results)
    pdf_path = generate_pdf_report(
        name,
        age,
        gender,
        model1_results,
        patterns,
        risk_score,
        borderline_notes
)
    with open(pdf_path, "rb") as file:
        st.download_button(
            label="⬇️ Download Health Report",
            data=file,
            file_name="AI_Health_Report.pdf",
            mime="application/pdf"
    )

    

    # ---------- BORDERLINE ----------
    st.subheader(" Borderline Observations")
    borderline_notes = detect_borderline_parameters(model1_results)

    if borderline_notes:
        for note in borderline_notes:
            st.write(f"• {note}")
    else:
        st.write("No borderline observations detected.")

# ---------- FINDINGS SYNTHESIS ----------
    st.subheader("Summary of Findings")
    summary = synthesize_findings(
    model1_results, patterns, risk_score, age, gender)
    st.write(summary)

# ---------- RECOMMENDATIONS ----------
    from models.recommendation_generator import generate_recommendations
    st.subheader("Personalized Recommendations")
    recommendations = generate_recommendations(patterns, model1_results, risk_score)
    for rec in recommendations:
        st.write("•", rec)

        # ---------- SAVE TO SUPABASE ----------
if st.button("Save Report to Database"):
    record = {
        "age": age,
        "gender": gender,
        "parameters": params,
        "model1_results": model1_results,
        "model_patterns": patterns,
        "risk_score": risk_score,
        
    }

    response = supabase_client.table("reports").insert(record).execute()

    if response.data:
        st.success("Report saved successfully to Supabase ✅")
    else:
        st.error("Failed to save report ❌")
# ================================
# 📂 VIEW SAVED REPORTS
# ---------- REPORT HISTORY ----------
st.subheader("📂 Report History (Supabase)")

import pandas as pd

if st.button("Load Report History"):

    data = supabase_client.table("reports").select("*").execute()

    if data.data:
        df = pd.DataFrame(data.data)

        # 🔽 ADD RISK FILTER HERE
        risk_filter = st.selectbox(
            "Filter by Risk Level",
            ["All", "High", "Moderate", "Low"]
        )

        if risk_filter == "High":
            df = df[df["risk_score"] >= 70]

        elif risk_filter == "Moderate":
            df = df[(df["risk_score"] >= 40) & (df["risk_score"] < 70)]

        elif risk_filter == "Low":
            df = df[df["risk_score"] < 40]

        st.dataframe(df)

    else:
        st.info("No saved reports found.")




