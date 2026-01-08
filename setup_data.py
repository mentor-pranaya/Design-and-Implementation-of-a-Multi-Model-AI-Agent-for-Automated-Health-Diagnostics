from reportlab.pdfgen import canvas

def create_sample_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "Medical Lab Report")
    c.drawString(100, 730, "Patient Name: John Doe")
    c.drawString(100, 700, "Test Results:")
    c.drawString(100, 680, "Hemoglobin 13.2 g/dL")
    c.drawString(100, 660, "Glucose 110 mg/dL")
    c.drawString(100, 640, "Cholesterol 210 mg/dL")
    c.save()

if __name__ == "__main__":
    create_sample_pdf("sample_blood_report.pdf")
    print("Sample PDF created.")
