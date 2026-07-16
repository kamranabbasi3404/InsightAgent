"""
ChromaDB Client — Persistent vector store for document chunks.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME
from app.ingestion.embedder import embed_texts, embed_query

# Module-level singleton
_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None


def _get_client() -> chromadb.ClientAPI:
    """Get or create the persistent ChromaDB client."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def _get_collection() -> chromadb.Collection:
    """Get or create the document collection."""
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(chunks: list[dict]) -> int:
    """
    Upsert document chunks into the ChromaDB collection.

    Args:
        chunks: List of chunk dicts from chunker, each with 'text' and 'metadata'.

    Returns:
        Number of chunks added.
    """
    collection = _get_collection()

    texts = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]

    # Generate embeddings
    embeddings = embed_texts(texts)

    # Upsert into ChromaDB
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    return len(chunks)


def query_chunks(query: str, top_k: int = 5) -> list[dict]:
    """
    Query the vector store for the most relevant chunks.

    Args:
        query: Search query text.
        top_k: Number of results to return.

    Returns:
        List of result dicts, each containing:
            - text: Chunk text.
            - metadata: Source filename, page number, chunk_id.
            - score: Similarity score (lower = more similar for cosine distance).
    """
    collection = _get_collection()

    # Check if collection is empty
    if collection.count() == 0:
        return []

    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    formatted_results: list[dict] = []
    if results["documents"] and results["documents"][0]:
        for i in range(len(results["documents"][0])):
            formatted_results.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "score": results["distances"][0][i] if results["distances"] else 0.0,
            })

    return formatted_results


def list_indexed_documents() -> list[dict]:
    """
    List all unique documents indexed in the collection with chunk counts.

    Returns:
        List of dicts with 'filename' and 'chunk_count'.
    """
    collection = _get_collection()

    if collection.count() == 0:
        return []

    # Get all metadata to count chunks per document
    all_data = collection.get(include=["metadatas"])
    doc_counts: dict[str, int] = {}

    if all_data["metadatas"]:
        for metadata in all_data["metadatas"]:
            filename = metadata.get("source_filename", "unknown")
            doc_counts[filename] = doc_counts.get(filename, 0) + 1

    return [
        {"filename": filename, "chunk_count": count}
        for filename, count in sorted(doc_counts.items())
    ]


def delete_document(filename: str) -> int:
    """
    Delete all chunks belonging to a specific document.

    Args:
        filename: The source_filename to delete.

    Returns:
        Number of chunks deleted.
    """
    collection = _get_collection()

    # Get IDs of chunks belonging to this document
    all_data = collection.get(
        where={"source_filename": filename},
        include=["metadatas"],
    )

    if not all_data["ids"]:
        return 0

    chunk_count = len(all_data["ids"])
    collection.delete(ids=all_data["ids"])
    return chunk_count
