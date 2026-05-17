"""Basic sanity tests for the detection pipeline."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.preprocessing import clean_text, extract_urls, suspicious_url_score
from app.data_loader import load_dataset


def test_clean_text_lowercases_and_strips():
    out = clean_text("HELLO!!! Visit http://evil.tk NOW.")
    assert "hello" in out
    assert "urltoken" in out
    assert "!" not in out


def test_extract_urls():
    urls = extract_urls("Click http://a.tk and https://b.com please")
    assert len(urls) == 2


def test_suspicious_url_score_flags_bad_tlds():
    assert suspicious_url_score("go to http://paypa1-verify.tk/login now") > 0.3
    assert suspicious_url_score("see https://github.com/repo") == 0.0


def test_load_dataset_sample():
    df = load_dataset(Path(__file__).resolve().parents[1] / "data" / "sample_emails.csv")
    assert {"text", "label"} <= set(df.columns)
    assert set(df["label"].unique()) <= {"ham", "spam", "phishing"}
    assert len(df) > 30


if __name__ == "__main__":
    test_clean_text_lowercases_and_strips()
    test_extract_urls()
    test_suspicious_url_score_flags_bad_tlds()
    test_load_dataset_sample()
    print("✅ All tests passed")
