from src.input_parser.input_handler import read_input
from src.extraction.extractor import extract_parameter
from src.config.parameters import REQUIRED_PARAMETERS
from src.model_1.interpretation import interpret_value
from src.model_2.pattern_detector import detect_all_patterns
from src.model_2.risk_calculator import calculate_overall_risk
from src.model_3.contextual_analyzer import analyze_with_context
from src.synthesis.findings_engine import synthesize_findings
from src.synthesis.recommendation_generator import generate_recommendations


#Read Input

# file_path = "data/json/Blood_report_json_2.json"
file_path = "data/images/blood_report_img_3.png"
# file_path = "data/pdf/Blood_report_pdf_3.pdf"

data = read_input(file_path)

results = {}

if isinstance(data, str):
    for param_name, keywords in REQUIRED_PARAMETERS.items():
        extracted = extract_parameter(data, param_name, keywords)
        results[param_name] = extracted.get(param_name) if extracted else None

elif isinstance(data, dict):
    for param_name in REQUIRED_PARAMETERS:
        results[param_name] = data.get(param_name)

else:
    raise ValueError("Unsupported input data type")


#Extract Age and Gender

age_data = results.get("Age")
USER_AGE = None
if age_data:
    age_value = age_data.get("value")
    if age_value is not None:
        try:
            USER_AGE = int(float(age_value))
        except (ValueError, TypeError):
            USER_AGE = None

gender_data = results.get("Gender")
USER_GENDER = None
if gender_data:
    gender_value = gender_data.get("value")
    if gender_value and isinstance(gender_value, str):
        USER_GENDER = gender_value.lower().strip()
        if USER_GENDER not in ["male", "female"]:
            USER_GENDER = None


#Model 1 - Raw Interpretation

for param_name, param_data in results.items():
    if param_name in ["Age", "Gender"]:
        continue
    
    if param_data:
        status = interpret_value(
            value=param_data.get("value"),
            reference_range=param_data.get("reference_range"),
            param_name=param_name,
            gender=USER_GENDER,
            age=USER_AGE
        )
        param_data["status"] = status


#Model 3 - Contextual Analysis

contextual_analysis = analyze_with_context(results, age=USER_AGE, gender=USER_GENDER)


#Model 2 - Pattern Detection

patterns = detect_all_patterns(
    results=results,
    contextual_results=contextual_analysis["detailed_results"],
    gender=USER_GENDER,
    age=USER_AGE
)


#Model 2 - Risk Assessment

risk_assessment = calculate_overall_risk(
    results=results,
    contextual_results=contextual_analysis["detailed_results"],
    gender=USER_GENDER,
    age=USER_AGE
)


#Milestone 3 - Synthesize Findings

synthesis = synthesize_findings(
    results=results,
    patterns=patterns,
    risk_assessment=risk_assessment,
    contextual_analysis=contextual_analysis,
    age=USER_AGE,
    gender=USER_GENDER
)


#Milestone 3 - Generate Recommendations

recommendations = generate_recommendations(
    synthesis_result=synthesis,
    age=USER_AGE,
    gender=USER_GENDER
)


#Final Output

print("-" * 70)
print("                    HEALTH DIAGNOSTIC REPORT")
print("-" * 70)

# --- Patient Context ---
print("\n" + "-" * 70)
print("  PATIENT INFORMATION")
print("-" * 70)
print(f"  Age      : {USER_AGE if USER_AGE else 'Not detected'} {'years' if USER_AGE else ''}")
print(f"  Gender   : {USER_GENDER.capitalize() if USER_GENDER else 'Not detected'}")
if USER_AGE or USER_GENDER:
    print(f"  Age Group: {synthesis['age_group'].capitalize()}")

# --- Summary ---
print("\n" + "-" * 70)
print("  CLINICAL SUMMARY")
print("-" * 70)
print(f"  {synthesis['summary_text']}")

# --- Key Findings ---
if synthesis['key_findings']:
    print("\n" + "-" * 70)
    print("  KEY FINDINGS")
    print("-" * 70)
    for finding in synthesis['key_findings']:
        # Replace emoji with text markers
        if finding['type'] == 'critical':
            marker = "[CRITICAL]"
        elif finding['type'] == 'abnormal':
            marker = "[ABNORMAL]"
        elif finding['type'] == 'borderline':
            marker = "[BORDERLINE]"
        else:
            marker = "[INFO]"
        print(f"  {marker} {finding['text']}")

# --- Parameters ---
print("\n" + "-" * 70)
print("  DETAILED PARAMETERS")
print("-" * 70)
print(f"  {'Parameter':<15} {'Value':<12} {'Range':<15} {'Status':<10}")
print("  " + "-" * 55)

for param_name, param_data in results.items():
    if param_name in ["Age", "Gender"]:
        continue
    
    if param_data:
        value = param_data.get("value")
        unit = param_data.get("unit", "")
        status = param_data.get("status", "UNKNOWN")
        display_range = param_data.get("contextual_range")
        if not display_range:
            display_range = param_data.get("reference_range", "N/A")
        
        value_str = f"{value} {unit}".strip()
        print(f"  {param_name:<15} {value_str:<12} {display_range:<15} {status:<10}")

# --- Detected Patterns ---
if patterns:
    print("\n" + "-" * 70)
    print("  DETECTED PATTERNS")
    print("-" * 70)
    for i, pattern in enumerate(patterns, 1):
        print(f"\n  Pattern {i}: {pattern['pattern']}")
        print(f"  Confidence: {pattern['confidence']}%")
        print(f"  Assessment: {pattern['description']}")
        print("  Indicators:")
        for indicator in pattern['indicators']:
            print(f"    - {indicator}")

# --- Risk Assessment ---
print("\n" + "-" * 70)
print("  RISK ASSESSMENT")
print("-" * 70)
overall = risk_assessment["overall_score"]
level = risk_assessment["risk_level"]
print(f"\n  Overall Risk Score: {overall}/100")
print(f"  Risk Level: {level}")

print("\n  Risk Breakdown:")
for risk in risk_assessment["individual_risks"]:
    if risk["score"] > 0:
        print(f"    - {risk['category']}: {risk['score']}/100")
        for factor in risk.get("risk_factors", []):
            print(f"        {factor}")

# --- Recommendations ---
print("\n" + "-" * 70)
print("  PERSONALIZED RECOMMENDATIONS")
print("-" * 70)
print(f"\n  Priority Level: {recommendations['overall_priority']}")
print(f"  Summary: {recommendations['summary']}")

for rec in recommendations['condition_recommendations']:
    print(f"\n  " + "=" * 60)
    print(f"  CONDITION: {rec['linked_condition'].upper()}")
    print(f"  Timeline: {rec.get('timeline', 'As needed')}")
    print("  " + "=" * 60)
    
    if rec.get('diet'):
        print(f"\n  DIETARY RECOMMENDATIONS:")
        for i, item in enumerate(rec['diet'][:4], 1):
            print(f"    {i}. {item}")
        if len(rec['diet']) > 4:
            print(f"    ... and {len(rec['diet']) - 4} more recommendations")
    
    if rec.get('lifestyle'):
        print(f"\n  LIFESTYLE MODIFICATIONS:")
        for i, item in enumerate(rec['lifestyle'][:4], 1):
            print(f"    {i}. {item}")
        if len(rec['lifestyle']) > 4:
            print(f"    ... and {len(rec['lifestyle']) - 4} more recommendations")
    
    if rec.get('followup'):
        print(f"\n  FOLLOW-UP ACTIONS:")
        for i, item in enumerate(rec['followup'][:4], 1):
            print(f"    {i}. {item}")
    
    if rec.get('warnings'):
        print(f"\n  IMPORTANT WARNINGS:")
        for i, item in enumerate(rec['warnings'], 1):
            print(f"    {i}. {item}")

# --- Age/Gender Specific Notes ---
age_advice = recommendations.get('age_specific_advice', {})
gender_advice = recommendations.get('gender_specific_advice', {})

if age_advice.get('notes') or gender_advice.get('notes'):
    print("\n" + "-" * 70)
    print("  PATIENT-SPECIFIC NOTES")
    print("-" * 70)
    if age_advice.get('notes'):
        print(f"\n  Age-Related Considerations:")
        print(f"    {age_advice['notes']}")
    if age_advice.get('diet_modifier'):
        print(f"    Dietary Note: {age_advice['diet_modifier']}")
    if gender_advice.get('notes'):
        print(f"\n  Gender-Related Considerations:")
        print(f"    {gender_advice['notes']}")

# --- General Advice ---
print("\n" + "-" * 70)
print("  GENERAL HEALTH GUIDELINES")
print("-" * 70)
general = recommendations.get('general_advice', {})
if general:
    print(f"\n  1. Hydration: {general.get('hydration', 'Stay hydrated')}")
    print(f"  2. Sleep: {general.get('sleep', 'Get adequate sleep')}")
    print(f"  3. Exercise: {general.get('exercise', 'Exercise regularly')}")
    print(f"  4. Stress Management: {general.get('stress', 'Manage stress')}")
    print(f"  5. Regular Checkups: {general.get('checkups', 'Get regular health checkups')}")

# --- Disclaimer ---
print("\n" + "-" * 70)
print("  DISCLAIMER")
print("-" * 70)
print("""
  This report is generated by an AI-based health diagnostics system
  for informational purposes only. It is NOT a substitute for 
  professional medical advice, diagnosis, or treatment.
  
  Always consult a qualified healthcare provider for:
    - Interpretation of these results
    - Medical advice and treatment decisions
    - Any health concerns or symptoms
  
  Do not disregard professional medical advice or delay seeking it
  based on information in this report.
""")

print("-" * 70)
print("                      END OF REPORT")
print("-" * 70)