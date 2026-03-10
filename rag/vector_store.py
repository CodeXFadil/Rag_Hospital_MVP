"""
rag/vector_store.py
Ingests patient doctor notes from CSV into ChromaDB using sentence-transformers embeddings.
Run this once (or whenever data changes) to build / refresh the vector store.
"""

import os
import sys
import pandas as pd
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# ── Constants ──────────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "patients.csv")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
COLLECTION_NAME = "clinical_notes"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 200  # approximate characters per chunk


def chunk_text(text: str, patient_id: str, chunk_size: int = CHUNK_SIZE) -> list[dict]:
    """Split a doctor notes string into overlapping chunks."""
    words = text.split()
    chunks = []
    step = max(1, chunk_size // 6)  # ~6-word overlap
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + step * 2])
        if chunk.strip():
            chunks.append({"text": chunk, "patient_id": patient_id, "chunk_index": i})
    return chunks


def build_vector_store(force_rebuild: bool = False) -> chromadb.Collection:
    """Build or load the ChromaDB collection with clinical notes embeddings."""
    os.makedirs(CHROMA_DIR, exist_ok=True)

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # If collection exists and not forcing rebuild, return it
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing and not force_rebuild:
        print(f"[VectorStore] Collection '{COLLECTION_NAME}' already exists. Using cached store.")
        return client.get_collection(COLLECTION_NAME)

    # Drop and recreate
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
        print(f"[VectorStore] Dropped existing collection for rebuild.")

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    print("[VectorStore] Loading patients.csv …")
    df = pd.read_csv(DATA_PATH)

    print(f"[VectorStore] Loading embedding model: {EMBEDDING_MODEL} …")
    model = SentenceTransformer(EMBEDDING_MODEL)

    all_documents = []
    all_embeddings = []
    all_metadatas = []
    all_ids = []

    for _, row in df.iterrows():
        patient_id = str(row["patient_id"])
        notes = str(row.get("doctor_notes", ""))
        if not notes.strip():
            continue

        chunks = chunk_text(notes, patient_id)
        for chunk in chunks:
            doc_id = f"{patient_id}_chunk_{chunk['chunk_index']}"
            all_documents.append(chunk["text"])
            all_metadatas.append({
                "patient_id": patient_id,
                "name": str(row.get("name", "")),
                "chunk_index": str(chunk["chunk_index"]),
            })
            all_ids.append(doc_id)

    if all_documents:
        print(f"[VectorStore] Encoding {len(all_documents)} chunks …")
        all_embeddings = model.encode(all_documents, show_progress_bar=True).tolist()

        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(all_documents), batch_size):
            collection.add(
                ids=all_ids[i : i + batch_size],
                documents=all_documents[i : i + batch_size],
                embeddings=all_embeddings[i : i + batch_size],
                metadatas=all_metadatas[i : i + batch_size],
            )
        print(f"[VectorStore] ✓ Indexed {len(all_documents)} chunks into '{COLLECTION_NAME}'.")
    else:
        print("[VectorStore] ⚠ No documents found to index.")

    return collection


if __name__ == "__main__":
    force = "--rebuild" in sys.argv
    build_vector_store(force_rebuild=force)
    print("[VectorStore] Done.")
