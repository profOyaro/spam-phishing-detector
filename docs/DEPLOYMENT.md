# Deployment recommendations

## Local demo

Use Streamlit for academic defense and portfolio demonstrations.

```bash
streamlit run app.py
```

## API service

Run FastAPI behind a reverse proxy with HTTPS:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker compose up --build
```

## Production hardening

- Use HTTPS only.
- Store secrets in environment variables.
- Add rate limiting at the reverse proxy or API gateway.
- Restrict upload types and sizes.
- Add antivirus sandboxing before processing real attachments.
- Monitor detection logs and rotate API keys.
- Use a managed database for multi-user deployments.
