"""Explainable AI helpers for analyst-friendly output."""
from __future__ import annotations
import re

SUSPICIOUS_TERMS = {
    "urgent", "verify", "password", "suspended", "invoice", "payment", "wire",
    "gift card", "login", "account", "security alert", "click", "limited time"
}


def keyword_highlights(text: str) -> list[str]:
    """Return suspicious words and phrases found in the email body."""
    lower = (text or "").lower()
    return sorted(term for term in SUSPICIOUS_TERMS if term in lower)


def feature_importance_summary(text: str, ml_result: dict) -> dict:
    """Provide a lightweight explanation that works even without SHAP/ELI5 installed."""
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text or "")
    highlights = keyword_highlights(text)
    return {
        "model_label": ml_result.get("label", "unknown"),
        "model_confidence": ml_result.get("confidence", 0),
        "suspicious_keywords": highlights,
        "top_tokens": tokens[:20],
        "summary": "High-risk language found" if highlights else "No strong suspicious keyword cluster found",
    }
