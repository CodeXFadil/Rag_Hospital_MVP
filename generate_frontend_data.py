import pandas as pd
import json
import os
import re

DATA_PATH = "data/patients.csv"
OUTPUT_PATH = "frontend/src/data/mockPatients.ts"

def parse_labs(lab_str):
    labs = []
    for item in str(lab_str).split(","):
        item = item.strip()
        if ":" in item:
            name, val_unit = item.split(":", 1)
            name = name.strip()
            val_unit = val_unit.strip()
            v_match = re.search(r"([0-9\./]+)\s*(.*)", val_unit)
            value = v_match.group(1) if v_match else val_unit
            unit = v_match.group(2) if v_match else ""
            
            status = "normal"
            if "HbA1c" in name:
                try:
                    v = float(value.replace("%", ""))
                    if v > 8.0: status = "critical"
                    elif v > 7.0: status = "warning"
                except: pass
            if "BP" in name or "Blood Pressure" in name:
                try:
                    sys = float(value.split("/")[0])
                    if sys > 160: status = "critical"
                    elif sys > 140: status = "warning"
                except: pass
            
            labs.append({
                "name": name,
                "value": value,
                "unit": unit,
                "normalRange": "See protocol",
                "status": status
            })
    return labs

def parse_meds(med_str):
    meds = []
    for m in str(med_str).split(","):
        m = m.strip()
        if m:
            parts = m.split(" ")
            name = parts[0]
            dosage = " ".join(parts[1:]) if len(parts) > 1 else ""
            meds.append({
                "name": name,
                "dosage": dosage,
                "frequency": "As prescribed",
                "since": "2023"
            })
    return meds

df = pd.read_csv(DATA_PATH)
patients_dict = {}

for _, row in df.iterrows():
    p_id = str(row["patient_id"])
    vh = str(row.get("visit_history", ""))
    last_visit = vh.split(";")[-1].split(":")[0].strip() if vh else "2024"
    ward = vh.split(":")[-1].strip() if ":" in vh else "General OPD"
    
    patients_dict[p_id] = {
        "id": p_id,
        "name": row["name"],
        "age": int(row["age"]),
        "gender": row["gender"],
        "bloodGroup": "Unknown",
        "diagnoses": [d.strip() for d in str(row["diagnoses"]).split(",")],
        "medications": parse_meds(row["medications"]),
        "labResults": parse_labs(row["lab_results"]),
        "lastVisit": last_visit,
        "ward": ward,
        "attendingDoctor": "Dr. Clinical AI",
        "notes": row["doctor_notes"]
    }

ts_content = f"""
export interface LabResult {{
  name: string;
  value: string;
  unit: string;
  normalRange: string;
  status: "normal" | "warning" | "critical";
}}

export interface Medication {{
  name: string;
  dosage: string;
  frequency: string;
  since: string;
}}

export interface Patient {{
  id: string;
  name: string;
  age: number;
  gender: string;
  bloodGroup: string;
  diagnoses: string[];
  medications: Medication[];
  labResults: LabResult[];
  lastVisit: string;
  ward: string;
  attendingDoctor: string;
  notes: string;
}}

export const mockPatients: Record<string, Patient> = {json.dumps(patients_dict, indent=2)};

export function searchPatients(query: string): Patient[] {{
  const q = query.toLowerCase();
  return Object.values(mockPatients).filter(
    (p) =>
      p.name.toLowerCase().includes(q) ||
      p.id.toLowerCase().includes(q) ||
      p.diagnoses.some((d) => d.toLowerCase().includes(q))
  );
}}

export function getPatientById(id: string): Patient | undefined {{
  return mockPatients[id.toUpperCase()];
}}

export const API_BASE_URL = (
  window.location.hostname === 'localhost' || 
  window.location.hostname === '127.0.0.1' || 
  window.location.hostname.startsWith('192.168.')
) ? 'http://localhost:8000' : '';

export async function fetchAllPatients(): Promise<Patient[]> {{
  try {{
    const response = await fetch(`${{API_BASE_URL}}/api/patients`);
    if (!response.ok) throw new Error('Failed to fetch patients');
    const data = await response.json();
    return data && data.length > 0 ? data : Object.values(mockPatients);
  }} catch (error) {{
    console.error('Error fetching patients:', error);
    return Object.values(mockPatients); // Fallback to mocks (now contains all 50)
  }}
}}
"""

with open(OUTPUT_PATH, "w") as f:
    f.write(ts_content)

print(f"Generated {len(patients_dict)} patients in {OUTPUT_PATH}")
