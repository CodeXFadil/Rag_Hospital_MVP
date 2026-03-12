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


def get_all_patients() -> Any:
    """Return the full patient dataframe."""
    return _load_data()
