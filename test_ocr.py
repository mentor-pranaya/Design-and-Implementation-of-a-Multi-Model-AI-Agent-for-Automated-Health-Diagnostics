import easyocr

# Initialize reader (English)
reader = easyocr.Reader(['en'])

# Image path
image_path = r"D:\Projects\heartflow-impact\src\assets\sample_report_json.png"
# Run OCR
results = reader.readtext(image_path)

# Print extracted text
for bbox, text, confidence in results:
    print(text, "->", confidence)

