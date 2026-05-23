"""FastAPI backend for programmatic phishing analysis."""
from fastapi import FastAPI, HTTPException
from app.attachment_scanner import scan_attachments
from app.explainability import feature_importance_summary
from app.header_analyzer import analyze_headers
from app.logging_db import log_detection
from app.risk_engine import calculate_risk
from app.sender_checker import check_sender
from app.url_analyzer import analyze_url, analyze_urls
from backend.schemas import AnalyzeRequest, UrlRequest
from predict import predict_email

api = FastAPI(title="Spam & Phishing Detection API", version="3.0.0")
app = api

@api.get("/health")
def health():
    return {"status": "ok"}

@api.post("/predict")
def predict(payload: AnalyzeRequest):
    try:
        return predict_email(payload.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@api.post("/scan-url")
def scan_url(payload: UrlRequest):
    return analyze_url(payload.url).__dict__

@api.post("/analyze")
def analyze(payload: AnalyzeRequest):
    try:
        ml = predict_email(payload.text)
        urls = analyze_urls(payload.text)
        sender = check_sender(payload.sender, payload.text)
        attachments = scan_attachments([])
        headers = analyze_headers(payload.text)
        risk = calculate_risk(ml, urls, sender, attachments, headers)
        xai = feature_importance_summary(payload.text, ml)
        result = {
            "subject": payload.subject,
            "sender": payload.sender,
            "ml": ml,
            "urls": urls,
            "sender_check": sender,
            "attachments": attachments,
            "headers": headers,
            "risk": risk,
            "explainability": xai,
        }
        log_detection(payload.subject, payload.sender, ml["label"], risk, result)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
