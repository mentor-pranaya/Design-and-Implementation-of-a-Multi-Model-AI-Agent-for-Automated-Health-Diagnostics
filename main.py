from src.input_parser.input_handler import read_input
from src.extraction.extractor import extract_parameter
from src.config.parameters import REQUIRED_PARAMETERS
from src.model_1.interpretation import interpret_value
from src.model_2.pattern_detector import detect_all_patterns


# Read input (ALL formats)


# file_path = "data/json/Blood_report_json_2.json"
# file_path = "data/images/blood_report_img_2.jpg"
file_path = "data/pdf/Blood_report_pdf_3.pdf"

data = read_input(file_path)

results = {}

#  Unstructured input (OCR / PDF → text)
if isinstance(data, str):
    for param_name, keywords in REQUIRED_PARAMETERS.items():
        extracted = extract_parameter(data, param_name, keywords)
        results[param_name] = extracted.get(param_name) if extracted else None

# Structured input (JSON → dict)
elif isinstance(data, dict):
    for param_name in REQUIRED_PARAMETERS:
        results[param_name] = data.get(param_name)

else:
    raise ValueError("Unsupported input data type")

# Model 1 Interpretation


for param_name, param_data in results.items():
    if param_data:
        status = interpret_value(
            param_data.get("value"),
            param_data.get("reference_range")
        )
        param_data["status"] = status

# model 2
patterns = detect_all_patterns(results)

#final output

print("FINAL EXTRACTED PARAMETERS (Model 1):")
print("\n")

for param_name, param_data in results.items():
    if param_data:
        value = param_data.get("value")
        unit = param_data.get("unit", "")
        status = param_data.get("status","")
        ref_range = param_data.get("reference_range","")
        print(f" {param_name}: {value} {unit} [{ref_range}] --> {status}")
    else:
        print(f" {param_name}: Not Found")

print("\n")

print("DETECTED PATTERNS (Model 2):")


if patterns:
    for i, pattern in enumerate(patterns,1):
        print(f"\n Patterns{i}: {pattern['pattern']}")
        print(f" Confidence: {pattern['confidence']}%")
        print(f" Description: {pattern['description']}")
        print(f" Indicators:")
        for indicator in pattern['indicators']:
            print(f"  -{indicator}")
else:
    print(" No concerning patterns detected. All values appear normal.")





# # Final Output
# print("Final Extracted Parameters:")
# print(results)
