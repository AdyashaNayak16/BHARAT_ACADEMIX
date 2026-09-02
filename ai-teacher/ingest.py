import os
from pypdf import PdfReader
def load_pdf_text(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF not found at: {path}")
    reader = PdfReader(path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()
    if not full_text.strip():
        raise ValueError("No readable text found in PDF. It may be a scanned/image-based PDF.")
    return full_text