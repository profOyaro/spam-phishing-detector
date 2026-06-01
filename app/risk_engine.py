"""Map numeric risk score to level + class."""
def level(score: int) -> str:
    if score >= 80: return "Critical"
    if score >= 60: return "High"
    if score >= 35: return "Medium"
    if score >= 15: return "Low"
    return "Safe"

def classify(score: int) -> str:
    if score >= 60: return "Phishing"
    if score >= 35: return "Suspicious"
    return "Legitimate"
