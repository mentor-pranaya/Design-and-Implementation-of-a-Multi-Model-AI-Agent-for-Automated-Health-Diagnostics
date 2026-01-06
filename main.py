from src.input_parser.input_handler import read_input
from src.extraction.extractor import extract_parameter
from src.config.parameters import REQUIRED_PARAMETERS
from src.model_1.interpretation import interpret_value

file_path = "data/pdf/Blood_report_pdf_1.pdf"
data = read_input(file_path)

results = {}

# for unstructured text pdf or image

if isinstance(data,str):
    for param_name, keywords in REQUIRED_PARAMETERS.items():
        extracted = extract_parameter(data, param_name, keywords)

        if extracted:
            results[param_name] = extracted[param_name]
        else:
            results[param_name] = None
elif isinstance(data, dict):
    for param_name in REQUIRED_PARAMETERS:
        results[param_name] = data.get(param_name,None)


## Model 1

for param_name, param_data in results.items():
    if param_data is not None:
        status = interpret_value(
            param_data.get("value"),
            param_data.get("reference_range")
        )
        results[param_name]['status'] = status

print("Final Extracted Parameters:")
print(results)
