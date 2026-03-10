"""
agents/notes_agent.py
Retrieves relevant clinical notes from ChromaDB using semantic search.
"""

import sys, os
from typing import Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rag.retriever import retrieve


def get_relevant_notes(
    query: str,
    patient_id: Optional[str] = None,
    top_k: int = 4,
) -> list:
    """
    Fetch semantically relevant clinical note chunks for the query.

    Args:
        query: User's natural language query.
        patient_id: If provided, filter to this patient's notes.
        top_k: Number of note chunks to return.

    Returns:
        List of dicts: {text, patient_id, name, score}
    """
    try:
        results = retrieve(query=query, patient_id=patient_id, top_k=top_k)
        return results
    except RuntimeError as e:
        return [{"text": str(e), "patient_id": "", "name": "", "score": 0.0}]
