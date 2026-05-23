"""Email header forensics for authentication and routing anomalies."""
from __future__ import annotations
from email import policy
from email.parser import Parser


def analyze_headers(raw_email: str) -> dict:
    """Inspect raw email headers for SPF, DKIM, DMARC, and identity mismatches."""
    msg = Parser(policy=policy.default).parsestr(raw_email or "")
    headers = {k.lower(): str(v) for k, v in msg.items()}
    reasons: list[str] = []
    score = 0
    auth = headers.get("authentication-results", "").lower()

    for mechanism in ["spf", "dkim", "dmarc"]:
        if mechanism in auth and "pass" not in auth.split(mechanism, 1)[1][:40]:
            score += 18
            reasons.append(f"{mechanism.upper()} did not clearly pass")
        elif mechanism not in auth:
            score += 8
            reasons.append(f"Missing {mechanism.upper()} result")

    from_header = headers.get("from", "")
    reply_to = headers.get("reply-to", "")
    return_path = headers.get("return-path", "")
    if reply_to and reply_to.lower() != from_header.lower():
        score += 18
        reasons.append("Reply-To differs from From")
    if return_path and from_header and return_path.lower() not in from_header.lower():
        score += 10
        reasons.append("Return-Path differs from From")

    received_count = sum(1 for k in headers if k == "received")
    if received_count >= 6:
        score += 8
        reasons.append("Long relay chain")

    return {"score": min(score, 100), "reasons": reasons or ["No major header indicators"], "headers_seen": sorted(headers.keys())}
