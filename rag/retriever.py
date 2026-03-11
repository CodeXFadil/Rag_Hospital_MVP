"""
rag/retriever.py
Semantic similarity retrieval over ChromaDB clinical notes.
"""

import os
import sys

# Try to apply SQLite patch
try:
    from patch_sqlite import apply_patch
    apply_patch()
except ImportError:
    # If called from a subfolder, we might need to adjust Path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    try:
        from patch_sqlite import apply_patch
        apply_patch()
    except Exception:
        pass

from typing import Optional

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
COLLECTION_NAME = "clinical_notes"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Globals for caching load results
_model_cache = None
_client_cache = None


def _get_model():
    """Lazy load the embedding model to save memory during import."""
    global _model_cache
    if _model_cache is None:
        print("[RETRIEVER] Loading SentenceTransformer...")
        from sentence_transformers import SentenceTransformer
        _model_cache = SentenceTransformer(EMBEDDING_MODEL)
        print("[RETRIEVER] Model loaded.")
    return _model_cache


def _get_collection():
    """Lazy load ChromaDB and get collection."""
    global _client_cache
    if _client_cache is None:
        print("[RETRIEVER] Initializing ChromaDB (with SQLite patch)...")
        try:
            from patch_sqlite import apply_patch
            apply_patch()
        except ImportError:
            pass
            
        import chromadb
        _client_cache = chromadb.PersistentClient(path=CHROMA_DIR)
        print("[RETRIEVER] ChromaDB initialized.")
    
    # The original code checked for existence and raised an error.
    # get_or_create_collection would create it if not found.
    # To maintain original behavior of raising an error if not initialized:
    existing = [c.name for c in _client_cache.list_collections()]
    if COLLECTION_NAME not in existing:
        raise RuntimeError(
            "Vector store not initialized. Please run: python rag/vector_store.py"
        )
    return _client_cache.get_collection(COLLECTION_NAME)


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
