"""
agents/patient_data_agent.py
Structured retrieval from the SINGLE patients table.
Simplified for flat-table architecture.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from data.database import (
    get_db_session,
    Patient,
)

# ── Retrieval Logic ─────────────────────────────────────────────────────────────

def find_patient(patient_id: Optional[str] = None, name: Optional[str] = None, session: Session = None, return_query: bool = False) -> Any:
    """Look up patient from the single patients table."""
    db = session or get_db_session()
    try:
        query = db.query(Patient)
        if patient_id:
            query = query.filter(Patient.patient_id.ilike(patient_id.strip()))
        if name:
            query = query.filter(Patient.name.ilike(f"%{name.strip()}%"))

        if return_query:
            return query

        results = query.all()
        return [serialize_patient(p) for p in results]
    finally:
        if not session and not return_query: db.close()


def filter_patients(entities: Dict, lightweight: bool = False, session: Session = None) -> List[Dict]:
    """Apply structured filters to the patients table."""
    db = session or get_db_session()
    try:
        query = db.query(Patient)

        # 1. Identity Filters
        pid = entities.get("patient_id")
        if pid and pid.upper() not in ["PXXX", "P000", "NONE"]:
            query = query.filter(Patient.patient_id.ilike(pid.strip()))

        pname = entities.get("patient_name")
        if pname and pname.lower().strip() not in ["full name", "name", "none"]:
            query = query.filter(Patient.name.ilike(f"%{pname.strip()}%"))

        # 2. Demographic Filters
        raw_gender = (entities.get("gender") or "").strip().lower()
        if raw_gender in {"male", "female", "f", "m"}:
            g_val = "F" if raw_gender.startswith("f") else "M"
            query = query.filter(Patient.gender.ilike(g_val))

        age_range = entities.get("age_range")
        if age_range and isinstance(age_range, dict):
            age_min = age_range.get("min")
            age_max = age_range.get("max")
            if age_min is not None: query = query.filter(Patient.age >= int(age_min))
            if age_max is not None: query = query.filter(Patient.age <= int(age_max))

        # 3. Text-based Clinical Filters
        def _apply_text_filter(col, key):
            nonlocal query
            val = entities.get(key)
            if val and val.lower().strip() not in ["none", "all", "unknown"]:
                query = query.filter(col.ilike(f"%{val.strip()}%"))

        _apply_text_filter(Patient.primary_diagnosis, "primary_diagnosis")
        _apply_text_filter(Patient.nationality, "nationality")
        _apply_text_filter(Patient.bmi_category, "bmi_category")
        _apply_text_filter(Patient.procedure,    "procedure")
        _apply_text_filter(Patient.complications,"complications")
        _apply_text_filter(Patient.mi_type,      "mi_type")
        _apply_text_filter(Patient.icu_admission, "icu_admission")
        _apply_text_filter(Patient.outcome,      "outcome")

        results = query.all()
        return [serialize_patient(p, lightweight=lightweight) for p in results]

    finally:
        if not session: db.close()


def get_all_patients(lightweight: bool = True, session: Session = None) -> List[Dict]:
    """Return all patients from the single table."""
    db = session or get_db_session()
    try:
        query = db.query(Patient)
        patients = query.all()
        return [serialize_patient(p, lightweight=lightweight) for p in patients]
    finally:
        if not session: db.close()


# ── Serialization ────────────────────────────────────────────────────────────────

def serialize_patient(p: Patient, lightweight: bool = False) -> Dict:
    """Convert Patient ORM to dictionary. All clinical data is now local to the model."""
    data = {
        "patient_id":   p.patient_id,
        "episode_id":   p.episode_id,
        "name":         p.name,
        "age":          p.age,
        "gender":       p.gender,
        "nationality":  p.nationality,
        "admission_date": p.admission_date,
        "primary_diagnosis": p.primary_diagnosis,
        "mi_type":      p.mi_type,
        "icu_admission": p.icu_admission,
        "outcome":       p.outcome,
    }
    
    if not lightweight:
        data.update({
            "discharge_date": p.discharge_date,
            "length_of_stay": p.length_of_stay,
            "risk_factors": {
                "smoking": p.risk_smoking,
                "hypertension": p.risk_hypertension,
                "diabetes": p.risk_diabetes,
                "bmi": p.bmi_category
            },
            "procedure":     p.procedure,
            "complications": p.complications,
            "death_flag":    p.death_flag,
            "doctor_notes": p.doctor_notes,
            "visit_history": p.visit_history,
        })
    return data
