"""
Module 3 & 4: Feature Engineering + Model Training
Trains Logistic Regression and Random Forest models, compares them,
and persists the best one to models/.

Usage:
    python train_model.py --data data/sample_emails.csv
"""
import argparse
import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.data_loader import load_dataset
from app.preprocessing import clean_text

MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


def build_pipelines() -> dict[str, Pipeline]:
    """Two TF-IDF + classifier pipelines for fair comparison."""
    tfidf_kwargs = dict(
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True,
    )
    return {
        "logistic_regression": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf_kwargs)),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]),
        "random_forest": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf_kwargs)),
            ("clf", RandomForestClassifier(
                n_estimators=200, class_weight="balanced", random_state=42, n_jobs=-1
            )),
        ]),
    }


def evaluate(name: str, model: Pipeline, X_test, y_test) -> dict:
    preds = model.predict(X_test)
    labels = sorted(set(y_test) | set(preds))
    metrics = {
        "model": name,
        "accuracy": float(accuracy_score(y_test, preds)),
        "precision_weighted": float(precision_score(y_test, preds, average="weighted", zero_division=0)),
        "recall_weighted": float(recall_score(y_test, preds, average="weighted", zero_division=0)),
        "f1_weighted": float(f1_score(y_test, preds, average="weighted", zero_division=0)),
        "labels": labels,
        "confusion_matrix": confusion_matrix(y_test, preds, labels=labels).tolist(),
        "report": classification_report(y_test, preds, zero_division=0),
    }
    return metrics


def main(data_path: str) -> None:
    print(f"[1/5] Loading dataset: {data_path}")
    df = load_dataset(data_path)
    print(f"      rows={len(df)}, label distribution:\n{df['label'].value_counts().to_string()}")

    print("[2/5] Cleaning text...")
    df["clean"] = df["text"].apply(clean_text)

    print("[3/5] Splitting train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        df["clean"], df["label"], test_size=0.2, stratify=df["label"], random_state=42
    )

    print("[4/5] Training models...")
    pipelines = build_pipelines()
    results = {}
    for name, pipe in pipelines.items():
        pipe.fit(X_train, y_train)
        results[name] = evaluate(name, pipe, X_test, y_test)
        print(f"      {name}: accuracy={results[name]['accuracy']:.3f} "
              f"f1={results[name]['f1_weighted']:.3f}")

    # Persist all models + metrics
    print("[5/5] Saving artifacts to models/...")
    for name, pipe in pipelines.items():
        joblib.dump(pipe, MODELS_DIR / f"{name}.joblib")

    best_name = max(results, key=lambda k: results[k]["f1_weighted"])
    joblib.dump(pipelines[best_name], MODELS_DIR / "best_model.joblib")

    summary = {
        "best_model": best_name,
        "results": {k: {kk: vv for kk, vv in v.items() if kk != "report"}
                    for k, v in results.items()},
        "reports": {k: v["report"] for k, v in results.items()},
    }
    (MODELS_DIR / "metrics.json").write_text(json.dumps(summary, indent=2))

    print(f"\n✅ Done. Best model: {best_name}")
    print(f"   Artifacts: {MODELS_DIR}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train spam/phishing email classifiers")
    parser.add_argument("--data", default="data/sample_emails.csv",
                        help="Path to labelled CSV (columns: text,label)")
    args = parser.parse_args()
    main(args.data)
