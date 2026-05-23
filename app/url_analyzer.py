"""URL extraction and local phishing heuristics."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import ipaddress
import re
import tldextract

URL_RE = re.compile(r"https?://[^\s<>'\"]+|www\.[^\s<>'\"]+", re.IGNORECASE)
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly", "cutt.ly", "rebrand.ly", "lnkd.in"}
SUSPICIOUS_TLDS = {"zip", "mov", "click", "country", "kim", "top", "work", "quest", "gq", "tk", "ml"}
BRANDS = {"paypal", "microsoft", "office", "apple", "google", "amazon", "netflix", "docusign", "bank", "linkedin"}

@dataclass
class UrlFinding:
    url: str
    domain: str
    score: int
    reasons: list[str]


def extract_urls(text: str) -> list[str]:
    """Extract URLs from plain text and normalize missing schemes."""
    urls = URL_RE.findall(text or "")
    return [u if u.lower().startswith("http") else f"http://{u}" for u in urls]


def _is_ip_host(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def analyze_url(url: str) -> UrlFinding:
    """Analyze a single URL and return a score plus reasons."""
    reasons: list[str] = []
    score = 0
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().strip(".")
    extracted = tldextract.extract(host)
    domain = ".".join(part for part in [extracted.domain, extracted.suffix] if part)

    if not host:
        return UrlFinding(url=url, domain="", score=40, reasons=["Malformed URL"])
    if _is_ip_host(host):
        score += 35
        reasons.append("IP-address-based URL")
    if domain in SHORTENERS:
        score += 25
        reasons.append("Shortened URL")
    if extracted.suffix in SUSPICIOUS_TLDS:
        score += 20
        reasons.append(f"Suspicious TLD .{extracted.suffix}")
    if "@" in parsed.netloc:
        score += 20
        reasons.append("URL contains @ symbol in host section")
    if host.count("-") >= 3:
        score += 10
        reasons.append("Excessive hyphen usage")
    if parsed.scheme != "https":
        score += 8
        reasons.append("Non-HTTPS link")
    for brand in BRANDS:
        if brand in host and brand not in domain:
            score += 25
            reasons.append(f"Possible {brand} lookalike or subdomain abuse")
            break
    if "xn--" in host:
        score += 25
        reasons.append("Punycode domain may indicate homograph attack")

    return UrlFinding(url=url, domain=domain or host, score=min(score, 100), reasons=reasons or ["No major local URL indicators"])


def analyze_urls(text: str) -> list[dict]:
    """Analyze all URLs in the supplied email body."""
    return [asdict(analyze_url(url)) for url in extract_urls(text)]
