from src.input_parser.input_handler import read_input
from src.extraction.extractor import extract_parameter
from src.config.parameters import REQUIRED_PARAMETERS
from src.model_1.interpretation import interpret_value
from src.model_2.pattern_detector import detect_all_patterns
from src.model_2.risk_calculator import calculate_overall_risk
from src.model_3.contextual_analyzer import analyze_with_context


# Read Input

file_path = "data/json/Blood_report_json_9.json"
# file_path = "data/images/blood_report_img_1.jpg"
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


# Extract Age and Gender

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


# STEP Model 1 - Raw Interpretation FIRST (BUG 1 FIX)
# Assigns initial status using dynamic reference ranges

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


# Model 3 - Contextual Analysis
# Adjusts status and UPDATES results dict (BUG 6 FIX)

contextual_analysis = analyze_with_context(results, age=USER_AGE, gender=USER_GENDER)


# Model 2 - Pattern Detection
# Uses results dict which now has contextual status

patterns = detect_all_patterns(
    results=results,
    contextual_results=contextual_analysis["detailed_results"],
    gender=USER_GENDER,
    age=USER_AGE
)


# Model 2 - Risk Assessment
# Uses results dict which now has contextual status

risk_assessment = calculate_overall_risk(
    results=results,
    contextual_results=contextual_analysis["detailed_results"],
    gender=USER_GENDER,
    age=USER_AGE
)


# Final Output

print("=" * 60)
print("             HEALTH DIAGNOSTIC REPORT")
print("=" * 60)

# --- Patient Context ---
print("\nPATIENT CONTEXT (Auto-Extracted):")
print("-" * 60)
print(f"  Age: {USER_AGE if USER_AGE else 'Not detected'} {'years' if USER_AGE else ''}")
print(f"  Gender: {USER_GENDER.capitalize() if USER_GENDER else 'Not detected'}")
if USER_AGE or USER_GENDER:
    print(f"  Age Group: {contextual_analysis['summary']['age_group'].capitalize()}")

# --- Parameters Output ---
print("\nEXTRACTED PARAMETERS:")
print("-" * 60)

for param_name, param_data in results.items():
    if param_name in ["Age", "Gender"]:
        continue
    
    if param_data:
        value = param_data.get("value")
        unit = param_data.get("unit", "")
        status = param_data.get("status", "UNKNOWN")
        
        # Display contextual range (BUG 3 FIX - already set by Model 3)
        display_range = param_data.get("contextual_range")
        if not display_range:
            display_range = param_data.get("reference_range", "N/A")
        
        print(f"  {param_name}: {value} {unit} [{display_range}] --> {status}")
    else:
        print(f"  {param_name}: Not Found")

# --- Contextual Analysis Summary ---
print("\nCONTEXTUAL ANALYSIS (Model 3):")
print("-" * 60)

summary = contextual_analysis["summary"]
print(f"\n  Parameters analyzed: {summary['parameters_analyzed']}")
print(f"  Parameters with status change: {summary['parameters_changed']}")

if summary["adjustments"]:
    print("\n  Status adjustments applied:")
    for adj in summary["adjustments"]:
        print(f"    - {adj['parameter']}: {adj['original_status']} --> {adj['new_status']}")
        print(f"        Reason: {adj['reason']}")

# --- Detected Patterns ---
print("\nDETECTED PATTERNS (Model 2) [Context-Aware]:")
print("-" * 60)

if patterns:
    for i, pattern in enumerate(patterns, 1):
        print(f"\n  Pattern {i}: {pattern['pattern']}")
        print(f"  Confidence: {pattern['confidence']}%")
        if pattern.get('data_quality'):
            print(f"  Data Quality: {pattern['data_quality']}")
        print(f"  Description: {pattern['description']}")
        print(f"  Indicators:")
        for indicator in pattern['indicators']:
            print(f"    - {indicator}")
else:
    print("  No concerning patterns detected. All values appear normal.")

# --- Risk Assessment ---
print("\nRISK ASSESSMENT (Model 2) [Context-Aware]:")
print("-" * 60)

overall = risk_assessment["overall_score"]
level = risk_assessment["risk_level"]

print(f"\n  OVERALL RISK SCORE: {overall}/100 ({level})")

print("\n  Individual Risk Breakdown:")
for risk in risk_assessment["individual_risks"]:
    category = risk["category"]
    score = risk["score"]
    print(f"    - {category}: {score}/100")
    if risk["risk_factors"]:
        for factor in risk["risk_factors"]:
            print(f"        > {factor}")

print("\n  RECOMMENDATION:")
print(f"    {risk_assessment['recommendation']}")

print("\n" + "=" * 60)
print("              END OF REPORT")
print("=" * 60)