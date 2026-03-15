import os
import re
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to local SQLite for development
    DATABASE_URL = "sqlite:///./hospital_data.db"
    print(f"DEBUG: No DATABASE_URL found. Using local fallback: {DATABASE_URL}")

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

# ── Migration Logic ─────────────────────────────────────────────────────────────

def migrate():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    csv_path = os.path.join(os.path.dirname(__file__), "data", "patients.csv")
    df = pd.read_csv(csv_path)
    
    db = SessionLocal()
    try:
        for _, row in df.iterrows():
            pid = row['patient_id']
            
            # 1. Add Patient
            patient = Patient(
                patient_id=pid,
                name=row['name'],
                age=int(row['age']),
                gender=row['gender'],
                doctor_notes=row['doctor_notes'],
                visit_history=row['visit_history']
            )
            db.add(patient)
            
            # 2. Extract Medications
            meds = [m.strip() for m in str(row['medications']).split(',')]
            for m in meds:
                if m and m.lower() != 'nan':
                    db.add(Medication(patient_id=pid, med_name=m))
            
            # 3. Extract Diagnoses
            diags = [d.strip() for d in str(row['diagnoses']).split(',')]
            for d in diags:
                if d and d.lower() != 'nan':
                    db.add(Diagnosis(patient_id=pid, diagnosis_name=d))
            
            # 4. Extract Labs (Regex)
            lab_str = str(row['lab_results'])
            # Pattern: Marker: Value (e.g., HbA1c: 8.2% or BP: 145/90)
            # We'll normalize BP by keeping Systolic for numeric thresholds
            lab_matches = re.findall(r"([a-zA-Z1-9]+):\s*([\d\.]+)", lab_str)
            for marker, val in lab_matches:
                db.add(LabResult(patient_id=pid, marker=marker, value=float(val)))
            
            # Special case for BP (Systolic)
            bp_match = re.search(r"BP:\s*(\d+)/", lab_str)
            if bp_match:
                db.add(LabResult(patient_id=pid, marker="BP", value=float(bp_match.group(1))))

        db.commit()
        print(f"SUCCESS: Migrated {len(df)} patients to {DATABASE_URL}")
    except Exception as e:
        db.rollback()
        print(f"ERROR: Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
