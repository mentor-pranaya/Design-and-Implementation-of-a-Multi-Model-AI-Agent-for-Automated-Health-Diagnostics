from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        # Title
        self.cell(0, 10, 'AI HEALTH DIAGNOSTICS REPORT', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'DISCLAIMER: This is an AI-generated report. Consult a doctor for medical advice. | Page ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('Arial', '', 11)
        # Handle emojis by stripping or replacing them since standard FPDF doesn't support them well
        safe_text = text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, safe_text)
        self.ln()

def generate_pdf(results):
    pdf = PDFReport()
    pdf.add_page()
    
    # 1. Patient Context
    pdf.chapter_title('PATIENT CONTEXT')
    patient = results.get('patient', {})
    age = patient.get('age', 'Unknown')
    gender = patient.get('gender', 'Unknown')
    pdf.chapter_body(f"Age: {age}\nGender: {gender}")
    
    # 2. Clinical Findings Table
    pdf.chapter_title('CLINICAL FINDINGS')
    detailed = results.get('detailed_biomarkers', [])
    
    if not detailed:
        pdf.chapter_body("No structured clinical data available.")
    else:
        # Table Header
        pdf.set_font('Arial', 'B', 10)
        # Columns widths: Param(60), Value(20), Unit(20), Ref(40), Status(50)
        col_widths = [60, 20, 20, 40, 50]
        headers = ["Parameter", "Value", "Unit", "Reference", "Status"]
        
        for i in range(len(headers)):
            pdf.cell(col_widths[i], 8, headers[i], 1, 0, 'C')
        pdf.ln()
        
        # Table Rows
        pdf.set_font('Arial', '', 9)
        for row in detailed:
            param = str(row.get('Parameter', ''))[:35] # Truncate if too long
            val = str(row.get('Value', ''))
            unit = str(row.get('Unit', ''))
            ref = str(row.get('Reference Range', ''))
            status = str(row.get('Status', ''))
            
            pdf.cell(col_widths[0], 8, param, 1, 0, 'L')
            pdf.cell(col_widths[1], 8, val, 1, 0, 'C')
            pdf.cell(col_widths[2], 8, unit, 1, 0, 'C')
            pdf.cell(col_widths[3], 8, ref, 1, 0, 'C')
            
            # Highlight status
            if "Normal" not in status:
                pdf.set_text_color(200, 0, 0)
            else:
                pdf.set_text_color(0, 100, 0)
            pdf.cell(col_widths[4], 8, status, 1, 0, 'L')
            pdf.set_text_color(0, 0, 0) # reset
            pdf.ln()
        pdf.ln(5)
    
    # 3. Risk Patterns Detected
    pdf.chapter_title('RISK PATTERNS DETECTED')
    risks = results.get('risks', [])
    if not risks:
        pdf.chapter_body("No complex risk patterns detected.")
    else:
        risk_text = ""
        for r in risks:
            risk_text += f"- {r['Pattern']}: {r['Significance']}\n"
        pdf.chapter_body(risk_text)

    # 4. Recommendations
    pdf.chapter_title('RECOMMENDATIONS')
    advice = results.get('advice', 'No specific advice generated.')
    # Strip emojis manually for FPDF compatibility
    advice = advice.replace("✅", "").replace("🥗", "").replace("💧", "").replace("😴", "").replace("🩺", "").replace("👉", "->").replace("⚠️", "[WARNING]").replace("🔬", "[ALERT]")
    
    # Strip markdown symbols
    advice = advice.replace("**", "")
    advice = advice.replace("### ", "")
    
    pdf.chapter_body(advice)

    # Return as bytes
    # fpdf's output returns a string if dest='S', so we must encode to latin-1
    return pdf.output(dest='S').encode('latin-1')
