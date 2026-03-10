"""
agents/coordinator_agent.py
Orchestrates all agents, calls OpenRouter LLM, and synthesizes the final response.

LLM is used in exactly two places:
  1. router_agent.classify_intent()  — intent classification
  2. This file — final response synthesis
"""

import os
import sys
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from openai import OpenAI

from agents.router_agent import (
    classify_intent,
    INTENT_PATIENT_LOOKUP,
    INTENT_MEDICATION,
    INTENT_LAB,
    INTENT_SUMMARY,
    INTENT_NOTES,
    INTENT_POPULATION,
)
from agents.patient_data_agent import find_patient, find_patients_by_lab_threshold, get_all_patients
from agents.notes_agent import get_relevant_notes
from agents.clinical_reasoning_agent import analyse_patient, analyse_multiple_patients

load_dotenv()

OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL       = "meta-llama/llama-3-8b-instruct"


def _get_llm_client() -> OpenAI:
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set. Please add it to your .env file.")
    return OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)


# ── Routing helpers ─────────────────────────────────────────────────────────────

def _resolve_patients(intent: str, pid: str | None, pname: str | None, query: str) -> list[dict]:
    """
    Deterministically retrieve patient records based on intent.
    LLM never touches the database — all retrieval is pandas/CSV.
    """
    # ── population_query: threshold-based multi-patient search ─────────────────
    if intent == INTENT_POPULATION:
        threshold_match = re.search(
            r"(HbA1c|BP|LDL|eGFR|Hb|TSH|BNP|cholesterol)[^\d]*([0-9]+\.?[0-9]*)",
            query, re.IGNORECASE,
        )
        direction = (
            "below"
            if any(w in query.lower() for w in ["below", "low", "less than"])
            else "above"
        )
        if threshold_match:
            marker    = threshold_match.group(1)
            threshold = float(threshold_match.group(2))
            return find_patients_by_lab_threshold(marker, direction, threshold)

        # No threshold found — fall back to individual lookup if we have an ID/name
        if pid or pname:
            return find_patient(patient_id=pid, name=pname)
        return []

    # ── All other intents: resolve by patient ID or name ───────────────────────
    if pid or pname:
        return find_patient(patient_id=pid, name=pname)

    return []


def _should_call_notes_agent(intent: str) -> bool:
    """Return True for intents that benefit from semantic note retrieval."""
    return intent in {INTENT_NOTES, INTENT_SUMMARY}


# ── Prompt builder ──────────────────────────────────────────────────────────────

def _build_prompt(
    query: str,
    patients: list[dict],
    notes: list[dict],
    risk_flags: list[dict],
) -> tuple[str, str]:
    """Assemble the system + user messages for final LLM synthesis."""
    sections = []

    if patients:
        patient_ctx = []
        for p in patients[:3]:
            patient_ctx.append(
                f"Patient: {p['name']} ({p['patient_id']}) | Age: {p['age']} | Gender: {p['gender']}\n"
                f"Diagnoses: {p['diagnoses']}\n"
                f"Medications: {p['medications']}\n"
                f"Lab Results: {p['lab_results']}\n"
                f"Visit History: {p['visit_history']}"
            )
        sections.append("=== STRUCTURED PATIENT DATA ===\n" + "\n\n".join(patient_ctx))

    if notes:
        notes_ctx = [
            f"[{n['patient_id']} – {n['name']}] {n['text']}"
            for n in notes[:4]
        ]
        sections.append("=== RETRIEVED CLINICAL NOTES ===\n" + "\n\n".join(notes_ctx))

    if risk_flags:
        flags_ctx = [f"{f['flag']}: {f['detail']}" for f in risk_flags]
        sections.append("=== CLINICAL RISK FLAGS ===\n" + "\n".join(flags_ctx))

    context_block = "\n\n".join(sections) if sections else "No relevant patient data found."

    system_prompt = (
        "You are a clinical AI assistant for hospital staff. "
        "Answer queries about patient records using ONLY the provided context. "
        "Never fabricate patient data. If information is absent, say so explicitly. "
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
        "Answer the query using only the above context "
        "and use the structured sections format specified."
    )

    return system_prompt, user_message


# ── Main pipeline ───────────────────────────────────────────────────────────────

def process_query(query: str) -> dict:
    """
    Full multi-agent pipeline:
      LLM Router → Hybrid Retrieval → Clinical Rules → Context Builder → LLM Synthesizer

    Returns dict with keys: intent, patients, notes, risk_flags, llm_response, error
    """
    result = {
        "intent":       None,
        "patients":     [],
        "notes":        [],
        "risk_flags":   [],
        "llm_response": "",
        "error":        None,
    }

    try:
        # ── Step 1: LLM Router (intent classification) ────────────────────────
        intent_data = classify_intent(query)
        result["intent"] = intent_data

        intent = intent_data["primary_intent"]
        pid    = intent_data["extracted_patient_id"]
        pname  = intent_data["extracted_patient_name"]

        # ── Step 2a: Structured retrieval (deterministic — pandas) ────────────
        patients = _resolve_patients(intent, pid, pname, query)
        result["patients"] = patients

        # ── Step 2b: Semantic retrieval (deterministic — ChromaDB) ───────────
        notes = []
        if _should_call_notes_agent(intent) or not patients:
            # Pin to single patient's notes when we have exactly one match
            note_pid = patients[0]["patient_id"] if len(patients) == 1 else None
            notes = get_relevant_notes(query=query, patient_id=note_pid, top_k=4)
        result["notes"] = notes

        # ── Step 3: Clinical Rules Engine (deterministic) ─────────────────────
        if patients:
            if len(patients) == 1:
                result["risk_flags"] = analyse_patient(patients[0])
            else:
                for p in analyse_multiple_patients(patients):
                    result["risk_flags"].extend(p.get("risk_flags", []))

        # ── Step 4: Context builder + LLM Synthesizer ─────────────────────────
        system_prompt, user_message = _build_prompt(
            query=query,
            patients=patients,
            notes=notes,
            risk_flags=result["risk_flags"],
        )

        client   = _get_llm_client()
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
        )
        result["llm_response"] = response.choices[0].message.content

    except ValueError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"Pipeline error: {str(e)}"

    return result
