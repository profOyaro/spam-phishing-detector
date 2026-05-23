"""Optional DistilBERT deep-learning classifier wrapper."""
from __future__ import annotations


def distilbert_predict(text: str) -> dict:
    """Return a deep-learning score if transformers are available; otherwise fallback."""
    try:
        from transformers import pipeline
        classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
        output = classifier((text or "")[:1500])[0]
        suspicious = output["label"].upper() == "NEGATIVE"
        return {"available": True, "label": "phishing" if suspicious else "safe", "confidence": float(output["score"])}
    except Exception as exc:
        return {"available": False, "label": "not_run", "confidence": 0.0, "reason": str(exc)}
