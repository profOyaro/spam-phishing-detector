"""Heuristic URL risk analysis."""
import re
from urllib.parse import urlparse

SHORTENERS = {"bit.ly","tinyurl.com","goo.gl","t.co","ow.ly","is.gd","buff.ly"}
BRANDS = ["paypal","google","apple","microsoft","amazon","bank"]
URL_RE = re.compile(r"https?://[^\s<>'\"]+", re.I)

def extract_urls(text: str):
    return URL_RE.findall(text or "")

def analyze(url: str) -> dict:
    p = urlparse(url)
    host = (p.hostname or "").lower()
    reasons, score = [], 0
    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host or ""):
        reasons.append("Uses raw IP address"); score += 35
    if host in SHORTENERS:
        reasons.append("Shortened URL"); score += 20
    if host.count(".") >= 4:
        reasons.append("Excessive subdomains"); score += 10
    if "xn--" in host:
        reasons.append("Punycode (possible homograph)"); score += 25
    for b in BRANDS:
        if b in host and not host.endswith(f"{b}.com"):
            reasons.append(f"Brand lookalike for {b}"); score += 30
    if p.scheme != "https":
        reasons.append("No HTTPS"); score += 10
    return {"url": url, "host": host, "score": min(score, 100), "reasons": reasons}
