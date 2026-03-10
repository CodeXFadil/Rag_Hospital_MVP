"""
agents/router_agent.py
Determines user query intent and routes to the appropriate agents.
"""

import re


# Query intent categories
INTENT_PATIENT_LOOKUP = "patient_lookup"
INTENT_MEDICATION = "medication_query"
INTENT_LAB = "lab_query"
INTENT_SUMMARY = "summary_request"
INTENT_NOTES = "notes_search"
INTENT_ABNORMAL_LABS = "abnormal_labs"
INTENT_GENERAL = "general"


def classify_intent(query: str) -> dict:
    """
    Classify the user's query into one or more intent categories.

    Returns:
        dict with keys:
          - primary_intent: str
          - extract_patient_id: str | None  (e.g. "P014")
          - extract_patient_name: str | None
          - intents: list[str]  all matched intents
    """
    q = query.lower().strip()
    intents = []

    # ── Pattern matching ───────────────────────────────────────────────────────
    # Patient ID extraction  e.g. "patient P014" or "P014"
    pid_match = re.search(r"\bp(\d{3})\b", q)
    extracted_pid = pid_match.group(0).upper() if pid_match else None

    # Summary / overview
    if any(word in q for word in ["summarize", "summary", "overview", "tell me about patient"]):
        intents.append(INTENT_SUMMARY)

    # Medication
    if any(word in q for word in ["medication", "medicine", "drug", "prescription", "taking", "prescribed"]):
        intents.append(INTENT_MEDICATION)

    # Lab results
    if any(word in q for word in ["lab", "result", "test", "hba1c", "blood pressure", "bp", "cholesterol",
                                   "glucose", "creatinine", "haemoglobin", "hemoglobin", "egfr", "psa",
                                   "tsh", "bmi", "ldl", "hdl", "triglyceride", "wbc", "rbc"]):
        intents.append(INTENT_LAB)

    # Abnormal labs detection
    if any(phrase in q for phrase in ["above", "below", "high", "low", "abnormal", "elevated", "which patients",
                                       "greater than", "less than", "uncontrolled"]):
        intents.append(INTENT_ABNORMAL_LABS)

    # Clinical notes / doctor notes
    if any(phrase in q for phrase in ["note", "concern", "doctor", "clinical", "history", "what does the"]):
        intents.append(INTENT_NOTES)

    # General patient lookup (name or ID present)
    if extracted_pid or any(word in q for word in ["patient", "who is", "find", "lookup", "look up"]):
        if INTENT_SUMMARY not in intents:
            intents.append(INTENT_PATIENT_LOOKUP)

    # Fallback
    if not intents:
        intents.append(INTENT_GENERAL)
        intents.append(INTENT_NOTES)

    # Primary intent priority order
    priority = [
        INTENT_SUMMARY,
        INTENT_ABNORMAL_LABS,
        INTENT_LAB,
        INTENT_MEDICATION,
        INTENT_NOTES,
        INTENT_PATIENT_LOOKUP,
        INTENT_GENERAL,
    ]
    primary = next((i for i in priority if i in intents), INTENT_GENERAL)

    # Try to extract a patient name (simple heuristic: capitalised words after "patient" or "is")
    name_match = re.search(
        r"(?:patient\s+|is\s+)([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", query
    )
    extracted_name = name_match.group(1) if name_match else None

    return {
        "primary_intent": primary,
        "intents": intents,
        "extracted_patient_id": extracted_pid,
        "extracted_patient_name": extracted_name,
    }
