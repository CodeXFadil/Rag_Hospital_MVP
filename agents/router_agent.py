"""
agents/router_agent.py
LLM-based structured query parser using OpenRouter.
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
INTENT_MEDICATION       = "medication_query"
INTENT_LAB              = "lab_query"
INTENT_SUMMARY          = "patient_summary"
INTENT_NOTES            = "clinical_notes"
INTENT_POPULATION       = "population_query"
FALLBACK_INTENT         = INTENT_SUMMARY

VALID_INTENTS = {
    INTENT_PATIENT_LOOKUP, INTENT_MEDICATION, INTENT_LAB,
    INTENT_SUMMARY, INTENT_NOTES, INTENT_POPULATION
}

OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL       = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")

# ── Prompts ─────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a clinical query parser. Extract criteria into structured JSON.\n"
    "Always return valid JSON. Standardize lab markers to: HbA1c, BP, LDL, eGFR, Glucose.\n\n"
    "OUTPUT RULES — follow these exactly:\n"
    "1. Output null for ANY field not explicitly stated in the query. Never invent values.\n"
    "2. 'gender' must be exactly 'male', 'female', or null. NEVER output combined values like 'male|female' or 'both'.\n"
    "3. 'age_range': only set min/max when the query states a specific age bound. Otherwise output null for each.\n"
    "4. 'patient_id': only set when the query contains an ID like P001, P023, etc. Otherwise null.\n"
    "5. 'patient_name': only set when a specific person's name is mentioned. Otherwise null.\n"
    "6. 'lab_filters': only populate when query mentions a specific lab marker + threshold. Otherwise empty [].\n"
    "7. 'medications': only populate when a specific drug name is mentioned. Otherwise empty [].\n"
    "8. 'diagnoses': only populate when a specific disease or condition (like diabetes, hypertension, asthma) is mentioned. Otherwise empty []."
)

SCHEMA_PROMPT = """Return JSON with null for any field not present in the query:
{{
  "primary_intent": "one of: [patient_lookup, medication_query, lab_query, patient_summary, clinical_notes, population_query]",
  "entities": {{
    "patient_id": null,
    "patient_name": null,
    "diagnoses": [],
    "lab_filters": [{{"marker": null, "operator": "> | < | >= | <= | == | !=", "value": null}}],
    "medications": [],
    "age_range": {{"min": null, "max": null}},
    "gender": null
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

        # 1. Clean keys recursively (strip whitespace and stray quotes)
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

        # 3. Extract entities
        entities = data.get("entities", {})
        if not isinstance(entities, dict):
            entities = {}

        # 4. Clean up empty lab_filters (remove entries where marker is null)
        lab_filters = entities.get("lab_filters", [])
        if isinstance(lab_filters, list):
            entities["lab_filters"] = [
                lf for lf in lab_filters
                if isinstance(lf, dict) and lf.get("marker") and lf.get("value") is not None
            ]

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
