"""
Chunker — Recursive text chunking with metadata preservation.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Split page-level documents into smaller chunks, preserving metadata.

    Args:
        pages: List of page dicts from pdf_parser.extract_text_from_pdf().
              Each dict has 'text' and 'metadata' keys.

    Returns:
        List of chunk dicts, each containing:
            - text: Chunk text content.
            - metadata: Dict with source_filename, page_number, chunk_id.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[dict] = []
    chunk_counter = 0

    for page in pages:
        page_chunks = splitter.split_text(page["text"])

        for chunk_text in page_chunks:
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    **page["metadata"],
                    "chunk_id": f"chunk_{chunk_counter}",
                },
            })
            chunk_counter += 1

    return chunks
