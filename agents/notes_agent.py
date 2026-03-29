"""
agents/notes_agent.py
Retrieves relevant clinical notes. 
Stubbed for now as the 'rag' module is missing in this workspace.
"""

from typing import Optional, List, Dict

def get_relevant_notes(
    query: str,
    patient_id: Optional[str] = None,
    top_k: int = 4,
) -> List[Dict]:
    """
    Fetch semantically relevant clinical note chunks for the query.
    STUBBED: Returns empty list as RAG module is unlocated.
    """
    # TODO: Restore RAG retriever logic once located
    return []
