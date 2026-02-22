
import streamlit as st
import pandas as pd
import time
from health_agent import HealthAgent, CommonInterpreter, Preprocessor
from pdf_report import generate_pdf


st.set_page_config(
    page_title="AI Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    /* Global Theme Overrides */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        background-image: radial-gradient(#1c1c1c 20%, transparent 20%), radial-gradient(#1c1c1c 20%, transparent 20%);
        background-position: 0 0, 50px 50px;
        background-size: 100px 100px;
    }
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #374151;
    }
    
    /* Typography */
    h1 {
        color: #ffffff !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    h2, h3 {
        color: #f3f4f6 !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
    }
    p, label, .stMarkdown {
        color: #e5e7eb !important;
        font-size: 16px;
    }
    
    /* Upload Widget */
    [data-testid="stFileUploader"] {
        background-color: #1f2937;
        border-radius: 10px;
        padding: 20px;
        border: 1px dashed #4b5563;
    }
    [data-testid="stFileUploader"] label {
        color: #38bdf8 !important; /* Sky Blue */
        font-size: 1.2rem;
        font-weight: 700;
        font-family: 'Helvetica Neue', sans-serif;
    }
    [data-testid="stFileUploader"] section {
        background-color: transparent;
    }
    /* Upload Instructions & Filename */
    [data-testid="stFileUploader"] div, [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] p {
        color: #fbbf24 !important; /* Bright Amber */
        font-weight: 600;
        opacity: 1 !important;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(145deg, #1f2937, #111827);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
        text-align: center;
        border: 1px solid #374151;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #60a5fa;
    }
    .metric-card h3 {
        color: #9ca3af !important;
        font-size: 14px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-card p {
        color: #f9fafb !important;
        font-size: 28px;
        font-weight: bold;
        margin: 0;
    }
    
    /* Advice Box */
    .advice-box {
        background-color: rgba(6, 78, 59, 0.4);
        color: #d1fae5 !important;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #10b981;
        margin-top: 10px;
    }
    
    /* Warning Box */
    .warning-box {
        background-color: rgba(127, 29, 29, 0.4);
        color: #fee2e2 !important;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #ef4444;
        margin-top: 10px;
    }
    
    /* Download Button Override */
    [data-testid="stDownloadButton"] button {
        background-color: #f3f4f6 !important;
        color: #000000 !important;
        font-weight: 700;
        border: 1px solid #d1d5db !important;
    }
    [data-testid="stDownloadButton"] button p {
        color: #000000 !important;
        font-weight: 700;
    }
    [data-testid="stDownloadButton"] button:hover {
        background-color: #e5e7eb !important;
        color: #000000 !important;
        border-color: #9ca3af !important;
    }
    [data-testid="stDownloadButton"] button:hover p {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Agent
if 'agent' not in st.session_state:
    st.session_state.agent = HealthAgent()
    st.session_state.interpreter = CommonInterpreter()
    st.session_state.preprocessor = Preprocessor()


with st.sidebar:
    st.title("🩺 AI Health Agent")
    st.markdown("---")
    st.markdown("**Capabilities:**")
    st.markdown("- 📄 PDF Report Analysis")
    st.markdown("- 🖼️ Image OCR Analysis")
    st.markdown("- 📊 CSV Data Support")
    st.markdown("- 💾 External JSON Support")
    st.markdown("---")
    
    # Tesseract OCR Configuration
    try:
        import pytesseract
        import os
        
        # Verify Tesseract installation
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            tesseract_cmd_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\LENOVO\AppData\Local\Tesseract-OCR\tesseract.exe"
            ]
            for path in tesseract_cmd_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
        
        # Verify configuration was successful
        pytesseract.get_tesseract_version()

    except Exception:
        st.error("❌ OCR Engine Missing")
        st.warning("To process images, please install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) and set it in your PATH.")

    st.info("Upload your medical report to get personalized insights and risk assessments.")
    
    st.markdown("---")
    st.markdown("**Patient History**")
    prev_conditions = st.multiselect(
        "Known Medical Conditions",
        [
            "Diabetes", "Hypertension", "Heart Disease", "Thyroid Disorder", 
            "Kidney Disease", "Anemia", "Liver Disease", "Asthma", 
            "COPD", "Arthritis", "Autoimmune Disease", "Gout", 
            "Obesity", "Bleeding Disorder"
        ],
        default=[],
        help="Select any pre-existing conditions so the AI can tailor its recommendations."
    )



# Hero Section
st.title("Automated Health Diagnostics")
st.markdown("### Upload your medical report for instant AI analysis")

uploaded_file = st.file_uploader(
    "Drag & Drop your report here (PDF, CSV, JPG, PNG, JSON)", 
    type=['pdf', 'csv', 'jpg', 'png', 'jpeg', 'json']
)

if uploaded_file is not None:
    # Processing Spinner
    with st.spinner('🤖 AI Agent is analyzing your report...'):
        time.sleep(1) # Simulate slight delay for effect
        
        try:

            # 1. FILE INGESTION
            raw_text = ""
            df = pd.DataFrame()
            
            file_type = uploaded_file.name.split('.')[-1].lower()
            
            if file_type == 'json':
                df = st.session_state.interpreter.read_json(uploaded_file)
            else:
                # For standard files, attempt direct reading
                df = st.session_state.interpreter.read_file(uploaded_file.name, file_obj=uploaded_file)
                
                if file_type == 'pdf':
                    raw_text = st.session_state.interpreter.extract_text_from_pdf(uploaded_file)
                
                elif file_type in ['jpg', 'jpeg', 'png']:
                    # Image processing requires a physical file for Tesseract/PIL stability in some environments.
                    # Save the uploaded buffer to a temporary file.
                    with open(uploaded_file.name, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Extract text for context analysis (identifying age/gender)
                    raw_text = st.session_state.interpreter.extract_text_from_image(uploaded_file.name)
                    
                    # Re-read structured data now that file exists on disk, ensuring robust OCR
                    df = st.session_state.interpreter.read_file(uploaded_file.name)
            
            # 2. DATA NORMALIZATION
            # Standardize column names to match internal knowledge base keys
            
            # 3. INTELLIGENT ANALYSIS
            # Run the health agent pipeline: Context Extraction -> Rule Adjustment -> Biomarker Analysis -> Risk Assessment
            results = st.session_state.agent.process_data(df, raw_text, prev_conditions=prev_conditions)
            
            st.markdown("---")
            
            st.subheader("📊 Analysis Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                age_val = results['patient']['age']
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Age</h3>
                    <p>{age_val if age_val else "Unknown"} { "Years" if age_val else ""}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                gender_val = results['patient']['gender']
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Gender</h3>
                    <p>{gender_val if gender_val else "Unknown"}</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                risk_count = len(results['risks'])
                color = "#ef4444" if risk_count > 0 else "#10b981"
                st.markdown(f"""
                <div class="metric-card" style="border-color: {color}">
                    <h3>Risks Detected</h3>
                    <p style="color: {color}">{risk_count}</p>
                </div>
                """, unsafe_allow_html=True)

            # Two Column Layout for Details
            c1, c2 = st.columns([2, 1])
            
            with c1:
                st.markdown("### 🧬 Biomarker Analysis")
                if results['detailed_biomarkers']:
                    st.dataframe(
                        pd.DataFrame(results['detailed_biomarkers']), 
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.warning("No structured biomarkers extracted. Please check file quality.")

            with c2:
                st.markdown("### ⚠️ Risk Patterns")
                if results['risks']:
                    for risk in results['risks']:
                        st.markdown(f"""
                        <div class="warning-box">
                            <strong>{risk['Pattern']}</strong><br>
                            <span style="font-size: 12px">{risk['Significance']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("No complex risk patterns detected.")

            # Recommendations
            if results.get('advice'):
                st.success(results['advice'])
            
            # Report Download - Generate PDF
            try:
                pdf_bytes = generate_pdf(results)
                
                st.download_button(
                    label="📥 Download Full Report",
                    data=pdf_bytes,
                    file_name="AI_Health_Report.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error generating PDF: {e}")
                # Fallback to plain text if PDF generation fails
                df_str = pd.DataFrame(results.get('detailed_biomarkers', [])).to_string(index=False)
                report_text = f"AI HEALTH DIAGNOSTICS REPORT\n\nFallback Plain Text (PDF error: {e})\n\n{df_str}"
                st.download_button(
                    label="📥 Download Raw Text (Fallback)",
                    data=report_text,
                    file_name="AI_Health_Report.txt",
                    mime="text/plain"
                )

        except Exception as e:
            st.error(f"Error processing file: {e}")
            import traceback
            st.code(traceback.format_exc())

else:
    # Empty State
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; color: #6b7280;">
        <h2>👋 Welcome!</h2>
        <p>Please upload a file to start the diagnostic process.</p>
    </div>
    """, unsafe_allow_html=True)
