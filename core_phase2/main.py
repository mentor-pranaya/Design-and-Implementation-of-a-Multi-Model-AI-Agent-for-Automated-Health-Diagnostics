from pathlib import Path
from core_phase2.extraction.parameter_extractor import extract_parameters

text = Path("core_phase2/input/ocr_output.txt").read_text(encoding="utf-8")

params = extract_parameters(text)

print("EXTRACTED PARAMETERS:")
print(params)
