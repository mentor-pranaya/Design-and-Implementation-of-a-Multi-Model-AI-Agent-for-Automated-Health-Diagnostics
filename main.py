from src.input_parser.input_handler import read_input
from src.extraction.extractor import extract_parameter
from src.config.parameters import REQUIRED_PARAMETERS
from src.model_1.interpretation import interpret_value
from src.model_2.pattern_detector import detect_all_patterns
from src.model_2.risk_calculator import calculate_overall_risk
from src.model_3.contextual_analyzer import analyze_with_context



#Read Input (ALL formats)


# file_path = "data/json/Blood_report_json_2.json"
# file_path = "data/images/blood_report_img_2.jpg"
file_path = "data/pdf/Blood_report_pdf_5.pdf"

data = read_input(file_path)

results = {}

# Unstructured input (OCR / PDF -> text)
if isinstance(data, str):
    for param_name, keywords in REQUIRED_PARAMETERS.items():
        extracted = extract_parameter(data, param_name, keywords)
        results[param_name] = extracted.get(param_name) if extracted else None

# Structured input (JSON -> dict)
elif isinstance(data, dict):
    for param_name in REQUIRED_PARAMETERS:
        results[param_name] = data.get(param_name)

else:
    raise ValueError("Unsupported input data type")



#Extract Age and Gender for Model 3



age_data = results.get("Age")
USER_AGE = age_data.get("value") if age_data else None

gender_data = results.get("Gender")
USER_GENDER = gender_data.get("value") if gender_data else None



# Model 1 - Parameter Interpretation


for param_name, param_data in results.items():
    # Skip Age and Gender for interpretation (not blood parameters)
    if param_name in ["Age", "Gender"]:
        continue
    
    if param_data:
        status = interpret_value(
            param_data.get("value"),
            param_data.get("reference_range")
        )
        param_data["status"] = status



# Pattern Detection
patterns = detect_all_patterns(results)
#Risk Assessment
risk_assessment = calculate_overall_risk(results)
#Model 3 - Contextual Analysis
contextual_analysis = analyze_with_context(results, age=USER_AGE, gender=USER_GENDER)
#Final Output


print("\n")
print("             HEALTH DIAGNOSTIC REPORT")


# Patient Context (Auto-Extracted)
print("\nPATIENT CONTEXT (Auto-Extracted):")
print("-" * 60)
print(f"  Age: {USER_AGE if USER_AGE else 'Not detected'} {'years' if USER_AGE else ''}")
print(f"  Gender: {USER_GENDER.capitalize() if USER_GENDER else 'Not detected'}")
if USER_AGE or USER_GENDER:
    print(f"  Age Group: {contextual_analysis['summary']['age_group'].capitalize()}")

#Model 1 Output 
print("\nEXTRACTED PARAMETERS (Model 1):")
print("-" * 60)

for param_name, param_data in results.items():
    # Skip Age and Gender in parameter list
    if param_name in ["Age", "Gender"]:
        continue
    
    if param_data:
        value = param_data.get("value")
        unit = param_data.get("unit", "")
        status = param_data.get("status", "")
        ref_range = param_data.get("reference_range", "")
        print(f"  {param_name}: {value} {unit} [{ref_range}] --> {status}")
    else:
        print(f"  {param_name}: Not Found")

#Model 3 Output: Contextual Analysis
print("\nCONTEXTUAL ANALYSIS (Model 3):")
print("-" * 60)

if USER_AGE is None and USER_GENDER is None:
    print("\n  Age/Gender not detected in report. Skipping contextual analysis.")
else:
    adjustments = contextual_analysis["summary"]["adjustments"]
    if adjustments:
        print("\n  Status adjustments based on age/gender:")
        for adj in adjustments:
            print(f"    - {adj['parameter']}: {adj['original_status']} --> {adj['new_status']}")
            print(f"        Reason: {adj['reason']}")
    else:
        print("\n  No status changes after applying age/gender context.")

    # Show contextual ranges for key parameters
    context_label = ""
    if USER_GENDER:
        context_label += f"{USER_GENDER}"
    if USER_AGE:
        context_label += f", age {USER_AGE}"
    
    print(f"\n  Contextual Reference Ranges (for {context_label}):")
    for param_name, context_data in contextual_analysis["detailed_results"].items():
        if context_data.get("context_applied"):
            print(f"    - {param_name}: {context_data['contextual_range']}")

#Model 2 Output: Patterns
print("\nDETECTED PATTERNS (Model 2):")
print("-" * 60)

if patterns:
    for i, pattern in enumerate(patterns, 1):
        print(f"\n  Pattern {i}: {pattern['pattern']}")
        print(f"  Confidence: {pattern['confidence']}%")
        print(f"  Description: {pattern['description']}")
        print(f"  Indicators:")
        for indicator in pattern['indicators']:
            print(f"    - {indicator}")
else:
    print("  No concerning patterns detected. All values appear normal.")

#Model 2 Output: Risk Assessment
print("\nRISK ASSESSMENT (Model 2):")
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

print("\n")
print("              END OF REPORT")
