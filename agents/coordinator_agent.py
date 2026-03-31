import os
import sys
import json
import time
import re
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv

# Local Imports
from .logger import log_step

load_dotenv()

# Configuration
DEFAULT_MODEL = "openai/gpt-4o-mini-2024-07-18"

def _get_llm_client():
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

def _build_prompt(query, intent, result_data) -> Tuple[str, str]:
    """
    Builds a clinical-context prompt using Ground Truth results.
    """
    sections = []
    patients = result_data.get("patients", [])
    filter_summary = "None"
    
    if isinstance(patients, dict):
        filter_summary = patients.get("metadata", {}).get("filters_applied", "None")
        
    count = 0
    agg_summary = None

    if isinstance(patients, dict) and "aggregation" in patients:
        agg_data = patients["aggregation"]
        res_list = agg_data.get("result", [])
        if res_list:
            summary_parts = []
            for item in res_list:
                grp = item.get("group", "Total")
                metrics = item.get("metrics", {})
                val = next(iter(metrics.values())) if metrics else "N/A"
                summary_parts.append(f"{grp}: {val}")
            agg_summary = ", ".join(summary_parts)
            count = len(res_list)

    elif isinstance(patients, dict):
        def find_count(obj):
            if isinstance(obj, (int, float)): return obj
            if isinstance(obj, dict):
                if "metrics" in obj: return find_count(obj["metrics"])
                for k, v in obj.items():
                    if k.startswith("count_") or k.startswith("avg_"): return v
                for v in obj.values():
                    res_inner = find_count(v)
                    if res_inner: return res_inner
            if isinstance(obj, list) and obj: return find_count(obj[0])
            return 0
        count = find_count(patients)

    elif isinstance(patients, list):
        count = len(patients)

    # 1. Main Logic: Ground Truth Data
    if agg_summary:
        sections.append(
            f"=== GROUND TRUTH DATA ===\n"
            f"Question: {query}\n"
            f"Detailed Breakdown: {agg_summary}\n"
            f"Note: These numbers represent the complete count from the hospital database.\n"
            f"Clinical Filters Applied: {filter_summary}"
        )
    elif count > 0 or filter_summary != "None":
        sections.append(
            f"=== GROUND TRUTH DATA ===\n"
            f"Question: {query}\n"
            f"Total Matches Found: {count}\n"
            f"Clinical Filters Applied: {filter_summary}"
        )

    # 2. Sample Population (if list)
    if isinstance(patients, list) and patients:
        is_actual_patient_list = isinstance(patients[0], dict) and "patient_id" in patients[0]
        if is_actual_patient_list:
            context_cap = min(100, len(patients))
            patient_ctx = []
            for p in patients[:context_cap]:
                patient_ctx.append(f"ID: {p['patient_id']} | {p['name']} | Age: {p['age']} | Gender: {p['gender']}")
            sections.append(f"=== SAMPLE CLINICAL RECORDS ({context_cap} records) ===\n" + "\n".join(patient_ctx))

    context_block = "\n\n".join(sections) if sections else "No clinical records found matching the criteria."
    
    system_prompt = (
        "You are an expert Clinical Data Analyst. Your goal is to provide a clear, professional, "
        "and accurate summary of the [GROUND TRUTH DATA].\n"
        "1. Mention every specific metric and category found in the data (e.g. mention both gender counts).\n"
        "2. Use full, natural sentences. Avoid being robotic.\n"
        "3. If the data is empty, explicitly state that no matching patients were found.\n"
        "4. Do not include internal IDs like patient_id unless specifically asked."
    )

    user_message = (
        f"Clinician Query: '{query}'\n\n"
        f"Available Data:\n{context_block}\n\n"
        "Provide a professional natural language summary of these clinical findings:"
    )

    return system_prompt, user_message

def process_query(query: str) -> dict:
    """
    Unified pipeline using query_engine.run_query for 100% structured retrieval.
    """
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
        log_step("COORDINATOR: RECEIVED QUERY", query)
        t0 = time.time()
        engine_result = run_query(query)
        result["timings"]["structured_engine"] = round(time.time() - t0, 3)
        
        result["intent"] = engine_result.get("parsed_intent")
        result["patients"] = engine_result.get("result", {})
        result["sql"] = engine_result.get("metadata", {}).get("sql")
        
        t1 = time.time()
        system_prompt, user_message = _build_prompt(
            query=query,
            intent=result["intent"].get("primary_intent") if result["intent"] else "analytics_query",
            result_data=result,
        )

        log_step("COORDINATOR: SYNTHESIS PROMPT", {"system": system_prompt, "user": user_message})

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
        log_step("COORDINATOR: FINAL RESPONSE", result["llm_response"])
        result["timings"]["synthesis_llm"] = round(time.time() - t1, 3)
        result["timings"]["total"] = round(time.time() - start_total, 3)

    except Exception as e:
        import traceback
        traceback.print_exc()
        result["error"] = f"Pipeline error: {str(e)}"

    return result
