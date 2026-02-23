from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap
import os


def generate_pdf(report_text, filename="final_health_report.pdf"):
    """
    Generates a PDF file from text and returns the filepath.
    """

    filepath = f"/tmp/{filename}"

    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    y = height - 50
    line_height = 14

    c.setFont("Helvetica", 11)

    wrapped_lines = []
    for line in report_text.split("\n"):
        wrapped_lines.extend(textwrap.wrap(line, width=95) or [""])

    for line in wrapped_lines:
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 50

        c.drawString(40, y, line)
        y -= line_height

    c.save()

    return filepath
