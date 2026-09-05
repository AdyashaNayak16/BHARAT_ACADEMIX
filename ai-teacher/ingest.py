import os
from pypdf import PdfReader

def load_pdf_text(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF not found at: {path}")
    reader = PdfReader(path)
    full_text = ""
    for page in reader.pages:
        txt = page.extract_text()
        if txt:
            full_text += txt + "\n"
    if not full_text.strip():
        raise ValueError("No readable text found in PDF. It may be a scanned/image-based PDF.")
    return full_text

def load_docx_text(path):
    import docx
    doc = docx.Document(path)
    full_text = []
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text)
    return "\n".join(full_text)

def load_document_text(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found at: {path}")
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return load_pdf_text(path)
    elif ext in [".docx", ".doc"]:
        return load_docx_text(path)
    elif ext in [".txt", ".md", ".json", ".csv", ".py", ".html"]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        # Try reading as text
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()