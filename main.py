from src.input_parser.input_handler import read_input
from src.extraction.extractor import extract_parameter
from src.config.parameters import REQUIRED_PARAMETERS
from src.model_1.interpretation import interpret_value


# Read input (ALL formats)


# file_path = "data/json/Blood_report_json_2.json"
file_path = "data/images/blood_report_img_1.jpg"
# file_path = "data/pdf/Blood_report_pdf_4.pdf"

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


# Final Output


print("Final Extracted Parameters:")
print(results)
