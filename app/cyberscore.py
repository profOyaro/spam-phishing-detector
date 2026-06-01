"""Compute per-user cybersecurity score."""
from . import db

def for_user(user_id: int) -> int:
    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) c FROM scans WHERE user_id=?", (user_id,))
        scans = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) c FROM incidents WHERE user_id=?", (user_id,))
        reports = cur.fetchone()["c"]
    return max(0, min(100, 40 + scans * 2 + reports * 5))
