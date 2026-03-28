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
    INTENT_ANALYTICS,
)
from agents.query_engine import parse_query_to_intent, route_intent, compact_intent
from agents.patient_data_agent import find_patient, get_all_patients
from agents.notes_agent import get_relevant_notes
from agents.clinical_reasoning_agent import analyse_patient, analyse_multiple_patients

load_dotenv()

OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL       = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")


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

from agents.patient_data_agent import filter_patients, get_all_patients

def _resolve_patients(intent_data: Dict, query: str) -> list:
    """
    Deterministically retrieve patient records based on structured LLM entities.
    """
    intent   = intent_data.get("primary_intent", "")
    entities = intent_data.get("entities", {})

    # For population-level queries with no specific patient identifier,
    # always return ALL patients so the LLM can count/group them correctly.
    has_patient_id   = bool(entities.get("patient_id"))
    has_patient_name = bool(entities.get("patient_name"))
    has_lab_filter   = bool(entities.get("lab_filters"))
    has_meds_filter  = bool(entities.get("medications"))
    has_gender_filter = (entities.get("gender") or "").strip().lower() in {"male", "female"}
    age_range = entities.get("age_range", {}) or {}
    has_age_filter = (age_range.get("min") is not None) or (age_range.get("max") is not None)
    has_diagnosis_filter = bool(entities.get("diagnoses"))
    has_outcome_filter   = bool(entities.get("outcome"))
    has_year_filter      = bool(entities.get("admission_year"))

    is_population = (intent == INTENT_POPULATION)
    has_narrow_filter = (
        has_patient_id or has_patient_name or has_lab_filter or 
        has_meds_filter or has_gender_filter or has_age_filter or 
        has_diagnosis_filter or has_outcome_filter or has_year_filter
    )

    if intent == INTENT_ANALYTICS:
        # 1. Parse natural language into a structured Query Engine intent
        analytical_intent = parse_query_to_intent(query)
        # 2. Add extra filters from the router to ensure parity
        analytical_intent["filters"].update(entities)
        # 3. Route to the structured query engine
        res = route_intent(analytical_intent)
        
        # NEW: Return the full analytical intent and generated SQL metadata
        return {
            "intent": "aggregation", 
            "result": res.get("result"),
            "analytical_intent": compact_intent(analytical_intent),
            "sql": res.get("metadata", {}).get("sql")
        }

    if is_population and not has_narrow_filter:
        # No specific filter — return all patients for counting / grouping
        return get_all_patients(lightweight=True)

    if entities:
        # Use lightweight for any broad multi-patient lookup
        is_single_lookup = bool(entities.get("patient_id") or entities.get("patient_name"))
        return filter_patients(entities, lightweight=not is_single_lookup)


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

    # 1. Database Metadata & Search Result Count
    try:
        # Optimization: Use lightweight for ALL meta-counts
        all_patients  = get_all_patients(lightweight=True)

        total_count   = len(all_patients)
        
        # Cap population scan at 1,000 for gender counts to save memory/tokens
        meta_sample = all_patients[:1000]
        male_count   = sum(1 for p in meta_sample if (p.get("gender") or "").lower() == "male")
        female_count = sum(1 for p in meta_sample if (p.get("gender") or "").lower() == "female")
        
        # Scaling estimates if we sampled
        if total_count > 1000:
            male_count   = int(male_count * (total_count / 1000))
            female_count = int(female_count * (total_count / 1000))

        if isinstance(patients, list):
            matched_count = len(patients)
        elif isinstance(patients, dict) and "result" in patients:
            res = patients["result"]
            # Multi-metric handling: Extract first count found
            if isinstance(res, dict):
                # Search for any value that looks like a count OR use the first metric found
                matched_count = next((v for k, v in res.items() if "count" in k), 0)
                if matched_count == 0 and res:
                    # If it's an aggregation like 'avg_age', we know at least some patients matched.
                    # Use a descriptive string to signal to the LLM that data IS available.
                    matched_count = f"Census matching cohorts found ({len(res)} metrics)"
            elif isinstance(res, list):
                matched_count = sum(item["metrics"].get("count_patients", 0) for item in res if "metrics" in item)
            else:
                matched_count = res
        else:
            matched_count = 0

        sections.append(
            f"=== DATABASE METADATA ===\n"
            f"Total Patients in Database: {total_count}\n"
            f"  - Gender Distribution (Estimated): Male: {male_count} | Female: {female_count}\n"
            f"Note: Your query currently matches {matched_count} patients."
        )
    except:
        pass

    # 2. Structured Patient Data / Analytics
    if isinstance(patients, dict) and patients.get("intent") == "aggregation":
        res_val = patients.get("result", "")
        if isinstance(res_val, list):
            # Format grouped results: Group: Metric1=Val, Metric2=Val
            lines = []
            for item in res_val:
                m_str = ", ".join([f"{k}={v}" for k, v in item.get('metrics', {}).items()])
                lines.append(f"- {item['group']}: {m_str}")
            res_val = "\n".join(lines)
        elif isinstance(res_val, dict):
            # Format single summary: Metric1=Val, Metric2=Val
            res_val = ", ".join([f"{k}={v}" for k, v in res_val.items()])
        
        sections.append(f"=== POPULATION ANALYTICS ===\n{res_val}")
    elif isinstance(patients, list) and patients:
        # STRICT CAP: Never pass more than 100 patients to LLM context
        context_cap = min(100, len(patients))
        patient_ctx = []
        for p in patients[:context_cap]:
            patient_ctx.append(
                f"ID: {p['patient_id']} | {p['name']} | Age: {p['age']} | Gender: {p['gender']}\n"
                f"Diagnosis: {p.get('primary_diagnosis', p.get('diagnoses', 'Unknown'))}"
            )
        label = f"=== SAMPLE PATIENT DATA (Showing {context_cap} of {len(patients)}) ==="
        sections.append(label + "\n" + "\n".join(patient_ctx))


    # 3. Retrieved Clinical Notes
    if notes:
        notes_ctx = [
            f"[{n['patient_id']} - {n['name']}] {n['text']}"
            for n in notes[:4]
        ]
        sections.append("=== RETRIEVED CLINICAL NOTES ===\n" + "\n\n".join(notes_ctx))

    # 4. Clinical Risk Flags (Deduplicated & Conditional)
    # Logic to decide if Risk Indicators should be shown
    risk_keywords = ["risk", "flag", "warning", "indicator", "concern", "problem", "danger", "alert", "analysis", "scrutini"]
    query_asks_for_risks = any(kw in query.lower() for kw in risk_keywords)
    
    # NEW: Suppress individual risk flags for broad population queries UNLESS specifically asked
    # This prevents the "wall of text" for simple count/list questions.
    include_risks = (intent == INTENT_SUMMARY) or (query_asks_for_risks and intent != INTENT_POPULATION)
    
    if risk_flags and include_risks:
        unique_flags = []
        seen = set()
        for f in risk_flags:
            p_id = f.get("patient_id", "")
            key = (f["flag"], p_id)
            if key not in seen:
                unique_flags.append(f)
                seen.add(key)
        
        flags_ctx = [f"{f['flag']}: {f['detail']}" for f in unique_flags]
        sections.append("=== CLINICAL RISK FLAGS ===\n" + "\n".join(flags_ctx[:10])) # Cap at 10 for safety

    context_block = "\n\n".join(sections) if sections else "No relevant patient data found."

    # Dynamic instructions based on intent
    intent_instructions = ""
    format_instructions = (
        "Structure your response with clear sections if multiple pieces of info are asked, "
        "but for simple questions (like counts or lists), BE DIRECT and concise."
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
        intent_instructions = (
            "Summarize the cohort found. "
            "Use the 'Patients matching current query' number from the context to answer 'how many' questions. "
        )
    elif intent == INTENT_ANALYTICS:
        intent_instructions = (
            "Explain the statistical findings clearly. "
            "If a distribution is provided, present it as a clean list or summary. "
            "Refer to the 'POPULATION ANALYTICS' section for the exact data."
        )

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
        "Answer the query directly using only the above context."
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
        patients = _resolve_patients(intent_data, query)
        result["timings"]["structured_retrieval"] = round(time.time() - t1, 3)
        
        # If patients is a dict, it contains metadata (from Analytics or Filtered structured lookups)
        if isinstance(patients, dict):
            result["analytical_intent"] = patients.get("analytical_intent")
            result["sql"]               = patients.get("sql")
            # Preserve the intent flag for the UI display logic
            p_res = patients.get("result", patients.get("patients", []))
            if isinstance(p_res, (dict, list)) and "intent" not in (p_res if isinstance(p_res, dict) else {}):
                if isinstance(p_res, dict):
                    p_res["intent"] = "aggregation"
            result["patients"]          = p_res
        else:
            result["patients"]          = patients

        # ── Step 2b: Semantic retrieval ────────────────────────────────
        t2 = time.time()
        notes = []
        # Fallback to global notes only if NOT a population-level query
        # This prevents "noise" in population queries while allowing specific 
        # patient semantic lookups to work even if the ID is slightly off.
        allow_global_fallback = (intent != INTENT_POPULATION)
        
        if _should_call_notes_agent(intent) or (not patients and allow_global_fallback):
            note_pid = patients[0]["patient_id"] if len(patients) == 1 else None
            notes = get_relevant_notes(query=query, patient_id=note_pid, top_k=4)
        result["timings"]["vector_search"] = round(time.time() - t2, 3)
        result["notes"] = notes

        # ── Step 3: Clinical Rules ─────────────────────────────────────
        t3 = time.time()
        risk_keywords = {"risk", "flag", "warning", "indicator", "concern",
                         "danger", "alert", "analysis", "problem", "critical"}
        query_asks_for_risks = any(kw in query.lower() for kw in risk_keywords)
        # Only run clinical rules for summary or explicit risk queries on a single patient
        should_run_rules = (intent == INTENT_SUMMARY) or (
            query_asks_for_risks and intent not in {INTENT_POPULATION}
        )

        risk_flags = []
        if isinstance(patients, list) and patients and should_run_rules:
            if len(patients) == 1:
                risk_flags = analyse_patient(patients[0])
                for f in risk_flags:
                    f["patient_id"] = patients[0]["patient_id"]
            else:
                for p in analyse_multiple_patients(patients):
                    p_flags = p.get("risk_flags", [])
                    for pf in p_flags:
                        pf["patient_id"] = p["patient_id"]
                    risk_flags.extend(p_flags)

        result["risk_flags"] = risk_flags
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
