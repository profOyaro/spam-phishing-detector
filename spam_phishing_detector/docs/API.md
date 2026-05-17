# Python API

## `EmailClassifier`

```python
from predict import EmailClassifier

clf = EmailClassifier()                     # loads models/best_model.joblib
result = clf.predict("Your account is suspended, click http://paypa1.tk")
```

### Returns
```json
{
  "label": "phishing",
  "confidence": 0.94,
  "risk_level": "HIGH",
  "probabilities": {"ham": 0.01, "phishing": 0.94, "spam": 0.05},
  "urls_found": ["http://paypa1.tk"],
  "url_risk_score": 1.0,
  "timestamp": "2025-05-17T12:34:56Z"
}
```

### Errors
- `TypeError` — non-string input
- `ValueError` — empty input
- `FileNotFoundError` — model file missing (run training first)

## Preprocessing helpers
```python
from app.preprocessing import clean_text, extract_urls, suspicious_url_score
```
