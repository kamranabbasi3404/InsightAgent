"""
PDF Parser — Extracts text per page from PDF files using PyMuPDF.
"""

import fitz  # PyMuPDF
from pathlib import Path


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Extract text from a PDF file, returning a list of page-level documents.

    Args:
        file_path: Path to the PDF file.

    Returns:
        List of dicts, each containing:
            - text: Extracted text content of the page.
            - metadata: Dict with source_filename, page_number.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    doc = fitz.open(str(file_path))
    pages: list[dict] = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()

        if text:  # Skip empty pages
            pages.append({
                "text": text,
                "metadata": {
                    "source_filename": file_path.name,
                    "page_number": page_num + 1,  # 1-indexed for human readability
                },
            })

    doc.close()
    return pages
