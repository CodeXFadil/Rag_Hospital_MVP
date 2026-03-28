# SQL Translation: Detailed 15-Case Analysis

This report provides a step-by-step breakdown of how natural language is converted into clinical insights, verified against the original 5,000-patient hospital dataset.

---

### CASE 1: Patient Census
**Natural Language**: "How many patients are in the database?"

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "aggregations": [{"type": "count", "field": "patients"}]
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT count(DISTINCT patients.patient_id) AS metric_0 
FROM patients
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT count(*) FROM patients
```

---

### CASE 2: Average Age
**Natural Language**: "What is the average age of all patients?"

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "aggregations": [{"type": "avg", "field": "age"}]
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT avg(patients.age) AS metric_0 
FROM patients
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT AVG(age) FROM patients
```

---

### CASE 3: Gender Breakdown
**Natural Language**: "Give me a breakdown of patients by gender."

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "aggregations": [{"type": "count", "field": "patients", "group_by": "gender"}]
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT patients.gender, count(DISTINCT patients.patient_id) AS metric_0 
FROM patients 
GROUP BY patients.gender
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT gender, count(*) FROM patients GROUP BY gender
```

---

### CASE 4: Diagnosis Comparison
**Natural Language**: "How many patients have Heart Failure vs Angina?"

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "filters": {"primary_diagnosis": "Heart Failure or Angina"},
  "aggregations": [{"type": "count", "field": "patients", "group_by": "primary_diagnosis"}]
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT patients.primary_diagnosis, count(DISTINCT patients.patient_id) AS metric_0 
FROM patients 
WHERE lower(patients.primary_diagnosis) LIKE ANY ('%heart failure%', '%angina%') 
GROUP BY patients.primary_diagnosis
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT primary_diagnosis, count(*) FROM patients GROUP BY primary_diagnosis
```

---

### CASE 5: Age by Outcome
**Natural Language**: "What is the average age of Discharged vs Deceased patients?"

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "aggregations": [{"type": "avg", "field": "age", "group_by": "outcome"}]
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT patients.outcome, avg(patients.age) AS metric_0 
FROM patients 
GROUP BY patients.outcome
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT outcome, AVG(age) FROM patients GROUP BY outcome
```

---

### CASE 6: Geriatric Female Filter
**Natural Language**: "How many female patients are over 70 years old?"

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "filters": {"gender": "Female", "age_range": {"min": 71}}
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT count(DISTINCT patients.patient_id) AS metric_0 
FROM patients 
WHERE lower(patients.gender) LIKE 'f' AND patients.age >= 71
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT count(*) FROM patients WHERE gender = 'F' AND age > 70
```

---

### CASE 7: Stay Duration
**Natural Language**: "What is the average length of stay for all patients?"

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "aggregations": [{"type": "avg", "field": "length_of_stay"}]
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT avg(patients.length_of_stay) AS metric_0 
FROM patients
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT AVG(length_of_stay) FROM patients
```

---

### CASE 8: STEMI Population
**Natural Language**: "How many STEMI patients are there?"

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "filters": {"mi_type": "STEMI"}
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT count(DISTINCT patients.patient_id) AS metric_0 
FROM patients 
WHERE lower(patients.mi_type) LIKE 'stemi'
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT count(*) FROM patients WHERE mi_type = 'STEMI'
```

---

### CASE 9: Diagnosis + Outcome Join
**Natural Language**: "Count Heart Failure patients by their outcome."

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "filters": {"diagnoses": ["Heart Failure"]},
  "aggregations": [{"type": "count", "field": "patients", "group_by": "outcome"}]
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT patients.outcome, count(DISTINCT patients.patient_id) AS metric_0 
FROM patients 
JOIN diagnoses ON patients.patient_id = diagnoses.patient_id 
WHERE lower(diagnoses.diagnosis_name) LIKE '%heart failure%' 
GROUP BY patients.outcome
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT outcome, count(*) FROM patients WHERE primary_diagnosis LIKE '%Heart Failure%' GROUP BY outcome
```

---

### CASE 10: Nationality Breakdown
**Natural Language**: "Break down the patient population by nationality."

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "aggregations": [{"type": "count", "field": "patients", "group_by": "nationality"}]
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT patients.nationality, count(DISTINCT patients.patient_id) AS metric_0 
FROM patients 
GROUP BY patients.nationality
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT nationality, count(*) FROM patients GROUP BY nationality
```

---

### CASE 11: BMI Breakdown
**Natural Language**: "How many patients are in each BMI category?"

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "aggregations": [{"type": "count", "field": "patients", "group_by": "bmi_category"}]
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT patients.bmi_category, count(DISTINCT patients.patient_id) AS metric_0 
FROM patients 
GROUP BY patients.bmi_category
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT bmi_category, count(*) FROM patients GROUP BY bmi_category
```

---

### CASE 12: Generic Procedure Count
**Natural Language**: "How many patients underwent a procedure?"

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "aggregations": [{"type": "count", "field": "patients", "group_by": "procedure"}]
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT patients.procedure, count(DISTINCT patients.patient_id) AS metric_0 
FROM patients 
GROUP BY patients.procedure
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT procedure, count(*) FROM patients GROUP BY procedure
```

---

### CASE 13: Admission Trends
**Natural Language**: "How many patients were admitted in each year?"

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "aggregations": [{"type": "count", "field": "patients", "group_by": "admission_year"}]
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT substr(patients.admission_date, 1, 4) AS year, count(DISTINCT patients.patient_id) AS metric_0 
FROM patients 
GROUP BY 1
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT strftime('%Y', admission_date), count(*) FROM patients GROUP BY 1
```

---

### CASE 14: Complex Co-morbidity Filter
**Natural Language**: "Count patients with Angina who are obese."

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["aggregation"],
  "filters": {"primary_diagnosis": "Angina", "bmi_category": "Obese"}
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT count(DISTINCT patients.patient_id) AS metric_0 
FROM patients 
WHERE lower(patients.primary_diagnosis) LIKE '%angina%' 
AND lower(patients.bmi_category) LIKE 'obese'
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT count(*) FROM patients WHERE primary_diagnosis LIKE '%Angina%' AND bmi_category = 'Obese'
```

---

### CASE 15: Individual Patient Lookup
**Natural Language**: "Get details for patient P00001."

**Step 1: LLM-Generated Intent**
```json
{
  "intents": ["lookup"],
  "filters": {"patient_id": "P00001"}
}
```

**Step 2: SQL Generated from Intent**
```sql
SELECT * FROM patients WHERE lower(patients.patient_id) LIKE 'p00001'
```

**Step 3: Verification SQL (Manual)**
```sql
SELECT * FROM patients WHERE patient_id = 'P00001'
```
