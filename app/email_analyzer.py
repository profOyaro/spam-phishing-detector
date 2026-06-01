"""Parses raw email text and runs ML + URL heuristics."""
import os, joblib, re
from email import message_from_string
from .url_analyzer import extract_urls, analyze as analyze_url

_MODEL = None
def _model():
    global _MODEL
    if _MODEL is None and os.path.exists("data/model.joblib"):
        _MODEL = joblib.load("data/model.joblib")
    return _MODEL

SUSPICIOUS_KEYWORDS = ["verify","urgent","click here","password","bank","wire","invoice","gift card","prize","lottery"]

def analyze(raw: str) -> dict:
    msg = message_from_string(raw) if "\n" in raw and ":" in raw.split("\n",1)[0] else None
    body = raw
    headers = {}
    if msg is not None:
        headers = {k: v for k, v in msg.items()}
        body = "\n".join(p.get_payload(decode=False) if isinstance(p.get_payload(), str)
                         else "" for p in (msg.walk() if msg.is_multipart() else [msg]))

    text_lower = body.lower()
    kw_hits = [k for k in SUSPICIOUS_KEYWORDS if k in text_lower]
    urls = [analyze_url(u) for u in extract_urls(body)]

    ml_prob = None
    m = _model()
    if m is not None:
        try:
            ml_prob = float(m.predict_proba([body])[0][1])
        except Exception:
            ml_prob = None

    score = 0
    if ml_prob is not None:
        score += int(ml_prob * 60)
    score += min(len(kw_hits) * 6, 25)
    score += min(sum(u["score"] for u in urls) // 2, 25)
    score = min(score, 100)
    return {
        "score": score,
        "headers": headers,
        "keywords": kw_hits,
        "urls": urls,
        "ml_probability": ml_prob,
    }
