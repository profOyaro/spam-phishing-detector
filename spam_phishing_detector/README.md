# 🛡️ AI-Powered Spam & Phishing Email Detection System

An academic capstone project that classifies emails as **legitimate (ham)**, **spam**, or **phishing** using classical machine learning (TF-IDF + Logistic Regression / Random Forest), NLP preprocessing, and a Streamlit cybersecurity-themed dashboard.

## ✨ Features

- 📥 Paste email text **or** upload a `.txt` / `.eml` file
- 🤖 Two ML models trained & compared (Logistic Regression, Random Forest)
- 🔤 NLP preprocessing: lowercase, punctuation removal, tokenization, stopwords
- 🔗 Suspicious-URL heuristic (cheap TLDs, brand look-alikes, IP URLs)
- 📊 Dashboard with accuracy, precision, recall, F1, confusion matrices
- 📝 Local prediction logging (`logs/predictions.log`)
- 🛡️ Input validation & safe file handling

## 📂 Project Structure

```
spam_phishing_detector/
├── data/                  # Datasets (CSV: text,label)
│   └── sample_emails.csv  # Bundled demo dataset (ham / spam / phishing)
├── models/                # Trained .joblib models + metrics.json
├── notebooks/             # Jupyter EDA notebook
├── app/
│   ├── data_loader.py     # Module 1: dataset loading + validation
│   └── preprocessing.py   # Module 2 & 3: text cleaning + URL features
├── logs/                  # Prediction logs (JSONL)
├── tests/
│   └── test_pipeline.py   # Unit tests
├── train_model.py         # Module 4: trains & saves models
├── predict.py             # Module 5: CLI/library prediction engine
├── app.py                 # Module 6: Streamlit dashboard
├── requirements.txt
└── README.md
```

## 🚀 Installation

```bash
# 1. Clone / unzip the project
cd spam_phishing_detector

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

The first run will auto-download NLTK `stopwords` + `punkt` (a few MB).

## 🏋️ Training

Train both models on the bundled sample dataset:

```bash
python train_model.py --data data/sample_emails.csv
```

This writes:
- `models/logistic_regression.joblib`
- `models/random_forest.joblib`
- `models/best_model.joblib`  ← used by the dashboard
- `models/metrics.json`       ← accuracy / precision / recall / F1 / confusion matrix

### Using your own dataset

Supply any CSV with `text` and `label` columns (labels: `ham`, `spam`, or `phishing`). Common alternatives like `message`/`category` are auto-mapped.

Recommended public datasets:
- [Kaggle — Spam Email Dataset](https://www.kaggle.com/datasets/venky73/spam-mails-dataset)
- [UCI — SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)
- [Kaggle — Phishing Email Dataset](https://www.kaggle.com/datasets/subhajournal/phishingemails)

## 🔮 Prediction (CLI)

```bash
python predict.py --text "URGENT: verify your PayPal at http://paypa1-verify.tk"
python predict.py --file my_email.eml
```

Outputs JSON with `label`, `confidence`, `risk_level`, `probabilities`, `urls_found`.

## 🖥️ Dashboard

```bash
streamlit run app.py
```

Then open <http://localhost:8501>. Tabs:
1. **🔍 Analyze** — paste/upload an email, get prediction + risk + URL list
2. **📊 Dashboard** — model comparison, confusion matrices, classification reports
3. **📜 Logs** — recent predictions, downloadable

## 🧪 Tests

```bash
python tests/test_pipeline.py
```

## 🏗️ Architecture

```
        ┌─────────────┐    ┌────────────────┐    ┌──────────────┐
Email → │ Preprocess  │ →  │  TF-IDF (1-2g) │ →  │ Classifier   │ → label + confidence
        │ (NLTK)      │    │                │    │ (LR / RF)    │
        └─────────────┘    └────────────────┘    └──────────────┘
                                                        │
                                                        ▼
                                          ┌──────────────────────┐
URL heuristics ─────────────────────────► │ Risk-level reasoner  │ → HIGH / MED / LOW
                                          └──────────────────────┘
                                                        │
                                                        ▼
                                              logs/predictions.log
```

## 🔒 Security Features

- Input length cap (50k chars) to prevent pathological inputs
- File uploads decoded with `errors="ignore"` (no crash on malformed bytes)
- Logging never raises — wraps OSError silently
- No `eval` / `pickle.loads` of user data — only trusted `joblib` model files
- Heuristic flags brand look-alike domains and free-TLD phishing infrastructure

## 📈 Evaluation Metrics

Stored in `models/metrics.json` and shown in the dashboard:
- Accuracy, weighted Precision / Recall / F1
- Per-class classification report
- Confusion matrix per model

## 🌐 Future Scalability

The modular layout supports adding:
- ☁️ **Cloud deployment** — containerize with Docker, deploy to AWS ECS / Azure App Service
- 🧠 **Deep learning** — swap `models/best_model.joblib` for a BERT fine-tune (same interface)
- 📨 **Email API integration** — call `EmailClassifier().predict()` from a Gmail/Outlook webhook
- 🚨 **SIEM** — forward `logs/predictions.log` (JSONL) to Splunk / ELK / Sentinel
- 🛰️ **Threat-intel** — enrich `extract_urls()` with VirusTotal / PhishTank lookups
- ⏱️ **Real-time monitoring** — wrap the predictor in a FastAPI service behind a queue

## 📚 Coding Standards

- Modular: each `Module N` lives in its own file
- OOP where appropriate (`EmailClassifier` class)
- Exception handling on I/O, file reads, NLTK downloads
- Type hints throughout
- Inline docstrings on every public function

## 📄 License

MIT — academic / educational use.
