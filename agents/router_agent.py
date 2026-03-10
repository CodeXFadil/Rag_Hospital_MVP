"""
agents/router_agent.py
LLM-based intent classifier using OpenRouter.
The LLM classifies intent; entity extraction (patient ID/name) stays deterministic.
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ── Intent category constants ───────────────────────────────────────────────────
INTENT_PATIENT_LOOKUP   = "patient_lookup"
INTENT_MEDICATION       = "medication_query"
INTENT_LAB              = "lab_query"
INTENT_SUMMARY          = "patient_summary"
INTENT_NOTES            = "clinical_notes"
INTENT_POPULATION       = "population_query"

VALID_INTENTS = {
    INTENT_PATIENT_LOOKUP,
    INTENT_MEDICATION,
    INTENT_LAB,
    INTENT_SUMMARY,
    INTENT_NOTES,
    INTENT_POPULATION,
}

FALLBACK_INTENT = INTENT_SUMMARY   # safe default

# ── LLM client (shared config with coordinator) ─────────────────────────────────
OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL       = "meta-llama/llama-3-8b-instruct"

SYSTEM_PROMPT = (
    "You are a query routing agent for a hospital patient records assistant. "
    "Your ONLY job is to classify the user's query into exactly one category."
)

CLASSIFICATION_PROMPT = """Classify the user query into exactly one of these categories:

patient_lookup    - finding or identifying a specific patient
medication_query  - questions about medications, drugs, prescriptions, or dosages
lab_query         - questions about lab results, test values, or specific biomarkers
patient_summary   - requests for an overall health summary or overview of a patient
clinical_notes    - requests about doctor notes, clinical observations, or medical history narratives
population_query  - questions about multiple patients, cohorts, or threshold-based filtering (e.g. "which patients have HbA1c above 8")

Return ONLY the category name, nothing else.

Query: {query}
Category:"""


def _get_llm_client() -> OpenAI:
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY not set. Please add it to your .env file."
        )
    return OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)


def _classify_with_llm(query: str) -> str:
    """Call LLM to classify intent. Returns a validated intent string."""
    client = _get_llm_client()
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        temperature=0,
        max_tokens=10,          # only need one short token
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": CLASSIFICATION_PROMPT.format(query=query)},
        ],
    )
    raw = response.choices[0].message.content.strip().lower()

    # Normalise: strip punctuation and extra whitespace
    cleaned = re.sub(r"[^a-z_]", "", raw)

    if cleaned in VALID_INTENTS:
        return cleaned

    # Partial match fallback (e.g. LLM says "summary" instead of "patient_summary")
    for intent in VALID_INTENTS:
        if cleaned in intent or intent in cleaned:
            return intent

    return FALLBACK_INTENT


# ── Deterministic entity extraction (no LLM) ───────────────────────────────────

def _extract_patient_id(query: str) -> str | None:
    """Extract a patient ID like P014 from the query string."""
    match = re.search(r"\bp(\d{3})\b", query, re.IGNORECASE)
    return match.group(0).upper() if match else None


def _extract_patient_name(query: str) -> str | None:
    """
    Heuristic name extraction: look for Title-Case word pairs after
    common trigger words, or just two consecutive capitalised words.
    """
    # After trigger words
    m = re.search(
        r"(?:patient|about|for|of|is|summarize|summary of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})",
        query,
    )
    if m:
        return m.group(1)

    # Fallback: two consecutive Title-Case words anywhere
    m = re.search(r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b", query)
    if m:
        return m.group(1)

    return None


# ── Public API ──────────────────────────────────────────────────────────────────

def classify_intent(query: str) -> dict:
    """
    Classify the user query and extract relevant entities.

    Returns:
        {
          "primary_intent":         str   — one of VALID_INTENTS
          "intents":                list  — [primary_intent]  (kept for coordinator compat)
          "extracted_patient_id":   str | None
          "extracted_patient_name": str | None
        }
    """
    intent = _classify_with_llm(query)

    return {
        "primary_intent":         intent,
        "intents":                [intent],          # coordinator reads intent["intents"]
        "extracted_patient_id":   _extract_patient_id(query),
        "extracted_patient_name": _extract_patient_name(query),
    }
