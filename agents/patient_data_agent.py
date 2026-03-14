"""
agents/patient_data_agent.py
Structured retrieval from patients.csv using pandas.
"""

import os
# import pandas as pd - moved inside functions
from typing import Optional, Any, List, Dict

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "patients.csv")

_df: Any = None


def _load_data() -> Any:
    global _df
    if _df is None:
        import pandas as pd
        _df = pd.read_csv(DATA_PATH)
        _df["patient_id_upper"] = _df["patient_id"].str.upper().str.strip()
        _df["name_lower"] = _df["name"].str.lower().str.strip()
    return _df


def find_patient(
    patient_id: Optional[str] = None,
    name: Optional[str] = None,
) -> List[Dict]:
    """
    Look up patient records from structured data.

    Args:
        patient_id: e.g. "P014"
        name: partial or full patient name (case-insensitive)

    Returns:
        List of matching patient record dicts. Empty list if none found.
    """
    df = _load_data()
    result = df.copy()

    if patient_id:
        result = result[result["patient_id_upper"] == patient_id.upper().strip()]

    if name and not result.empty:
        name_lower = name.lower().strip()
        result = result[result["name_lower"].str.contains(name_lower, na=False)]
    elif name:
        name_lower = name.lower().strip()
        result = df[df["name_lower"].str.contains(name_lower, na=False)]

    records = []
    for _, row in result.iterrows():
        records.append({
            "patient_id": row["patient_id"],
            "name": row["name"],
            "age": row["age"],
            "gender": row["gender"],
            "diagnoses": row["diagnoses"],
            "medications": row["medications"],
            "lab_results": row["lab_results"],
            "doctor_notes": row["doctor_notes"],
            "visit_history": row["visit_history"],
        })
    return records


def find_patients_by_lab_threshold(lab_marker: str, condition: str, threshold: float) -> List[Dict]:
    """
    Find patients where a specific lab marker exceeds / is below a threshold.

    Args:
        lab_marker: e.g. "HbA1c", "BP"
        condition: "above" or "below"
        threshold: numeric threshold value

    Returns:
        List of matching patient dicts with the extracted lab value.
    """
    df = _load_data()
    results = []

    import re
    pattern = re.compile(rf"{re.escape(lab_marker)}[:\s]*([0-9]+\.?[0-9]*)", re.IGNORECASE)

    for _, row in df.iterrows():
        lab_str = str(row.get("lab_results", ""))
        match = pattern.search(lab_str)
        if match:
            try:
                value = float(match.group(1))
                if condition == "above" and value > threshold:
                    results.append({**find_patient(patient_id=row["patient_id"])[0], "extracted_value": value})
                elif condition == "below" and value < threshold:
                    results.append({**find_patient(patient_id=row["patient_id"])[0], "extracted_value": value})
            except (ValueError, IndexError):
                continue

    return results


def filter_patients(entities: Dict) -> List[Dict]:
    """
    Apply multiple structured filters to the patient database.
    """
    df = _load_data()
    result_df = df.copy()

    # 1. Patient ID / Name (Deterministic)
    pid = entities.get("patient_id")
    if pid and pid.upper() not in ["PXXX", "P000", "NONE"]:
        result_df = result_df[result_df["patient_id_upper"] == pid.upper().strip()]
    
    pname = entities.get("patient_name")
    if pname and pname.lower().strip() not in ["full name", "name", "none"]:
        name_lower = pname.lower().strip()
        result_df = result_df[result_df["name_lower"].str.contains(name_lower, na=False)]

    # 2. Gender
    if entities.get("gender"):
        gender = entities["gender"].lower().strip()
        result_df = result_df[result_df["gender"].str.lower() == gender]

    # 3. Age Range
    age_range = entities.get("age_range")
    if age_range:
        if age_range.get("min") is not None:
            result_df = result_df[result_df["age"] >= age_range["min"]]
        if age_range.get("max") is not None:
            result_df = result_df[result_df["age"] <= age_range["max"]]

    # 4. Medications (String search)
    meds = entities.get("medications", [])
    if meds:
        for med in meds:
            result_df = result_df[result_df["medications"].str.contains(med, case=False, na=False)]

    records = []
    import re
    
    # 5. Lab Filters (Regex applied row-by-row on the filtered subset)
    lab_filters = entities.get("lab_filters", [])
    
    for _, row in result_df.iterrows():
        keep = True
        for f in lab_filters:
            marker = f.get("marker")
            op = f.get("operator")
            target = f.get("value")
            
            if not marker or target is None: continue
            
            pattern = re.compile(rf"{re.escape(marker)}[:\s]*([0-9]+\.?[0-9]*)", re.IGNORECASE)
            lab_str = str(row.get("lab_results", ""))
            match = pattern.search(lab_str)
            
            if not match:
                keep = False # Missing marker fails the filter
                break
            
            try:
                val = float(match.group(1))
                if op == ">" and not (val > target): keep = False
                elif op == ">=" and not (val >= target): keep = False
                elif op == "<" and not (val < target): keep = False
                elif op == "<=" and not (val <= target): keep = False
                elif (op == "==" or op == "=") and not (val == target): keep = False
                elif op == "!=" and not (val != target): keep = False
            except:
                keep = False
            
            if not keep: break
            
        if keep:
            records.append({
                "patient_id": row["patient_id"],
                "name": row["name"],
                "age": row["age"],
                "gender": row["gender"],
                "diagnoses": row["diagnoses"],
                "medications": row["medications"],
                "lab_results": row["lab_results"],
                "doctor_notes": row["doctor_notes"],
                "visit_history": row["visit_history"],
            })
            
    return records


def get_all_patients() -> Any:
    """Return the full patient dataframe."""
    return _load_data()
