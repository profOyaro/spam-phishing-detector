"""
Module 2: Data Preprocessing
Cleans and prepares raw email text for ML feature extraction.
"""
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure NLTK resources are available (download on first run)
for _pkg in ("stopwords", "punkt", "punkt_tab"):
    try:
        nltk.data.find(f"corpora/{_pkg}" if _pkg == "stopwords" else f"tokenizers/{_pkg}")
    except LookupError:
        try:
            nltk.download(_pkg, quiet=True)
        except Exception:
            pass

try:
    STOPWORDS = set(stopwords.words("english"))
except Exception:
    # Minimal fallback if NLTK download fails
    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
        "to", "of", "in", "on", "at", "for", "with", "by", "from", "as",
        "this", "that", "it", "be", "have", "has", "had", "i", "you", "we",
        "they", "he", "she", "my", "your", "our", "their",
    }

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+")
NUMBER_PATTERN = re.compile(r"\b\d+\b")


def extract_urls(text: str) -> list[str]:
    """Return all URLs found in the text (used for phishing URL inspection)."""
    if not isinstance(text, str):
        return []
    return URL_PATTERN.findall(text)


def clean_text(text: str) -> str:
    """
    Full preprocessing pipeline:
      1. Lowercase
      2. Replace URLs/emails with tokens (preserve signal)
      3. Strip punctuation
      4. Tokenize
      5. Remove stopwords and short tokens
    """
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = URL_PATTERN.sub(" urltoken ", text)
    text = EMAIL_PATTERN.sub(" emailtoken ", text)
    text = NUMBER_PATTERN.sub(" numtoken ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))

    try:
        tokens = word_tokenize(text)
    except Exception:
        tokens = text.split()

    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    return " ".join(tokens)


def suspicious_url_score(text: str) -> float:
    """Heuristic 0..1 score for phishing-style URLs (cheap TLDs, IPs, look-alikes)."""
    urls = extract_urls(text)
    if not urls:
        return 0.0
    bad_tlds = (".tk", ".ml", ".gq", ".xyz", ".ru", ".cf", ".top", ".co")
    brands = ("paypal", "apple", "amazon", "microsoft", "google", "bank",
              "netflix", "chase", "wellsfargo", "office365", "dropbox", "icloud")
    score = 0
    for u in urls:
        low = u.lower()
        if any(low.endswith(t) or t + "/" in low for t in bad_tlds):
            score += 2
        if re.search(r"https?://\d+\.\d+\.\d+\.\d+", low):
            score += 2
        if any(b in low for b in brands) and not any(
            f"{b}.com" in low for b in brands
        ):
            score += 1
    return min(score / (2 * len(urls)), 1.0)
