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

SYSTEM_PROMPT = (
    "You are a clinical query parser. Extract criteria into structured JSON. "
    "Always return valid JSON. Standardize markers to: HbA1c, BP, LDL, eGFR, Glucose."
)

SCHEMA_PROMPT = """Extract into JSON:
{{
  "primary_intent": "one of: [patient_lookup, medication_query, lab_query, patient_summary, clinical_notes, population_query]",
  "entities": {{
    "patient_id": "PXXX",
    "patient_name": "Name",
    "lab_filters": [{{"marker": "name", "operator": ">|<|==", "value": 0.0}}],
    "medications": [],
    "age_range": {{"min": 0, "max": 120}},
    "gender": "male|female"
  }}
}}
Query: {query}"""

def _get_llm_client() -> OpenAI:
    return OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)

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
        
        # 1. CLEAN KEYS RECURSIVELY
        def clean_obj(obj):
            if isinstance(obj, dict):
                return {k.strip().replace('"', '').replace("'", ""): clean_obj(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_obj(i) for i in obj]
            return obj

        data = clean_obj(data)
        
        # 2. EXTRACT INTENT
        raw_intent = data.get("primary_intent", FALLBACK_INTENT)
        # Validate intent
        final_intent = FALLBACK_INTENT
        for v in VALID_INTENTS:
            if v in str(raw_intent).lower():
                final_intent = v
                break
        
        # 3. GET ENTITIES
        entities = data.get("entities", {})
        if not isinstance(entities, dict): entities = {}
        
        return {
            "primary_intent": final_intent,
            "intents": [final_intent],
            "entities": entities,
            "extracted_patient_id": entities.get("patient_id"),
            "extracted_patient_name": entities.get("patient_name")
        }

    except Exception as e:
        print(f"ROUTER FALLBACK: {e}")
        return {
            "primary_intent": FALLBACK_INTENT,
            "intents": [FALLBACK_INTENT],
            "entities": {},
            "extracted_patient_id": None,
            "extracted_patient_name": None
        }
