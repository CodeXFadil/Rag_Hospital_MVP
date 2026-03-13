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
from typing import Optional, List, Dict, Tuple
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from openai import OpenAI

# Streamlit secrets support
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

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
    api_key = OPENROUTER_API_KEY
    
    # Fallback to Streamlit secrets if running in Streamlit Cloud
    if not api_key and HAS_STREAMLIT:
        try:
            api_key = st.secrets.get("OPENROUTER_API_KEY", "")
        except FileNotFoundError:
            pass

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set. Please add it to your .env file or Streamlit app Secrets.")
    return OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)



# ── Routing helpers ─────────────────────────────────────────────────────────────

def _resolve_patients(intent: str, pid: Optional[str], pname: Optional[str], query: str) -> list:
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
    # Almost all clinical queries benefit from checking doctor notes for context
    return intent in {INTENT_NOTES, INTENT_SUMMARY, INTENT_MEDICATION, INTENT_LAB}


# ── Prompt builder ──────────────────────────────────────────────────────────────

def _build_prompt(
    query: str,
    intent: str,
    patients: List[Dict],
    notes: List[Dict],
    risk_flags: List[Dict],
) -> Tuple[str, str]:
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

        notes_ctx = [
            f"[{n['patient_id']} - {n['name']}] {n['text']}"
            for n in notes[:4]
        ]
        sections.append("=== RETRIEVED CLINICAL NOTES ===\n" + "\n\n".join(notes_ctx))

    if risk_flags:
        flags_ctx = [f"{f['flag']}: {f['detail']}" for f in risk_flags]
        sections.append("=== CLINICAL RISK FLAGS ===\n" + "\n".join(flags_ctx))

    context_block = "\n\n".join(sections) if sections else "No relevant patient data found."

    # Logic to decide if Risk Indicators should be shown
    risk_keywords = ["risk", "flag", "warning", "indicator", "concern", "problem", "danger", "alert"]
    query_asks_for_risks = any(kw in query.lower() for kw in risk_keywords)
    include_risks = (intent == INTENT_SUMMARY) or query_asks_for_risks

    # If we shouldn't include risks, remove the risk context from the block passed to LLM
    # However, if the query is a population query about a threshold, we might want to keep it
    # But the user specifically complained about the long list of risks in the population query.
    if not include_risks and risk_flags:
        # Rebuild sections without risks
        filtered_sections = []
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
            filtered_sections.append("=== STRUCTURED PATIENT DATA ===\n" + "\n\n".join(patient_ctx))

            notes_ctx = [
                f"[{n['patient_id']} - {n['name']}] {n['text']}"
                for n in notes[:4]
            ]
            filtered_sections.append("=== RETRIEVED CLINICAL NOTES ===\n" + "\n\n".join(notes_ctx))
        context_block = "\n\n".join(filtered_sections) if filtered_sections else "No relevant patient data found."

    # Dynamic instructions based on intent
    intent_instructions = ""
    format_instructions = (
        "Structure your response with clear sections if multiple pieces of info are asked, "
        "but for simple questions, BE DIRECT and concise."
    )

    if intent == INTENT_MEDICATION:
        intent_instructions = "Focus specifically on the patient's medications, dosages, and any mentions of drug effectiveness or side effects in the notes."
    elif intent == INTENT_LAB:
        intent_instructions = "Focus on the specific lab values, ranges, and any clinical flags related to these metrics."
    elif intent == INTENT_PATIENT_LOOKUP:
        intent_instructions = "Provide the basic identification details and current status of the patient."
    elif intent == INTENT_SUMMARY:
        intent_instructions = "Provide a comprehensive overview based on structured data and notes."
        format_instructions = (
            "Structure your response with these sections:\n"
            "1. Patient Overview\n"
            "2. Current Medications\n"
            "3. Recent Lab Results\n"
            "4. Clinical Notes Summary\n"
            "5. Risk Indicators"
        )
    elif intent == INTENT_POPULATION:
        intent_instructions = "Summarize the cohort found based on the criteria in the query."

    system_prompt = (
        "You are a clinical AI assistant for hospital staff. "
        "Answer queries about patient records using ONLY the provided context. "
        "Never fabricate patient data. If information is absent, say so explicitly. "
        f"{intent_instructions}\n"
        f"{format_instructions}\n"
        "Be factual and clinically precise."
    )

    user_message = (
        f"Query: {query}\n\n"
        f"Context:\n{context_block}\n\n"
        "Answer the query directly using only the above context. "
        "If the answer is a simple fact (e.g. a medication name), give it directly without boilerplate."
    )

    return system_prompt, user_message


# ── Main pipeline ───────────────────────────────────────────────────────────────

def process_query(query: str) -> dict:
    """
    Full multi-agent pipeline with timing logs.
    """
    import time
    start_total = time.time()
    
    result = {
        "intent":       None,
        "patients":     [],
        "notes":        [],
        "risk_flags":   [],
        "llm_response": "",
        "timings":      {},
        "error":        None,
    }

    try:
        # ── Step 1: LLM Router ──────────────────────────────────────────
        t0 = time.time()
        intent_data = classify_intent(query)
        result["timings"]["router_llm"] = round(time.time() - t0, 3)
        result["intent"] = intent_data

        intent = intent_data["primary_intent"]
        pid    = intent_data["extracted_patient_id"]
        pname  = intent_data["extracted_patient_name"]

        # ── Step 2a: Structured retrieval ──────────────────────────────
        t1 = time.time()
        patients = _resolve_patients(intent, pid, pname, query)
        result["timings"]["structured_retrieval"] = round(time.time() - t1, 3)
        result["patients"] = patients

        # ── Step 2b: Semantic retrieval ────────────────────────────────
        t2 = time.time()
        notes = []
        if _should_call_notes_agent(intent) or not patients:
            note_pid = patients[0]["patient_id"] if len(patients) == 1 else None
            notes = get_relevant_notes(query=query, patient_id=note_pid, top_k=4)
        result["timings"]["vector_search"] = round(time.time() - t2, 3)
        result["notes"] = notes

        # ── Step 3: Clinical Rules ─────────────────────────────────────
        t3 = time.time()
        if patients:
            if len(patients) == 1:
                result["risk_flags"] = analyse_patient(patients[0])
            else:
                for p in analyse_multiple_patients(patients):
                    result["risk_flags"].extend(p.get("risk_flags", []))
        result["timings"]["clinical_rules"] = round(time.time() - t3, 3)

        # ── Step 4: LLM Synthesizer ────────────────────────────────────
        t4 = time.time()
        system_prompt, user_message = _build_prompt(
            query=query,
            intent=intent,
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
        result["timings"]["synthesis_llm"] = round(time.time() - t4, 3)
        
        result["timings"]["total"] = round(time.time() - start_total, 3)

    except ValueError as e:
        result["error"] = str(e)
    except Exception as e:
        import traceback
        traceback.print_exc()
        result["error"] = f"Pipeline error: {str(e)}"

    return result
