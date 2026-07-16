"""
Upload router — handles PDF file uploads and ingestion pipeline.
"""

import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.config import UPLOAD_DIR
from app.ingestion.pdf_parser import extract_text_from_pdf
from app.ingestion.chunker import chunk_pages
from app.vectorstore.chroma_client import add_chunks

router = APIRouter()


class UploadResponse(BaseModel):
    """Response model for PDF upload."""
    filename: str
    pages_extracted: int
    chunks_created: int
    message: str


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload a PDF file, parse it, chunk it, embed it, and store in ChromaDB.

    Args:
        file: The uploaded PDF file.

    Returns:
        Upload result with filename, page count, and chunk count.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Save the uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Run the ingestion pipeline
    try:
        # 1. Extract text per page
        pages = extract_text_from_pdf(file_path)
        if not pages:
            raise HTTPException(status_code=400, detail="No text content found in the PDF.")

        # 2. Chunk the pages
        chunks = chunk_pages(pages)

        # 3. Embed and store in ChromaDB
        # Prefix chunk IDs with filename to avoid collisions across documents
        for chunk in chunks:
            chunk["metadata"]["chunk_id"] = f"{file.filename}_{chunk['metadata']['chunk_id']}"

        chunk_count = add_chunks(chunks)

        return UploadResponse(
            filename=file.filename,
            pages_extracted=len(pages),
            chunks_created=chunk_count,
            message=f"Successfully indexed {file.filename}: {len(pages)} pages, {chunk_count} chunks.",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
