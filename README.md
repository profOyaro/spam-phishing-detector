# AI Spam & Phishing Email Detection Platform v3

A lightweight enterprise-grade cybersecurity and machine-learning platform for detecting spam, phishing, malicious URLs, suspicious senders, dangerous attachments, and OCR-based screenshot phishing.

## Features

- Streamlit analyst dashboard with login
- FastAPI backend service with REST endpoints
- Classical ML using TF-IDF + Logistic Regression / Random Forest
- Optional DistilBERT deep-learning scoring wrapper
- URL analysis: shorteners, IP URLs, suspicious TLDs, punycode, brand impersonation
- Sender and header checks: SPF, DKIM, DMARC markers, Reply-To mismatch, free-mail abuse
- Attachment scanner: dangerous extensions, macro documents, double extensions, oversize files
- Risk engine: weighted 0-100 threat score with Low/Medium/High/Critical levels
- Explainable AI: keyword highlights and model feature contribution summaries
- OCR screenshot phishing checks with optional Tesseract/OpenCV
- SQLite logging and CSV export
- PDF incident reporting
- Docker and deployment notes

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python train.py
streamlit run app.py
```

Default login:

- Username: `admin`
- Password: `admin123`

## Optional API server

```bash
uvicorn backend.main:app --reload --port 8000
```

Open API docs at: `http://localhost:8000/docs`

## Environment variables

Copy `.env.example` to `.env` and fill optional keys:

```bash
cp .env.example .env
```

Threat-intelligence integrations are optional. If keys are missing, the app falls back to local heuristic checks.

## Project structure

```text
spam_phishing_detector/
├── app.py
├── train.py
├── predict.py
├── config.py
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── backend/
│   ├── main.py
│   └── schemas.py
├── app/
│   ├── attachment_scanner.py
│   ├── deep_model.py
│   ├── email_parser.py
│   ├── explainability.py
│   ├── header_analyzer.py
│   ├── logging_db.py
│   ├── ocr_phishing.py
│   ├── pdf_report.py
│   ├── risk_engine.py
│   ├── sender_checker.py
│   ├── url_analyzer.py
│   └── url_reputation.py
├── data/
│   ├── sample_emails.csv
│   └── schema.sql
├── examples/
│   ├── phishing_invoice.eml
│   ├── safe_newsletter.eml
│   └── phishing_test_cases.md
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
└── tests/
    └── test_advanced.py
```

## Security notes

- Do not upload untrusted files to production without antivirus sandboxing.
- Limit attachment size and allowed MIME types.
- Keep API keys in environment variables only.
- Put FastAPI behind HTTPS and rate limiting.
- Treat all results as analyst decision support, not a sole enforcement authority.
