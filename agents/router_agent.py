"""
agents/router_agent.py
LLM-based structured query parser using OpenRouter.
Simplified for Single-Table (Patients) architecture.
"""

import os
import re
import sys
import json
from typing import Optional, Dict
from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
load_dotenv()

# ── Intent category constants ───────────────────────────────────────────────────
INTENT_PATIENT_LOOKUP   = "patient_lookup"
INTENT_SUMMARY          = "patient_summary"
INTENT_NOTES            = "clinical_notes"
INTENT_POPULATION       = "population_query"
INTENT_ANALYTICS        = "analytics_query"
FALLBACK_INTENT         = INTENT_SUMMARY

VALID_INTENTS = {
    INTENT_PATIENT_LOOKUP, INTENT_SUMMARY, INTENT_NOTES, 
    INTENT_POPULATION, INTENT_ANALYTICS
}

# Mapping old intents to new ones for backward compatibility in the coordinator if needed
# (Though we are cleaning the coordinator next)
INTENT_MEDICATION = INTENT_SUMMARY
INTENT_LAB        = INTENT_SUMMARY

OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL       = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")

# ── Prompts ─────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a clinical query parser. Extract medical search criteria into structured JSON.\n"
    "The entire dataset is in a SINGLE table. There are no separate medication or lab tables.\n\n"
    "OUTPUT RULES:\n"
    "1. Output null for ANY field not explicitly mentioned.\n"
    "2. 'gender' must be 'male', 'female', or null.\n"
    "3. 'primary_intent' rules:\n"
    "    - 'analytics_query': for statistical questions (how many, average, mean, count by, group by).\n"
    "    - 'patient_summary': for questions about a specific patient's clinical history, medications, or status.\n"
    "    - 'population_query': for finding lists of patients matching criteria without statistics.\n"
    "    - 'patient_lookup': for identifying a patient by ID or Name."
)

SCHEMA_PROMPT = """Return JSON with null for any field not present in the query:
{{
  "primary_intent": "one of: [patient_lookup, patient_summary, clinical_notes, population_query, analytics_query]",
  "entities": {{
    "patient_id": null,
    "patient_name": null,
    "primary_diagnosis": null,
    "mi_type": null,
    "icu_admission": null,
    "age_range": {{"min": null, "max": null}},
    "gender": null,
    "outcome": null,
    "admission_year": null
  }}
}}
Query: {query}"""

# ── LLM Client ──────────────────────────────────────────────────────────────────

def _get_llm_client() -> OpenAI:
    return OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)

# ── Intent Classifier ───────────────────────────────────────────────────────────

def classify_intent(query: str) -> Dict:
    client = _get_llm_client()
    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": SCHEMA_PROMPT.format(query=query)},
            ],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)

        # 1. Clean keys
        def clean_obj(obj):
            if isinstance(obj, dict):
                return {k.strip().replace('"', '').replace("'", ""): clean_obj(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_obj(i) for i in obj]
            return obj

        data = clean_obj(data)

        # 2. Validate intent
        raw_intent  = data.get("primary_intent", FALLBACK_INTENT)
        final_intent = FALLBACK_INTENT
        for v in VALID_INTENTS:
            if v in str(raw_intent).lower():
                final_intent = v
                break

        # 3. Extract entities with cleaning
        raw_entities = data.get("entities", {})
        if not isinstance(raw_entities, dict):
            raw_entities = {}
        
        entities = {}
        for k, v in raw_entities.items():
            if v is not None:
                if isinstance(v, dict):
                    entities[k] = v
                else:
                    val = str(v).strip()
                    # Clinical Normalization
                    if k == "primary_diagnosis":
                        low_val = val.lower()
                        if low_val in ["mi", "heart attack", "myocardial infarction", "myocardal infarction"]:
                            val = "Myocardial Infarction"
                    
                    # Check for MI types specifically
                    if "stemi" in str(val).lower():
                        entities["mi_type"] = "STEMI"
                        if k == "primary_diagnosis" and "infarction" not in val.lower():
                            val = "Myocardial Infarction"

                    entities[k] = val
            else:
                entities[k] = None

        return {
            "primary_intent":        final_intent,
            "intents":               [final_intent],
            "entities":              entities,
            "extracted_patient_id":  entities.get("patient_id"),
            "extracted_patient_name": entities.get("patient_name"),
        }

    except Exception as e:
        print(f"ROUTER FALLBACK: {e}")
        return {
            "primary_intent":        FALLBACK_INTENT,
            "intents":               [FALLBACK_INTENT],
            "entities":              {},
            "extracted_patient_id":  None,
            "extracted_patient_name": None,
        }
