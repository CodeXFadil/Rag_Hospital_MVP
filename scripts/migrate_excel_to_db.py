import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.database import Base, Patient, Medication, Diagnosis, LabResult, engine

def migrate():
    # 1. Reset Database
    print("[Migration] Dropping and recreating tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # 2. Load Excel
    excel_path = os.path.join("data", "cardiology_inpatient_dataset.xlsx")
    print(f"[Migration] Loading {excel_path}...")
    df = pd.read_excel(excel_path)
    
    # 3. Process Rows
    print(f"[Migration] Processing {len(df)} rows...")
    patients_to_add = []
    
    for _, row in df.iterrows():
        # Handle NaN values and convert types
        def clean(val):
            if pd.isna(val): return None
            return str(val).strip()

        # Date handling
        adm_date = row.get("Admission_Date")
        if pd.notna(adm_date):
            adm_date = str(adm_date).split(" ")[0] # Keep YYYY-MM-DD
            
        dis_date = row.get("Discharge_Date")
        if pd.notna(dis_date):
            dis_date = str(dis_date).split(" ")[0]

        p = Patient(
            patient_id     = clean(row.get("Patient_ID")),
            episode_id     = clean(row.get("Episode_ID")),
            name           = clean(row.get("Name")),
            age            = int(row.get("Age")) if pd.notna(row.get("Age")) else None,
            gender         = clean(row.get("Gender")),
            nationality    = clean(row.get("Nationality_Group")),
            admission_date = adm_date,
            discharge_date = dis_date,
            length_of_stay = int(row.get("Length_of_Stay")) if pd.notna(row.get("Length_of_Stay")) else None,
            primary_diagnosis = clean(row.get("Primary_Diagnosis")),
            mi_type        = clean(row.get("MI_Type")),
            
            risk_smoking      = clean(row.get("Risk_Smoking")),
            risk_hypertension = clean(row.get("Risk_Hypertension")),
            risk_diabetes     = clean(row.get("Risk_Diabetes")),
            bmi_category      = clean(row.get("BMI_Category")),
            
            icu_admission = clean(row.get("ICU_Admission")),
            procedure     = clean(row.get("Procedure")),
            complications = clean(row.get("Complications")),
            outcome       = clean(row.get("Outcome")),
            death_flag    = int(row.get("Death_Flag")) if pd.notna(row.get("Death_Flag")) else 0,
            
            doctor_notes  = f"Clinical history for {row.get('Name')}. Admitted for {row.get('Primary_Diagnosis')} ({row.get('MI_Type')}). Procedure: {row.get('Procedure')}.",
            visit_history = f"Admission: {adm_date} | Discharge: {dis_date}"
        )
        patients_to_add.append(p)
        
        # Also populate relational table for clinical reasoning joins
        if p.primary_diagnosis:
            db.add(Diagnosis(patient_id=p.patient_id, diagnosis_name=p.primary_diagnosis))
        if p.mi_type:
            db.add(Diagnosis(patient_id=p.patient_id, diagnosis_name=p.mi_type))
        
        # Batch commit for speed
        if len(patients_to_add) >= 500:
            db.add_all(patients_to_add)
            db.commit()
            patients_to_add = []
            print(f"  Inserted {(_+1)} patients...")

    # Final commit
    if patients_to_add:
        db.add_all(patients_to_add)
        db.commit()
        
    print(f"[Migration] SUCCESS: Imported {len(df)} patients.")
    db.close()

if __name__ == "__main__":
    migrate()
