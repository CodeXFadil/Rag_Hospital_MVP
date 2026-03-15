import os
import re
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from agents.patient_data_agent import Base, Patient, Medication, Diagnosis, LabResult
from dotenv import load_dotenv

load_dotenv()

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./hospital_data.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def migrate():
    # Fresh start: drop and recreate tables with new indexes/relationships
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
            
            # 4. Extract Labs (Regex + Units)
            lab_str = str(row['lab_results'])
            # Match Marker: Value (e.g., HbA1c: 8.2 or LDL: 130 mg/dL)
            # This regex captures the marker, the numeric value, and optionally a unit
            lab_matches = re.findall(r"([a-zA-Z1-9]+):\s*([\d\.]+)\s*([%a-zA-Z/]*)", lab_str)
            
            for marker, val, unit in lab_matches:
                unit = unit.strip() if unit else None
                db.add(LabResult(
                    patient_id=pid, 
                    marker=marker, 
                    value=float(val),
                    unit=unit or ("%" if marker.lower() == "hba1c" else "mg/dL"),
                    test_date=datetime.now().strftime("%Y-%m-%d") # Placeholder date
                ))
            
            # Special case for BP
            bp_match = re.search(r"BP:\s*(\d+)/(\d+)", lab_str)
            if bp_match:
                db.add(LabResult(
                    patient_id=pid, 
                    marker="BP", 
                    value=float(bp_match.group(1)),
                    unit="mmHg",
                    test_date=datetime.now().strftime("%Y-%m-%d")
                ))

        db.commit()
        print(f"SUCCESS: Migrated {len(df)} patients to {DATABASE_URL} with enhanced schema.")
    except Exception as e:
        db.rollback()
        print(f"ERROR: Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
