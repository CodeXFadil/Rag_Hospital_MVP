"""
db_migration.py
Reads data/patients.csv and populates the SQL database.

Run this once (or when data changes):
    python db_migration.py
"""

import os
import re
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from data.database import Base, engine, SessionLocal, Patient, Medication, Diagnosis, LabResult

load_dotenv()


def migrate():
    """Drop and recreate all tables, then seed from data/patients.csv."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    csv_path = os.path.join(os.path.dirname(__file__), "data", "patients.csv")
    df = pd.read_csv(csv_path)

    db = SessionLocal()
    try:
        for _, row in df.iterrows():
            pid = row["patient_id"]

            # 1. Patient core record
            db.add(Patient(
                patient_id=pid,
                name=row["name"],
                age=int(row["age"]),
                gender=row["gender"],
                doctor_notes=row["doctor_notes"],
                visit_history=row["visit_history"],
            ))

            # 2. Medications (comma-separated string)
            for m in str(row["medications"]).split(","):
                m = m.strip()
                if m and m.lower() != "nan":
                    db.add(Medication(patient_id=pid, med_name=m))

            # 3. Diagnoses (comma-separated string)
            for d in str(row["diagnoses"]).split(","):
                d = d.strip()
                if d and d.lower() != "nan":
                    db.add(Diagnosis(patient_id=pid, diagnosis_name=d))

            # 4. Lab results — e.g. "HbA1c: 8.2, LDL: 130 mg/dL"
            lab_str = str(row["lab_results"])
            for marker, val, unit in re.findall(r"([a-zA-Z1-9]+):\s*([\d\.]+)\s*([%a-zA-Z/]*)", lab_str):
                unit = unit.strip() or ("%" if marker.lower() == "hba1c" else "mg/dL")
                db.add(LabResult(
                    patient_id=pid,
                    marker=marker,
                    value=float(val),
                    unit=unit,
                    test_date=datetime.now().strftime("%Y-%m-%d"),
                ))

            # 5. Blood pressure — stored as separate systolic LabResult
            bp_match = re.search(r"BP:\s*(\d+)/(\d+)", lab_str)
            if bp_match:
                db.add(LabResult(
                    patient_id=pid,
                    marker="BP",
                    value=float(bp_match.group(1)),
                    unit="mmHg",
                    test_date=datetime.now().strftime("%Y-%m-%d"),
                ))

        db.commit()
        print(f"SUCCESS: Migrated {len(df)} patients to {os.getenv('DATABASE_URL', 'sqlite:///./hospital_data.db')}")
    except Exception as e:
        db.rollback()
        print(f"ERROR: Migration failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
