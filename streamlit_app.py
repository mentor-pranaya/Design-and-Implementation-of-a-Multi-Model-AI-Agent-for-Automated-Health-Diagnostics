import os
import tempfile
import streamlit as st

from main import process_report_complete_pipeline


st.set_page_config(page_title="Lab Report Analyzer", layout="wide")

st.title("Lab Report Analyzer ")

uploaded = st.file_uploader("Upload a blood report (PDF)", type=["pdf"])
age = st.number_input("Age", min_value=0, max_value=130, value=35)
gender = st.selectbox("Gender", ["male", "female", "other"])
output_format = st.selectbox("Output format", ["text", "html", "json", "markdown"], index=0)
save_report = st.checkbox("Save report to workspace (./outputs)", value=True)

if st.button("Analyze"):
    if not uploaded:
        st.warning("Please upload a PDF report first.")
    else:
        out_dir = os.path.join(os.getcwd(), "outputs")
        os.makedirs(out_dir, exist_ok=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=out_dir) as tmp:
            tmp.write(uploaded.getbuffer())
            tmp_path = tmp.name

        try:
            result = process_report_complete_pipeline(tmp_path, age=age, gender=gender, output_format=output_format, save_to_file=save_report)
        except Exception as e:
            st.error(f"Processing failed: {e}")
        else:
            report_content = result.get("report")
            
            if output_format == "json":
                st.subheader("Report — JSON")
                st.json(result)
            elif output_format == "html":
                st.subheader("Report — HTML")
                st.components.v1.html(report_content, height=600, scrolling=True)
            elif output_format == "markdown":
                st.subheader("Report — Markdown")
                st.markdown(report_content)
            else:
                st.subheader("Report — Text")
                st.text(report_content)
            
