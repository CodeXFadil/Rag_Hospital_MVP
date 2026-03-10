"""
rag/retriever.py
Semantic similarity retrieval over ChromaDB clinical notes.
"""

import os
import sys

# Streamlit Cloud (Linux) sqlite3 override for ChromaDB
if sys.platform.startswith('linux'):
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
from typing import Optional
from sentence_transformers import SentenceTransformer

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
COLLECTION_NAME = "clinical_notes"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Singleton model to avoid reloading on each call
_model: Optional[SentenceTransformer] = None
_client: Optional[chromadb.PersistentClient] = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_DIR)
        existing = [c.name for c in _client.list_collections()]
        if COLLECTION_NAME not in existing:
            raise RuntimeError(
                "Vector store not initialized. Please run: python rag/vector_store.py"
            )
        _collection = _client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(
    query: str,
    patient_id: Optional[str] = None,
    top_k: int = 4,
) -> list:
    """
    Retrieve the most relevant clinical note chunks for a query.

    Args:
        query: Natural language query string.
        patient_id: If provided, restrict results to this patient's notes.
        top_k: Number of results to return.

    Returns:
        List of dicts with keys: text, patient_id, name, score
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode(query).tolist()

    where_filter = {"patient_id": patient_id} if patient_id else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append({
            "text": doc,
            "patient_id": meta.get("patient_id", ""),
            "name": meta.get("name", ""),
            "score": round(1 - dist, 4),  # cosine similarity
        })

    return output
