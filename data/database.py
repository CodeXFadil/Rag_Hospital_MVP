"""
data/database.py
Centralised SQLAlchemy setup: engine, session factory, Base, and all ORM models.

This is the single source of truth for the database schema.
Import models and the session factory from here — never define them elsewhere.
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from dotenv import load_dotenv

load_dotenv()

# ── Engine & Session Factory ────────────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./hospital_data.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ── ORM Models ──────────────────────────────────────────────────────────────────

class Patient(Base):
    __tablename__ = "patients"
    patient_id   = Column(String, primary_key=True, index=True)
    name         = Column(String, index=True)
    age          = Column(Integer, index=True)
    gender       = Column(String, index=True)
    doctor_notes = Column(Text)
    visit_history = Column(Text)

    medications = relationship("Medication", back_populates="patient", cascade="all, delete-orphan")
    diagnoses   = relationship("Diagnosis",  back_populates="patient", cascade="all, delete-orphan")
    lab_results = relationship("LabResult",  back_populates="patient", cascade="all, delete-orphan")


class Medication(Base):
    __tablename__ = "medications"
    id         = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), index=True)
    med_name   = Column(String, index=True)

    patient = relationship("Patient", back_populates="medications")


class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id             = Column(Integer, primary_key=True, index=True)
    patient_id     = Column(String, ForeignKey("patients.patient_id"), index=True)
    diagnosis_name = Column(String, index=True)

    patient = relationship("Patient", back_populates="diagnoses")


class LabResult(Base):
    __tablename__ = "labs"
    id         = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), index=True)
    marker     = Column(String, index=True)
    value      = Column(Float, index=True)
    unit       = Column(String)
    test_date  = Column(String, index=True)

    patient = relationship("Patient", back_populates="lab_results")


# ── Session Helper ──────────────────────────────────────────────────────────────

def get_db_session() -> Session:
    """Return a new database session. Caller is responsible for closing it."""
    return SessionLocal()
