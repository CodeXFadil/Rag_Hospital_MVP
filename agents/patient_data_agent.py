"""
agents/patient_data_agent.py
Structured retrieval from SQL database (PostgreSQL/SQLite) using SQLAlchemy.
"""

import os
from typing import Optional, Any, List, Dict
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, or_, and_, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, session
from dotenv import load_dotenv

load_dotenv()

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to local SQLite
    DATABASE_URL = "sqlite:///./hospital_data.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ── Schema Definitions ──────────────────────────────────────────────────────────

class Patient(Base):
    __tablename__ = "patients"
    patient_id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    doctor_notes = Column(Text)
    visit_history = Column(Text)

class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"))
    med_name = Column(String, index=True)

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"))
    diagnosis_name = Column(String, index=True)

class LabResult(Base):
    __tablename__ = "labs"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"))
    marker = Column(String, index=True)
    value = Column(Float)

# ── Retrieval Logic ─────────────────────────────────────────────────────────────

def _get_db():
    return SessionLocal()

def find_patient(patient_id: Optional[str] = None, name: Optional[str] = None) -> List[Dict]:
    db = _get_db()
    try:
        query = db.query(Patient)
        if patient_id:
            query = query.filter(Patient.patient_id.ilike(patient_id.strip()))
        if name:
            query = query.filter(Patient.name.ilike(f"%{name.strip()}%"))
        
        results = query.all()
        return [serialize_patient(p) for p in results]
    finally:
        db.close()

def filter_patients(entities: Dict) -> List[Dict]:
    """
    Apply multiple structured filters via SQL JOINs.
    """
    db = _get_db()
    try:
        query = db.query(Patient)

        # 1. Identity
        pid = entities.get("patient_id")
        if pid and pid.upper() not in ["PXXX", "P000", "NONE"]:
            query = query.filter(Patient.patient_id.ilike(pid.strip()))
        
        pname = entities.get("patient_name")
        if pname and pname.lower().strip() not in ["full name", "name", "none"]:
            query = query.filter(Patient.name.ilike(f"%{pname.strip()}%"))

        # 2. Gender & Age
        if entities.get("gender"):
            query = query.filter(Patient.gender.ilike(entities["gender"].strip()))
        
        age_range = entities.get("age_range")
        if age_range:
            if age_range.get("min") is not None:
                query = query.filter(Patient.age >= age_range["min"])
            if age_range.get("max") is not None:
                query = query.filter(Patient.age <= age_range["max"])

        # 3. Medications (JOIN med table)
        meds = entities.get("medications", [])
        if meds:
            for med in meds:
                query = query.filter(Patient.patient_id.in_(
                    db.query(Medication.patient_id).filter(Medication.med_name.ilike(f"%{med}%"))
                ))

        # 4. Lab Filters (JOIN labs table)
        lab_filters = entities.get("lab_filters", [])
        for f in lab_filters:
            marker = f.get("marker")
            op = f.get("operator")
            target = f.get("value")
            if not marker or target is None: continue
            
            # Subquery to find patients matching clinical criteria
            lab_subquery = db.query(LabResult.patient_id).filter(LabResult.marker.ilike(marker))
            if op == ">": lab_subquery = lab_subquery.filter(LabResult.value > target)
            elif op == ">=": lab_subquery = lab_subquery.filter(LabResult.value >= target)
            elif op == "<": lab_subquery = lab_subquery.filter(LabResult.value < target)
            elif op == "<=": lab_subquery = lab_subquery.filter(LabResult.value <= target)
            elif op in ["==", "=", "!="]:
                if op == "!=": lab_subquery = lab_subquery.filter(LabResult.value != target)
                else: lab_subquery = lab_subquery.filter(LabResult.value == target)
            
            query = query.filter(Patient.patient_id.in_(lab_subquery))

        results = query.all()
        return [serialize_patient(p) for p in results]
    finally:
        db.close()

def find_patients_by_lab_threshold(lab_marker: str, condition: str, threshold: float) -> List[Dict]:
    db = _get_db()
    try:
        query = db.query(Patient).join(LabResult)
        query = query.filter(LabResult.marker.ilike(lab_marker))
        if condition == "above":
            query = query.filter(LabResult.value > threshold)
        else:
            query = query.filter(LabResult.value < threshold)
        
        results = query.all()
        return [serialize_patient(p) for p in results]
    finally:
        db.close()

def get_all_patients() -> List[Dict]:
    db = _get_db()
    try:
        return [serialize_patient(p) for p in db.query(Patient).all()]
    finally:
        db.close()

def serialize_patient(p: Patient) -> Dict:
    """Combine data from multiple tables back into the format expected by agents."""
    db = _get_db()
    try:
        meds = [m.med_name for m in db.query(Medication).filter_by(patient_id=p.patient_id).all()]
        diags = [d.diagnosis_name for d in db.query(Diagnosis).filter_by(patient_id=p.patient_id).all()]
        labs = [f"{l.marker}: {l.value}" for l in db.query(LabResult).filter_by(patient_id=p.patient_id).all()]
        
        return {
            "patient_id": p.patient_id,
            "name": p.name,
            "age": p.age,
            "gender": p.gender,
            "diagnoses": ", ".join(diags),
            "medications": ", ".join(meds),
            "lab_results": ", ".join(labs),
            "doctor_notes": p.doctor_notes,
            "visit_history": p.visit_history
        }
    finally:
        db.close()
