from extractor import extract_text
from ocr_extractor import extract_text_with_ocr

pdf_path = "Milestone1_Blood_Report_Dataset.pdf"
print("--- TEST-BASED EXTRACTION ---")
text = extract_text(pdf_path)
print(f"Length: {len(text)}")
print(text[:500])

print("\n--- OCR-BASED EXTRACTION ---")
text_ocr = extract_text_with_ocr(pdf_path)
print(f"Length: {len(text_ocr)}")
print(text_ocr[:500])
