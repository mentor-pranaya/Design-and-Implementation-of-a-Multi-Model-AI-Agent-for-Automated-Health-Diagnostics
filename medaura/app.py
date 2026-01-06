%%writefile app.py

import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import re
import io
from datetime import datetime

import easyocr
import pdfplumber
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import plotly.express as px

# -------------------------------------------------
# STREAMLIT CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="MedAura",
    layout="wide",
    page_icon="🩺"
)

# -------------------------------------------------
# SESSION STATE INIT (CRITICAL)
# -------------------------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if "user" not in st.session_state:
    st.session_state.user = None

if "latest" not in st.session_state:
    st.session_state.latest = None

# -------------------------------------------------
# DATABASE
# -------------------------------------------------
conn = sqlite3.connect("medaura.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    age INTEGER,
    gender TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS health_logs (
    username TEXT,
    date TEXT,
    biomarker TEXT,
    value REAL
)
""")

conn.commit()

# -------------------------------------------------
# CONSTANTS
# -------------------------------------------------
REFERENCE_RANGES = {
    "Glucose": (70, 99),
    "Cholesterol": (125, 200),
    "Hemoglobin": (13.5, 17.5)
}

# -------------------------------------------------
# UTILITIES
# -------------------------------------------------
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

@st.cache_resource
def load_ocr():
    return easyocr.Reader(["en"])

def preprocess_image(img):
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return thresh

def extract_text_from_image(img):
    reader = load_ocr()
    processed = preprocess_image(img)
    results = reader.readtext(processed)
    return " ".join([r[1] for r in results])

def extract_text_from_pdf(file_bytes):
    text = ""

    # Try text-based extraction
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"

    # OCR fallback for scanned PDFs
    if len(text.strip()) < 100:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text += extract_text_from_image(img) + "\n"

    return text.strip()

def extract_text_from_report(file):
    if file.type == "application/pdf":
        return extract_text_from_pdf(file.read())
    else:
        return extract_text_from_image(Image.open(file))

def extract_biomarkers(text):
    patterns = {
        "Glucose": r"Glucose\s*[:\-]?\s*(\d+\.?\d*)",
        "Cholesterol": r"Cholesterol\s*[:\-]?\s*(\d+\.?\d*)",
        "Hemoglobin": r"Hemoglobin\s*[:\-]?\s*(\d+\.?\d*)"
    }
    found = {}
    for k, p in patterns.items():
        m = re.search(p, text, re.IGNORECASE)
        if m:
            found[k] = float(m.group(1))
    return found

def get_last_two(username, biomarker):
    df = pd.read_sql(
        """
        SELECT value, date FROM health_logs
        WHERE username=? AND biomarker=?
        ORDER BY date DESC LIMIT 2
        """,
        conn,
        params=(username, biomarker)
    )
    if len(df) < 2:
        return None
    return df.iloc[0], df.iloc[1]

def analyze_delta(curr, prev):
    delta = curr - prev
    pct = (delta / prev) * 100 if prev != 0 else 0
    if abs(pct) < 5:
        return pct, "stable"
    elif pct >= 15:
        return pct, "sudden increase"
    elif pct >= 5:
        return pct, "gradual increase"
    elif pct <= -5:
        return pct, "decrease"
    return pct, "stable"

# -------------------------------------------------
# SIDEBAR AUTH
# -------------------------------------------------
with st.sidebar:
    st.title("🔐 MedAura Secure")

    if not st.session_state.auth:
        mode = st.radio("Mode", ["Login", "Sign Up"])
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if mode == "Sign Up":
            age = st.number_input("Age", 18, 100)
            gender = st.selectbox("Gender", ["Male", "Female"])
            if st.button("Create Account"):
                c.execute(
                    "INSERT OR REPLACE INTO users VALUES (?,?,?,?)",
                    (u, hash_password(p), age, gender)
                )
                conn.commit()
                st.success("Account created")
        else:
            if st.button("Login"):
                res = c.execute(
                    "SELECT * FROM users WHERE username=?",
                    (u,)
                ).fetchone()
                if res and hash_password(p) == res[1]:
                    st.session_state.auth = True
                    st.session_state.user = {
                        "name": res[0],
                        "age": res[2],
                        "gender": res[3]
                    }
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    else:
        st.success(f"Logged in as {st.session_state.user['name']}")
        if st.button("Logout"):
            st.session_state.auth = False
            st.session_state.user = None
            st.rerun()

# -------------------------------------------------
# MAIN APP
# -------------------------------------------------
# ---- AUTH GUARD (CRITICAL) ----
if not st.session_state.auth or st.session_state.user is None:
    st.info("Please login to continue.")
    st.stop()

user = st.session_state.user
username = user.get("name")

if not username:
    st.error("Session error. Please log in again.")
    st.session_state.auth = False
    st.session_state.user = None
    st.stop()


st.title("🧠 Personal Health Dashboard")

tab1, tab2 = st.tabs(["📄 New Report", "📈 History"])

# ---------------- NEW REPORT ----------------
with tab1:
    uploaded = st.file_uploader(
        "Upload Lab Report (Image or PDF)",
        ["png", "jpg", "jpeg", "pdf"]
    )

    if uploaded and st.button("Analyze My Report"):
        raw_text = extract_text_from_report(uploaded)

        if len(raw_text) < 50:
            st.error("Could not extract readable text.")
            st.stop()

        biomarkers = extract_biomarkers(raw_text)
        today = datetime.now().strftime("%Y-%m-%d")

        for k, v in biomarkers.items():
            c.execute(
                "INSERT INTO health_logs VALUES (?,?,?,?)",
                (username, today, k, v)
            )
        conn.commit()

        st.session_state.latest = biomarkers
        st.success("Report analyzed successfully")

        with st.expander("🔍 Extracted Text (Debug)"):
            st.text(raw_text[:3000])

    if st.session_state.latest:
        st.subheader("📊 Personal Trend Analysis")

        for biomarker, val in st.session_state.latest.items():
            baseline = get_last_two(username, biomarker)

            if not baseline:
                st.info(f"{biomarker}: First recorded value ({val})")
                continue

            curr, prev = baseline
            pct, trend = analyze_delta(curr["value"], prev["value"])

            st.markdown(f"""
            **{biomarker}**
            - Current: {curr['value']}
            - Previous: {prev['value']} ({prev['date']})
            - Change: {pct:.2f}% → {trend}
            """)

# ---------------- HISTORY ----------------
with tab2:
    df = pd.read_sql(
        "SELECT date, biomarker, value FROM health_logs WHERE username=?",
        conn,
        params=(username,)
    )

    if df.empty:
        st.info("No history yet.")
    else:
        fig = px.line(
            df,
            x="date",
            y="value",
            color="biomarker",
            markers=True,
            title="Biomarker Trends"
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Raw Data"):
            st.dataframe(df.sort_values("date", ascending=False))
