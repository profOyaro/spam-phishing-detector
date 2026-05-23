from app.url_analyzer import analyze_urls
from app.attachment_scanner import scan_attachment
from app.risk_engine import calculate_risk


def test_url_analyzer_flags_ip_url():
    findings = analyze_urls("Login at http://192.168.0.5/account now")
    assert findings[0]["score"] > 0


def test_attachment_double_extension():
    finding = scan_attachment("invoice.pdf.exe", 1000)
    assert finding["score"] >= 50


def test_risk_engine_returns_level():
    risk = calculate_risk(
        {"probabilities": {"phishing": 0.9, "spam": 0.1}},
        [{"score": 80}],
        {"score": 50},
        [],
        {"score": 30},
    )
    assert risk["level"] in {"Low", "Medium", "High", "Critical"}
