import fitz

def extract_pages(path):
    doc=fitz.open(path)
    pages=[(i+1, page.get_text('text')) for i,page in enumerate(doc)]
    count=len(doc); doc.close()
    if not any(t.strip() for _,t in pages):
        raise ValueError('No extractable text was found. This may be a scanned PDF; OCR is not included yet.')
    return pages, count
