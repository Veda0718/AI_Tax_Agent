"""
File: form1040_generator.py
Description:
    Generates a simplified U.S. Form 1040 PDF from computed tax summary data.
    Uses ReportLab to render numeric values in a clean, printable format.

Author: Veda Sahaja Bandi
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def generate_1040(summary, output_path="static/output_1040.pdf"):
    """Generate a simplified IRS Form 1040 PDF with user’s tax details."""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        os.remove(output_path)

    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, height - 50, "U.S. Individual Income Tax Return (Form 1040)")
    c.setFont("Helvetica", 10)
    c.drawString(200, height - 70, f"Tax Year 2024 – Generated {datetime.now():%b %d, %Y}")

    # Filing status (optional if you want to display it)
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 110, f"Filing Status: {summary.get('Filing Status', 'N/A')}")

    # Income + Tax summary
    start_y = height - 150
    line_height = 22
    c.setFont("Helvetica", 12)

    fields = [
        ("Total Income", summary.get("Total Income", 0.0)),
        ("Standard Deduction", summary.get("Standard Deduction", 0.0)),
        ("Taxable Income", summary.get("Taxable Income", 0.0)),
        ("Tax (Owed Before Withholding)", summary.get("Federal Tax Owed", 0.0)),
        ("Federal Tax Withheld", summary.get("Federal Tax Withheld", 0.0)),
        ("Refund / Amount Due", summary.get("Refund or Balance Due", 0.0)),
    ]

    for label, value in fields:
        c.drawString(80, start_y, f"{label}")
        c.drawRightString(500, start_y, f"${value:,.2f}")
        start_y -= line_height

    # Refund Highlight
    c.setFont("Helvetica-Bold", 13)
    c.setFillColorRGB(0, 0.4, 0)
    refund = summary.get("Refund or Balance Due", 0.0)
    c.drawString(80, start_y - 20, f"Refund Due to You: ${refund:,.2f}")
    c.setFillColorRGB(0, 0, 0)

    # Footer / disclaimer
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(80, 80, "This automatically generated summary is for demonstration only and not an official IRS filing.")

    c.save()
    return output_path
