"""
Embedder — Generates embeddings using sentence-transformers (local, no API cost).
"""

from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL

# Module-level singleton to avoid reloading the model on every call
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Lazy-load the embedding model (singleton)."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of text strings.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors (each a list of floats).
    """
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """
    Generate an embedding for a single query string.

    Args:
        query: Query text to embed.

    Returns:
        Embedding vector as a list of floats.
    """
    model = _get_model()
    embedding = model.encode(query, normalize_embeddings=True)
    return embedding.tolist()
