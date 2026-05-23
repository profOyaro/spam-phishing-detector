"""OCR-based phishing checks for screenshots and images."""
from __future__ import annotations
from PIL import Image
from app.explainability import keyword_highlights


def extract_text_from_image(image: Image.Image) -> str:
    """Extract text using pytesseract when available."""
    try:
        import pytesseract
        return pytesseract.image_to_string(image)
    except Exception:
        return ""


def analyze_screenshot(image: Image.Image) -> dict:
    """Analyze OCR text from a screenshot for phishing language."""
    text = extract_text_from_image(image)
    highlights = keyword_highlights(text)
    score = min(100, len(highlights) * 15)
    return {"score": score, "text": text, "suspicious_keywords": highlights}
