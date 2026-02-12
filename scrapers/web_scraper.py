import requests
from bs4 import BeautifulSoup
from utils.text_cleaner import clean_html, truncate

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_url(url: str):
    try:
        html = requests.get(url, headers=HEADERS, timeout=10).text
    except:
        return None

    soup = BeautifulSoup(html, "html.parser")

    paragraphs = [p.get_text().strip() for p in soup.find_all("p")]
    code_blocks = [c.get_text() for c in soup.find_all("code")]
    lists = []

    for ul in soup.find_all("ul"):
        items = [li.get_text().strip() for li in ul.find_all("li")]
        lists.append(items)

    return {
        "url": url,
        "text": truncate(" ".join(paragraphs), 800),
        "code": code_blocks[:3],
        "lists": lists[:3]
    }


def scrape_urls(urls: list):
    output = []
    for u in urls:
        data = scrape_url(u)
        if data:
            output.append(data)
    return output
