import fitz

def get_pdf_info(path: str):
    doc = fitz.open(path)
    try:
        return {
            "total_pages": len(doc),
            "is_scanned": is_scanned_pdf(doc)
        }
    finally:
        doc.close()

def is_scanned_pdf(doc):
    for page in doc:
        if page.get_text("text").strip():
            return False
    return True
