"""PDF incident report generation."""
from __future__ import annotations
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def build_pdf_report(result: dict) -> bytes:
    """Create a concise PDF report for a scan result."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Email Threat Analysis Report")
    y -= 35
    c.setFont("Helvetica", 10)
    for line in [
        f"Subject: {result.get('subject', '')}",
        f"Sender: {result.get('sender', '')}",
        f"Prediction: {result.get('ml', {}).get('label', '')}",
        f"Threat Score: {result.get('risk', {}).get('score', 0)} / 100",
        f"Threat Level: {result.get('risk', {}).get('level', '')}",
    ]:
        c.drawString(50, y, line[:110])
        y -= 18
    y -= 12
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Key Findings")
    y -= 18
    c.setFont("Helvetica", 9)
    for section in ["urls", "sender_check", "attachments", "headers", "explainability"]:
        c.drawString(50, y, f"{section}: {str(result.get(section, ''))[:105]}")
        y -= 16
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 9)
    c.save()
    return buffer.getvalue()
