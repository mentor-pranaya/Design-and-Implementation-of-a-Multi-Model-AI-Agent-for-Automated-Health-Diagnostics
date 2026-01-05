# from src.input_parser.json_reader import read_json

# json_path = "data/json/sample_report.json"

# data = read_json(json_path)

# print("JSON Data Read Successfully:")
# print(data)



# from src.input_parser.pdf_reader import read_pdf
# pdf_path = "data/pdf/Blood_report_pdf_1.pdf"

# text = read_pdf(pdf_path)
# print("PDF Text Output:\n")
# print(text[:1000])

# from src.input_parser.image_reader import read_image
# image_path = "data/images/blood_report_img_2.jpg"


# text = read_image(image_path)
# print("OCR Text Output:\n")
# print(text[:1000])



from src.input_parser.input_handler import read_input

from src.extraction.extractor import extract_rbc
file_path = "data/pdf/Blood_report_pdf_2.pdf"
text = read_input(file_path)


rbc_data = extract_rbc(text)

print("Extracted RBC Data:")
print(rbc_data)
