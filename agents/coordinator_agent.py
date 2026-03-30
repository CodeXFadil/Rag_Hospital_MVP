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

from agents.query_engine import run_query

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





def _build_prompt(
    query: str,
    intent: str,
    result_data: Dict,
) -> Tuple[str, str]:
    
    """Assemble the system + user messages for final LLM synthesis."""
    sections = []

    # 1. Structured Results
    # result_data might contain "patients" as a list, a dict, or a nested wrapper
    patients = result_data.get("patients", [])
    print(f"\n[DEBUG] _build_prompt received patients type: {type(patients)}")
    if isinstance(patients, dict):
        print(f"[DEBUG] patients keys: {patients.keys()}")
    elif isinstance(patients, list):
        print(f"[DEBUG] patients length: {len(patients)}")

    count = 0
    filter_summary = "None"
    
    # count extraction logic
    if isinstance(patients, dict):
        # Extract Filter Summary
        filter_summary = patients.get("metadata", {}).get("filters_applied", "None")
        
        # Robust Recursive Search for Metrics
        def find_count(obj):
            if isinstance(obj, (int, float)): return obj
            if isinstance(obj, dict):
                # Check for metrics key
                if "metrics" in obj:
                    return find_count(obj["metrics"])
                # Check for direct count keys
                for k, v in obj.items():
                    if k.startswith("count_") or k.startswith("avg_"): return v
                # Recurse
                for v in obj.values():
                    res_inner = find_count(v)
                    if res_inner: return res_inner
            if isinstance(obj, list) and obj:
                return find_count(obj[0])
            return 0

        count = find_count(patients)

    elif isinstance(patients, list):
        count = len(patients)

    print(f"[DEBUG] Final Count Identified: {count}")

    # 2. Main Logic: Ground Truth Data
    if count > 0 or filter_summary != "None":
        sections.append(
            f"=== GROUND TRUTH DATA ===\n"
            f"Question: {query}\n"
            f"Matched Patient Count: {count}\n"
            f"Clinical Filters Applied: {filter_summary}"
        )

    # 3. Sample Population (if list)
    if isinstance(patients, list) and patients:
        is_actual_patient_list = isinstance(patients[0], dict) and "patient_id" in patients[0]
        if is_actual_patient_list:
            context_cap = min(100, len(patients))
            patient_ctx = []
            for p in patients[:context_cap]:
                patient_ctx.append(f"ID: {p['patient_id']} | {p['name']} | Age: {p['age']} | Gender: {p['gender']}")
            sections.append(f"=== SAMPLE DATA ({context_cap} records) ===\n" + "\n".join(patient_ctx))

    context_block = "\n\n".join(sections) if sections else "No relevant data found."
    
    # DEBUG: Print exactly what we are sending
    print(f"\n[DEBUG] PROMPT CONTEXT:\n{context_block}\n")

    system_prompt = (
        "You are a clinical AI assistant. Answer queries using ONLY the [GROUND TRUTH DATA]. "
        "If a count or average is provided, that is the literal answer. "
        "Be direct, concise, and clinically precise. Do not apologize or add fluff."
    )

    user_message = f"Query: {query}\n\nContext:\n{context_block}\n\nAnswer directly:"

    return system_prompt, user_message


# ── Main pipeline ───────────────────────────────────────────────────────────────

def process_query(query: str) -> dict:
    """
    Unified pipeline using query_engine.run_query for 100% structured retrieval.
    """
    import time
    from agents.query_engine import run_query
    start_total = time.time()
    
    result = {
        "intent":       None,
        "patients":     [],
        "llm_response": "",
        "timings":      {},
        "error":        None,
    }

    try:
        # 1. Unified Structured Engine (Parsing + Routing + Execution)
        t0 = time.time()
        engine_result = run_query(query)
        result["timings"]["structured_engine"] = round(time.time() - t0, 3)
        
        # 2. Extract Data
        result["intent"] = engine_result.get("parsed_intent")
        result["patients"] = engine_result.get("result", {})
        result["sql"] = engine_result.get("metadata", {}).get("sql")
        
        # 3. LLM Synthesizer
        t1 = time.time()
        system_prompt, user_message = _build_prompt(
            query=query,
            intent=result["intent"].get("primary_intent") if result["intent"] else "analytics_query",
            result_data=result,
        )

        client   = _get_llm_client()
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            max_tokens=600
        )
        result["llm_response"] = response.choices[0].message.content
        result["timings"]["synthesis_llm"] = round(time.time() - t1, 3)
        
        result["timings"]["total"] = round(time.time() - start_total, 3)

    except Exception as e:
        import traceback
        traceback.print_exc()
        result["error"] = f"Pipeline error: {str(e)}"

    return result
