# API documentation

Start the API:

```bash
uvicorn backend.main:app --reload --port 8000
```

## GET /health

Returns service status.

## POST /predict

```json
{
  "text": "email body",
  "sender": "sender@example.com",
  "subject": "subject"
}
```

## POST /analyze

Runs the full detection pipeline and logs the result.

## POST /scan-url

```json
{
  "url": "http://paypal-security-login.tk"
}
```
