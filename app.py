"""
Health Diagnostics System - Streamlit UI
Professional Medical-Themed Web Interface
"""

import streamlit as st
import tempfile
import os
import json
from datetime import datetime

from src.orchestrator.workflow import HealthDiagnosticsOrchestrator
from src.reporting.report_generator import ReportGenerator


# PAGE CONFIGURATION

st.set_page_config(
    page_title="Health Diagnostics System",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================
# CUSTOM CSS - MEDICAL THEME (COMPLETE FIX)
# ============================================

st.markdown("""
<style>
    /* ===== GLOBAL STYLES ===== */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ===== FORCE ALL TEXT TO BE VISIBLE ===== */
    * {
        color: #1E293B;
    }
    
    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3, h4, h5, h6 {
        color: #1E293B !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    p, span, div, label, li {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #1E293B;
    }
    
    /* ===== FILE UPLOADER - COMPLETE FIX ===== */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
    }
    
    [data-testid="stFileUploader"] label {
        color: #1E293B !important;
    }
    
    [data-testid="stFileUploader"] section {
        background-color: #FFFFFF !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    [data-testid="stFileUploader"] section:hover {
        border-color: #2563EB !important;
    }
    
    /* File uploader text - "Drag and drop file here" */
    [data-testid="stFileUploader"] section > div {
        color: #64748B !important;
    }
    
    [data-testid="stFileUploader"] section > div > div {
        color: #64748B !important;
    }
    
    [data-testid="stFileUploader"] section > div > div > span {
        color: #64748B !important;
    }
    
    [data-testid="stFileUploader"] section span {
        color: #64748B !important;
    }
    
    [data-testid="stFileUploader"] section small {
        color: #94A3B8 !important;
    }
    
    /* File uploader - uploaded file info */
    [data-testid="stFileUploader"] section > div:last-child {
        color: #1E293B !important;
    }
    
    /* File size limit text */
    [data-testid="stFileUploader"] section [data-testid="stMarkdownContainer"] p {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
    }
    
    /* Browse files button */
    [data-testid="stFileUploader"] button {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stFileUploader"] button:hover {
        background-color: #334155 !important;
    }
    
    /* Uploaded file name display */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] {
        color: #1E293B !important;
    }
    
    /* ===== EXPANDER - COMPLETE FIX ===== */
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 8px !important;
        margin-bottom: 0.5rem !important;
    }
    
    [data-testid="stExpander"] summary {
        color: #1E293B !important;
        font-weight: 500 !important;
        padding: 0.75rem 1rem !important;
        background-color: #FFFFFF !important;
    }
    
    [data-testid="stExpander"] summary:hover {
        background-color: #F8FAFC !important;
    }
    
    [data-testid="stExpander"] summary span {
        color: #1E293B !important;
    }
    
    [data-testid="stExpander"] summary p {
        color: #1E293B !important;
    }
    
    [data-testid="stExpander"] summary svg {
        fill: #1E293B !important;
        stroke: #1E293B !important;
    }
    
    [data-testid="stExpander"] > div {
        padding: 0 1rem 1rem 1rem !important;
        background-color: #FFFFFF !important;
    }
    
    [data-testid="stExpander"] > div > div {
        color: #1E293B !important;
    }
    
    /* Legacy expander classes */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
    }
    
    .streamlit-expanderHeader p {
        color: #1E293B !important;
    }
    
    .streamlit-expanderContent {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
    }
    
    /* ===== HEADER STYLES ===== */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E293B !important;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        color: #64748B !important;
        font-weight: 400;
    }
    
    .title-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* ===== CARD STYLES ===== */
    .card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
    }
    
    .card-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1E293B !important;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #E5E7EB;
    }
    
    /* ===== UPLOAD SECTION ===== */
    .upload-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 2px dashed #CBD5E1;
        text-align: center;
        max-width: 600px;
        margin: 0 auto 1rem auto;
    }
    
    .upload-card:hover {
        border-color: #2563EB;
    }
    
    .upload-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1E293B !important;
        margin-bottom: 0.5rem;
    }
    
    .upload-subtitle {
        font-size: 0.9rem;
        color: #64748B !important;
        margin-bottom: 0;
    }
    
    /* ===== METRIC CARDS ===== */
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        border: 1px solid #E5E7EB;
        text-align: center;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1E293B !important;
    }
    
    /* ===== RISK ASSESSMENT ===== */
    .risk-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
        text-align: center;
    }
    
    .risk-score {
        font-size: 3.5rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .risk-score-minimal { color: #16A34A !important; }
    .risk-score-low { color: #F59E0B !important; }
    .risk-score-moderate { color: #EA580C !important; }
    .risk-score-high { color: #DC2626 !important; }
    
    .risk-label {
        font-size: 0.9rem;
        color: #64748B !important;
        margin-bottom: 1rem;
    }
    
    .risk-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-minimal {
        background-color: #DCFCE7;
        color: #166534 !important;
    }
    
    .badge-low {
        background-color: #FEF3C7;
        color: #92400E !important;
    }
    
    .badge-moderate {
        background-color: #FFEDD5;
        color: #C2410C !important;
    }
    
    .badge-high {
        background-color: #FEE2E2;
        color: #991B1B !important;
    }
    
    /* ===== PARAMETER CARDS ===== */
    .param-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
        margin-bottom: 0.75rem;
    }
    
    .param-name {
        font-size: 0.85rem;
        color: #64748B !important;
        margin-bottom: 0.25rem;
    }
    
    .param-value {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1E293B !important;
        margin-bottom: 0.25rem;
    }
    
    .param-status {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        display: inline-block;
    }
    
    .status-normal {
        background-color: #DCFCE7;
        color: #166534 !important;
    }
    
    .status-low {
        background-color: #FEE2E2;
        color: #991B1B !important;
    }
    
    .status-high {
        background-color: #FEF3C7;
        color: #92400E !important;
    }
    
    .status-borderline {
        background-color: #FEF9C3;
        color: #854D0E !important;
    }
    
    .status-unknown {
        background-color: #F3F4F6;
        color: #6B7280 !important;
    }
    
    /* ===== AI INSIGHTS ===== */
    .insights-card {
        background-color: #EFF6FF;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #BFDBFE;
        margin-bottom: 1rem;
    }
    
    .insights-header {
        font-size: 1rem;
        font-weight: 600;
        color: #1E40AF !important;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .insights-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .insights-list li {
        padding: 0.5rem 0;
        padding-left: 1.5rem;
        position: relative;
        color: #1E3A5F !important;
        font-size: 0.95rem;
    }
    
    .insights-list li::before {
        content: "•";
        color: #2563EB !important;
        font-weight: bold;
        position: absolute;
        left: 0;
    }
    
    /* ===== FINDINGS BADGES ===== */
    .finding-item {
        display: flex;
        align-items: center;
        padding: 0.75rem 1rem;
        background-color: #FFFFFF;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid;
    }
    
    .finding-item span {
        color: #1E293B !important;
    }
    
    .finding-critical {
        border-left-color: #DC2626;
        background-color: #FEF2F2;
    }
    
    .finding-abnormal {
        border-left-color: #F59E0B;
        background-color: #FFFBEB;
    }
    
    .finding-borderline {
        border-left-color: #EAB308;
        background-color: #FEFCE8;
    }
    
    .finding-label {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        margin-right: 0.75rem;
        text-transform: uppercase;
    }
    
    .label-critical {
        background-color: #DC2626;
        color: #FFFFFF !important;
    }
    
    .label-abnormal {
        background-color: #F59E0B;
        color: #FFFFFF !important;
    }
    
    .label-borderline {
        background-color: #EAB308;
        color: #FFFFFF !important;
    }
    
    /* ===== RECOMMENDATION CARD ===== */
    .recommendation-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
    }
    
    .recommendation-card strong {
        color: #1E293B !important;
    }
    
    .recommendation-card span {
        color: #64748B !important;
    }
    
    /* ===== DISCLAIMER ===== */
    .disclaimer-box {
        background-color: #F9FAFB;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        border: 1px solid #E5E7EB;
        margin-top: 2rem;
    }
    
    .disclaimer-text {
        font-size: 0.85rem;
        color: #6B7280 !important;
        margin: 0;
        line-height: 1.5;
    }
    
    .disclaimer-text strong {
        color: #4B5563 !important;
    }
    
    /* ===== SECTION HEADERS ===== */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1E293B !important;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E5E7EB;
    }
    
    /* ===== DOWNLOAD BUTTONS ===== */
    .download-section {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #E5E7EB;
        text-align: center;
    }
    
    .stDownloadButton button {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
    }
    
    .stDownloadButton button:hover {
        background-color: #334155 !important;
    }
    
    .stDownloadButton button p {
        color: #FFFFFF !important;
    }
    
    /* ===== DIVIDER ===== */
    .section-divider {
        height: 1px;
        background-color: #E5E7EB;
        margin: 2rem 0;
    }
    
    /* ===== PROCESSING INFO ===== */
    .processing-info {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 1rem;
        font-size: 0.85rem;
        color: #64748B !important;
    }
    
    .processing-info strong {
        color: #1E293B !important;
    }
    
    /* ===== SPINNER ===== */
    .stSpinner > div {
        color: #2563EB !important;
    }
    
    .stSpinner > div > div {
        color: #64748B !important;
    }
    
    /* ===== ALERTS (INFO/WARNING/ERROR) ===== */
    .stAlert {
        border-radius: 8px !important;
    }
    
    .stAlert > div {
        color: #1E293B !important;
    }
    
    [data-testid="stAlertContainer"] {
        color: #1E293B !important;
    }
    
    [data-testid="stAlertContainer"] p {
        color: #1E293B !important;
    }
    
    /* ===== MARKDOWN TEXT ===== */
    .stMarkdown {
        color: #1E293B !important;
    }
    
    .stMarkdown p {
        color: #1E293B !important;
    }
    
    .stMarkdown li {
        color: #1E293B !important;
    }
    
    .stMarkdown strong {
        color: #1E293B !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1E293B !important;
    }
    
    [data-testid="stMarkdownContainer"] {
        color: #1E293B !important;
    }
    
    [data-testid="stMarkdownContainer"] p {
        color: #1E293B !important;
    }
    
    /* ===== WELCOME CARD ===== */
    .welcome-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
        text-align: center;
    }
    
    .welcome-card h3 {
        color: #1E293B !important;
        margin-bottom: 1rem;
    }
    
    .welcome-card p {
        color: #64748B !important;
        margin-bottom: 1.5rem;
    }
    
    .welcome-feature {
        text-align: center;
    }
    
    .welcome-feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .welcome-feature-text {
        font-size: 0.9rem;
        color: #64748B !important;
    }
    
    /* ===== COLUMNS ===== */
    [data-testid="column"] {
        background-color: transparent;
    }
    
    /* ===== WIDGET LABELS ===== */
    .stTextInput label, .stSelectbox label, .stMultiSelect label {
        color: #1E293B !important;
    }
    # Add this to your CSS section

    /* ===== FILE UPLOADER X BUTTON FIX ===== */
    [data-testid="stFileUploader"] button[kind="secondary"] {
        background-color: #F3F4F6 !important;
        color: #1E293B !important;
        border: 1px solid #E5E7EB !important;
    }
    
    [data-testid="stFileUploader"] button[kind="secondary"]:hover {
        background-color: #E5E7EB !important;
    }
    
    /* X button specifically */
    [data-testid="stFileUploader"] [data-testid="baseButton-secondary"] {
        background-color: #F3F4F6 !important;
        color: #DC2626 !important;
        border: 1px solid #E5E7EB !important;
    }
    
    [data-testid="stFileUploader"] svg {
        fill: #1E293B !important;
        stroke: #1E293B !important;
    }
    
    /* File delete button */
    [data-testid="stFileUploader"] [aria-label="Delete file"] {
        background-color: #FEE2E2 !important;
        color: #DC2626 !important;
    }
    
    [data-testid="stFileUploader"] [aria-label="Delete file"] svg {
        fill: #DC2626 !important;
        stroke: #DC2626 !important;
    }

    /* ===== FILE UPLOADER X BUTTON VISIBILITY ===== */
    [data-testid="stFileUploader"] button {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #E5E7EB !important;
    }

    [data-testid="stFileUploader"] svg {
        fill: #DC2626 !important;
    }

    [data-testid="stFileUploader"] [aria-label*="delete" i] svg,
    [data-testid="stFileUploader"] [aria-label*="remove" i] svg {
        fill: #DC2626 !important;
    }

</style>
""", unsafe_allow_html=True)

# HELPER FUNCTIONS

def render_header():
    """Render the main header"""
    st.markdown("""
        <div class="main-header">
            <div class="title-icon">⚕️</div>
            <div class="main-title">Health Diagnostics System</div>
            <div class="main-subtitle">AI-Powered Blood Report Analysis</div>
        </div>
    """, unsafe_allow_html=True)


def render_upload_section():
    """Render the upload section"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Upload Blood Report")
        st.caption("Supported formats: PDF, Images (JPG, PNG), JSON")
        
        uploaded_file = st.file_uploader(
            "Upload your blood report",
            type=["jpg", "jpeg", "png", "pdf", "json"],
            label_visibility="collapsed",
            help="Drag and drop or click to browse"
        )
        
        return uploaded_file


def render_patient_info(patient_info):
    """Render patient information section"""
    st.markdown('<div class="section-header">Patient Information</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    age = patient_info.get("age")
    gender = patient_info.get("gender")
    age_group = patient_info.get("age_group")
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Age</div>
                <div class="metric-value">{f"{age} years" if age else "Not detected"}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Gender</div>
                <div class="metric-value">{gender.capitalize() if gender else "Not detected"}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Category</div>
                <div class="metric-value">{age_group.capitalize() if age_group else "N/A"}</div>
            </div>
        """, unsafe_allow_html=True)


def render_risk_assessment(risk_assessment):
    """Render risk assessment section"""
    st.markdown('<div class="section-header">Risk Assessment</div>', unsafe_allow_html=True)
    
    score = risk_assessment.get("overall_score", 0)
    level = risk_assessment.get("risk_level", "UNKNOWN")
    
    # Determine color class
    if "MINIMAL" in level:
        score_class = "risk-score-minimal"
        badge_class = "badge-minimal"
    elif "LOW" in level:
        score_class = "risk-score-low"
        badge_class = "badge-low"
    elif "MODERATE" in level:
        score_class = "risk-score-moderate"
        badge_class = "badge-moderate"
    else:
        score_class = "risk-score-high"
        badge_class = "badge-high"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
            <div class="risk-card">
                <div class="risk-score {score_class}">{score}</div>
                <div class="risk-label">out of 100</div>
                <div class="risk-badge {badge_class}">{level}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Show individual risks
    st.markdown("<br>", unsafe_allow_html=True)
    
    individual_risks = risk_assessment.get("individual_risks", [])
    active_risks = [r for r in individual_risks if r.get("score", 0) > 0]
    
    if active_risks:
        cols = st.columns(len(active_risks))
        for i, risk in enumerate(active_risks):
            with cols[i]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{risk.get('category', '')}</div>
                        <div class="metric-value">{risk.get('score', 0)}/100</div>
                    </div>
                """, unsafe_allow_html=True)


def render_parameters(parameters):
    """Render parameters section"""
    st.markdown('<div class="section-header">Parameter Overview</div>', unsafe_allow_html=True)
    
    # Filter out Age and Gender, and None values
    param_list = [
        (name, data) for name, data in parameters.items() 
        if name not in ["Age", "Gender"] and data is not None
    ]
    
    # Display in rows of 3
    for i in range(0, len(param_list), 3):
        cols = st.columns(3)
        
        for j, col in enumerate(cols):
            if i + j < len(param_list):
                name, data = param_list[i + j]
                
                value = data.get("value", "--")
                unit = data.get("unit", "")
                status = data.get("status", "UNKNOWN")
                
                # Determine status class
                status_lower = status.lower()
                if status_lower == "normal":
                    status_class = "status-normal"
                elif status_lower == "low":
                    status_class = "status-low"
                elif status_lower == "high":
                    status_class = "status-high"
                elif "borderline" in status_lower:
                    status_class = "status-borderline"
                else:
                    status_class = "status-unknown"
                
                with col:
                    st.markdown(f"""
                        <div class="param-card">
                            <div class="param-name">{name}</div>
                            <div class="param-value">{value} {unit}</div>
                            <span class="param-status {status_class}">{status}</span>
                        </div>
                    """, unsafe_allow_html=True)
    
    # Missing parameters are intentionally omitted from the UI.


def render_key_findings(synthesis):
    """Render key findings section"""
    key_findings = synthesis.get("key_findings", [])
    
    if not key_findings:
        st.markdown("""
            <div class="insights-card">
                <div class="insights-header">✓ All Clear</div>
                <p style="color: #166534; margin: 0;">All parameters are within normal range. No concerns identified.</p>
            </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown('<div class="section-header">Key Findings</div>', unsafe_allow_html=True)
    
    for finding in key_findings:
        finding_type = finding.get("type", "info")
        text = finding.get("text", "")
        
        if finding_type == "critical":
            finding_class = "finding-critical"
            label_class = "label-critical"
            label_text = "Critical"
        elif finding_type == "abnormal":
            finding_class = "finding-abnormal"
            label_class = "label-abnormal"
            label_text = "Abnormal"
        else:
            finding_class = "finding-borderline"
            label_class = "label-borderline"
            label_text = "Borderline"
        
        st.markdown(f"""
            <div class="finding-item {finding_class}">
                <span class="finding-label {label_class}">{label_text}</span>
                <span>{text}</span>
            </div>
        """, unsafe_allow_html=True)


def render_ai_insights(synthesis):
    """Render AI insights section"""
    summary = synthesis.get("summary_text", "")
    
    if not summary:
        return
    
    st.markdown('<div class="section-header">AI Insights</div>', unsafe_allow_html=True)
    
    # Split summary into bullet points
    sentences = summary.split(". ")
    sentences = [s.strip() + "." for s in sentences if s.strip()]
    
    bullet_points = "".join([f"<li>{s}</li>" for s in sentences])
    
    st.markdown(f"""
        <div class="insights-card">
            <div class="insights-header">
                <span>👩🏻‍⚕️</span>
                <span>Clinical Summary</span>
            </div>
            <ul class="insights-list">
                {bullet_points}
            </ul>
        </div>
    """, unsafe_allow_html=True)


def render_patterns(patterns):
    """Render detected patterns section"""
    if not patterns:
        return
    
    st.markdown('<div class="section-header">Detected Patterns</div>', unsafe_allow_html=True)
    
    for pattern in patterns:
        pattern_name = pattern.get("pattern", "Unknown")
        confidence = pattern.get("confidence", 0)
        description = pattern.get("description", "")
        indicators = pattern.get("indicators", [])
        
        with st.expander(f"🔍 {pattern_name} (Confidence: {confidence}%)"):
            st.markdown(f"**Assessment:** {description}")
            
            if indicators:
                st.markdown("**Indicators:**")
                for indicator in indicators:
                    st.markdown(f"- {indicator}")


def render_recommendations(recommendations):
    """Render recommendations section"""
    if not recommendations:
        return
    
    st.markdown('<div class="section-header">Personalized Recommendations</div>', unsafe_allow_html=True)
    
    # Priority and summary
    priority = recommendations.get("overall_priority", "MEDIUM")
    summary = recommendations.get("summary", "")
    
    st.markdown(f"""
        <div class="recommendation-card">
            <strong>Priority Level:</strong> {priority}<br>
            <span>{summary}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Condition-specific recommendations
    for rec in recommendations.get("condition_recommendations", []):
        condition = rec.get("linked_condition", "General")
        timeline = rec.get("timeline", "")
        
        with st.expander(f"📋 {condition} - {timeline}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                # Diet
                diet = rec.get("diet", [])
                if diet:
                    st.markdown("**🥗 Diet Recommendations**")
                    for item in diet:
                        st.markdown(f"- {item}")
                
                # Follow-up
                followup = rec.get("followup", [])
                if followup:
                    st.markdown("**📅 Follow-up Actions**")
                    for item in followup:
                        st.markdown(f"- {item}")
            
            with col2:
                # Lifestyle
                lifestyle = rec.get("lifestyle", [])
                if lifestyle:
                    st.markdown("**🧘🏻‍♀️ Lifestyle Modifications**")
                    for item in lifestyle:
                        st.markdown(f"- {item}")
                
                # Warnings
                warnings = rec.get("warnings", [])
                if warnings:
                    st.markdown("**⚠️ Important Warnings**")
                    for item in warnings:
                        st.markdown(f"- {item}")
    
    # Age and gender specific notes
    age_advice = recommendations.get("age_specific_advice", {})
    gender_advice = recommendations.get("gender_specific_advice", {})
    
    if age_advice.get("notes") or gender_advice.get("notes"):
        with st.expander("📌 Patient-Specific Notes", expanded=False):
            if age_advice.get("notes"):
                st.info(f"**Age-related:** {age_advice['notes']}")
                if age_advice.get("diet_modifier"):
                    st.markdown(f"*Dietary note: {age_advice['diet_modifier']}*")
            
            if gender_advice.get("notes"):
                st.info(f"**Gender-related:** {gender_advice['notes']}")
    
    # # Age and gender specific notes
    # age_advice = recommendations.get("age_specific_advice", {})
    # gender_advice = recommendations.get("gender_specific_advice", {})
    
    # if age_advice.get("notes") or gender_advice.get("notes"):
    #     with st.expander("📌 Patient-Specific Notes"):
    #         if age_advice.get("notes"):
    #             st.info(f"**Age-related:** {age_advice['notes']}")
    #             if age_advice.get("diet_modifier"):
    #                 st.markdown(f"*Dietary note: {age_advice['diet_modifier']}*")
            
    #         if gender_advice.get("notes"):
    #             st.info(f"**Gender-related:** {gender_advice['notes']}")


def render_download_section(results):
    """Render download section"""
    st.markdown('<div class="section-header">Download Report</div>', unsafe_allow_html=True)
    
    report_gen = ReportGenerator(results)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        
        dcol1, dcol2, dcol3 = st.columns(3)

        if not report_gen.weasyprint_available:
            st.info("Styled PDF is unavailable. Install WeasyPrint to enable the full-color PDF layout.")
        
        with dcol1:
            text_report = report_gen.generate_text_report()
            st.download_button(
                label="📄 Download Text Report",
                data=text_report,
                file_name=f"health_report_{report_gen.report_id}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with dcol2:
            json_report = report_gen.generate_json_report()
            st.download_button(
                label="📊 Download JSON Report",
                data=json.dumps(json_report, indent=2),
                file_name=f"health_report_{report_gen.report_id}.json",
                mime="application/json",
                use_container_width=True
            )

        with dcol3:
            pdf_report = report_gen.generate_pdf_report()
            st.download_button(
                label="🧾 Download PDF Report",
                data=pdf_report,
                file_name=f"health_report_{report_gen.report_id}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_disclaimer():
    """Render disclaimer section"""
    st.markdown("""
        <div class="disclaimer-box">
            <p class="disclaimer-text">
                <strong>Disclaimer:</strong> This AI analysis is for informational purposes only 
                and is not a substitute for professional medical advice, diagnosis, or treatment. 
                Always consult a qualified healthcare provider for interpretation of these results 
                and any health concerns.
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_processing_info(results):
    """Render processing information"""
    with st.expander("ℹ️ Processing Information"):
        processing_time = results.get("processing_time_seconds", 0)
        workflow = results.get("workflow_status", {})
        completed = sum(1 for v in workflow.values() if v == "completed")
        total = len(workflow)
        
        st.markdown(f"""
            <div class="processing-info">
                <strong>Processing Time:</strong> {processing_time:.2f} seconds<br>
                <strong>Workflow Status:</strong> {completed}/{total} steps completed
            </div>
        """, unsafe_allow_html=True)
        
        # Show warnings if any
        warnings = results.get("warnings", [])
        if warnings:
            st.markdown("**Processing Notes:**")
            for warning in warnings:
                st.markdown(f"- {warning.get('message', '')}")


def process_file(uploaded_file):
    """Process the uploaded file"""
    try:
        # Save uploaded file temporarily
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Run diagnostics
        orchestrator = HealthDiagnosticsOrchestrator()
        results = orchestrator.run_full_workflow(file_path=tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return results
        
    except Exception as e:
        return {
            "success": False,
            "errors": [{"message": str(e)}]
        }


def render_welcome():
    """Render welcome content"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="welcome-card">
                <h3>Welcome to Health Diagnostics</h3>
                <p>
                    Upload your blood report to get started. Our AI will analyze your results 
                    and provide personalized insights and recommendations.
                </p>
                <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 1.5rem;">
                    <div class="welcome-feature">
                        <div class="welcome-feature-icon">📊</div>
                        <div class="welcome-feature-text">Parameter Analysis</div>
                    </div>
                    <div class="welcome-feature">
                        <div class="welcome-feature-icon">🔍</div>
                        <div class="welcome-feature-text">Pattern Detection</div>
                    </div>
                    <div class="welcome-feature">
                        <div class="welcome-feature-icon">⚡</div>
                        <div class="welcome-feature-text">Risk Assessment</div>
                    </div>
                    <div class="welcome-feature">
                        <div class="welcome-feature-icon">💡</div>
                        <div class="welcome-feature-text">Recommendations</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        render_disclaimer()

def render_error(results):
    """Render error message"""
    st.error("❌ Failed to analyze the report")
    
    errors = results.get("errors", [])
    for error in errors:
        st.error(f"Error: {error.get('message', 'Unknown error')}")
    
    st.info("Please ensure the uploaded file is a valid blood report in a supported format.")


def render_results(results):
    """Render all results"""
    
    # Patient Information
    render_patient_info(results.get("patient_info", {}))
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Risk Assessment
    render_risk_assessment(results.get("risk_assessment", {}))
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Parameters
    render_parameters(results.get("parameters", {}))
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Key Findings
    render_key_findings(results.get("synthesis", {}))
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # AI Insights
    render_ai_insights(results.get("synthesis", {}))
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Patterns
    render_patterns(results.get("patterns", []))
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Recommendations
    render_recommendations(results.get("recommendations", {}))
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Download
    render_download_section(results)
    
    # Processing Info
    render_processing_info(results)
    
    # Disclaimer
    render_disclaimer()


# MAIN APPLICATION

def main():
    """Main application entry point"""
    
    # Render header
    render_header()
    
    # Render upload section
    uploaded_file = render_upload_section()
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Process and display results
    if uploaded_file is not None:
        with st.spinner("🔬 Analyzing your blood report..."):
            results = process_file(uploaded_file)
        
        if results and results.get("success"):
            render_results(results)
        else:
            render_error(results)
    else:
        render_welcome()


if __name__ == "__main__":
    main()