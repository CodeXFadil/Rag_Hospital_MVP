"""
agents/clinical_reasoning_agent.py
Rule-based clinical reasoning over structured patient data.
Never fabricates information – only reasons over retrieved data.
"""

import re
from typing import List, Dict


# ── Clinical thresholds ────────────────────────────────────────────────────────
RULES = [
    {
        "marker": "HbA1c",
        "pattern": r"HbA1c[:\s]*([0-9]+\.?[0-9]*)%?",
        "threshold": 7.0,
        "condition": "above",
        "flag": "⚠️ Uncontrolled Diabetes",
        "detail": "HbA1c > 7% indicates suboptimal glycaemic control.",
    },
    {
        "marker": "HbA1c",
        "pattern": r"HbA1c[:\s]*([0-9]+\.?[0-9]*)%?",
        "threshold": 8.0,
        "condition": "above",
        "flag": "🔴 Severely Uncontrolled Diabetes",
        "detail": "HbA1c > 8% — significant risk of diabetic complications.",
    },
    {
        "marker": "BP_systolic",
        "pattern": r"BP[:\s]*([0-9]+)/[0-9]+",
        "threshold": 140,
        "condition": "above",
        "flag": "⚠️ Hypertension Risk",
        "detail": "Systolic BP > 140 mmHg — hypertension management review recommended.",
    },
    {
        "marker": "BP_systolic",
        "pattern": r"BP[:\s]*([0-9]+)/[0-9]+",
        "threshold": 160,
        "condition": "above",
        "flag": "🔴 Severe Hypertension",
        "detail": "Systolic BP > 160 mmHg — urgent hypertension management required.",
    },
    {
        "marker": "LDL",
        "pattern": r"LDL[:\s]*([0-9]+\.?[0-9]*)\s*mg/dL",
        "threshold": 130,
        "condition": "above",
        "flag": "⚠️ Elevated LDL Cholesterol",
        "detail": "LDL > 130 mg/dL — cardiovascular risk elevated. Review statin therapy.",
    },
    {
        "marker": "eGFR",
        "pattern": r"eGFR[:\s]*([0-9]+\.?[0-9]*)\s*mL/min",
        "threshold": 60,
        "condition": "below",
        "flag": "⚠️ Reduced Kidney Function",
        "detail": "eGFR < 60 mL/min — consistent with Chronic Kidney Disease. Monitor closely.",
    },
    {
        "marker": "eGFR",
        "pattern": r"eGFR[:\s]*([0-9]+\.?[0-9]*)\s*mL/min",
        "threshold": 30,
        "condition": "below",
        "flag": "🔴 Severely Reduced Kidney Function",
        "detail": "eGFR < 30 mL/min — CKD Stage 4–5. Nephrology urgency.",
    },
    {
        "marker": "Hb",
        "pattern": r"Hb[:\s]*([0-9]+\.?[0-9]*)\s*g/dL",
        "threshold": 10.0,
        "condition": "below",
        "flag": "⚠️ Anaemia Detected",
        "detail": "Haemoglobin < 10 g/dL — investigate cause and consider supplementation/treatment.",
    },
    {
        "marker": "TSH",
        "pattern": r"TSH[:\s]*([0-9]+\.?[0-9]*)\s*mIU/L",
        "threshold": 5.0,
        "condition": "above",
        "flag": "⚠️ Elevated TSH — Possible Hypothyroidism",
        "detail": "TSH > 5 mIU/L — consider reviewing thyroid replacement dose.",
    },
    {
        "marker": "BNP",
        "pattern": r"BNP[:\s]*([0-9]+\.?[0-9]*)\s*pg/mL",
        "threshold": 400,
        "condition": "above",
        "flag": "🔴 Elevated BNP — Heart Failure Risk",
        "detail": "BNP > 400 pg/mL — significant cardiac stress. Cardiology review advised.",
    },
]


def analyse_patient(patient_data: Dict) -> List[Dict]:
    """
    Run clinical rules over a single patient's lab_results string.

    Args:
        patient_data: Dict from patient_data_agent.find_patient()

    Returns:
        List of risk flag dicts: {flag, detail, marker, value}
    """
    lab_str = str(patient_data.get("lab_results", ""))
    flags = []
    seen_rules = set()

    for rule in RULES:
        rule_key = (rule["marker"], rule["threshold"])
        if rule_key in seen_rules:
            continue

        match = re.search(rule["pattern"], lab_str, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1))
                triggered = (
                    (rule["condition"] == "above" and value > rule["threshold"])
                    or (rule["condition"] == "below" and value < rule["threshold"])
                )
                if triggered:
                    flags.append({
                        "flag": rule["flag"],
                        "detail": rule["detail"],
                        "marker": rule["marker"],
                        "value": value,
                    })
                    seen_rules.add(rule_key)
            except (ValueError, IndexError):
                continue

    return flags


def analyse_multiple_patients(patients: List[Dict]) -> List[Dict]:
    """
    Analyse a list of patients and return those with risk flags.

    Returns:
        List of dicts: patient data + "risk_flags" key
    """
    results = []
    for patient in patients:
        flags = analyse_patient(patient)
        results.append({**patient, "risk_flags": flags})
    return results
