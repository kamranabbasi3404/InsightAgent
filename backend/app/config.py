"""
InsightAgent Configuration
Centralized configuration loading from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


# --- API Keys ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

# --- LLM Models ---
PRIMARY_MODEL: str = "llama-3.1-8b-instant"
FALLBACK_MODEL: str = "llama-3.1-8b-instant"

# --- Chunking ---
CHUNK_SIZE: int = 600  # tokens
CHUNK_OVERLAP: int = 100

# --- Retrieval ---
TOP_K: int = 5  # number of chunks to retrieve
MAX_RETRIES: int = 2  # max query rewrite retries

# --- ChromaDB ---
CHROMA_PERSIST_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
CHROMA_COLLECTION_NAME: str = "insightagent_docs"

# --- Embedding Model ---
EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

# --- Upload ---
UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

# --- Server ---
BACKEND_HOST: str = "0.0.0.0"
BACKEND_PORT: int = 8000
CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
