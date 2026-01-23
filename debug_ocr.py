from ocr_extractor import extract_text_with_ocr
from cleaner import extract_parameters

pdf_path = "OCR_Test_Scanned_Report.pdf"

print("=== OCR TEXT EXTRACTION DEBUG ===\n")
text = extract_text_with_ocr(pdf_path)
print("--- RAW OCR TEXT ---")
print(text)
print("--- END RAW TEXT ---\n")

print("--- EXTRACTED PARAMETERS ---")
parameters = extract_parameters(text)
print(parameters)
