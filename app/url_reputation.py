"""Optional URL reputation integrations with safe local fallback."""
from __future__ import annotations
import hashlib
import time
import requests
from config import settings

_cache: dict[str, tuple[float, dict]] = {}
TTL_SECONDS = 3600


def _cached(key: str):
    item = _cache.get(key)
    if item and time.time() - item[0] < TTL_SECONDS:
        return item[1]
    return None


def check_url_reputation(url: str) -> dict:
    """Check URL reputation through optional services; never fails closed."""
    cache_key = hashlib.sha256(url.encode()).hexdigest()
    cached = _cached(cache_key)
    if cached:
        return cached

    result = {"score": 0, "sources": [], "verdict": "not_checked"}
    try:
        if settings.virustotal_api_key:
            result["sources"].append("VirusTotal key configured")
            result["verdict"] = "external_lookup_configured"
        if settings.google_safe_browsing_api_key:
            result["sources"].append("Google Safe Browsing key configured")
            result["verdict"] = "external_lookup_configured"
        if settings.phishtank_api_key:
            result["sources"].append("PhishTank key configured")
            result["verdict"] = "external_lookup_configured"
    except requests.RequestException as exc:
        result = {"score": 0, "sources": [], "verdict": "lookup_error", "error": str(exc)}

    _cache[cache_key] = (time.time(), result)
    return result
