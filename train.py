"""Train classical ML classifiers for spam and phishing detection."""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion

DATA_PATH = Path("data/sample_emails.csv")
MODEL_DIR = Path("models")


def main():
    MODEL_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(DATA_PATH)
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.25, random_state=42, stratify=df["label"]
    )
    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        stop_words="english",
        ngram_range=(1, 2),
        max_features=12000,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    logistic = LogisticRegression(max_iter=1500, class_weight="balanced")
    logistic.fit(X_train_vec, y_train)
    print("Logistic Regression")
    print(classification_report(y_test, logistic.predict(X_test_vec)))

    forest = RandomForestClassifier(n_estimators=160, random_state=42, class_weight="balanced")
    forest.fit(X_train_vec, y_train)
    print("Random Forest")
    print(classification_report(y_test, forest.predict(X_test_vec)))

    joblib.dump(vectorizer, MODEL_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(logistic, MODEL_DIR / "spam_classifier.joblib")
    joblib.dump(forest, MODEL_DIR / "random_forest_classifier.joblib")
    print("Models saved in models/")


if __name__ == "__main__":
    main()
