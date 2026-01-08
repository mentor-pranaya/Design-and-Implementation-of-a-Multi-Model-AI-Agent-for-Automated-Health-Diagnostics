from extraction.parameter_extractor import extract_parameters

ocr_text = """
Crystal Data Inc.
COMPLETE BLOOD COUNT
Hemoglobin 14.5 g/dL
TOTAL WBC COUNT 8100
Platelet Count 250000
MCV 84.0
MCHC 32.5
"""

params = extract_parameters(ocr_text)

print("Extracted Parameters:")
for k, v in params.items():
    print(k, ":", v)
