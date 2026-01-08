from extractor import extract_text
from cleaner import extract_parameters
from model1 import interpret

if __name__ == "__main__":
    pdf_path = "Milestone1_Blood_Report_Dataset.pdf"

    text = extract_text(pdf_path)
    parameters = extract_parameters(text)
    interpretation = interpret(parameters)

    print("Extracted Parameters:", parameters)
    print("Interpretation:", interpretation)
