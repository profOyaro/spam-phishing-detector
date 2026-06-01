"""Train TF-IDF + LogisticRegression / RandomForest classical model."""
import os, joblib, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

DATA = [
    ("Win a FREE iPhone now!!! Click http://bit.ly/x", 1),
    ("Urgent: verify your bank account http://192.168.0.1/login", 1),
    ("Your package is delayed, confirm at http://paypa1.com", 1),
    ("Meeting moved to 3pm tomorrow", 0),
    ("Lunch next week?", 0),
    ("Quarterly report attached", 0),
    ("Your invoice from Acme Corp", 0),
    ("Reset your password at http://secure-paypal.support", 1),
    ("Project status update for sprint 7", 0),
    ("CONGRATULATIONS you won a lottery 1,000,000 USD", 1),
] * 40

def main():
    df = pd.DataFrame(DATA, columns=["text", "label"])
    Xtr, Xte, ytr, yte = train_test_split(df.text, df.label, test_size=0.2, random_state=42)
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,2), min_df=1)),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    pipe.fit(Xtr, ytr)
    print(classification_report(yte, pipe.predict(Xte)))
    os.makedirs("data", exist_ok=True)
    joblib.dump(pipe, "data/model.joblib")
    print("Saved data/model.joblib")

if __name__ == "__main__":
    main()
