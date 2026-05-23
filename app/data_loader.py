"""
Module 1: Data Collection
Loads CSV datasets and validates required columns.
"""
import pandas as pd
from pathlib import Path

REQUIRED_COLS = {"text", "label"}
VALID_LABELS = {"ham", "spam", "phishing"}


def load_dataset(csv_path: str | Path) -> pd.DataFrame:
    """Load a CSV with 'text' and 'label' columns. Validate and clean."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    df.columns = [c.lower().strip() for c in df.columns]

    # Auto-map common alternative column names
    rename = {}
    for c in df.columns:
        if c in ("message", "email", "content", "body"):
            rename[c] = "text"
        if c in ("class", "category", "type", "target"):
            rename[c] = "label"
    df = df.rename(columns=rename)

    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {missing}")

    df = df[["text", "label"]].dropna()
    df["label"] = df["label"].astype(str).str.lower().str.strip()
    df = df[df["label"].isin(VALID_LABELS)].reset_index(drop=True)

    if df.empty:
        raise ValueError("No valid rows after cleaning. Expected labels: ham/spam/phishing.")
    return df
