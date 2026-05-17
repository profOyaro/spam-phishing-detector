"""
Module 6: Streamlit Dashboard
Cybersecurity-themed UI for the Spam & Phishing Email Detection System.

Run:
    streamlit run app.py
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from predict import EmailClassifier, LOG_FILE

ROOT = Path(__file__).parent
METRICS_PATH = ROOT / "models" / "metrics.json"

st.set_page_config(
    page_title="Spam & Phishing Detector",
    page_icon="🛡️",
    layout="wide",
)

# Cybersecurity theme
st.markdown("""
<style>
    .stApp { background-color: #0b1220; color: #e6edf3; }
    h1, h2, h3 { color: #58a6ff; }
    .stButton>button {
        background-color: #238636; color: white; border: none;
        font-weight: 600; padding: 0.5rem 1.5rem;
    }
    .stButton>button:hover { background-color: #2ea043; }
    .risk-high { color: #f85149; font-weight: 700; }
    .risk-medium { color: #d29922; font-weight: 700; }
    .risk-low { color: #3fb950; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ AI Spam & Phishing Email Detector")
st.caption("Cybersecurity capstone · TF-IDF + Logistic Regression / Random Forest")


@st.cache_resource
def get_classifier() -> EmailClassifier:
    return EmailClassifier()


try:
    clf = get_classifier()
    model_ready = True
except FileNotFoundError as e:
    st.error(f"⚠️ {e}")
    st.code("python train_model.py --data data/sample_emails.csv", language="bash")
    model_ready = False

tab_predict, tab_dashboard, tab_logs = st.tabs(["🔍 Analyze", "📊 Dashboard", "📜 Logs"])

# ───────────────────────── ANALYZE ─────────────────────────
with tab_predict:
    col1, col2 = st.columns([2, 1])
    with col1:
        text_input = st.text_area(
            "Paste email content",
            height=240,
            placeholder="Subject: Your account has been suspended...\n\nDear customer, click here to verify...",
        )
        uploaded = st.file_uploader("…or upload an email file", type=["txt", "eml", "csv"])
        analyze = st.button("🔍 Analyze Email", disabled=not model_ready)

    email_text = text_input
    if uploaded is not None:
        try:
            email_text = uploaded.read().decode("utf-8", errors="ignore")
            st.success(f"Loaded {uploaded.name} ({len(email_text)} chars)")
        except Exception as e:
            st.error(f"Could not read file: {e}")

    with col2:
        st.info(
            "**How it works**\n\n"
            "1. Text is cleaned (lowercase, stopwords, punctuation)\n"
            "2. TF-IDF features extracted\n"
            "3. Trained classifier predicts label + confidence\n"
            "4. URL heuristics raise risk for phishing patterns"
        )

    if analyze and model_ready:
        if not email_text.strip():
            st.warning("Please paste or upload some email content first.")
        else:
            try:
                result = clf.predict(email_text)
            except Exception as e:
                st.error(f"Prediction failed: {e}")
            else:
                label = result["label"]
                conf = result["confidence"] * 100
                risk = result["risk_level"]

                badges = {"ham": ("✅ LEGITIMATE", "risk-low"),
                          "spam": ("⚠️ SPAM", "risk-medium"),
                          "phishing": ("🚨 PHISHING", "risk-high")}
                txt, css = badges.get(label, (label.upper(), ""))

                st.markdown(f"## Result: <span class='{css}'>{txt}</span>",
                            unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                m1.metric("Confidence", f"{conf:.1f}%")
                m2.metric("Risk level", risk)
                m3.metric("URLs detected", len(result["urls_found"]))

                st.subheader("Class probabilities")
                st.bar_chart(pd.Series(result["probabilities"]))

                if result["urls_found"]:
                    st.subheader("URLs in email")
                    for u in result["urls_found"]:
                        st.code(u)
                    st.caption(f"Suspicious-URL heuristic score: {result['url_risk_score']:.2f}")

                with st.expander("Raw JSON result"):
                    st.json(result)

# ───────────────────────── DASHBOARD ─────────────────────────
with tab_dashboard:
    st.subheader("Model performance")
    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text())
        st.success(f"Best model: **{metrics['best_model']}**")
        rows = []
        for name, m in metrics["results"].items():
            rows.append({
                "Model": name,
                "Accuracy": f"{m['accuracy']:.3f}",
                "Precision": f"{m['precision_weighted']:.3f}",
                "Recall": f"{m['recall_weighted']:.3f}",
                "F1": f"{m['f1_weighted']:.3f}",
            })
        st.table(pd.DataFrame(rows))

        st.subheader("Confusion matrices")
        cols = st.columns(len(metrics["results"]))
        for col, (name, m) in zip(cols, metrics["results"].items()):
            with col:
                st.caption(name)
                cm = pd.DataFrame(m["confusion_matrix"],
                                  index=m["labels"], columns=m["labels"])
                st.dataframe(cm)

        st.subheader("Classification reports")
        for name, report in metrics["reports"].items():
            with st.expander(name):
                st.code(report)
    else:
        st.warning("No metrics found. Train the model first.")

# ───────────────────────── LOGS ─────────────────────────
with tab_logs:
    st.subheader("Recent predictions")
    if LOG_FILE.exists():
        lines = LOG_FILE.read_text(encoding="utf-8").strip().splitlines()[-100:]
        if lines:
            df = pd.DataFrame([json.loads(l) for l in lines])
            st.dataframe(df[::-1], width="stretch")
            st.download_button(
                "Download logs",
                LOG_FILE.read_bytes(),
                file_name="predictions.log",
                mime="application/json",
            )
        else:
            st.info("No predictions logged yet.")
    else:
        st.info("Log file will be created after the first prediction.")
