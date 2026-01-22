from core_phase2.processing.text_cleaner import clean_ocr_text
from core_phase2.extraction.parameter_extractor import extract_parameters
from core_phase1.validation.validator import validate_parameters
from core_phase2.interpreter.model1_classifier import classify_parameters

# Load OCR output
with open("core_phase2/input/ocr_output.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

cleaned_text = clean_ocr_text(raw_text)
extracted = extract_parameters(cleaned_text)
validated = validate_parameters(extracted)
classified = classify_parameters(validated)

print("\n" + "="*60)
print("INDIVIDUAL PARAMETER CLASSIFICATION (Model 1)")
print("="*60)
for k, v in classified.items():
    status = v.get('status', 'N/A')
    value = v.get('value', 'N/A')
    unit = v.get('unit', '')
    print(f"{k:30s}: {value} {unit:10s} [{status}]")

from core_phase2.interpreter.model2_patterns import (
    cholesterol_hdl_risk,
    diabetes_indicator,
    metabolic_syndrome_indicators,
    kidney_function_assessment,
    thyroid_function_assessment,
    anemia_assessment
)

patterns = []

# Cardiovascular Risk
cv_risk = cholesterol_hdl_risk(extracted)
if cv_risk:
    patterns.append(cv_risk)

# Diabetes Risk
diabetes = diabetes_indicator(extracted)
if diabetes:
    patterns.append(diabetes)

# Metabolic Syndrome
metabolic = metabolic_syndrome_indicators(extracted)
if metabolic:
    patterns.append(metabolic)

# Kidney Function
kidney = kidney_function_assessment(extracted)
if kidney:
    patterns.append(kidney)

# Thyroid Function
thyroid = thyroid_function_assessment(extracted)
if thyroid:
    patterns.append(thyroid)

# Anemia
anemia = anemia_assessment(extracted)
if anemia:
    patterns.append(anemia)

print("\n" + "="*60)
print("PATTERN ANALYSIS & RISK ASSESSMENT (Model 2)")
print("="*60)
if patterns:
    for i, p in enumerate(patterns, 1):
        print(f"\n{i}. {p.get('pattern', p.get('metric', 'Unknown Pattern'))}")
        if 'risk_level' in p:
            print(f"   Risk Level: {p['risk_level']}")
        if 'risk' in p:
            print(f"   Risk: {p['risk']}")
        if 'value' in p and 'metric' in p:
            print(f"   Value: {p['value']}")
        if 'indicators' in p:
            print(f"   Indicators:")
            for ind in p['indicators']:
                print(f"      - {ind}")
        if 'severity' in p:
            print(f"   Severity: {p['severity']}")
        if 'recommendation' in p:
            print(f"   Recommendation: {p['recommendation']}")
else:
    print("No significant patterns detected. All parameters within normal ranges.")

print("\n" + "="*60)

