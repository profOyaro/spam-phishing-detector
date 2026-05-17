"""
Module 5: Prediction Engine
Loads the trained best_model.joblib and classifies email text.

Usage:
    python predict.py --text "Your account has been suspended, click here..."
    python predict.py --file path/to/email.txt
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

import joblib

from app.preprocessing import clean_text, extract_urls, suspicious_url_score

ROOT = Path(__file__).parent
MODEL_PATH = ROOT / "models" / "best_model.joblib"
LOGS_DIR = ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "predictions.log"

MAX_INPUT_LEN = 50_000  # protect against pathological inputs


class EmailClassifier:
    """OOP wrapper around the trained pipeline."""

    def __init__(self, model_path: Path = MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}. Run `python train_model.py` first."
            )
        self.model = joblib.load(model_path)
        self.classes_ = list(self.model.classes_)

    def predict(self, raw_text: str) -> dict:
        if not isinstance(raw_text, str):
            raise TypeError("Email text must be a string.")
        if not raw_text.strip():
            raise ValueError("Email text is empty.")
        if len(raw_text) > MAX_INPUT_LEN:
            raw_text = raw_text[:MAX_INPUT_LEN]

        cleaned = clean_text(raw_text)
        probs = self.model.predict_proba([cleaned])[0]
        idx = int(probs.argmax())
        label = self.classes_[idx]
        confidence = float(probs[idx])

        urls = extract_urls(raw_text)
        url_risk = suspicious_url_score(raw_text)

        # Bump prediction toward "phishing" if URL heuristics strongly disagree
        if "phishing" in self.classes_ and url_risk >= 0.75 and label == "spam":
            label = "phishing"
            confidence = max(confidence, 0.5 + url_risk / 2)

        risk_level = self._risk_level(label, confidence, url_risk)

        result = {
            "label": label,
            "confidence": round(confidence, 4),
            "risk_level": risk_level,
            "probabilities": {c: round(float(p), 4) for c, p in zip(self.classes_, probs)},
            "urls_found": urls,
            "url_risk_score": round(url_risk, 4),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        self._log(raw_text, result)
        return result

    @staticmethod
    def _risk_level(label: str, conf: float, url_risk: float) -> str:
        if label == "phishing":
            return "HIGH"
        if label == "spam":
            return "MEDIUM" if conf > 0.6 else "LOW-MEDIUM"
        if url_risk > 0.5:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _log(raw_text: str, result: dict) -> None:
        entry = {
            "ts": result["timestamp"],
            "label": result["label"],
            "confidence": result["confidence"],
            "risk_level": result["risk_level"],
            "preview": raw_text[:120].replace("\n", " "),
        }
        try:
            with LOG_FILE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError:
            pass  # logging must never break prediction


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify an email as ham/spam/phishing")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="Raw email text")
    g.add_argument("--file", help="Path to .txt/.eml file")
    args = parser.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8", errors="ignore")
    else:
        text = args.text

    clf = EmailClassifier()
    result = clf.predict(text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
