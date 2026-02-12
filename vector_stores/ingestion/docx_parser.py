import docx

def parse_docx(filepath: str):
    """Extracts text + URLs from DOCX."""
    doc = docx.Document(filepath)
    items = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # naive split: Title - URL - Description
        parts = text.split(" - ")

        entry = {
            "title": parts[0],
            "url": parts[1] if len(parts) > 1 else "",
            "description": parts[2] if len(parts) > 2 else ""
        }

        items.append(entry)

    return items
