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
    episode_id   = Column(String, index=True)
    name         = Column(String, index=True)
    age          = Column(Integer, index=True)
    gender       = Column(String, index=True)
    nationality  = Column(String, index=True)
    admission_date = Column(String, index=True)
    discharge_date = Column(String)
    length_of_stay = Column(Integer)
    primary_diagnosis = Column(String, index=True)
    mi_type      = Column(String, index=True)
    
    # Risk Factors & Physicals
    risk_smoking      = Column(String)
    risk_hypertension = Column(String)
    risk_diabetes     = Column(String)
    bmi_category      = Column(String, index=True)
    
    # Clinical Status
    icu_admission = Column(String, index=True)
    procedure     = Column(String, index=True)
    complications = Column(String, index=True)
    outcome       = Column(String, index=True)
    death_flag    = Column(Integer, index=True)  # 0 or 1
    
    doctor_notes  = Column(Text)
    visit_history = Column(Text)


# ── Session Helper ──────────────────────────────────────────────────────────────

def get_db_session() -> Session:
    """Return a new database session. Caller is responsible for closing it."""
    return SessionLocal()
