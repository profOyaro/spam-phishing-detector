"""FastAPI backend exposing analyzer endpoints."""
from fastapi import FastAPI
from pydantic import BaseModel
from app import email_analyzer, url_analyzer, risk_engine, xai

app = FastAPI(title="Spam/Phishing/Quishing API", version="4.0")

class EmailIn(BaseModel):
    text: str

class URLIn(BaseModel):
    url: str

@app.get("/health")
def health(): return {"ok": True}

@app.post("/analyze")
def analyze(p: EmailIn):
    r = email_analyzer.analyze(p.text)
    return {**r, "level": risk_engine.level(r["score"]),
            "classification": risk_engine.classify(r["score"]),
            "explanation": xai.explain(r)}

@app.post("/scan-url")
def scan_url(p: URLIn):
    r = url_analyzer.analyze(p.url)
    return {**r, "level": risk_engine.level(r["score"])}
