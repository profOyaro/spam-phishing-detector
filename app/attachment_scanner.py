"""Attachment risk scoring."""
DANGEROUS = {"exe","scr","bat","cmd","js","vbs","ps1","jar","msi","hta","wsf"}
OFFICE = {"doc","docm","xls","xlsm","ppt","pptm"}

def scan(filename: str, content: bytes) -> dict:
    name = filename.lower()
    parts = name.split(".")
    ext = parts[-1] if len(parts) > 1 else ""
    score, reasons = 0, []
    if ext in DANGEROUS:
        score += 60; reasons.append(f"Dangerous extension .{ext}")
    if len(parts) >= 3 and parts[-2] in {"pdf","jpg","png","doc","txt"} and ext in DANGEROUS:
        score += 25; reasons.append("Double extension")
    if ext in OFFICE:
        score += 20; reasons.append("Macro-capable Office document")
    if content[:2] == b"MZ":
        score += 30; reasons.append("Windows PE executable signature")
    if b"vbaProject.bin" in content[:8192]:
        score += 25; reasons.append("Embedded VBA macro detected")
    return {"filename": filename, "score": min(score, 100), "reasons": reasons or ["No obvious risks"]}
