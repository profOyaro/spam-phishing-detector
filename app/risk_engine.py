"""Weighted threat scoring engine."""
from __future__ import annotations


def _avg(items: list[dict], key: str = "score") -> float:
    if not items:
        return 0.0
    return sum(float(i.get(key, 0)) for i in items) / len(items)


def risk_level(score: float) -> str:
    """Convert a numeric score into a SOC-friendly severity label."""
    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


def calculate_risk(ml_result: dict, urls: list[dict], sender: dict, attachments: list[dict], headers: dict | None = None) -> dict:
    """Combine ML, URL, sender, attachment, and header signals into one score."""
    probabilities = ml_result.get("probabilities", {})
    ml_score = max(float(probabilities.get("spam", 0)), float(probabilities.get("phishing", 0))) * 100
    url_score = _avg(urls)
    sender_score = float(sender.get("score", 0))
    attachment_score = _avg(attachments)
    header_score = float((headers or {}).get("score", 0))

    score = (
        ml_score * 0.35
        + url_score * 0.22
        + sender_score * 0.16
        + attachment_score * 0.14
        + header_score * 0.13
    )
    score = round(min(max(score, 0), 100), 2)
    return {
        "score": score,
        "level": risk_level(score),
        "components": {
            "ml": round(ml_score, 2),
            "url": round(url_score, 2),
            "sender": round(sender_score, 2),
            "attachments": round(attachment_score, 2),
            "headers": round(header_score, 2),
        },
    }
