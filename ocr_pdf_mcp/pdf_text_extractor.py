import fitz

def extract_text_from_pdf(path: str):
    doc = fitz.open(path)
    text_pages = []
    for i, page in enumerate(doc, start=1):
        text_pages.append({
            "page": i,
            "type": "digital",
            "text": page.get_text("text")
        })
    return text_pages
