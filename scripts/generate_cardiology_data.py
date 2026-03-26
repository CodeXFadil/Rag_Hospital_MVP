import os
import sys
import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

# Add the project root to sys.path so we can import apps correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import Base, engine, Patient, Medication, Diagnosis, LabResult, get_db_session

# --- Configuration ---
NUM_PATIENTS = 5000
START_YEAR = 2019
END_YEAR = 2024

# --- Names Configuration ---
# Arabic, Asian, and Western Names
ARABIC_FIRST = ["Ahmed", "Fatima", "Mohammed", "Aisha", "Omar", "Zainab", "Ali", "Mariam", "Tariq", "Layla", "Hassan", "Khadija"]
ARABIC_LAST = ["Al-Fayed", "Habib", "Mansour", "Khalil", "Saeed", "Nassar", "Haddad", "Qasim", "Najib", "Salim"]

ASIAN_FIRST = ["Wei", "Yuki", "Mei", "Kenji", "Raj", "Priya", "Ji-hoon", "Cho", "Arjun", "Ananya", "Hiroshi", "Sakura"]
ASIAN_LAST = ["Chen", "Tanaka", "Patel", "Wang", "Kim", "Sharma", "Singh", "Nguyen", "Gupta", "Lee"]

WESTERN_FIRST = ["James", "Emma", "William", "Olivia", "Michael", "Sophia", "David", "Isabella", "John", "Mia", "Robert", "Charlotte"]
WESTERN_LAST = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

def generate_name():
    group = random.choices(["arabic", "asian", "western"], weights=[0.40, 0.40, 0.20], k=1)[0]
    if group == "arabic":
        return f"{random.choice(ARABIC_FIRST)} {random.choice(ARABIC_LAST)}"
    elif group == "asian":
        return f"{random.choice(ASIAN_FIRST)} {random.choice(ASIAN_LAST)}"
    else:
        return f"{random.choice(WESTERN_FIRST)} {random.choice(WESTERN_LAST)}"

# --- Data Generation Logic ---
def random_date(start_year, end_year):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randrange(delta.days)
    return start + timedelta(days=random_days)

def generate_patient_data():
    patients = []
    meds_data = []
    diags_data = []
    labs_data = []
    
    for i in range(1, NUM_PATIENTS + 1):
        pid = f"C{i:05d}"
        name = generate_name()
        
        # Cardiology patients typically older
        age = int(random.triangular(35, 95, 65))
        gender = random.choice(["Male", "Female"])
        
        # Admission date between 2019 and 2024
        admission = random_date(START_YEAR, END_YEAR)
        
        # Length of stay: 1 to 21 days
        los = random.randint(1, 21)
        discharge = admission + timedelta(days=los)
        
        # Diagnosis: majority MI
        primary_dx = random.choices(
            ["STEMI", "NSTEMI", "Unstable Angina", "Heart Failure", "Arrhythmia"], 
            weights=[0.40, 0.30, 0.10, 0.15, 0.05], k=1
        )[0]
        
        comorbidities = []
        if random.random() < 0.65: comorbidities.append("Hypertension")
        if random.random() < 0.45: comorbidities.append("Type 2 Diabetes")
        if random.random() < 0.35: comorbidities.append("Hyperlipidemia")
        if random.random() < 0.10: comorbidities.append("Chronic Kidney Disease")
        
        # Risk factors tracking via conditions
        smoker = random.random() < 0.30
        
        # Outcome calculation based on age, dx, and comorbidities
        death_chance = 0.02
        if age > 75: death_chance += 0.08
        if primary_dx in ["STEMI", "Heart Failure"]: death_chance += 0.06
        if "Type 2 Diabetes" in comorbidities: death_chance += 0.03
        if smoker: death_chance += 0.02
        
        outcome = "Deceased" if random.random() < death_chance else "Discharged"
        if outcome == "Deceased":
            # Discharge date is death date
            pass
        
        # Doctor notes
        notes = f"Patient admitted with {primary_dx}. "
        if smoker: notes += "Patient is a known chronic smoker. "
        if "Hypertension" in comorbidities: notes += "History of HTN noted. "
            
        patients.append(Patient(
            patient_id=pid,
            name=name,
            age=age,
            gender=gender,
            admission_date=admission.strftime("%Y-%m-%d"),
            discharge_date=discharge.strftime("%Y-%m-%d"),
            outcome=outcome,
            doctor_notes=notes,
            visit_history=f"Admitted {admission.year}"
        ))
        
        # Diagnoses rows
        all_dx = [primary_dx] + comorbidities
        for dx in all_dx:
            diags_data.append(Diagnosis(patient_id=pid, diagnosis_name=dx))
            
        # Meds
        if primary_dx in ["STEMI", "NSTEMI"]:
            meds_data.append(Medication(patient_id=pid, med_name="Aspirin 81mg"))
            meds_data.append(Medication(patient_id=pid, med_name="Atorvastatin 40mg"))
            if random.random() < 0.8:
                meds_data.append(Medication(patient_id=pid, med_name="Metoprolol 25mg"))
        if "Type 2 Diabetes" in comorbidities:
            meds_data.append(Medication(patient_id=pid, med_name="Metformin 500mg"))
        if "Hypertension" in comorbidities:
            meds_data.append(Medication(patient_id=pid, med_name="Lisinopril 10mg"))
            
        # Labs
        # LDL
        ldl_val = round(random.uniform(70, 190), 1)
        if "Hyperlipidemia" in comorbidities: ldl_val += 40
        labs_data.append(LabResult(patient_id=pid, marker="LDL", value=ldl_val, unit="mg/dL", test_date=admission.strftime("%Y-%m-%d")))
        
        # HbA1c
        hba1c_val = round(random.uniform(4.5, 6.4), 1)
        if "Type 2 Diabetes" in comorbidities: hba1c_val = round(random.uniform(6.5, 11.0), 1)
        labs_data.append(LabResult(patient_id=pid, marker="HbA1c", value=hba1c_val, unit="%", test_date=admission.strftime("%Y-%m-%d")))
        
        # Troponin (elevated for MI)
        trop_val = round(random.uniform(0.01, 0.04), 2)
        if primary_dx in ["STEMI", "NSTEMI"]: trop_val = round(random.uniform(0.5, 12.0), 2)
        labs_data.append(LabResult(patient_id=pid, marker="Troponin", value=trop_val, unit="ng/mL", test_date=admission.strftime("%Y-%m-%d")))
        
    return patients, meds_data, diags_data, labs_data

def main():
    print("Dropping existing tables and recreating schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    print(f"Generating {NUM_PATIENTS} cardiology patient records...")
    patients, meds, diags, labs = generate_patient_data()
    
    db = get_db_session()
    try:
        print("Inserting Patients...")
        # Batch insert for performance
        db.bulk_save_objects(patients)
        db.commit()
        
        print("Inserting Medications...")
        db.bulk_save_objects(meds)
        db.commit()
        
        print("Inserting Diagnoses...")
        db.bulk_save_objects(diags)
        db.commit()
        
        print("Inserting Lab Results...")
        db.bulk_save_objects(labs)
        db.commit()
        
        print("✅ Database successfully seeded with 5,000 cardiology patients!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
