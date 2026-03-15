"""
agents/patient_data_agent.py
Optimized structured retrieval from SQL database using SQLAlchemy relationships, 
eager loading, and production-grade session management.
"""

import os
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, Index, and_, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload, Session
from dotenv import load_dotenv

load_dotenv()

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./hospital_data.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ── Schema Definitions with Indexing & Relationships ──────────────────────────

class Patient(Base):
    __tablename__ = "patients"
    patient_id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer, index=True)
    gender = Column(String, index=True)
    doctor_notes = Column(Text)
    visit_history = Column(Text)

    # Relationships with eager loading capability
    medications = relationship("Medication", back_populates="patient", cascade="all, delete-orphan")
    diagnoses = relationship("Diagnosis", back_populates="patient", cascade="all, delete-orphan")
    lab_results = relationship("LabResult", back_populates="patient", cascade="all, delete-orphan")

class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), index=True)
    med_name = Column(String, index=True)
    
    patient = relationship("Patient", back_populates="medications")

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), index=True)
    diagnosis_name = Column(String, index=True)
    
    patient = relationship("Patient", back_populates="diagnoses")

class LabResult(Base):
    __tablename__ = "labs"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), index=True)
    marker = Column(String, index=True)
    value = Column(Float, index=True)
    unit = Column(String)  # New field
    test_date = Column(String, index=True) # New field

    patient = relationship("Patient", back_populates="lab_results")

# ── Session Management ──────────────────────────────────────────────────────────

def get_db_session():
    """Create a new database session."""
    return SessionLocal()

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
    """
    Apply multiple structured filters using optimized SQL JOINs.
    """
    db = session or get_db_session()
    try:
        # Start with a base query and eager load all related data
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
        if entities.get("gender"):
            query = query.filter(Patient.gender.ilike(entities["gender"].strip()))
        
        age_range = entities.get("age_range")
        if age_range:
            if age_range.get("min") is not None:
                query = query.filter(Patient.age >= age_range["min"])
            if age_range.get("max") is not None:
                query = query.filter(Patient.age <= age_range["max"])

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
            op = f.get("operator")
            target = f.get("value")
            if not marker or target is None: continue
            
            # Use an aliased join if multiple lab filters are applied
            query = query.join(LabResult, Patient.patient_id == LabResult.patient_id)\
                         .filter(LabResult.marker.ilike(marker))
            
            if op == ">": query = query.filter(LabResult.value > target)
            elif op == ">=": query = query.filter(LabResult.value >= target)
            elif op == "<": query = query.filter(LabResult.value < target)
            elif op == "<=": query = query.filter(LabResult.value <= target)
            elif op in ["==", "=", "!="]:
                if op == "!=": query = query.filter(LabResult.value != target)
                else: query = query.filter(LabResult.value == target)

        results = query.all()
        return [serialize_patient(p) for p in results]
    finally:
        if not session: db.close()

# ── Advanced Analytics Helpers ──────────────────────────────────────────────

def get_lab_statistics(marker: str, session: Session = None) -> Dict[str, float]:
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
            "min": stats.min or 0,
            "max": stats.max or 0,
            "count": stats.count or 0
        }
    finally:
        if not session: db.close()

def find_extreme_lab_cases(marker: str, top_n: int = 5, order: str = "desc", session: Session = None) -> List[Dict]:
    """Find patients with the highest/lowest values for a specific lab marker."""
    db = session or get_db_session()
    try:
        order_func = LabResult.value.desc() if order == "desc" else LabResult.value.asc()
        results = db.query(Patient, LabResult.value)\
                    .join(LabResult)\
                    .filter(LabResult.marker.ilike(marker))\
                    .options(joinedload(Patient.medications), joinedload(Patient.diagnoses))\
                    .order_by(order_func)\
                    .limit(top_n).all()
        
        cases = []
        for p, val in results:
            ser = serialize_patient(p)
            ser["extracted_value"] = val
            cases.append(ser)
        return cases
    finally:
        if not session: db.close()

def get_all_patients(session: Session = None) -> List[Dict]:
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

# ── Serialization Logic (Fixed N+1) ──────────────────────────────────────────

def serialize_patient(p: Patient) -> Dict:
    """
    Converts ORM objects into dictionary format.
    CRITICAL: Assumes relationships are already eager-loaded to avoid queries.
    """
    return {
        "patient_id": p.patient_id,
        "name": p.name,
        "age": p.age,
        "gender": p.gender,
        "diagnoses": ", ".join([d.diagnosis_name for d in p.diagnoses]),
        "medications": ", ".join([m.med_name for m in p.medications]),
        "lab_results": ", ".join([f"{l.marker}: {l.value}{' ' + l.unit if l.unit else ''}" for l in p.lab_results]),
        "doctor_notes": p.doctor_notes,
        "visit_history": p.visit_history
    }
