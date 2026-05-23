"""Model loading and prediction helpers for classical ML models."""
from pathlib import Path
import joblib

MODEL_DIR = Path("models")
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.joblib"
MODEL_PATH = MODEL_DIR / "spam_classifier.joblib"


def load_model_bundle():
    """Load trained vectorizer and classifier from disk."""
    if not VECTORIZER_PATH.exists() or not MODEL_PATH.exists():
        raise FileNotFoundError("Model files not found. Run `python train.py` first.")
    return joblib.load(VECTORIZER_PATH), joblib.load(MODEL_PATH)


def predict_email(text: str) -> dict:
    """Predict spam/phishing likelihood from email text."""
    clean_text = (text or "").strip()
    if not clean_text:
        return {"label": "safe", "confidence": 0.0, "probabilities": {"safe": 1.0, "spam": 0.0, "phishing": 0.0}}

    vectorizer, model = load_model_bundle()
    features = vectorizer.transform([clean_text])
    label = str(model.predict(features)[0])

    probabilities = {"safe": 0.0, "spam": 0.0, "phishing": 0.0}
    confidence = 0.75
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(features)[0]
        classes = [str(c) for c in model.classes_]
        probabilities.update({cls: float(score) for cls, score in zip(classes, proba)})
        confidence = float(max(proba))

    return {"label": label, "confidence": confidence, "probabilities": probabilities}
