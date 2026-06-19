"""
utils/doc_parser.py

Parses uploaded PDF and DOCX files into plain text for the agent pipeline.
"""

import io
from pathlib import Path


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages).strip()
    except Exception as e:
        return f"[PDF parsing error: {e}]"


def parse_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs).strip()
    except Exception as e:
        return f"[DOCX parsing error: {e}]"


def parse_uploaded_file(file_name: str, file_bytes: bytes) -> str:
    """Route file to correct parser based on extension."""
    ext = Path(file_name).suffix.lower()
    if ext == ".pdf":
        return parse_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return parse_docx(file_bytes)
    elif ext in (".txt", ".md"):
        return file_bytes.decode("utf-8", errors="replace")
    else:
        return file_bytes.decode("utf-8", errors="replace")
