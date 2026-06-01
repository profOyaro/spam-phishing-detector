"""Explainable AI: weighted, human-readable reasons + recommendations."""
def explain(result: dict) -> dict:
    reasons = []
    for u in result.get("urls", []):
        for r in u.get("reasons", []):
            reasons.append(f"URL {u['host']}: {r}")
    for k in result.get("keywords", []):
        reasons.append(f"Suspicious keyword: '{k}'")
    if result.get("ml_probability") is not None:
        reasons.append(f"ML phishing probability: {result['ml_probability']:.0%}")
    recs = []
    if result.get("score", 0) >= 60:
        recs += ["Do not click any links", "Report to your security team",
                 "Delete the message after reporting"]
    elif result.get("score", 0) >= 35:
        recs += ["Verify sender via a trusted channel", "Hover over links before clicking"]
    else:
        recs += ["No immediate action needed"]
    return {"reasons": reasons, "recommendations": recs}
