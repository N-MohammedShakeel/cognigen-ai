import re
from bs4 import BeautifulSoup

def clean_html(raw_html: str) -> str:
    """Remove HTML tags and keep clean text."""
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", text).strip()


def clean_whitespace(text: str) -> str:
    """Normalize whitespace, remove excessive newlines."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, max_chars: int = 500) -> str:
    """Limit text length."""
    if not text:
        return ""
    return text[:max_chars] + ("..." if len(text) > max_chars else "")


def normalize(text: str) -> str:
    """Full cleaning pipeline."""
    return clean_whitespace(clean_html(text))
