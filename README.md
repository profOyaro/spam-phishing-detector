# AI Spam, Phishing & Quishing Detection (v4)

Enterprise-grade Streamlit + FastAPI platform for detecting spam, phishing,
quishing (QR code phishing), malicious URLs, and suspicious attachments.

## Features
- Verified user accounts (email + phone OTP, dev-mode OTP shown on screen)
- Single Administrator console (admin@system.local / Admin@123)
- Explainable AI (keyword highlighting + weighted reasons)
- URL / Email-header / QR / Attachment analyzers
- Threat intelligence stubs (VirusTotal, Google Safe Browsing, PhishTank)
- Per-user Cybersecurity Score
- Incident PDF reports
- Phishing simulation tracking
- SQLite persistence (data/app.db)
- FastAPI backend (REST: /predict, /analyze, /scan-url)
- Dockerfile + docker-compose

## Quick start
    pip install -r requirements.txt
    python train.py            # train classical ML
    streamlit run app.py       # frontend
    uvicorn backend.main:app --port 8000   # backend (optional)

Admin login: admin@system.local / Admin@123
