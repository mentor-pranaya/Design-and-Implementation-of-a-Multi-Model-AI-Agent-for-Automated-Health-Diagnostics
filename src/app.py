import streamlit as st
import pytesseract
import pdfplumber
import os
import re
from PIL import Image
from openai import OpenAI
import pandas as pd
import plotly.express as px
from database import *

init_db()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

tesseract_path = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path



class HealthReferenceRanges:

    def __init__(self):

        self.reference_ranges = {

        'hemoglobin': {'female': (12, 16), 'male': (13.5, 17.5)},
        'rbc': {'female': (4.2, 5.4), 'male': (4.7, 6.1)},
        'wbc': {'normal': (4, 11)},
        'platelets': {'normal': (150, 450)},
        'hematocrit': {'male': (40, 52), 'female': (36, 48)},

        'creatinine': {'male': (0.7, 1.3), 'female': (0.6, 1.1)},
        'uric_acid': {'male': (3.4, 7.0), 'female': (2.4, 6.0)},
        'crp': {'normal': (0, 5)},
        'egfr': {'normal': (90, 200)},

        'fasting_blood_glucose': {'normal': (70, 99)}
    }

    def get_range(self, parameter, value, gender=None):

        ref = self.reference_ranges.get(parameter)

        if not ref:
            return "Unknown"

        if gender and gender in ref:
            low, high = ref[gender]
        elif 'normal' in ref:
            low, high = ref['normal']
        else:
            return "Unknown"

        if value < low:
            return "Low"
        elif value > high:
            return "High"
        else:
            return "Normal"



class DataExtractor:

    def __init__(self):

        self.patterns = {
            "hemoglobin": r"ha?emoglobin\s*[:\-]?\s*(\d+\.?\d*)",
            "rbc": r"\brbc\b\s*[:\-]?\s*(\d+\.?\d*)",
            "wbc": r"(total\s*wbc\s*count|wbc)\s*[:\-]?\s*(\d+\.?\d*)",
            "platelets": r"platelet\s*[:\-]?\s*(\d+\.?\d*)",
            "hematocrit": r"hematocrit\s*[:\-]?\s*(\d+\.?\d*)",
            "total_cholesterol": r"(total\s*cholesterol|cholesterol)\s*[:\-]?\s*(\d+\.?\d*)",
            "ldl": r"\bldl\b\s*[:\-]?\s*(\d+\.?\d*)",
            "hdl": r"\bhdl\b\s*[:\-]?\s*(\d+\.?\d*)",

            "creatinine": r"creatinine\s*[:\-]?\s*(\d+\.?\d*)",
            "uric_acid": r"uric\s*acid\s*[:\-]?\s*(\d+\.?\d*)",
            "crp": r"(c[-\s]*reactive\s*protein|crp)[^\d]*(\d+\.?\d*)",
            "egfr": r"egfr\s*[:\-]?\s*(\d+\.?\d*)",

            "fasting_blood_glucose": r"glucose\s*[:\-]?\s*(\d+\.?\d*)"
        }

    def extract_text_from_pdf(self, file):

        text = ""

        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"

        return text.lower()

    def extract_text_from_image(self, file):

        img = Image.open(file)
        return pytesseract.image_to_string(img).lower()

    def extract(self, text):

        data = {}

        for param, pattern in self.patterns.items():

            match = re.search(pattern, text)

            if match:
                try:
                    value = float(match.groups()[-1])
                    data[param] = {"value": value}
                except:
                    pass

        # gender
        g = re.search(r"(male|female)", text)
        if g:
            data["gender"] = {"value": g.group(1)}

        return data


class ParameterClassifier:

    def __init__(self, ref):
        self.ref = ref

    def classify(self, param, value, gender=None):

        if isinstance(gender, dict):
            gender = gender.get("value")

        if param not in self.ref.reference_ranges:
            return "Unknown"

        return self.ref.get_range(param, value, gender)



class RiskAssessor:

    def assess(self, data):

        score = 0
        factors = []

        if 'total_cholesterol' in data:
            if data['total_cholesterol']['value'] > 200:
                score += 1
                factors.append("High Cholesterol")

        if 'ldl' in data:
            if data['ldl']['value'] > 130:
                score += 1
                factors.append("High LDL")

        if 'hdl' in data:
            if data['hdl']['value'] < 40:
                score += 1
                factors.append("Low HDL")

        level = "Low"
        if score >= 3:
            level = "High"
        elif score >= 1:
            level = "Moderate"

        return {
            "score": score,
            "level": level,
            "factors": factors
        }



class FindingsSynthesizer:

    def synthesize(self, classifications, risk):

        conditions = []

        if 'hemoglobin' in classifications:
            if classifications['hemoglobin'] == "Low":
                conditions.append("Possible Anemia")

        if 'ldl' in classifications or 'total_cholesterol' in classifications:
            if risk["level"] != "Low":
                conditions.append("Possible Dyslipidemia")

        return {
            "conditions": conditions,
            "risk_level": risk["level"]
        }



class RecommendationEngine:

    def generate(self, classifications):

        recs = []

        if classifications.get("ldl") == "High":
            recs.append("Reduce saturated fat and increase exercise.")

        if classifications.get("hemoglobin") == "Low":
            recs.append("Consider iron-rich foods and consult doctor.")

        if classifications.get("fasting_blood_glucose") == "High":
            recs.append("Monitor blood sugar and reduce sugar intake.")

        return recs



class HealthAgent:

    def __init__(self):

        self.ref = HealthReferenceRanges()
        self.extractor = DataExtractor()
        self.classifier = ParameterClassifier(self.ref)
        self.risk = RiskAssessor()
        self.synth = FindingsSynthesizer()
        self.recommender = RecommendationEngine()

    def run(self, text):

        extracted = self.extractor.extract(text)

        gender = extracted.get("gender")

        classifications = {}

        for p, d in extracted.items():

            if p == "gender":
                continue

            classifications[p] = self.classifier.classify(
                p, d["value"], gender
            )

        risk = self.risk.assess(extracted)

        findings = self.synth.synthesize(classifications, risk)

        recs = self.recommender.generate(classifications)

        return extracted, classifications, risk, findings, recs



def generate_llm_report(classifications, risk, findings, recs):
    if client is None:
        return "LLM report unavailable. Set OPENAI_API_KEY to enable AI report generation."

    prompt = f"""
You are a medical AI assistant.

Classifications:
{classifications}

Risk:
{risk}

Findings:
{findings}

Recommendations:
{recs}

Generate a professional health report.
Include disclaimer: not medical diagnosis.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful medical AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception:
        return "LLM report generation failed. Please verify API key and network access."


def visualize(classifications):
    if not classifications:
        st.info("No parameters were extracted from the uploaded report.")
        return

    df = pd.DataFrame(
        [{"Parameter": k, "Status": v} for k, v in classifications.items()]
    )

    st.dataframe(df)

    counts = df["Status"].value_counts()

    fig = px.pie(
        values=counts.values,
        names=counts.index,
        title="Parameter Status Distribution"
    )

    st.plotly_chart(fig)


if "user" not in st.session_state:

    st.title("Login / Signup")

    menu = ["Login", "Signup"]
    choice = st.selectbox("Select", menu)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Signup":

        if st.button("Create Account"):
            if create_user(username, password):
                st.success("Account created")
            else:
                st.error("User exists")

    if choice == "Login":

        if st.button("Login"):
            user = login_user(username, password)

            if user:
                st.session_state.user = username
                st.success("Logged in")
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.stop()


def main():

    st.title("🩸 Multi-Model AI Health Diagnostics Agent")

    agent = HealthAgent()

    file = st.file_uploader(
        "Upload Blood Report",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if file:

        if file.type == "application/pdf":
            text = agent.extractor.extract_text_from_pdf(file)
        else:
            text = agent.extractor.extract_text_from_image(file)

        with st.spinner("Analyzing..."):

            extracted, classifications, risk, findings, recs = agent.run(text)

            st.subheader("Classifications")
            visualize(classifications)

            st.subheader("Risk Level")
            st.write(risk)

            st.subheader("Findings")
            st.write(findings)

            st.subheader("Recommendations")
            st.write(recs)

            report = generate_llm_report(
                classifications, risk, findings, recs
            )

            st.subheader("AI Medical Report")
            st.write(report)

            save_report(st.session_state.user, {
                "classifications": classifications,
                "risk": risk
                }
            )

            if st.button("View My Reports"):

                reports = get_reports(st.session_state.user)

                for r in reports:
                    st.write(r)

if __name__ == "__main__":
    main()
