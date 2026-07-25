"""
Text extraction utilities for the Knowledge Base upload pipeline.
Supports PDF, DOCX and TXT files.
"""
import logging
import os

from pypdf import PdfReader
from docx import Document

logger = logging.getLogger("brightside")


class UnsupportedFileTypeError(Exception):
    pass


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_pdf(file_path)
    if ext == ".docx":
        return _extract_docx(file_path)
    if ext == ".txt":
        return _extract_txt(file_path)

    raise UnsupportedFileTypeError(f"Unsupported file type: {ext}")


def _extract_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx(file_path: str) -> str:
    document = Document(file_path)
    return "\n".join(p.text for p in document.paragraphs)


def _extract_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
