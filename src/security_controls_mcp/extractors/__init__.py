"""Extractors for importing security standards from PDF files."""

try:
    from .pdf_extractor import extract_standard

    __all__ = ["extract_standard"]
except ImportError:
    # pdfplumber not installed - extractors module available but pdf extraction disabled
    __all__ = []
