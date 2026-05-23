"""Attachment risk scanning by filename, extension, and size."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path

DANGEROUS = {".exe", ".scr", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".jar", ".iso", ".lnk"}
MACRO_DOCS = {".docm", ".xlsm", ".pptm"}
ARCHIVES = {".zip", ".rar", ".7z", ".gz"}

@dataclass
class AttachmentFinding:
    filename: str
    score: int
    reasons: list[str]


def scan_attachment(filename: str, size_bytes: int = 0) -> dict:
    """Scan attachment metadata without executing or opening file contents."""
    name = Path(filename or "").name
    suffixes = [s.lower() for s in Path(name).suffixes]
    ext = suffixes[-1] if suffixes else ""
    reasons: list[str] = []
    score = 0

    if ext in DANGEROUS:
        score += 55
        reasons.append(f"Dangerous executable/script extension {ext}")
    if ext in MACRO_DOCS:
        score += 35
        reasons.append("Macro-enabled Office document")
    if ext in ARCHIVES:
        score += 18
        reasons.append("Archive file may conceal payloads")
    if len(suffixes) >= 2 and suffixes[-1] in DANGEROUS:
        score += 30
        reasons.append("Double extension ending in executable type")
    if size_bytes > 20 * 1024 * 1024:
        score += 10
        reasons.append("Large attachment size")
    if not name:
        score += 15
        reasons.append("Missing filename")

    return asdict(AttachmentFinding(filename=name, score=min(score, 100), reasons=reasons or ["No major attachment indicators"]))


def scan_attachments(files: list[tuple[str, int]]) -> list[dict]:
    """Scan a list of (filename, size_bytes) tuples."""
    return [scan_attachment(name, size) for name, size in files]
