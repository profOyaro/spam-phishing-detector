"""SQLite persistence for scan history."""
from __future__ import annotations
from pathlib import Path
import json
import sqlite3
from datetime import datetime, timezone
from config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    subject TEXT,
    sender TEXT,
    label TEXT NOT NULL,
    risk_score REAL NOT NULL,
    risk_level TEXT NOT NULL,
    details_json TEXT NOT NULL
);
"""


def get_connection():
    """Open a SQLite connection and ensure parent directories exist."""
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(settings.database_path)
    con.execute(SCHEMA)
    return con


def log_detection(subject: str, sender: str, label: str, risk: dict, details: dict) -> int:
    """Insert one detection result and return its database ID."""
    con = get_connection()
    cur = con.execute(
        "INSERT INTO detections(created_at, subject, sender, label, risk_score, risk_level, details_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), subject, sender, label, risk["score"], risk["level"], json.dumps(details, default=str)),
    )
    con.commit()
    row_id = int(cur.lastrowid)
    con.close()
    return row_id


def list_detections(limit: int = 200) -> list[dict]:
    """Return recent detections for the dashboard history tab."""
    con = get_connection()
    rows = con.execute(
        "SELECT id, created_at, subject, sender, label, risk_score, risk_level FROM detections ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    con.close()
    keys = ["id", "created_at", "subject", "sender", "label", "risk_score", "risk_level"]
    return [dict(zip(keys, row)) for row in rows]
