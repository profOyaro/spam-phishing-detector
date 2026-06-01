"""Generate downloadable PDF incident reports."""
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def build(title: str, result: dict, explanation: dict) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 50
    c.setFont("Helvetica-Bold", 16); c.drawString(40, y, title); y -= 30
    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Risk score: {result.get('score','?')}/100"); y -= 18
    c.drawString(40, y, "Reasons:"); y -= 16
    for r in explanation.get("reasons", []):
        c.drawString(60, y, f"- {r[:90]}"); y -= 14
        if y < 80: c.showPage(); y = h - 50
    y -= 10; c.drawString(40, y, "Recommendations:"); y -= 16
    for r in explanation.get("recommendations", []):
        c.drawString(60, y, f"- {r[:90]}"); y -= 14
    c.showPage(); c.save()
    return buf.getvalue()
