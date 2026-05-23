"""Sender identity and authentication checks."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from email.utils import parseaddr
import re

FREE_MAIL = {"gmail.com", "outlook.com", "hotmail.com", "yahoo.com", "proton.me", "icloud.com"}

@dataclass
class SenderFinding:
    sender: str
    domain: str
    score: int
    reasons: list[str]


def sender_domain(sender: str) -> str:
    """Extract sender domain from an email address or From header."""
    _, addr = parseaddr(sender or "")
    if "@" not in addr:
        return ""
    return addr.rsplit("@", 1)[1].lower()


def check_sender(sender: str, body: str = "") -> dict:
    """Score sender risk based on domain, display-name tricks, and brand usage."""
    reasons: list[str] = []
    score = 0
    domain = sender_domain(sender)
    lower_sender = (sender or "").lower()

    if not domain:
        return asdict(SenderFinding(sender=sender, domain="", score=35, reasons=["Missing or invalid sender address"]))
    if domain in FREE_MAIL and any(word in lower_sender for word in ["support", "security", "billing", "admin"]):
        score += 25
        reasons.append("Free-mail account using official-sounding identity")
    if re.search(r"[0-9]{4,}", domain):
        score += 10
        reasons.append("Domain contains long number sequence")
    if any(brand in lower_sender and brand not in domain for brand in ["paypal", "microsoft", "amazon", "apple", "google"]):
        score += 25
        reasons.append("Display name references a brand not matching sender domain")
    if "reply-to" in (body or "").lower() and domain not in (body or "").lower():
        score += 15
        reasons.append("Possible Reply-To domain mismatch in pasted headers")

    return asdict(SenderFinding(sender=sender, domain=domain, score=min(score, 100), reasons=reasons or ["No major sender indicators"]))
