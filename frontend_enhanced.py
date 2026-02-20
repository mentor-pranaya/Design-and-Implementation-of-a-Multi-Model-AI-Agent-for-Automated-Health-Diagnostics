"""
Enhanced Streamlit Frontend: Production-grade health report interface.

Provides beautiful, intuitive UI with:
- Color-coded severity visualization
- Real-time risk dashboard
- Structured findings and recommendations
- Responsive layout
- Accessibility-first design

Usage:
    streamlit run frontend_enhanced.py
"""

import logging
from typing import Dict, List, Optional

import requests
import streamlit as st
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Health Report AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
    <style>
    /* Main container */
    .main {
        padding: 20px;
    }
    
    /* Urgency banners */
    .urgency-critical {
        background-color: #FFE0E0;
        border: 2px solid #F44336;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .urgency-high {
        background-color: #FFF3E0;
        border: 2px solid #FF9800;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .urgency-moderate {
        background-color: #FFFDE7;
        border: 2px solid #FFC107;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .urgency-low {
        background-color: #E8F5E9;
        border: 2px solid #4CAF50;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Severity badges */
    .severity-normal { color: #4CAF50; font-weight: bold; }
    .severity-mild { color: #8BC34A; font-weight: bold; }
    .severity-moderate { color: #FFC107; font-weight: bold; }
    .severity-high { color: #FF9800; font-weight: bold; }
    .severity-critical { color: #F44336; font-weight: bold; }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Finding box */
    .finding-box {
        background: #f9f9f9;
        border-left: 4px solid #2196F3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    
    /* Recommendation box */
    .recommendation-box {
        background: #f9f9f9;
        border-left: 4px solid #4CAF50;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
    }
    
    /* Parameter table */
    .param-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .param-table th, .param-table td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    
    .param-table th {
        background-color: #2196F3;
        color: white;
    }
    
    .param-table tr:hover {
        background-color: #f9f9f9;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "report" not in st.session_state:
    st.session_state.report = None
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_severity_color(severity: str) -> str:
    """Map severity to color for display."""
    severity_colors = {
        "Normal": "#4CAF50",
        "Mild Deviation": "#8BC34A",
        "Mild": "#8BC34A",
        "Moderate": "#FFC107",
        "High": "#FF9800",
        "Critical": "#F44336"
    }
    return severity_colors.get(severity, "#2196F3")


def get_urgency_color(urgency: str) -> str:
    """Map urgency to color."""
    color_map = {
        "Critical": "#F44336",
        "High": "#FF9800",
        "Moderate": "#FFC107",
        "Low": "#4CAF50"
    }
    return color_map.get(urgency, "#2196F3")


def render_urgency_banner(urgency: str, guidance: str = "") -> None:
    """Render urgency banner at top of report."""
    
    banner_emoji = {
        "Critical": "🔴",
        "High": "🟠",
        "Moderate": "🟡",
        "Low": "🟢"
    }
    
    emoji = banner_emoji.get(urgency, "ℹ️")
    color = get_urgency_color(urgency)
    
    urgency_class = f"urgency-{urgency.lower()}"
    
    html = f"""
    <div class="{urgency_class}">
        <h2 style="margin: 0; color: {color};">{emoji} Overall Urgency: {urgency}</h2>
        <p style="margin: 10px 0 0 0; font-size: 14px;">{guidance}</p>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


def render_severity_badge(value: float, severity: str, unit: str = "") -> None:
    """Render severity badge for a parameter."""
    
    color = get_severity_color(severity)
    icon = {
        "Normal": "✓",
        "Mild Deviation": "⚠️",
        "Mild": "⚠️",
        "Moderate": "⚠️",
        "High": "⚠️",
        "Critical": "🔴"
    }.get(severity, "•")
    
    st.write(
        f"<span style='color: {color}; font-weight: bold;'>{icon} {severity}</span> "
        f"→ {value} {unit}",
        unsafe_allow_html=True
    )


def render_findings_section(findings: List[str], key_findings: List[str] = None) -> None:
    """Render key findings section."""
    
    st.subheader("📋 Key Findings")
    
    if key_findings and len(key_findings) > 0:
        for i, finding in enumerate(key_findings, 1):
            st.markdown(
                f"""
                <div class="finding-box">
                    <strong>{i}. {finding}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("✓ No significant abnormal findings detected.")


def render_recommendations_section(recommendations: List[Dict]) -> None:
    """Render recommendations section."""
    
    st.subheader("📝 Recommendations")
    
    if recommendations and len(recommendations) > 0:
        # Group by category
        by_category = {}
        for rec in recommendations:
            category = rec.get("category", "medical")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(rec)
        
        # Display by category
        category_icons = {
            "urgent": "🔴",
            "medical": "👨‍⚕️",
            "monitoring": "📊",
            "testing": "🧪",
            "lifestyle": "🏃"
        }
        
        for category, recs in by_category.items():
            icon = category_icons.get(category, "•")
            st.markdown(f"#### {icon} {category.title()} Recommendations")
            
            for rec in recs:
                urgency = rec.get("urgency", "Moderate")
                priority = rec.get("priority", 5)
                
                color = get_urgency_color(urgency)
                
                st.markdown(
                    f"""
                    <div class="recommendation-box">
                        <strong style="color: {color};">Priority {priority}: {rec['text']}</strong>
                        <br/>
                        <small>Urgency: {urgency} | Evidence: {rec.get('evidence_level', 'clinical')}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("✓ No specific recommendations at this time.")


def render_parameters_table(severity_results: Dict) -> None:
    """Render parameters assessment table."""
    
    if not severity_results:
        return
    
    st.subheader("📊 Parameter Assessment")
    
    # Build table data
    table_html = """
    <table class="param-table">
        <thead>
            <tr>
                <th>Parameter</th>
                <th>Value</th>
                <th>Reference Range</th>
                <th>Severity</th>
                <th>Deviation</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for param_name, result in severity_results.items():
        severity = result.get("severity", "Normal")
        color = get_severity_color(severity)
        
        table_html += f"""
        <tr>
            <td><strong>{param_name.replace('_', ' ').title()}</strong></td>
            <td>{result.get('value', 'N/A')} {result.get('unit', '')}</td>
            <td>{result.get('reference_min', 'N/A')} - {result.get('reference_max', 'N/A')} {result.get('unit', '')}</td>
            <td><span style="color: {color}; font-weight: bold;">{severity}</span></td>
            <td>{result.get('deviation_percent', 0):.1f}%</td>
        </tr>
        """
    
    table_html += """
        </tbody>
    </table>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)


def render_summary_section(summary: Dict) -> None:
    """Render medical summary section."""
    
    st.subheader("📄 Medical Summary")
    
    st.markdown(
        f"""
        <div class="card">
            <p style="font-size: 16px; line-height: 1.8;">
                {summary.get('summary_text', 'No summary available.')}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Key insights
    if summary.get('key_insights'):
        st.markdown("**Key Insights:**")
        for insight in summary['key_insights']:
            st.write(f"• {insight}")


# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.title("⚙️ Settings")
    
    # Backend URL
    default_backend = "http://localhost:8000"
    backend_url = st.text_input(
        "Backend API URL",
        value=default_backend,
        help="URL of the Health Report AI backend API"
    )
    
    st.divider()
    
    st.markdown("### About")
    st.write(
        """
        **Health Report AI** is a production-grade medical report analysis system.
        
        It provides:
        - Intelligent OCR processing
        - Medical parameter extraction
        - Severity classification
        - Risk aggregation
        - Personalized recommendations
        
        **Always consult healthcare professionals for medical decisions.**
        """
    )


# ============================================================================
# MAIN INTERFACE
# ============================================================================

st.title("🏥 Health Report AI")
st.markdown("*Production-Grade Medical Report Analysis*")

st.divider()

# File upload section
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📁 Upload Medical Report")
    uploaded_file = st.file_uploader(
        "Select a medical report (PDF, JPG, PNG, or JSON)",
        type=["pdf", "jpg", "jpeg", "png", "json"]
    )

with col2:
    st.subheader("👤 Patient Info")
    age = st.number_input("Age", min_value=0, max_value=150, value=45)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])

# Patient history
st.subheader("📋 Medical History")
medical_history = st.text_area(
    "Enter any known conditions (comma-separated)",
    placeholder="e.g., Diabetes, Hypertension, Heart Disease",
    height=80
)

lifestyle_info = st.text_area(
    "Lifestyle Information",
    placeholder="e.g., Non-smoker, Exercise regularly, Sedentary job",
    height=80
)

st.divider()

# Analyze button
if st.button("🔍 Analyze Report", use_container_width=True, type="primary"):
    if not uploaded_file:
        st.error("❌ Please upload a medical report first.")
    else:
        with st.spinner("⏳ Analyzing your report..."):
            try:
                # Prepare files and data
                files = {"file": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)}
                
                data = {
                    "age": age,
                    "gender": gender,
                    "medical_history": medical_history.split(",") if medical_history else [],
                    "lifestyle": lifestyle_info
                }
                
                # Send to API
                response = requests.post(
                    f"{backend_url}/analyze",
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    st.session_state.report = response.json()
                    st.session_state.analysis_complete = True
                    st.success("✅ Analysis complete!")
                else:
                    st.error(f"❌ API Error: {response.status_code}")
                    logger.error(f"API Error: {response.text}")
            
            except requests.exceptions.ConnectionError:
                st.error(
                    f"❌ Cannot connect to backend at {backend_url}\n\n"
                    f"Make sure the API server is running:"
                )
                st.code(
                    ".venv\\Scripts\\python.exe -m uvicorn api.main:app --reload --port 8000",
                    language="powershell"
                )
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Error during analysis: {str(e)}")

st.divider()

# ============================================================================
# RESULTS DISPLAY
# ============================================================================

if st.session_state.analysis_complete and st.session_state.report:
    report = st.session_state.report
    
    # Urgency banner
    urgency = report.get("overall_urgency", "Low")
    guidance = report.get("guidance", "")
    render_urgency_banner(urgency, guidance)
    
    # Tabs for organized view
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Summary", "Parameters", "Findings", "Recommendations"]
    )
    
    with tab1:
        st.header("📄 Summary & Overview")
        
        # Summary section
        if "medical_summary" in report:
            summary = report["medical_summary"]
            render_summary_section(summary)
        
        # Risk aggregation info
        if "risk_aggregation" in report:
            risk = report["risk_aggregation"]
            
            st.subheader("🎯 Risk Assessment")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Abnormal Parameters", risk.get("num_abnormal_parameters", 0))
            
            with col2:
                dist = risk.get("severity_distribution", {})
                st.metric("Critical", dist.get("critical", 0))
            
            with col3:
                st.metric("High Severity", dist.get("high", 0))
            
            with col4:
                max_dev = risk.get("max_deviation_percent", 0)
                st.metric("Max Deviation", f"{max_dev:.0f}%")
    
    with tab2:
        st.header("📊 Parameter Details")
        
        if "severity_results" in report:
            render_parameters_table(report["severity_results"])
        else:
            st.info("No parameter data available.")
    
    with tab3:
        st.header("📋 Key Findings")
        
        findings = report.get("key_findings", [])
        key_findings = report.get("medical_summary", {}).get("key_insights", [])
        render_findings_section(findings, key_findings)
    
    with tab4:
        st.header("📝 Clinical Recommendations")
        
        recommendations = report.get("recommendations", [])
        render_recommendations_section(recommendations)
    
    # Results metadata
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Analysis Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col2:
        if st.button("📥 Download Report as JSON"):
            import json
            json_str = json.dumps(report, indent=2)
            st.download_button(
                label="Click to download",
                data=json_str,
                file_name=f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

else:
    # Welcome message
    st.info(
        """
        👋 **Welcome to Health Report AI**
        
        This system provides intelligent analysis of medical reports with:
        - ✓ Advanced OCR processing
        - ✓ Medical parameter extraction
        - ✓ Severity classification
        - ✓ Risk assessment
        - ✓ Personalized recommendations
        
        **To get started:**
        1. Upload a medical report (PDF, image, or JSON)
        2. Enter your patient information
        3. Click "Analyze Report"
        
        **Disclaimer:** This system is for informational purposes only and 
        should not replace professional medical advice. Always consult qualified 
        healthcare providers for diagnosis and treatment decisions.
        """
    )

st.markdown(
    """
    ---
    *Health Report AI v1.0 | Production Ready*
    
    For issues or feedback: contact your healthcare provider or system administrator.
    """
)
