# User Manual

## 1. Launching the App
```bash
streamlit run app.py
```
The dashboard opens at http://localhost:8501.

## 2. Analyzing an Email
1. Open the **🔍 Analyze** tab.
2. Paste the email body into the text box **or** upload a `.txt` / `.eml` file.
3. Click **Analyze Email**.
4. Read the result:
   - **LEGITIMATE / SPAM / PHISHING** badge
   - Confidence percentage
   - Risk level (LOW / MEDIUM / HIGH)
   - Per-class probability bar chart
   - List of URLs found in the email

## 3. Reviewing Model Performance
Open the **📊 Dashboard** tab to see:
- Best model name
- Accuracy / Precision / Recall / F1 per model
- Confusion matrix per model
- Full classification reports

## 4. Inspecting Logs
The **📜 Logs** tab lists the last 100 predictions. Use **Download logs** to export the full JSONL file (`logs/predictions.log`).

## 5. Retraining
After replacing or extending `data/sample_emails.csv`:
```bash
python train_model.py --data data/sample_emails.csv
```
Restart Streamlit to load the new model.
