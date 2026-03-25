"""
agents/patient_data_agent.py
Structured retrieval from the SQL database using SQLAlchemy relationships,
eager loading, and production-grade session management.

Models and DB setup live in data/database.py — import from there.
"""

from typing import Optional, List, Dict
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import func

from data.database import (
    get_db_session,
    Patient, Medication, Diagnosis, LabResult,
    # Re-exported so db_migration and other legacy callers still work
    Base, engine, SessionLocal,
)

# ── Retrieval Logic with Eager Loading ──────────────────────────────────────────

def find_patient(patient_id: Optional[str] = None, name: Optional[str] = None, session: Session = None) -> List[Dict]:
    """Look up patient with pre-loaded relationships to avoid N+1 queries."""
    db = session or get_db_session()
    try:
        query = db.query(Patient).options(
            joinedload(Patient.medications),
            joinedload(Patient.diagnoses),
            joinedload(Patient.lab_results)
        )
        if patient_id:
            query = query.filter(Patient.patient_id.ilike(patient_id.strip()))
        if name:
            query = query.filter(Patient.name.ilike(f"%{name.strip()}%"))

        results = query.all()
        return [serialize_patient(p) for p in results]
    finally:
        if not session: db.close()


def filter_patients(entities: Dict, session: Session = None) -> List[Dict]:
    """Apply multiple structured filters using optimized SQL JOINs."""
    db = session or get_db_session()
    try:
        query = db.query(Patient).options(
            joinedload(Patient.medications),
            joinedload(Patient.diagnoses),
            joinedload(Patient.lab_results)
        )

        # 1. Identity Filters
        pid = entities.get("patient_id")
        if pid and pid.upper() not in ["PXXX", "P000", "NONE"]:
            query = query.filter(Patient.patient_id.ilike(pid.strip()))

        pname = entities.get("patient_name")
        if pname and pname.lower().strip() not in ["full name", "name", "none"]:
            query = query.filter(Patient.name.ilike(f"%{pname.strip()}%"))

        # 2. Demographic Filters
        # Sanitize gender: only apply if it's a single valid value (not 'male|female' etc.)
        raw_gender = (entities.get("gender") or "").strip().lower()
        if raw_gender in {"male", "female"}:
            query = query.filter(Patient.gender.ilike(raw_gender))

        age_range = entities.get("age_range")
        if age_range and isinstance(age_range, dict):
            # Ignore the router's default placeholder of {min:0, max:120} — not a real filter
            age_min = age_range.get("min")
            age_max = age_range.get("max")
            if age_min is not None and int(age_min) > 0:
                query = query.filter(Patient.age >= int(age_min))
            if age_max is not None and int(age_max) < 120:
                query = query.filter(Patient.age <= int(age_max))

        # 3. Medication Filters (Optimized with JOIN)
        meds = entities.get("medications", [])
        if meds:
            for med in meds:
                query = query.join(Medication, Patient.patient_id == Medication.patient_id)\
                             .filter(Medication.med_name.ilike(f"%{med}%"))

        # 4. Lab Filters (Optimized with JOIN)
        lab_filters = entities.get("lab_filters", [])
        for f in lab_filters:
            marker = f.get("marker")
            op     = f.get("operator")
            target = f.get("value")
            if not marker or target is None:
                continue

            query = query.join(LabResult, Patient.patient_id == LabResult.patient_id)\
                         .filter(LabResult.marker.ilike(marker))

            if   op == ">":              query = query.filter(LabResult.value >  target)
            elif op == ">=":             query = query.filter(LabResult.value >= target)
            elif op == "<":              query = query.filter(LabResult.value <  target)
            elif op == "<=":             query = query.filter(LabResult.value <= target)
            elif op in ["==", "=", "!="]:
                if op == "!=":           query = query.filter(LabResult.value != target)
                else:                    query = query.filter(LabResult.value == target)

        results = query.all()
        return [serialize_patient(p) for p in results]
    finally:
        if not session: db.close()


def find_patients_by_lab_threshold(lab_marker: str, condition: str, threshold: float, session: Session = None) -> List[Dict]:
    """Helper for simple threshold queries (e.g. 'all patients with HbA1c above 8')."""
    db = session or get_db_session()
    try:
        query = db.query(Patient).join(LabResult).options(
            joinedload(Patient.medications),
            joinedload(Patient.diagnoses),
            joinedload(Patient.lab_results)
        ).filter(LabResult.marker.ilike(lab_marker))

        if condition == "above":
            query = query.filter(LabResult.value > threshold)
        else:
            query = query.filter(LabResult.value < threshold)

        return [serialize_patient(p) for p in query.all()]
    finally:
        if not session: db.close()


# ── Analytics Helpers ────────────────────────────────────────────────────────────

def get_lab_statistics(marker: str, session: Session = None) -> Dict:
    """Calculate aggregate statistics for a lab marker."""
    db = session or get_db_session()
    try:
        stats = db.query(
            func.avg(LabResult.value).label("average"),
            func.min(LabResult.value).label("min"),
            func.max(LabResult.value).label("max"),
            func.count(LabResult.id).label("count")
        ).filter(LabResult.marker.ilike(marker)).first()

        return {
            "average": round(float(stats.average), 2) if stats.average else 0,
            "min":   stats.min   or 0,
            "max":   stats.max   or 0,
            "count": stats.count or 0,
        }
    finally:
        if not session: db.close()


def find_extreme_lab_cases(marker: str, top_n: int = 5, order: str = "desc", session: Session = None) -> List[Dict]:
    """Find patients with the highest/lowest values for a specific lab marker."""
    db = session or get_db_session()
    try:
        order_func = LabResult.value.desc() if order == "desc" else LabResult.value.asc()
        results = (
            db.query(Patient, LabResult.value)
            .join(LabResult)
            .filter(LabResult.marker.ilike(marker))
            .options(joinedload(Patient.medications), joinedload(Patient.diagnoses))
            .order_by(order_func)
            .limit(top_n)
            .all()
        )

        cases = []
        for p, val in results:
            ser = serialize_patient(p)
            ser["extracted_value"] = val
            cases.append(ser)
        return cases
    finally:
        if not session: db.close()


def get_all_patients(session: Session = None) -> List[Dict]:
    """Return all patients with eager-loaded relationships."""
    db = session or get_db_session()
    try:
        patients = db.query(Patient).options(
            joinedload(Patient.medications),
            joinedload(Patient.diagnoses),
            joinedload(Patient.lab_results)
        ).all()
        return [serialize_patient(p) for p in patients]
    finally:
        if not session: db.close()


# ── Serialization ────────────────────────────────────────────────────────────────

def serialize_patient(p: Patient) -> Dict:
    """Convert an ORM Patient object to a plain dictionary.
    IMPORTANT: Assumes relationships are already eager-loaded to avoid N+1 queries.
    """
    return {
        "patient_id":   p.patient_id,
        "name":         p.name,
        "age":          p.age,
        "gender":       p.gender,
        "diagnoses":    ", ".join([d.diagnosis_name for d in p.diagnoses]),
        "medications":  ", ".join([m.med_name for m in p.medications]),
        "lab_results":  ", ".join([
            f"{l.marker}: {l.value}{' ' + l.unit if l.unit else ''}"
            for l in p.lab_results
        ]),
        "doctor_notes": p.doctor_notes,
        "visit_history": p.visit_history,
    }
