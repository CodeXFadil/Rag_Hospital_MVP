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
    Patient,
)
from agents.patient_data_agent import (
    filter_patients,
    find_patient,
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


DERIVED_RULES = {
    "heart failure": {"primary_diagnosis": "Heart Failure"},
    "angina":        {"primary_diagnosis": "Angina"},
    "high hba1c":    {"lab_filters": [{"marker": "HbA1c", "operator": ">", "value": 6.5}]},
    "stemi":         {"mi_type": "STEMI"},
    "nstemi":        {"mi_type": "NSTEMI"},
    "obese":         {"bmi_category": "Obese"},
    "elderly":       {"age_range": {"min": 65, "max": 120}},
}


INTENT_SCHEMA = {
    "intents": ["filter", "aggregation", "extreme", "lookup"], 
    "filters": {
        "patient_id":   None,
        "patient_name": None,
        "gender":       None,
        "age_range":    {"min": None, "max": None},
        "primary_diagnosis": None,  
        "mi_type":      None,        # STEMI | NSTEMI
        "icu_admission": None,       # Yes | No
        "outcome":      None,        # Discharged | Deceased
        "death_flag":   None,        # 1 (Deceased) | 0 (Discharged)
        "admission_year": None,
        "nationality":  None,
        "bmi_category": None,
        "procedure":    None,
        "risk_smoking": None,
        "risk_hypertension": None,
        "risk_diabetes": None,
    },
    "aggregations": [
        {
            "type":     "count | avg | sum | min | max",
            "field":    "age | length_of_stay | death_flag",
            "group_by": "gender | age | outcome | year | nationality | bmi_category | procedure | mi_type | primary_diagnosis | icu_admission",
        }
    ],
    "extreme": {
        "type":  "top | bottom",
        "field": "age | length_of_stay",
        "top_n": 5,
    },
}

_SYSTEM_PROMPT = (
    "You are a Clinical Data Assistant. The dataset is a SINGLE TABLE called 'patients'.\n"
    "- Identify ALL intents: filter, aggregation, extreme, or lookup\n"
    "- All clinical data (diagnoses, procedures, risk factors) are columns in the 'patients' table.\n"
    "- Use 'primary_diagnosis' for main clinical conditions.\n"
    "- Use 'death_flag' for mortality (avg = rate).\n"
    "- Only return valid JSON.\n"
    f"Schema:\n{json.dumps(INTENT_SCHEMA, indent=2)}"
)



def parse_query_to_intent(query: str) -> Dict:
    """End-to-end intent processing: Parse -> Normalize -> Validate."""
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
            max_tokens=600,
        )
        raw = response.choices[0].message.content
        raw = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
        raw = re.sub(r"```\s*$", "", raw.strip(), flags=re.MULTILINE)

        data = json.loads(raw)
        
        # New Pipeline: Normalize then Validate
        normalized = normalize_intent(data, query)
        validated  = _validate_intent(normalized)
        return compact_intent(validated)

    except Exception as e:
        print(f"[query_engine] parse_query_to_intent failed: {e}")
        return _empty_intent()


def compact_intent(data: Any) -> Any:
    """Recursively remove None, [], and {} values for a cleaner UI view."""
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            compact_v = compact_intent(v)
            if compact_v is not None and compact_v != [] and compact_v != {}:
                new_dict[k] = compact_v
        return new_dict
    elif isinstance(data, list):
        new_list = [compact_intent(v) for v in data]
        return [v for v in new_list if v is not None and v != [] and v != {}]
    else:
        return data


def normalize_intent(intent: Dict, query: str) -> Dict:
    """
    Apply clinical rules, fill defaults, and clean up ambiguous LLM output.
    """
    q_lower = query.lower()
    
    # Ensure filters exists and is a dict
    if "filters" not in intent or not isinstance(intent["filters"], dict):
        intent["filters"] = {}
    filters = intent["filters"]
    
    # 0. Basic Normalization (Gender)
    g = str(filters.get("gender", "")).lower()

    # 1. Check for explicit MI subtypes in the query text
    if "stemi" in q_lower and "nstemi" not in q_lower:
        filters["mi_type"] = "STEMI"
    elif "nstemi" in q_lower:
        filters["mi_type"] = "NSTEMI"
    
    # 2. Handle heart attack synonyms
    if "heart attack" in q_lower or "infarction" in q_lower or " mi " in f" {q_lower} ":
        if not filters.get("primary_diagnosis"):
            filters["primary_diagnosis"] = "Myocardial Infarction"
    if "female" in g or g == "f": filters["gender"] = "F"
    elif "male" in g or g == "m":  filters["gender"] = "M"

    # 1. Apply Derived Rules

    for term, rules in DERIVED_RULES.items():
        if term in q_lower:
            # Merge rules into filters
            if "primary_diagnosis" in rules:
                filters["primary_diagnosis"] = rules["primary_diagnosis"]
                # If we found a primary diagnosis, the LLM-extracted list is likely redundant/wrong
                filters["diagnoses"] = [] 
            if "mi_type" in rules:
                filters["mi_type"] = rules["mi_type"]
            if "diagnoses" in rules:
                existing = filters.setdefault("diagnoses", [])
                for d in rules["diagnoses"]:
                    if d not in existing: existing.append(d)
            if "lab_filters" in rules:
                existing = filters.setdefault("lab_filters", [])
                existing.extend(rules["lab_filters"])
            if "age_range" in rules:
                filters["age_range"] = rules["age_range"]
            if "bmi_category" in rules:
                filters["bmi_category"] = rules["bmi_category"]

    # 1c. Risk factor and outcome keyword extraction
    if "smoker" in q_lower or "smoking" in q_lower:
        filters["risk_smoking"] = "Yes"
        if "how many" in q_lower or "count" in q_lower:
            intent.setdefault("aggregations", []).append({"type": "count", "field": "patient_id"})
            if "aggregation" not in intent.get("intents", []):
                intent.setdefault("intents", []).append("aggregation")
    if "dm" in q_lower or "diabetes" in q_lower:
        filters["risk_diabetes"] = "Yes"
        if "how many" in q_lower or "count" in q_lower:
            intent.setdefault("aggregations", []).append({"type": "count", "field": "patient_id"})
    if "hypertension" in q_lower or " htn " in f" {q_lower} ":
        filters["risk_hypertension"] = "Yes"
        if "how many" in q_lower or "count" in q_lower:
            intent.setdefault("aggregations", []).append({"type": "count", "field": "patient_id"})
    if "death" in q_lower or "fatal" in q_lower or "died" in q_lower:
        filters["death_flag"] = 1
    if "icu" in q_lower:
        filters["icu_admission"] = "Yes"
    if "complications" in q_lower:
        filters["complications"] = "Yes"

    # 1d. Length of Stay extraction (e.g., "over 10 days")
    import re
    los_match = re.search(r"(?:over|more than|longer than|>)\s*(\d+)\s*days", q_lower)
    if los_match:
        filters["length_of_stay"] = {"min": int(los_match.group(1))}
    else:
        los_exact = re.search(r"exactly\s*(\d+)\s*days", q_lower)
        if los_exact:
            filters["length_of_stay"] = int(los_exact.group(1))

    # 3. Ensure intents is a list
    intents_list = intent.get("intents", [])
    if "intent" in intent and not intents_list:
        intents_list = [intent["intent"]]
    
    # 4. Global Analytics fallback
    if "analytics_query" in intents_list or intent.get("primary_intent") == "analytics_query":
        if not intent.get("aggregations"):
            intent["aggregations"] = [{"type": "count", "field": "patient_id"}]
        if "aggregation" not in intents_list:
            intents_list.append("aggregation")

    intent["intents"] = intents_list
    if not intent["intents"]:
        intent["intents"] = ["filter"]

    return intent


def _validate_intent(data: Dict) -> Dict:
    """Verify structure without silent destructive overrides."""
    if not isinstance(data.get("intents"), list):
        return {"error": "Invalid intent format", "raw": data}

    filters = data.setdefault("filters", {})
    filters.setdefault("patient_id",   None)
    filters.setdefault("patient_name", None)
    filters.setdefault("medications",  [])
    filters.setdefault("diagnoses",    [])
    filters.setdefault("lab_filters",  [])

    aggs = data.setdefault("aggregations", [])
    if not isinstance(aggs, list):
        data["aggregations"] = []

    return data


def _empty_intent() -> Dict:
    return {
        "intents": ["filter"],
        "filters": {
            "patient_id": None, "patient_name": None, "gender": None,
            "age_range": {}, "medications": [], "diagnoses": [], "lab_filters": [],
            "outcome": None, "admission_year": None,
            "nationality": None, "bmi_category": None, "procedure": None, "mi_type": None,
            "icu_admission": None, "risk_smoking": None, "risk_hypertension": None, 
            "risk_diabetes": None, "death_flag": None, "length_of_stay": None,
            "complications": None
        },
        "aggregations": [],
        "extreme": {},
    }


# ── Shared Filter Builder (no duplicate joins, no raw SQL) ──────────────────────

def _get_required_joins(filters: Dict, aggregations: List[Dict]) -> set:
    """Determine which tables must be joined. Now always empty for single-table."""
    return set()


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
        g = str(filters["gender"]).strip().lower()
        if g.startswith("f"): 
            gender_val = "F"
        elif g.startswith("m"): 
            gender_val = "M"
        else: 
            gender_val = g
        base_query = base_query.filter(Patient.gender.ilike(gender_val))

    # 4. Age range
    age_range = filters.get("age_range") or {}
    if isinstance(age_range, dict):
        if age_range.get("min") is not None:
            base_query = base_query.filter(Patient.age >= int(age_range["min"]))
        if age_range.get("max") is not None:
            base_query = base_query.filter(Patient.age <= int(age_range["max"]))

    # 4b. Outcome and Admission Year
    if filters.get("outcome"):
        base_query = base_query.filter(Patient.outcome.ilike(filters["outcome"].strip()))
    if filters.get("admission_year"):
        year_str = str(filters["admission_year"]).strip()
        base_query = base_query.filter(Patient.admission_date.like(f"{year_str}-%"))
    
    # 4c. New Excel Fields
    def _to_yes_no(val):
        if val is None: return None
        s = str(val).strip().lower()
        if s in {"true", "1", "yes", "y", "t"}: return "Yes"
        if s in {"false", "0", "no", "n", "f"}: return "No"
        return val

    if filters.get("primary_diagnosis"):
        base_query = base_query.filter(Patient.primary_diagnosis.ilike(f"%{filters['primary_diagnosis'].strip()}%"))
    if filters.get("nationality"):
        base_query = base_query.filter(Patient.nationality.ilike(filters["nationality"].strip()))
    if filters.get("bmi_category"):
        base_query = base_query.filter(Patient.bmi_category.ilike(filters["bmi_category"].strip()))
    if filters.get("procedure"):
        base_query = base_query.filter(Patient.procedure.ilike(filters["procedure"].strip()))
    if i_type := filters.get("mi_type"):
        base_query = base_query.filter(Patient.mi_type.ilike(str(i_type).strip()))
    if icu := filters.get("icu_admission"):
        base_query = base_query.filter(Patient.icu_admission.ilike(_to_yes_no(icu)))
    if (d_flag := filters.get("death_flag")) is not None:
        base_query = base_query.filter(Patient.death_flag == int(d_flag))
    if comp := filters.get("complications"):
        base_query = base_query.filter(Patient.complications.ilike(_to_yes_no(comp)))
    
    # 4d. Length of Stay
    los = filters.get("length_of_stay")
    if isinstance(los, dict):
        if los.get("min") is not None:
            base_query = base_query.filter(Patient.length_of_stay >= int(los["min"]))
        if los.get("max") is not None:
            base_query = base_query.filter(Patient.length_of_stay <= int(los["max"]))
    elif los is not None:
        try:
            base_query = base_query.filter(Patient.length_of_stay == int(los))
        except: pass

    # 4e. Risk Factors
    if r_smoke := filters.get("risk_smoking"):
        base_query = base_query.filter(Patient.risk_smoking.ilike(_to_yes_no(r_smoke)))
    if r_hyper := filters.get("risk_hypertension"):
        base_query = base_query.filter(Patient.risk_hypertension.ilike(_to_yes_no(r_hyper)))
    if r_diabetes := filters.get("risk_diabetes"):
        base_query = base_query.filter(Patient.risk_diabetes.ilike(_to_yes_no(r_diabetes)))


    # 5. Lab filters removed (No labs table)
    # 6. Medications/Diagnoses are handled as direct clinical columns in Patient

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
    Refactored to support MULTIPLE aggregations in a single SQL query.
    Returns: {"result": {metric1: val, metric2: val}, "metadata": {...}}
    """
    db = session or get_db_session()
    filters = intent.get("filters", {})
    aggs    = intent.get("aggregations", [])
    if not aggs:
        return {"result": 0, "metadata": {"status": "no aggregations requested"}}

    try:
        joined: set = _get_required_joins(filters, aggs)
        active_joins: set = set()
        
        # 1. Build the Selection List + Group By
        select_cols = []
        group_col = None
        
        # We only support ONE group_by for now (from the first aggregation that has it)
        main_gb = next((a.get("group_by") for a in aggs if a.get("group_by")), None)
        if main_gb:
            gb = str(main_gb).lower()
            if gb == "gender":       group_col = Patient.gender
            elif gb == "age":        group_col = Patient.age
            elif gb == "outcome":    group_col = Patient.outcome
            elif gb == "nationality": group_col = Patient.nationality
            elif gb == "mi_type":     group_col = Patient.mi_type
            elif gb == "bmi_category": group_col = Patient.bmi_category
            elif gb in ["length_of_stay", "los"]: group_col = Patient.length_of_stay
            elif gb == "complications": group_col = Patient.complications
            elif gb == "icu_admission": group_col = Patient.icu_admission
            elif gb == "admission_year": group_col = func.substr(Patient.admission_date, 1, 4)
            elif gb == "nationality": group_col = Patient.nationality
            elif gb == "bmi_category":group_col = Patient.bmi_category
            elif gb == "procedure":   group_col = Patient.procedure
            elif gb == "mi_type":     group_col = Patient.mi_type
            elif gb == "complications":group_col = Patient.complications
            elif gb == "diagnosis":   group_col = Diagnosis.diagnosis_name
            elif gb == "primary_diagnosis": group_col = Patient.primary_diagnosis
            elif gb == "icu_admission":     group_col = Patient.icu_admission
            elif gb in ["year", "admission_year"]:
                group_col = func.substr(Patient.admission_date, 1, 4)
            
            if group_col is not None:
                select_cols.append(group_col)

        # 2. Map Metrics to SQL Columns
        for i, agg in enumerate(aggs):
            a_type  = str(agg.get("type", "count")).lower()
            a_field = str(agg.get("field", "")).lower()
            a_func  = _AGG_FUNC_MAP.get(a_type, func.count)
            
            # Label the column uniquely for extraction
            label = f"metric_{i}"
            
            if a_field == "lab_value":
                col = a_func(LabResult.value).label(label)
            elif a_field == "age" and a_type != "count":
                col = a_func(Patient.age).label(label)
            elif a_field == "length_of_stay":
                col = a_func(Patient.length_of_stay).label(label)
            elif a_field == "death_flag":
                col = a_func(Patient.death_flag).label(label)
            else:
                # Default to counting distinct patients
                col = func.count(Patient.patient_id.distinct()).label(label)
                # Force field name to 'patients' for cleaner output keys if it was 'patients' or ambiguous
                if a_field in ["", "none", "null", "age", "name"]:
                    agg["field"] = "patients"
            
            select_cols.append(col)

        # 3. Create query and apply Joins
        query = db.query(*select_cols).select_from(Patient)
        if "medications" in joined:
            query = query.join(Medication, Patient.patient_id == Medication.patient_id)
            active_joins.add("medications")
        if "diagnoses" in joined:
            query = query.join(Diagnosis, Patient.patient_id == Diagnosis.patient_id)
            active_joins.add("diagnoses")
        if "labs" in joined:
            query = query.join(LabResult, Patient.patient_id == LabResult.patient_id)
            active_joins.add("labs")

        # 4. Apply Filters using standard logic
        query = _build_filtered_query(query, filters, active_joins)

        # 5. Execute and Format
        if group_col is not None:
            query = query.group_by(group_col)
            sql_str = _compile_query(query)
            rows = query.all()
            
            final_result = []
            for r in rows:
                metrics = {}
                for i, agg in enumerate(aggs):
                    label = f"metric_{i}"
                    val = r[i+1]
                    field = agg.get('field', 'patients')
                    metrics[f"{agg['type']}_{field}"] = _safe_round(val)
                final_result.append({"group": r[0], "metrics": metrics})
        else:
            sql_str = _compile_query(query)
            row = query.first()
            final_result = {}
            for i, agg in enumerate(aggs):
                val = row[i] if row else 0
                field = agg.get('field', 'patients')
                final_result[f"{agg['type']}_{field}"] = _safe_round(val)


        return {
            "result": final_result,
            "metadata": {
                "filters_applied": _summarise_filters(filters),
                "aggregations": aggs,
                "joins": list(active_joins),
                "sql": sql_str
            },
        }


    except Exception as e:
        import traceback
        print(f"[query_engine] aggregate_patients error: {e}")
        print(traceback.format_exc())
        return {"result": None, "error": str(e)}
    finally:
        if not session: db.close()



# ── Step 3: Router ───────────────────────────────────────────────────────────────

def route_intent(intent_json: Dict) -> Dict:
    """
    Updated for MULTI-INTENT compatibility.
    Sequentially processes filter, extreme, and aggregation.
    """
    intents = intent_json.get("intents", ["filter"])
    filters = intent_json.get("filters", {})
    extreme = intent_json.get("extreme", {})
    
    # NEW: Log raw intent for transparency
    print(f"\n[INTENT DEBUG] Raw LLM Intent: {intent_json}\n", flush=True)
    
    if "error" in intent_json:
        return intent_json

    db = get_db_session()
    results = {}

    try:
        current_sql = []

        # Sequential Execution Logic
        # 1. Aggregation (Statistical metrics) - PRIORITIZE THIS for analytics
        if any(i in intents for i in ["aggregation", "analytics_query"]):
            agg_res = aggregate_patients(intent_json, session=db)
            results["aggregation"] = agg_res
            if agg_res.get("metadata", {}).get("sql"):
                if isinstance(agg_res["metadata"]["sql"], list):
                    current_sql.extend(agg_res["metadata"]["sql"])
                else:
                    current_sql.append(agg_res["metadata"]["sql"])

        # 2. Lookup (Independent)
        if "lookup" in intents:
            from agents.patient_data_agent import serialize_patient

        # 4. Extreme cases
        if "extreme" in intents:
            marker = extreme.get("marker") or _first_lab_marker(filters)
            top_n  = int(extreme.get("top_n") or 5)
            order  = "asc" if str(extreme.get("type", "top")).lower() == "bottom" else "desc"
            
            q = find_extreme_lab_cases(
                marker=marker or "HbA1c", 
                top_n=top_n, 
                order=order, 
                session=db,
                return_query=True
            )
            current_sql.append(_compile_query(q))
            
            # Execute and format
            from agents.patient_data_agent import serialize_patient
            results["extreme"] = []
            for p, val in q.all():
                ser = serialize_patient(p)
                ser["extracted_value"] = val
                results["extreme"].append(ser)

        return {
            "result":   results,
            "metadata": {
                "filters_applied": _summarise_filters(filters),
                "intents": intents,
                "sql": current_sql if current_sql else None
            }
        }

    except Exception as e:
        print(f"[query_engine] route_intent error: {e}")
        return {"result": None, "error": str(e), "metadata": {"intents": intents}}
    finally:
        db.close()




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
        "outcome":      filters.get("outcome"),
        "admission_year": filters.get("admission_year"),
        "nationality":  filters.get("nationality"),
        "bmi_category": filters.get("bmi_category"),
        "procedure":    filters.get("procedure"),
        "mi_type":      filters.get("mi_type"),
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
    if filters.get("primary_diagnosis"): summary["primary_diagnosis"] = filters["primary_diagnosis"]
    if filters.get("mi_type"):      summary["mi_type"]      = filters["mi_type"]
    if filters.get("outcome"):      summary["outcome"]      = filters["outcome"]
    if filters.get("admission_year"): summary["admission_year"] = filters["admission_year"]

    if filters.get("nationality"):  summary["nationality"]  = filters["nationality"]
    if filters.get("bmi_category"): summary["bmi_category"] = filters["bmi_category"]
    if filters.get("procedure"):    summary["procedure"]    = filters["procedure"]
    if filters.get("mi_type"):      summary["mi_type"]      = filters["mi_type"]
    if filters.get("lab_filters"):  summary["lab_filters"]  = filters["lab_filters"]

    return summary


def _safe_round(value: Any, decimals: int = 2) -> Any:
    """Round floats for display; pass through int/None/str unchanged."""
    if isinstance(value, float):
        return round(value, decimals)
    return value

def _compile_query(query) -> str:
    """Helper to convert a SQLAlchemy query object to a raw SQL string."""
    try:
        from sqlalchemy.dialects import sqlite
        sql = str(query.statement.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True}))
        print(f"\n[SQL DEBUG] Generated SQL:\n{sql}\n", flush=True)
        return sql
    except Exception as e:
        err = f"-- Error compiling SQL: {e}"
        print(f"\n[SQL DEBUG] {err}\n", flush=True)
        return err

