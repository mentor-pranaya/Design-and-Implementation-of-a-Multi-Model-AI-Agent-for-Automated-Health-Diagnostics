# core_phase1/ocr/test_ocr.py

from core_phase1.ocr.pdf_ocr import extract_text_from_pdf
from pathlib import Path

pdf_path = Path("core_phase1/data/sample_report.pdf")
output_path = Path("core_phase2/input/ocr_output.txt")

text = extract_text_from_pdf(str(pdf_path))

# Save OCR output for Phase 2
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(text, encoding="utf-8")

print("OCR completed and text saved for Phase 2.")
