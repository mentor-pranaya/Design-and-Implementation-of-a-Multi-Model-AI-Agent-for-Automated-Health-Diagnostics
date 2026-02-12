import os
import json
import csv
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "test_samples"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_json_sample():
    data = {
        "patient_id": "P001",
        "hemoglobin": 14.5,
        "wbc": 7000,
        "platelets": 250000,
        "glucose": 95,
        "cholesterol": 180,
        "blood_pressure": 120,
        "description": "Normal healthy patient"
    }
    path = os.path.join(OUTPUT_DIR, "normal.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Created {path}")

def create_csv_sample():
    data = [
        ["Parameter", "Value", "Unit"],
        ["Hemoglobin", "10.5", "g/dL"],
        ["WBC", "12000", "/mm3"],
        ["Platelets", "150000", "/mm3"],
        ["Cholesterol", "240", "mg/dL"]
    ]
    path = os.path.join(OUTPUT_DIR, "anemic_high_cholesterol.csv")
    with open(path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    print(f"Created {path}")

def create_txt_sample():
    content = """
    BLOOD TEST REPORT
    -----------------
    Patient Name: John Doe
    Date: 2024-02-12
    
    Glucose: 250 mg/dL  (High)
    HbA1c: 8.5 %        (High)
    Cholesterol: 210 mg/dL
    Triglycerides: 180 mg/dL
    
    Notes: Patient shows signs of diabetes.
    """
    path = os.path.join(OUTPUT_DIR, "diabetic.txt")
    with open(path, "w") as f:
        f.write(content)
    print(f"Created {path}")

def create_pdf_sample():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    lines = [
        "LABORATORY REPORT",
        "-----------------",
        "Parameter       Value   Unit",
        "Hemoglobin      13.0    g/dL",
        "RBC             4.8     mill/mm3",
        "WBC             6500    /mm3",
        "Platelets       280000  /mm3",
        "Sodium          140     mmol/L",
        "Potassium       4.2     mmol/L"
    ]
    
    for line in lines:
        pdf.cell(200, 10, txt=line, ln=1, align='L')
        
    path = os.path.join(OUTPUT_DIR, "standard_report.pdf")
    pdf.output(path)
    print(f"Created {path}")

def create_image_sample():
    # Create a simple image with text
    img = Image.new('RGB', (800, 600), color='white')
    d = ImageDraw.Draw(img)
    
    # We can't easily rely on system fonts being available in a specific path, 
    # so we use the default bitmap font which is small but readable for OCR in theory.
    # Ideally we'd load a TTF but to keep it simple and dependency-free:
    
    text = """
    URGENT CARE LABS
    
    Glucose: 60 mg/dL
    Cholesterol: 150 mg/dL
    Hemoglobin: 9.0 g/dL
    
    Status: Critical Hypoglycemia & Anemia
    """
    
    # Draw text (default font)
    d.text((50, 50), text, fill=(0, 0, 0))
    
    path = os.path.join(OUTPUT_DIR, "critical_image.png")
    img.save(path)
    print(f"Created {path}")

if __name__ == "__main__":
    create_json_sample()
    create_csv_sample()
    create_txt_sample()
    create_pdf_sample()
    create_image_sample()
    print("\nAll sample files generated in 'test_samples/' directory.")
