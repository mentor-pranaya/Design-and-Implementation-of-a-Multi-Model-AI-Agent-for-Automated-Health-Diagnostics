from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime


def generate_pdf_report(interpreted_data, patterns, recommendations, user_context):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("AI HEALTH DIAGNOSTIC REPORT", styles["Heading1"]))
    elements.append(Spacer(1, 10))

    # User Info
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    elements.append(Paragraph(f"User: {user_context['age']} yrs | {user_context['gender']}", styles["Normal"]))
    elements.append(Paragraph(f"Goal: {user_context['goal']}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    # Table for Lab Results
    table_data = [["Parameter", "Value", "Unit", "Status"]]
    for item in interpreted_data:
        table_data.append([
            item["parameter"],
            str(item["value"]),
            item["unit"],
            item["status"]
        ])

    table = Table(table_data)
    table.setStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("BACKGROUND",(0,1),(-1,-1),colors.beige),
    ])
    elements.append(table)
    elements.append(Spacer(1, 10))

    # Patterns
    elements.append(Paragraph("Key Clinical Patterns", styles["Heading2"]))
    for p in patterns:
        elements.append(Paragraph(f"- {p['pattern']}: {p['finding']} ({p['severity']})", styles["Normal"]))
    elements.append(Spacer(1, 10))

    # Recommendations
    elements.append(Paragraph("Personalized Recommendations", styles["Heading2"]))
    elements.append(Paragraph(recommendations.replace("\n", "<br/>"), styles["Normal"]))

    # Disclaimer
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        "DISCLAIMER: This AI-generated report is for educational purposes only and is NOT medical advice.",
        styles["Italic"]
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


