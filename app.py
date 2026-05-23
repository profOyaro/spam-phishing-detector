"""Streamlit dashboard for the AI spam and phishing detection platform."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from app.attachment_scanner import scan_attachments
from app.email_parser import parse_eml_bytes, parse_raw_text
from app.explainability import feature_importance_summary
from app.header_analyzer import analyze_headers
from app.logging_db import list_detections, log_detection
from app.ocr_phishing import analyze_screenshot
from app.pdf_report import build_pdf_report
from app.risk_engine import calculate_risk
from app.sender_checker import check_sender
from app.url_analyzer import analyze_urls
from config import settings
from predict import predict_email
from PIL import Image

st.set_page_config(page_title="Email Threat Detection Platform", page_icon="🛡️", layout="wide")


def authenticate() -> bool:
    """Small demo login for local showcases."""
    if st.session_state.get("authenticated"):
        return True
    st.title("Email Threat Detection Platform")
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")
    if submitted and username == settings.username and password == settings.password:
        st.session_state["authenticated"] = True
        st.rerun()
    elif submitted:
        st.error("Invalid username or password")
    return False


def run_analysis(subject: str, sender: str, body: str, raw: str, attachments: list[tuple[str, int]]) -> dict:
    """Execute the full analysis pipeline with graceful error handling."""
    ml = predict_email(body)
    urls = analyze_urls(body)
    sender_check = check_sender(sender, raw or body)
    attachment_results = scan_attachments(attachments)
    headers = analyze_headers(raw)
    risk = calculate_risk(ml, urls, sender_check, attachment_results, headers)
    xai = feature_importance_summary(body, ml)
    result = {
        "subject": subject,
        "sender": sender,
        "ml": ml,
        "urls": urls,
        "sender_check": sender_check,
        "attachments": attachment_results,
        "headers": headers,
        "risk": risk,
        "explainability": xai,
    }
    log_detection(subject, sender, ml["label"], risk, result)
    return result


def render_result(result: dict):
    """Render analysis output in SOC-style panels."""
    risk = result["risk"]
    st.metric("Threat score", f"{risk['score']} / 100", risk["level"])
    st.progress(int(risk["score"]))
    c1, c2, c3 = st.columns(3)
    c1.metric("ML label", result["ml"]["label"], f"{result['ml']['confidence']:.0%}")
    c2.metric("URLs found", len(result["urls"]))
    c3.metric("Attachments", len(result["attachments"]))

    tabs = st.tabs(["URL Analysis", "Sender & Headers", "Attachments", "Explainability", "Report"])
    with tabs[0]:
        st.dataframe(pd.DataFrame(result["urls"]), use_container_width=True)
    with tabs[1]:
        st.json({"sender": result["sender_check"], "headers": result["headers"]})
    with tabs[2]:
        st.dataframe(pd.DataFrame(result["attachments"]), use_container_width=True)
    with tabs[3]:
        st.json(result["explainability"])
        st.write("Component scores")
        st.bar_chart(pd.Series(risk["components"]))
    with tabs[4]:
        pdf = build_pdf_report(result)
        st.download_button("Download PDF incident report", data=pdf, file_name="email_threat_report.pdf", mime="application/pdf")


def main():
    if not authenticate():
        return

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose view", ["Analyze Email", "OCR Screenshot", "History"])

    if page == "Analyze Email":
        st.title("Email Threat Analysis")
        mode = st.radio("Input type", ["Paste email text", "Upload .eml file"], horizontal=True)
        subject = ""
        sender = ""
        body = ""
        raw = ""
        attachments: list[tuple[str, int]] = []

        if mode == "Paste email text":
            sender = st.text_input("Sender / From")
            subject = st.text_input("Subject")
            body = st.text_area("Email body or raw headers", height=260)
            raw = body
        else:
            uploaded = st.file_uploader("Upload RFC822 .eml file", type=["eml"], accept_multiple_files=False)
            if uploaded:
                parsed = parse_eml_bytes(uploaded.read())
                sender = parsed["from"]
                subject = parsed["subject"]
                body = parsed["body"]
                raw = parsed["raw"]
                attachments = parsed["attachments"]
                st.info(f"Parsed sender: {sender} | subject: {subject}")
                st.text_area("Extracted body", body, height=200)

        extra_files = st.file_uploader("Optional attachment metadata scan", accept_multiple_files=True)
        if extra_files:
            attachments.extend([(f.name, int(f.size)) for f in extra_files])

        if st.button("Analyze", type="primary"):
            try:
                result = run_analysis(subject, sender, body, raw, attachments)
                render_result(result)
            except FileNotFoundError as exc:
                st.error(str(exc))
                st.info("Run `python train.py` first to create model files.")
            except Exception as exc:
                st.exception(exc)

    elif page == "OCR Screenshot":
        st.title("OCR Screenshot Phishing")
        image_file = st.file_uploader("Upload screenshot", type=["png", "jpg", "jpeg"])
        if image_file:
            image = Image.open(image_file)
            st.image(image, use_column_width=True)
            result = analyze_screenshot(image)
            st.metric("OCR phishing score", result["score"])
            st.write(result["suspicious_keywords"])
            st.text_area("Extracted text", result["text"], height=220)

    else:
        st.title("Detection History")
        rows = list_detections()
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        st.download_button("Export CSV", data=df.to_csv(index=False), file_name="detection_history.csv", mime="text/csv")


if __name__ == "__main__":
    main()
