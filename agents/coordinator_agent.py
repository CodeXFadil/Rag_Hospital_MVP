"""
agents/coordinator_agent.py
Orchestrates all agents, calls OpenRouter LLM, and synthesizes the final response.
"""

import os
import sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from openai import OpenAI

from agents.router_agent import (
    classify_intent,
    INTENT_SUMMARY, INTENT_MEDICATION, INTENT_LAB,
    INTENT_PATIENT_LOOKUP, INTENT_NOTES, INTENT_ABNORMAL_LABS,
)
from agents.patient_data_agent import find_patient, find_patients_by_lab_threshold
from agents.notes_agent import get_relevant_notes
from agents.clinical_reasoning_agent import analyse_patient, analyse_multiple_patients

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "meta-llama/llama-3-8b-instruct"


def _get_llm_client() -> OpenAI:
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set. Please add it to your .env file.")
    return OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )


def _build_prompt(
    query: str,
    patients: list[dict],
    notes: list[dict],
    risk_flags: list[dict],
    intent: dict,
) -> str:
    """Build the LLM prompt from retrieved context."""
    sections = []

    # Patient structured data
    if patients:
        patient_ctx = []
        for p in patients[:3]:  # max 3 patients to keep prompt size reasonable
            patient_ctx.append(
                f"Patient: {p['name']} ({p['patient_id']}) | Age: {p['age']} | Gender: {p['gender']}\n"
                f"Diagnoses: {p['diagnoses']}\n"
                f"Medications: {p['medications']}\n"
                f"Lab Results: {p['lab_results']}\n"
                f"Visit History: {p['visit_history']}"
            )
        sections.append("=== STRUCTURED PATIENT DATA ===\n" + "\n\n".join(patient_ctx))

    # Clinical notes (RAG)
    if notes:
        notes_ctx = []
        for n in notes[:4]:
            notes_ctx.append(f"[{n['patient_id']} – {n['name']}] {n['text']}")
        sections.append("=== RETRIEVED CLINICAL NOTES ===\n" + "\n\n".join(notes_ctx))

    # Risk flags
    if risk_flags:
        flags_ctx = []
        for f in risk_flags:
            flags_ctx.append(f"{f['flag']}: {f['detail']}")
        sections.append("=== CLINICAL RISK FLAGS ===\n" + "\n".join(flags_ctx))

    context_block = "\n\n".join(sections) if sections else "No relevant patient data found."

    system_prompt = (
        "You are a clinical AI assistant for hospital staff. "
        "Your role is to answer queries about patient records using ONLY the provided context. "
        "Never fabricate patient data. If information is not in the context, say so clearly. "
        "Structure your response with clear sections:\n"
        "1. Patient Overview\n"
        "2. Current Medications\n"
        "3. Recent Lab Results\n"
        "4. Clinical Notes Summary\n"
        "5. Risk Indicators\n"
        "Be concise, factual, and clinically precise."
    )

    user_message = (
        f"Query: {query}\n\n"
        f"Context:\n{context_block}\n\n"
        "Please answer the query using only the above context. "
        "Use the structured sections format specified."
    )

    return system_prompt, user_message


def process_query(query: str) -> dict:
    """
    Main entry point: process a user query through the multi-agent pipeline.

    Returns:
        dict with keys:
          - intent: dict from router
          - patients: list of matched patient records
          - notes: list of retrieved note chunks
          - risk_flags: list of clinical risk flags
          - llm_response: str (final synthesized answer)
          - error: str | None
    """
    result = {
        "intent": None,
        "patients": [],
        "notes": [],
        "risk_flags": [],
        "llm_response": "",
        "error": None,
    }

    try:
        # ── Step 1: Router ────────────────────────────────────────────────────
        intent = classify_intent(query)
        result["intent"] = intent
        pid = intent["extracted_patient_id"]
        pname = intent["extracted_patient_name"]
        intents = intent["intents"]

        # ── Step 2: Structured data retrieval ─────────────────────────────────
        patients = []
        
        # Abnormal labs search (e.g. "HbA1c above 8")
        if INTENT_ABNORMAL_LABS in intents:
            import re
            # Try to extract marker + threshold from query
            threshold_match = re.search(
                r"(HbA1c|BP|LDL|eGFR|Hb|TSH|BNP|cholesterol)[^\d]*([0-9]+\.?[0-9]*)",
                query, re.IGNORECASE
            )
            direction = "below" if any(w in query.lower() for w in ["below", "low", "less than"]) else "above"
            
            if threshold_match:
                marker = threshold_match.group(1)
                threshold = float(threshold_match.group(2))
                patients = find_patients_by_lab_threshold(marker, direction, threshold)
            elif pid or pname:
                patients = find_patient(patient_id=pid, name=pname)
            else:
                patients = find_patient()

        # Direct patient lookup by ID or name
        if not patients and (pid or pname):
            patients = find_patient(patient_id=pid, name=pname)

        # No patient resolved yet – fallback notes search only
        result["patients"] = patients

        # ── Step 3: Clinical notes retrieval (RAG) ────────────────────────────
        note_patient_id = patients[0]["patient_id"] if len(patients) == 1 else None
        notes = get_relevant_notes(query=query, patient_id=note_patient_id, top_k=4)
        result["notes"] = notes

        # ── Step 4: Clinical reasoning ────────────────────────────────────────
        if patients:
            if len(patients) == 1:
                flags = analyse_patient(patients[0])
                result["risk_flags"] = flags
            else:
                analysed = analyse_multiple_patients(patients)
                # Collect all flags
                for p in analysed:
                    result["risk_flags"].extend(p.get("risk_flags", []))

        # ── Step 5: LLM synthesis ─────────────────────────────────────────────
        system_prompt, user_message = _build_prompt(
            query=query,
            patients=patients,
            notes=notes,
            risk_flags=result["risk_flags"],
            intent=intent,
        )

        client = _get_llm_client()
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        result["llm_response"] = response.choices[0].message.content

    except ValueError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"Pipeline error: {str(e)}"

    return result
