"""
QUICK REFERENCE: Using the New Modules

Fast lookup for developers integrating the production upgrade modules.
"""

# ============================================================================
# SEVERITY ENGINE QUICK REFERENCE
# ============================================================================

SEVERITY_ENGINE_USAGE = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEVERITY ENGINE - Classify parameter severity based on deviation from normal
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORT:
    from severity_engine import SeverityEngine, SeverityLevel, SeverityResult

CREATE INSTANCE:
    engine = SeverityEngine()

CALCULATE SINGLE PARAMETER:
    result = engine.calculate_severity(
        value=250,           # Measured value
        reference_min=70,    # Min normal
        reference_max=100,   # Max normal
        unit="mg/dL",        # Display unit
        age=55,              # Optional: Age adjustment
        gender="Male"        # Optional: Gender adjustment
    )
    
    # Access result:
    result.severity         # SeverityLevel enum
    result.deviation_percent    # Float (e.g., 150.0)
    result.is_abnormal      # Boolean
    result.reasoning        # String explanation
    result.to_dict()        # JSON-ready dict

CALCULATE MULTIPLE PARAMETERS:
    params = {
        "glucose": (250, 70, 100),
        "hemoglobin": (9.5, 12, 16),
        "cholesterol": (220, 0, 200)
    }
    
    units = {
        "glucose": "mg/dL",
        "hemoglobin": "g/dL",
        "cholesterol": "mg/dL"
    }
    
    results = engine.batch_calculate_severity(
        parameters=params,
        age=55,
        units=units
    )
    # Returns: Dict[str, SeverityResult]

COUNT ABNORMALITIES:
    abnormal_count = engine.get_abnormality_count(
        severity_results,
        severity_threshold=SeverityLevel.MODERATE  # Count Moderate+
    )

SEVERITY LEVELS (in order):
    NORMAL < MILD < MODERATE < HIGH < CRITICAL

DEVIATION THRESHOLDS:
    0-10% deviation   → Mild
    10-20% deviation  → Moderate
    20-35% deviation  → High
    35%+ deviation    → Critical

AGE ADJUSTMENTS:
    Age > 65          → Thresholds 15% stricter
    Age < 18          → Thresholds 10% stricter
    Age 18-65         → Standard thresholds
"""

# ============================================================================
# RISK AGGREGATOR QUICK REFERENCE
# ============================================================================

RISK_AGGREGATOR_USAGE = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RISK AGGREGATOR - Combine multiple abnormalities into global urgency
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORT:
    from risk_aggregator import RiskAggregator, UrgencyLevel, RiskAggregation

CREATE INSTANCE:
    aggregator = RiskAggregator()

AGGREGATE RISKS:
    risk = aggregator.aggregate_risks(
        severity_results=severity_dict,  # From SeverityEngine
        age=58,                          # Optional
        gender="Male",                   # Optional
        medical_history=["Diabetes", "Hypertension"]  # Optional list
    )
    
    # Access result:
    risk.global_urgency               # UrgencyLevel enum
    risk.critical_parameters          # List[str]
    risk.high_risk_parameters         # List[str]
    risk.moderate_parameters          # List[str]
    risk.severity_distribution        # Dict with counts
    risk.escalation_reasons           # List[str]
    risk.num_abnormal_parameters      # Int
    risk.max_deviation_percent        # Float
    risk.to_dict()                    # JSON-ready dict

ESCALATION RULES:
    1+ Critical abnormalities     → CRITICAL urgency
    1+ High abnormalities         → HIGH urgency
    2+ Moderate abnormalities     → HIGH urgency
    1+ Moderate abnormality       → MODERATE urgency
    3+ Mild abnormalities         → MODERATE urgency
    Else (if any abnormal)        → MODERATE urgency
    No abnormalities              → LOW urgency

MEDICAL HISTORY ESCALATION:
    Diabetes, Hypertension, Cardiac, Heart Disease, Stroke,
    Kidney Disease, Liver Disease, Cancer
    → Escalates urgency by 1 level

IDENTIFY AFFECTED DOMAINS:
    domains = aggregator.identify_risk_domains(
        critical_parameters=risk.critical_parameters,
        high_parameters=risk.high_risk_parameters
    )
    # Returns: Dict[str, List[str]]
    # Example: {"Cardiovascular": ["glucose"], "Metabolic": ["cholesterol"]}

GET ACTION ITEMS:
    actions = aggregator.get_action_items(risk.global_urgency)
    # Returns: List[str] with emoji indicators
    # CRITICAL: "🔴 SEEK IMMEDIATE MEDICAL ATTENTION"
    # HIGH: "🟠 Schedule appointment within 1-3 days"
    # MODERATE: "🟡 Schedule routine appointment within 1-2 weeks"
    # LOW: "🟢 No immediate action required"

URGENCY LEVELS:
    LOW < MODERATE < HIGH < CRITICAL
"""

# ============================================================================
# SUMMARY GENERATOR QUICK REFERENCE
# ============================================================================

SUMMARY_GENERATOR_USAGE = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUMMARY GENERATOR - Create conversational medical summaries
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORT:
    from summary_generator import SummaryGenerator, MedicalSummary

CREATE INSTANCE:
    generator = SummaryGenerator()

GENERATE SUMMARY:
    summary = generator.generate_medical_summary(
        severity_results=severity_dict,      # From SeverityEngine
        risk_aggregation=risk,               # From RiskAggregator
        age=58,                              # Optional
        gender="Male",                       # Optional
        test_name="Blood Work"               # Optional
    )
    
    # Access result:
    summary.summary_text                # Narrative paragraph
    summary.key_insights                # List of insights
    summary.top_2_severe_findings       # List[str] of top 2
    summary.overall_urgency             # String
    summary.abnormal_parameter_count    # Int
    summary.tone                        # "low_concern", "moderate_concern", etc.
    summary.guidance                    # Action guidance
    summary.to_dict()                   # JSON-ready dict

TONE MAPPING:
    Low Concern     → "Your recent health report shows..."
    Moderate Concern → "Your health report indicates..."
    High Concern    → "Your health report reveals..."
    Critical Concern → "⚠️ Your health report indicates..."

GENERATE HTML:
    html = generator.generate_summary_html(summary)
    # Returns: HTML string for Streamlit display
    st.markdown(html, unsafe_allow_html=True)

SUMMARY INCLUDES:
    ✓ Opening statement with tone
    ✓ Patient context (age, gender)
    ✓ Top 2 findings highlighted
    ✓ Urgency statement with emoji
    ✓ Key insights (3-5 points)
    ✓ Closing statement
    ✓ Guidance for next steps
"""

# ============================================================================
# RECOMMENDATION ENGINE QUICK REFERENCE
# ============================================================================

RECOMMENDATION_ENGINE_USAGE = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDATION ENGINE - Generate context-aware recommendations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORT:
    from recommendation_engine import RecommendationEngine, Recommendation

CREATE INSTANCE:
    engine = RecommendationEngine()

GENERATE RECOMMENDATIONS:
    abnormal_params = {
        "glucose": {"value": 250, "severity": "High"},
        "cholesterol": {"value": 220, "severity": "High"}
    }
    
    recommendations = engine.generate_recommendations(
        urgency_level=UrgencyLevel.HIGH,           # From RiskAggregator
        abnormal_parameters=abnormal_params,       # Dict
        age=58,                                    # Optional
        gender="Male",                             # Optional
        medical_history=["Type 2 Diabetes"],      # Optional list
        max_recommendations=10                     # Default: 10
    )
    
    # Access result (List[Recommendation]):
    for rec in recommendations:
        rec.text                # String recommendation
        rec.category            # "urgent", "medical", "testing", "lifestyle", "monitoring"
        rec.urgency             # UrgencyLevel
        rec.priority            # 1 (highest) to 5 (lowest)
        rec.parameter_related   # String or None
        rec.evidence_level      # "clinical", "preventive", "lifestyle"
        rec.to_dict()           # JSON-ready dict

RECOMMENDATION CATEGORIES:
    urgent    → Immediate attention (use sparingly)
    medical   → Healthcare provider consultation
    testing   → Diagnostic testing needed
    monitoring → Regular monitoring/follow-up
    lifestyle → Behavioral/diet/exercise changes

PRIORITY LEVELS:
    1 → Critical/urgent action
    2 → High importance
    3 → Medium importance
    4 → Low importance
    5 → Preventive/maintenance

PARAMETER-SPECIFIC RECOMMENDATIONS:
    Supported: glucose, hemoglobin, total_cholesterol, hdl, ldl,
              triglycerides, creatinine, blood_pressure_systolic,
              wbc, platelets
    
    Each has custom recommendations for CRITICAL, HIGH, MODERATE

GET SUMMARY:
    summary = engine.get_recommendation_summary(recommendations)
    # Returns: Dict with category counts
    # {"urgent": 2, "medical": 4, "testing": 1, "lifestyle": 2, "monitoring": 1}

RECOMMENDATION TYPES:
    ✓ Parameter-specific guidance
    ✓ Urgency-escalated language
    ✓ Medical history aware
    ✓ Demographic appropriate
    ✓ Preventive suggestions
    ✓ Lifestyle modifications
    ✓ Medical consultations
    ✓ Testing recommendations
"""

# ============================================================================
# FRONTEND ENHANCED QUICK REFERENCE
# ============================================================================

FRONTEND_ENHANCED_USAGE = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FRONTEND ENHANCED - Production Streamlit UI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

START:
    streamlit run frontend_enhanced.py

FEATURES:
    ✓ File upload (PDF, JPG, PNG, JSON)
    ✓ Patient info input (age, gender, history)
    ✓ Real-time analysis status
    ✓ Urgency banner with emoji
    ✓ Color-coded severity
    ✓ Tabbed results view
    ✓ Parameter table with badges
    ✓ Recommendation grouping
    ✓ Medical summary display
    ✓ JSON export

COLOR MAPPING:
    🟢 Green   (GREEN #4CAF50)   → Normal / Low Urgency
    🟡 Yellow  (YELLOW #FFC107)  → Moderate
    🟠 Orange  (ORANGE #FF9800)  → High
    🔴 Red     (RED #F44336)     → Critical

TABS:
    1. Summary & Overview
       - Medical narrative
       - Risk metrics
       
    2. Parameter Details
       - Assessment table
       - Reference ranges
       - Severity badges
       
    3. Key Findings
       - Top abnormalities
       - Clinical insights
       
    4. Recommendations
       - Grouped by category
       - Prioritized
       - Timestamped

API INTEGRATION:
    Expects response from /analyze endpoint with:
    - overall_urgency: str
    - severity_results: Dict
    - risk_aggregation: Dict
    - medical_summary: Dict
    - recommendations: List
    - action_items: List
"""

# ============================================================================
# INTEGRATION PATTERNS
# ============================================================================

API_INTEGRATION = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMMON INTEGRATION PATTERNS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PATTERN 1: Complete Pipeline (Recommended)
    parameters → severity → risk → summary + recommendations → response

PATTERN 2: Severity Only
    parameters → severity → return severity_results

PATTERN 3: Risk Assessment Only
    severity_results → risk → return risk_aggregation

PATTERN 4: Summary Only
    severity_results + risk → summary → return summary

PATTERN 5: Recommendations Only
    risk + abnormal_params → recommendations → return recommendations

REFERENCE RANGES SOURCE:
    Option A: Get from existing model_2/reference_ranges.py
    Option B: Create new config file with all ranges
    Option C: Query from database
    
    Recommended structure:
    REFERENCE_RANGES = {
        "parameter_name": {
            "min": float,
            "max": float,
            "unit": "str",
            "category": "str"  # Metabolic, Cardiovascular, etc.
        }
    }

ERROR HANDLING:
    try:
        # API logic
        severity = engine.calculate_severity(...)
    except ValueError as e:
        logger.error(f"Severity calculation failed: {e}")
        # Graceful degradation
        return {"status": "error", "message": str(e)}
"""

# ============================================================================
# EXAMPLE CODE SNIPPETS
# ============================================================================

EXAMPLE_SNIPPETS = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRODUCTION CODE EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXAMPLE 1: Simple Severity Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from severity_engine import SeverityEngine

engine = SeverityEngine()
result = engine.calculate_severity(250, 70, 100, "mg/dL")

if result.is_abnormal:
    print(f"{result.severity.value}: {result.deviation_percent:.1f}% above normal")

EXAMPLE 2: Multi-Parameter Assessment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from severity_engine import SeverityEngine
from risk_aggregator import RiskAggregator

engine = SeverityEngine()
aggregator = RiskAggregator()

# Calculate all severities
params = {
    "glucose": (250, 70, 100),
    "hemoglobin": (9.5, 12, 16)
}
results = engine.batch_calculate_severity(params)

# Aggregate risk
risk = aggregator.aggregate_risks(results, age=55)

print(f"Overall Risk Level: {risk.global_urgency.value}")
print(f"Action: {aggregator.get_action_items(risk.global_urgency)[0]}")

EXAMPLE 3: Complete Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from severity_engine import SeverityEngine
from risk_aggregator import RiskAggregator
from summary_generator import SummaryGenerator
from recommendation_engine import RecommendationEngine

# Step 1: Severity
severity_engine = SeverityEngine()
severity_results = severity_engine.batch_calculate_severity(params, age=55)

# Step 2: Risk
risk_aggregator = RiskAggregator()
risk = risk_aggregator.aggregate_risks(severity_results, age=55, 
                                       medical_history=["Diabetes"])

# Step 3: Summary
summary_gen = SummaryGenerator()
summary = summary_gen.generate_medical_summary(severity_results, risk, age=55)

# Step 4: Recommendations
rec_engine = RecommendationEngine()
abnormal = {k: {"value": v.value, "severity": v.severity.value} 
           for k, v in severity_results.items() if v.is_abnormal}
recs = rec_engine.generate_recommendations(risk.global_urgency, abnormal, age=55)

# Return all
return {
    "severity": severity_results,
    "risk": risk,
    "summary": summary,
    "recommendations": recs
}

EXAMPLE 4: Streamlit Display
━━━━━━━━━━━━━━━━━━━━
import streamlit as st

# Display urgency banner
color = {"Critical": "#F44336", "High": "#FF9800", 
         "Moderate": "#FFC107", "Low": "#4CAF50"}[urgency]

st.markdown(f'''
    <div style='border: 2px solid {color}; padding: 20px; background: lighten({color}, 40%);'>
    <h2 style='color: {color}'>{urgency}</h2>
    </div>
''', unsafe_allow_html=True)

# Display findings
for finding in summary.key_insights:
    st.write(f"• {finding}")

# Display recommendations by category
for category in ["urgent", "medical", "lifestyle"]:
    category_recs = [r for r in recommendations if r.category == category]
    if category_recs:
        st.subheader(f"{category.title()} Recommendations")
        for rec in category_recs:
            st.write(f"**{rec.priority}. {rec.text}**")
"""

# ============================================================================
# TESTING
# ============================================================================

TESTING = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TESTING THE MODULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST 1: Run Module Examples
    python severity_engine.py
    python risk_aggregator.py
    python summary_generator.py
    python recommendation_engine.py

TEST 2: Check Imports
    python -c "from severity_engine import SeverityEngine; print('✓ Imports OK')"

TEST 3: Verify Output Types
    engine = SeverityEngine()
    result = engine.calculate_severity(250, 70, 100)
    assert isinstance(result.severity.value, str)
    assert isinstance(result.deviation_percent, float)
    assert isinstance(result.is_abnormal, bool)

TEST 4: Check JSON Serialization
    import json
    result = engine.calculate_severity(250, 70, 100)
    json_str = json.dumps(result.to_dict())
    assert '"severity"' in json_str

TEST 5: Integration Test
    python IMPLEMENTATION_CHECKLIST.py
    # Runs all modules together

TEST 6: API Endpoint
    curl -X POST http://localhost:8000/analyze \\
         -F "file=@report.pdf" \\
         -F "age=55" \\
         -F "gender=Male"

TEST 7: Frontend
    streamlit run frontend_enhanced.py
    # Open http://localhost:8501
    # Upload test file and verify all fields populated
"""

# ============================================================================
# PRINT QUICK REFERENCE
# ============================================================================

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║         PRODUCTION HEALTH REPORT AI - QUICK REFERENCE CARD                ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    print(SEVERITY_ENGINE_USAGE)
    print("\n" + RISK_AGGREGATOR_USAGE)
    print("\n" + SUMMARY_GENERATOR_USAGE)
    print("\n" + RECOMMENDATION_ENGINE_USAGE)
    print("\n" + FRONTEND_ENHANCED_USAGE)
    print("\n" + API_INTEGRATION)
    print("\n" + EXAMPLE_SNIPPETS)
    print("\n" + TESTING)
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      QUICK START COMMAND                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

1. Test modules:     python severity_engine.py
2. Start API:        .venv\\Scripts\\python.exe -m uvicorn api.main:app --reload
3. Start frontend:   streamlit run frontend_enhanced.py
4. Open browser:     http://localhost:8501

📖 Detailed docs:
   - INTEGRATION_GUIDE.py - Full API integration examples
   - IMPLEMENTATION_CHECKLIST.py - Step-by-step deployment
   - PRODUCTION_UPGRADE_SUMMARY.md - Complete overview
    """)
