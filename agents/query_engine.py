"""
agents/query_engine.py

LLM-powered structured query engine over the hospital SQL database.

Three public entry points:
  - parse_query_to_intent(query)  → Dict (structured JSON from LLM)
  - route_intent(intent_json)     → uniform result envelope
  - aggregate_patients(intent)    → Dict with count/avg/sum/min/max

SAFETY: No raw SQL is ever generated. All queries use SQLAlchemy ORM only.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from openai import OpenAI
from dotenv import load_dotenv

from data.database import (
    get_db_session,
    Patient, Medication, Diagnosis, LabResult,
)
from agents.patient_data_agent import (
    filter_patients,
    find_patient,
    find_extreme_lab_cases,
    serialize_patient,
)

load_dotenv()

# ── LLM Client ──────────────────────────────────────────────────────────────────

OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL       = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")


def _get_llm_client() -> OpenAI:
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in environment.")
    return OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)


# ── Intent Schema ───────────────────────────────────────────────────────────────

INTENT_SCHEMA = {
    "intent": "filter | aggregation | extreme | lookup",
    "filters": {
        "patient_id":   None,
        "patient_name": None,
        "gender":       None,
        "age_range":    {"min": None, "max": None},
        "medications":  [],
        "diagnoses":    [],
        "lab_filters":  [
            {"marker": None, "operator": "> | < | >= | <= | = | !=", "value": None}
        ],
    },
    "aggregation": {
        "type":     "count | avg | sum | min | max",
        "field":    "age | lab_value",
        "group_by": None,
    },
    "extreme": {
        "type":  "top | bottom",
        "field": "lab_value",
        "marker": None,
        "top_n": 5,
    },
}

_SYSTEM_PROMPT = (
    "You are a medical data query parser.\n"
    "Convert the user query into structured JSON matching the schema exactly.\n"
    "Rules:\n"
    "- Identify intent: filter, aggregation, extreme, or lookup\n"
    "- Extract filters (age, gender, medications, diagnosis, lab markers)\n"
    "- Extract aggregation if present (count, average, sum, min, max)\n"
    "- Extract extreme queries (top N, highest, lowest) — always include 'marker'\n"
    "- Standardise lab marker names to: HbA1c, BP, LDL, eGFR, Glucose, Cholesterol\n"
    "- Only return valid JSON. No explanations.\n"
    f"Schema:\n{json.dumps(INTENT_SCHEMA, indent=2)}"
)


# ── Step 1: LLM Intent Parser ───────────────────────────────────────────────────

def parse_query_to_intent(query: str) -> Dict:
    """
    Use the LLM to convert a natural language query into a structured intent dict.

    Returns a validated dict matching INTENT_SCHEMA.
    On any failure, returns a safe fallback with intent='filter' and empty filters.
    """
    client = _get_llm_client()
    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": f"User Query:\n{query}"},
            ],
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content

        # Strip markdown code fences if the model wraps its response
        raw = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
        raw = re.sub(r"```\s*$", "", raw.strip(), flags=re.MULTILINE)

        data = json.loads(raw)
        return _validate_intent(data)

    except Exception as e:
        print(f"[query_engine] parse_query_to_intent failed: {e}")
        return _empty_intent()


def _validate_intent(data: Dict) -> Dict:
    """Ensure all required keys are present with sane defaults."""
    intent = data.get("intent", "filter")
    if intent not in {"filter", "aggregation", "extreme", "lookup"}:
        intent = "filter"

    filters = data.get("filters", {})
    if not isinstance(filters, dict):
        filters = {}
    filters.setdefault("patient_id",   None)
    filters.setdefault("patient_name", None)
    filters.setdefault("gender",       None)
    filters.setdefault("age_range",    {})
    filters.setdefault("medications",  [])
    filters.setdefault("diagnoses",    [])
    filters.setdefault("lab_filters",  [])

    agg = data.get("aggregation", {})
    if not isinstance(agg, dict):
        agg = {}

    extreme = data.get("extreme", {})
    if not isinstance(extreme, dict):
        extreme = {}

    return {
        "intent":      intent,
        "filters":     filters,
        "aggregation": agg,
        "extreme":     extreme,
    }


def _empty_intent() -> Dict:
    return {
        "intent":      "filter",
        "filters":     {
            "patient_id": None, "patient_name": None, "gender": None,
            "age_range": {}, "medications": [], "diagnoses": [], "lab_filters": [],
        },
        "aggregation": {},
        "extreme":     {},
    }


# ── Shared Filter Builder (no duplicate joins, no raw SQL) ──────────────────────

def _build_filtered_query(base_query, filters: Dict, joined: set):
    """
    Apply all filter criteria to a SQLAlchemy query object.

    Uses a `joined` set to prevent duplicate table joins when multiple
    filters target the same related table.

    Args:
        base_query: SQLAlchemy Query object to augment
        filters:    dict of filter criteria from the intent
        joined:     mutable set tracking which tables are already joined

    Returns:
        The augmented query object (no .all() called yet)
    """
    # 1. Patient ID
    pid = filters.get("patient_id")
    if pid and str(pid).upper() not in {"PXXX", "P000", "NONE", "NULL"}:
        base_query = base_query.filter(Patient.patient_id.ilike(pid.strip()))

    # 2. Patient name
    pname = filters.get("patient_name")
    if pname and str(pname).lower().strip() not in {"name", "full name", "none", "null"}:
        base_query = base_query.filter(Patient.name.ilike(f"%{pname.strip()}%"))

    # 3. Gender
    if filters.get("gender"):
        base_query = base_query.filter(Patient.gender.ilike(filters["gender"].strip()))

    # 4. Age range
    age_range = filters.get("age_range") or {}
    if isinstance(age_range, dict):
        if age_range.get("min") is not None:
            base_query = base_query.filter(Patient.age >= int(age_range["min"]))
        if age_range.get("max") is not None:
            base_query = base_query.filter(Patient.age <= int(age_range["max"]))

    # 5. Medications — join once only
    meds = [m for m in (filters.get("medications") or []) if m]
    if meds:
        if "medications" not in joined:
            base_query = base_query.join(Medication, Patient.patient_id == Medication.patient_id)
            joined.add("medications")
        for med in meds:
            base_query = base_query.filter(Medication.med_name.ilike(f"%{med}%"))

    # 6. Diagnoses — join once only
    diagnoses = [d for d in (filters.get("diagnoses") or []) if d]
    if diagnoses:
        if "diagnoses" not in joined:
            base_query = base_query.join(Diagnosis, Patient.patient_id == Diagnosis.patient_id)
            joined.add("diagnoses")
        for diag in diagnoses:
            base_query = base_query.filter(Diagnosis.diagnosis_name.ilike(f"%{diag}%"))

    # 7. Lab filters — join once only, then chain .filter() per rule
    lab_filters = filters.get("lab_filters") or []
    valid_ops = {">", ">=", "<", "<=", "=", "==", "!="}
    for lf in lab_filters:
        marker = lf.get("marker")
        op     = lf.get("operator", "")
        value  = lf.get("value")
        if not marker or op not in valid_ops or value is None:
            continue
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue

        if "labs" not in joined:
            base_query = base_query.join(LabResult, Patient.patient_id == LabResult.patient_id)
            joined.add("labs")

        base_query = base_query.filter(LabResult.marker.ilike(marker))

        op_map = {
            ">":  LabResult.value.__gt__,
            ">=": LabResult.value.__ge__,
            "<":  LabResult.value.__lt__,
            "<=": LabResult.value.__le__,
            "=":  LabResult.value.__eq__,
            "==": LabResult.value.__eq__,
            "!=": LabResult.value.__ne__,
        }
        base_query = base_query.filter(op_map[op](value))

    return base_query


# ── Step 4: Aggregation Handler ─────────────────────────────────────────────────

_AGG_FUNC_MAP = {
    "count": func.count,
    "avg":   func.avg,
    "sum":   func.sum,
    "min":   func.min,
    "max":   func.max,
}


def aggregate_patients(intent: Dict, session: Session = None) -> Dict:
    """
    Apply filters then aggregate using SQLAlchemy func expressions.

    Supports:
      - count patients
      - avg / sum / min / max on Patient.age or LabResult.value
      - optional GROUP BY on Patient.gender or Patient.age

    Returns:
      {"result": value_or_list, "metadata": {"filters_applied": ..., "aggregation": ...}}
    """
    db = session or get_db_session()
    filters    = intent.get("filters", {})
    agg        = intent.get("aggregation", {})
    agg_type   = str(agg.get("type", "count")).lower()
    agg_field  = str(agg.get("field", "")).lower()
    group_by   = agg.get("group_by")

    agg_func = _AGG_FUNC_MAP.get(agg_type, func.count)

    try:
        joined: set = set()

        # Decide what column to aggregate over
        if agg_field == "lab_value":
            # Ensure labs are joined
            if "labs" not in joined:
                # We need the lab marker from lab_filters to be meaningful
                base_col = LabResult.value
                agg_col  = agg_func(base_col).label("result")
            else:
                base_col = LabResult.value
                agg_col  = agg_func(base_col).label("result")
        elif agg_field == "age":
            base_col = Patient.age
            agg_col  = agg_func(base_col).label("result")
        else:
            # Default: count distinct patients
            agg_col  = func.count(Patient.patient_id.distinct()).label("result")

        # Build GROUP BY columns
        group_col = None
        if group_by:
            gb = str(group_by).lower()
            if gb == "gender":
                group_col = Patient.gender
            elif gb == "age":
                group_col = Patient.age

        # Construct query
        select_cols = [agg_col]
        if group_col is not None:
            select_cols = [group_col, agg_col]

        query = db.query(*select_cols)

        # If we need lab aggregation and labs not yet joined
        if agg_field == "lab_value" and "labs" not in joined:
            query = query.join(LabResult, Patient.patient_id == LabResult.patient_id)
            joined.add("labs")

        # Apply filters
        query = _build_filtered_query(query, filters, joined)

        if group_col is not None:
            query = query.group_by(group_col)
            rows = query.all()
            result = [{"group": r[0], "value": _safe_round(r[1])} for r in rows]
        else:
            row    = query.first()
            result = _safe_round(row[0]) if row else 0

        return {
            "result": result,
            "metadata": {
                "filters_applied": _summarise_filters(filters),
                "aggregation": agg,
            },
        }

    except Exception as e:
        print(f"[query_engine] aggregate_patients error: {e}")
        return {
            "result":   None,
            "error":    str(e),
            "metadata": {"filters_applied": _summarise_filters(filters), "aggregation": agg},
        }
    finally:
        if not session:
            db.close()


# ── Step 3: Router ───────────────────────────────────────────────────────────────

def route_intent(intent_json: Dict) -> Dict:
    """
    Dispatch a parsed intent dict to the correct handler and return a
    uniform result envelope:

        {"result": ..., "metadata": {"filters_applied": ..., ...}}

    Intent values:
        "filter"      → filter_patients()
        "lookup"      → find_patient()
        "extreme"     → find_extreme_lab_cases()
        "aggregation" → aggregate_patients()
    """
    intent  = intent_json.get("intent", "filter")
    filters = intent_json.get("filters", {})
    extreme = intent_json.get("extreme", {})

    try:
        if intent == "lookup":
            patients = find_patient(
                patient_id=filters.get("patient_id"),
                name=filters.get("patient_name"),
            )
            return {
                "result":   patients,
                "metadata": {"filters_applied": _summarise_filters(filters), "intent": intent},
            }

        elif intent == "filter":
            # Remap query_engine filter schema → patient_data_agent entities schema
            entities = _filters_to_entities(filters)
            patients = filter_patients(entities)
            return {
                "result":   patients,
                "metadata": {"filters_applied": _summarise_filters(filters), "intent": intent},
            }

        elif intent == "extreme":
            marker = extreme.get("marker") or _first_lab_marker(filters)
            top_n  = int(extreme.get("top_n") or 5)
            order  = "asc" if str(extreme.get("type", "top")).lower() == "bottom" else "desc"
            cases  = find_extreme_lab_cases(marker=marker or "HbA1c", top_n=top_n, order=order)
            return {
                "result":   cases,
                "metadata": {
                    "filters_applied": _summarise_filters(filters),
                    "intent":  intent,
                    "marker":  marker,
                    "top_n":   top_n,
                    "order":   order,
                },
            }

        elif intent == "aggregation":
            return aggregate_patients(intent_json)

        else:
            return {"result": None, "error": f"Unknown intent: '{intent}'", "metadata": {}}

    except Exception as e:
        print(f"[query_engine] route_intent error: {e}")
        return {"result": None, "error": str(e), "metadata": {"intent": intent}}


# ── Public End-to-End Helper ─────────────────────────────────────────────────────

def run_query(query: str) -> Dict:
    """
    Parse a natural language query, route it, and return the result.
    Single entry point for external callers.
    """
    intent_json = parse_query_to_intent(query)
    result      = route_intent(intent_json)
    result["parsed_intent"] = intent_json
    return result


# ── Internal Utilities ───────────────────────────────────────────────────────────

def _filters_to_entities(filters: Dict) -> Dict:
    """Translate query_engine filter keys → patient_data_agent entities keys."""
    return {
        "patient_id":   filters.get("patient_id"),
        "patient_name": filters.get("patient_name"),
        "gender":       filters.get("gender"),
        "age_range":    filters.get("age_range") or {},
        "medications":  filters.get("medications") or [],
        "diagnoses":    filters.get("diagnoses") or [],
        "lab_filters":  [
            {
                "marker":   lf.get("marker"),
                "operator": lf.get("operator"),
                "value":    lf.get("value"),
            }
            for lf in (filters.get("lab_filters") or [])
        ],
    }


def _first_lab_marker(filters: Dict) -> Optional[str]:
    """Extract the first lab marker mentioned in filters, if any."""
    for lf in (filters.get("lab_filters") or []):
        if lf.get("marker"):
            return lf["marker"]
    return None


def _summarise_filters(filters: Dict) -> Dict:
    """Return a compact, human-readable summary of applied filters."""
    summary: Dict[str, Any] = {}
    if filters.get("patient_id"):   summary["patient_id"]   = filters["patient_id"]
    if filters.get("patient_name"): summary["patient_name"] = filters["patient_name"]
    if filters.get("gender"):       summary["gender"]       = filters["gender"]
    ar = filters.get("age_range") or {}
    if ar.get("min") is not None or ar.get("max") is not None:
        summary["age_range"] = ar
    if filters.get("medications"):  summary["medications"]  = filters["medications"]
    if filters.get("diagnoses"):    summary["diagnoses"]    = filters["diagnoses"]
    if filters.get("lab_filters"):  summary["lab_filters"]  = filters["lab_filters"]
    return summary


def _safe_round(value: Any, decimals: int = 2) -> Any:
    """Round floats for display; pass through int/None/str unchanged."""
    if isinstance(value, float):
        return round(value, decimals)
    return value
