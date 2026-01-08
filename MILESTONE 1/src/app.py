import streamlit as st
from src.parser import parse_input
from src.extractor import extract_data
from src.validator import standardize_data
from src.interpreter import interpret_parameters

st.set_page_config(page_title="HealthAI Diagnostics", layout="wide")

st.title("🩸 Milestone 1: Automated Blood Report Extraction")

uploaded_file = st.file_uploader("Upload Blood Report (PDF, Image, JSON)", type=['pdf', 'png', 'jpg', 'json'])

if uploaded_file:
    # 1. Parsing
    raw_content, content_type = parse_input(uploaded_file)
    
    # 2. Extraction
    if content_type == "text":
        structured_data = extract_data(raw_content)
        
        # 3. Validation
        valid_data = standardize_data(structured_data)
        
        # 4. Interpretation
        final_report = interpret_parameters(valid_data)
        
        st.subheader("Interpreted Results")
        st.table(final_report)
