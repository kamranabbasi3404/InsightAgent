"""
Documents router — lists and manages indexed documents.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.vectorstore.chroma_client import list_indexed_documents, delete_document

router = APIRouter()


class DocumentInfo(BaseModel):
    """Model for a single indexed document."""
    filename: str
    chunk_count: int


class DocumentsResponse(BaseModel):
    """Response model for listing documents."""
    documents: list[DocumentInfo]
    total: int


class DeleteResponse(BaseModel):
    """Response model for deleting a document."""
    filename: str
    chunks_deleted: int
    message: str


@router.get("/documents", response_model=DocumentsResponse)
async def get_documents() -> DocumentsResponse:
    """List all indexed documents with their chunk counts."""
    docs = list_indexed_documents()
    return DocumentsResponse(
        documents=[DocumentInfo(**doc) for doc in docs],
        total=len(docs),
    )


@router.delete("/documents/{filename}", response_model=DeleteResponse)
async def remove_document(filename: str) -> DeleteResponse:
    """Delete all chunks belonging to a specific document."""
    chunks_deleted = delete_document(filename)
    if chunks_deleted == 0:
        raise HTTPException(status_code=404, detail=f"Document '{filename}' not found.")

    return DeleteResponse(
        filename=filename,
        chunks_deleted=chunks_deleted,
        message=f"Deleted {chunks_deleted} chunks from '{filename}'.",
    )
