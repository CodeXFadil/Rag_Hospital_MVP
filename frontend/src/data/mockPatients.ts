
export interface LabResult {
  name: string;
  value: string;
  unit: string;
  normalRange: string;
  status: "normal" | "warning" | "critical";
}

export interface Medication {
  name: string;
  dosage: string;
  frequency: string;
  since: string;
}

export interface Patient {
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
}

export const mockPatients: Record<string, Patient> = {
  "P001": {
    "id": "P001",
    "name": "Rahul Sharma",
    "age": 52,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Type 2 Diabetes",
      "Hypertension"
    ],
    "medications": [
      {
        "name": "Metformin",
        "dosage": "500mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Amlodipine",
        "dosage": "5mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "HbA1c",
        "value": "8.2",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "critical"
      },
      {
        "name": "BP",
        "value": "145/90",
        "unit": "mmHg",
        "normalRange": "See protocol",
        "status": "warning"
      },
      {
        "name": "LDL",
        "value": "142",
        "unit": "mg/dL",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-10",
    "ward": "Diabetes review",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Patient presents with poorly controlled diabetes. HbA1c remains elevated despite medication adherence. Blood pressure is borderline hypertensive. Advised dietary changes and increased physical activity. Follow-up in 4 weeks."
  },
  "P002": {
    "id": "P002",
    "name": "Priya Patel",
    "age": 34,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Asthma"
    ],
    "medications": [
      {
        "name": "Salbutamol",
        "dosage": "inhaler",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Budesonide",
        "dosage": "inhaler",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "Peak Flow",
        "value": "380",
        "unit": "L/min",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "SpO2",
        "value": "97",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-20",
    "ward": "Asthma review",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Patient reports two asthma attacks last month triggered by dust and cold air. Inhaler technique reviewed and corrected. Advised to avoid allergens. Spirometry scheduled for next visit."
  },
  "P003": {
    "id": "P003",
    "name": "Amit Kumar",
    "age": 67,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Coronary Artery Disease",
      "Hyperlipidemia"
    ],
    "medications": [
      {
        "name": "Aspirin",
        "dosage": "75mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Atorvastatin",
        "dosage": "40mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Bisoprolol",
        "dosage": "5mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "LDL",
        "value": "180",
        "unit": "mg/dL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "HDL",
        "value": "38",
        "unit": "mg/dL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "ECG",
        "value": "ST changes",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-01",
    "ward": "Follow-up",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Patient has history of MI three years ago. Current LDL elevated above target. Increased Atorvastatin dose. ECG shows mild ST changes, cardiology referral made. Patient advised to restrict salt and fat intake."
  },
  "P004": {
    "id": "P004",
    "name": "Sunita Verma",
    "age": 45,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Hypothyroidism",
      "Anaemia"
    ],
    "medications": [
      {
        "name": "Levothyroxine",
        "dosage": "50mcg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Ferrous",
        "dosage": "Sulfate 200mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "TSH",
        "value": "6.8",
        "unit": "mIU/L",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Hb",
        "value": "9.2",
        "unit": "g/dL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Iron",
        "value": "42",
        "unit": "mcg/dL",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-28",
    "ward": "Follow-up",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Patient reports fatigue and cold intolerance. TSH elevated suggesting undertreated hypothyroidism. Haemoglobin low consistent with iron deficiency anaemia. Levothyroxine dose adjusted. Iron supplementation continued."
  },
  "P005": {
    "id": "P005",
    "name": "Mohammed Ali",
    "age": 29,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Type 1 Diabetes"
    ],
    "medications": [
      {
        "name": "Insulin",
        "dosage": "Glargine 20U",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Insulin",
        "dosage": "Lispro sliding scale",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "HbA1c",
        "value": "7.9",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "warning"
      },
      {
        "name": "Fasting Glucose",
        "value": "156",
        "unit": "mg/dL",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-05",
    "ward": "Diabetes clinic",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Young patient with Type 1 DM struggling with glycaemic control. Reports difficulty adjusting insulin doses. Continuous glucose monitoring discussed. Dietitian referral made. HbA1c trending upward."
  },
  "P006": {
    "id": "P006",
    "name": "Kavita Singh",
    "age": 58,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Osteoarthritis",
      "Hypertension"
    ],
    "medications": [
      {
        "name": "Ibuprofen",
        "dosage": "400mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Ramipril",
        "dosage": "5mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "BP",
        "value": "138/85",
        "unit": "mmHg",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "ESR",
        "value": "45",
        "unit": "mm/hr",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-08",
    "ward": "Follow-up",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Bilateral knee pain worsening. NSAID use may be causing mild hypertension. Discussed risks of long-term NSAID use. Physiotherapy referral made. BP monitoring advised weekly."
  },
  "P007": {
    "id": "P007",
    "name": "Deepak Joshi",
    "age": 71,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "COPD",
      "Type 2 Diabetes"
    ],
    "medications": [
      {
        "name": "Tiotropium",
        "dosage": "inhaler",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Metformin",
        "dosage": "1000mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Prednisolone",
        "dosage": "5mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "FEV1",
        "value": "48",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "HbA1c",
        "value": "7.4",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "warning"
      },
      {
        "name": "BP",
        "value": "132/80",
        "unit": "mmHg",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-12",
    "ward": "COPD review",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Patient with severe COPD requiring frequent steroid bursts. Corticosteroid-induced glucose elevation noted. HbA1c rising. Pulmonology co-management arranged. Patient counselled on smoking cessation."
  },
  "P008": {
    "id": "P008",
    "name": "Anita Roy",
    "age": 39,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Migraine",
      "Anxiety Disorder"
    ],
    "medications": [
      {
        "name": "Sumatriptan",
        "dosage": "50mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Sertraline",
        "dosage": "50mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "Neurological exam",
        "value": "Normal",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "MRI",
        "value": "No abnormality",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-15",
    "ward": "Neurology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Frequent migraines averaging 6 per month. Trigger diary started. Sertraline for comorbid anxiety. Discussed prophylactic migraine therapy. MRI brain normal. Stress management counselling referred."
  },
  "P009": {
    "id": "P009",
    "name": "Ravi Nair",
    "age": 62,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Chronic Kidney Disease Stage 3",
      "Hypertension"
    ],
    "medications": [
      {
        "name": "Amlodipine",
        "dosage": "10mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Furosemide",
        "dosage": "40mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "eGFR",
        "value": "42",
        "unit": "mL/min",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Creatinine",
        "value": "1.9",
        "unit": "mg/dL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "BP",
        "value": "152/95",
        "unit": "mmHg",
        "normalRange": "See protocol",
        "status": "warning"
      }
    ],
    "lastVisit": "2024-03-06",
    "ward": "Labs",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Patient with progressive CKD. BP poorly controlled. Nephrology referral made. Dietary protein restriction advised. NSAID use contraindicated. ACEi started with close monitoring."
  },
  "P010": {
    "id": "P010",
    "name": "Meena Gupta",
    "age": 55,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Type 2 Diabetes",
      "Dyslipidaemia"
    ],
    "medications": [
      {
        "name": "Glipizide",
        "dosage": "5mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Rosuvastatin",
        "dosage": "10mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "HbA1c",
        "value": "9.1",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "critical"
      },
      {
        "name": "LDL",
        "value": "168",
        "unit": "mg/dL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "TG",
        "value": "220",
        "unit": "mg/dL",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-25",
    "ward": "Endocrinology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Patient with very poorly controlled diabetes and high cardiovascular risk. Intensification of diabetes management discussed. Low-carb diet prescribed. Statin dose increased. Referred to diabetes educator."
  },
  "P011": {
    "id": "P011",
    "name": "Suresh Reddy",
    "age": 48,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Peptic Ulcer Disease",
      "GERD"
    ],
    "medications": [
      {
        "name": "Omeprazole",
        "dosage": "20mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Sucralfate",
        "dosage": "1g",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "H. pylori",
        "value": "Positive",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Endoscopy",
        "value": "1.2",
        "unit": "cm",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-01",
    "ward": "Gastroenterology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "H. pylori eradication therapy initiated: Amoxicillin, Clarithromycin, Omeprazole for 14 days. Patient advised to avoid NSAIDs, alcohol, and spicy food. Repeat endoscopy in 6 weeks."
  },
  "P012": {
    "id": "P012",
    "name": "Lakshmi Iyer",
    "age": 74,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Heart Failure",
      "Atrial Fibrillation"
    ],
    "medications": [
      {
        "name": "Digoxin",
        "dosage": "0.125mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Warfarin",
        "dosage": "5mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Furosemide",
        "dosage": "80mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "BNP",
        "value": "1450",
        "unit": "pg/mL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "INR",
        "value": "2.3",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Echo",
        "value": "35",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-09",
    "ward": "Cardiology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Patient with decompensated heart failure. BNP markedly elevated. Ejection fraction reduced. Fluid overload present. Diuretic dose increased. Strict fluid restriction and daily weight monitoring advised. Cardiology urgent review."
  },
  "P013": {
    "id": "P013",
    "name": "Arun Mishra",
    "age": 36,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Depression",
      "Insomnia"
    ],
    "medications": [
      {
        "name": "Escitalopram",
        "dosage": "10mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Melatonin",
        "dosage": "3mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "PHQ-9 score",
        "value": "16",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Sleep study",
        "value": "Mild sleep apnoea",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-18",
    "ward": "Psychiatry",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Moderate-to-severe depression. PHQ-9 score 16. Sleep study reveals mild OSA. CPAP referral made. Escitalopram dose may need upward titration. CBT referral made. Review in 4 weeks."
  },
  "P014": {
    "id": "P014",
    "name": "Fatima Khan",
    "age": 61,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Type 2 Diabetes",
      "CKD Stage 2",
      "Hypertension"
    ],
    "medications": [
      {
        "name": "Sitagliptin",
        "dosage": "100mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Losartan",
        "dosage": "50mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Amlodipine",
        "dosage": "5mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "HbA1c",
        "value": "7.8",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "warning"
      },
      {
        "name": "eGFR",
        "value": "65",
        "unit": "mL/min",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "BP",
        "value": "140/88",
        "unit": "mmHg",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "LDL",
        "value": "122",
        "unit": "mg/dL",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-05",
    "ward": "Nephrology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Patient with multiple comorbidities requiring close monitoring. Diabetic nephropathy suspected. eGFR slightly reduced. BP on target but HbA1c above goal. Discussed importance of medication adherence. Annual retinal screening arranged."
  },
  "P015": {
    "id": "P015",
    "name": "Vijay Sharma",
    "age": 53,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Gout",
      "Hypertension"
    ],
    "medications": [
      {
        "name": "Allopurinol",
        "dosage": "300mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Ramipril",
        "dosage": "10mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "Uric Acid",
        "value": "9.2",
        "unit": "mg/dL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "BP",
        "value": "142/88",
        "unit": "mmHg",
        "normalRange": "See protocol",
        "status": "warning"
      }
    ],
    "lastVisit": "2024-02-28",
    "ward": "Rheumatology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Recurrent gout attacks in bilateral feet. Uric acid remains elevated despite Allopurinol. Dietary review: excessive red meat and beer intake. Lifestyle counselling given. Ramipril for BP control."
  },
  "P016": {
    "id": "P016",
    "name": "Nisha Kapoor",
    "age": 27,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Polycystic Ovary Syndrome (PCOS)",
      "Insulin Resistance"
    ],
    "medications": [
      {
        "name": "Metformin",
        "dosage": "500mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Oral",
        "dosage": "contraceptive pill",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "Testosterone",
        "value": "78",
        "unit": "ng/dL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Fasting Insulin",
        "value": "24",
        "unit": "mIU/L",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "LH",
        "value": "3.2",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-10",
    "ward": "Gynaecology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Young patient with PCOS, irregular periods, and hirsutism. Insulin resistance noted. Metformin started. Weight loss of 5-10% discussed as first-line treatment. Endocrinology referral pending."
  },
  "P017": {
    "id": "P017",
    "name": "Harish Bose",
    "age": 69,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Prostate Cancer",
      "Hypertension"
    ],
    "medications": [
      {
        "name": "Bicalutamide",
        "dosage": "50mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Leuprolide",
        "dosage": "injection",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Amlodipine",
        "dosage": "5mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "PSA",
        "value": "12.4",
        "unit": "ng/mL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "BP",
        "value": "136/84",
        "unit": "mmHg",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Bone scan",
        "value": "No metastasis",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-03",
    "ward": "Follow-up",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Patient on hormonal therapy for localised prostate cancer. PSA declining from 28 ng/mL. No evidence of metastasis. BP well controlled. Bone health monitoring with DEXA scan arranged."
  },
  "P018": {
    "id": "P018",
    "name": "Rekha Patil",
    "age": 42,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Rheumatoid Arthritis"
    ],
    "medications": [
      {
        "name": "Methotrexate",
        "dosage": "15mg weekly",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Folic",
        "dosage": "acid 5mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "CRP",
        "value": "34",
        "unit": "mg/L",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "ESR",
        "value": "62",
        "unit": "mm/hr",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Anti-CCP",
        "value": "Positive",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-05",
    "ward": "Rheumatology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Active rheumatoid arthritis with elevated inflammatory markers. Joint examination shows swelling of MCP joints bilaterally. Methotrexate dose optimised. Hydroxychloroquine addition considered. Physiotherapy ongoing."
  },
  "P019": {
    "id": "P019",
    "name": "Sunil Das",
    "age": 57,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Liver Cirrhosis",
      "Alcohol Use Disorder"
    ],
    "medications": [
      {
        "name": "Propranolol",
        "dosage": "40mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Spironolactone",
        "dosage": "100mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Lactulose",
        "dosage": "30ml",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "LFTs",
        "value": "78",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "INR",
        "value": "1.6",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Platelets",
        "value": "98",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-07",
    "ward": "Hepatology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Decompensated cirrhosis with ascites. INR elevated indicating poor synthetic function. Advised complete alcohol abstinence. Referred to hepatology. Endoscopy shows grade 2 varices. Ascites management with diuretics."
  },
  "P020": {
    "id": "P020",
    "name": "Pooja Mehta",
    "age": 32,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Systemic Lupus Erythematosus"
    ],
    "medications": [
      {
        "name": "Hydroxychloroquine",
        "dosage": "200mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Prednisolone",
        "dosage": "10mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "Anti-dsDNA",
        "value": "Positive",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Complement C3",
        "value": "Low",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Creatinine",
        "value": "1.1",
        "unit": "mg/dL",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-05",
    "ward": "Nephrology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "SLE with active nephritis. Anti-dsDNA elevated. Renal biopsy planned. Prednisolone dose may need increase. Sun protection and regular monitoring of blood counts and renal function advised."
  },
  "P021": {
    "id": "P021",
    "name": "Kiran Rao",
    "age": 66,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Parkinson's Disease",
      "Depression"
    ],
    "medications": [
      {
        "name": "Levodopa/Carbidopa",
        "dosage": "100/25mg TID",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Ropinirole",
        "dosage": "2mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "UPDRS motor score",
        "value": "28",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "PHQ-9",
        "value": "12",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-01-25",
    "ward": "Neurology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Moderate Parkinson's disease with motor fluctuations. On-off phenomenon noted. Ropinirole added. Mild-moderate depression comorbid. Psychiatry co-management arranged. Physiotherapy for gait and balance."
  },
  "P022": {
    "id": "P022",
    "name": "Geeta Pillai",
    "age": 49,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Thyroid Cancer (Post thyroidectomy)"
    ],
    "medications": [
      {
        "name": "Levothyroxine",
        "dosage": "150mcg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "TSH",
        "value": "0.1",
        "unit": "mIU/L (suppressed)",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Thyroglobulin",
        "value": "0.3",
        "unit": "ng/mL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "CT",
        "value": "No recurrence",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-01",
    "ward": "Oncology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Post-thyroidectomy on suppressive Levothyroxine therapy. TSH appropriately suppressed. Thyroglobulin undetectable. Annual CT neck and chest confirms no recurrence. Patient doing well."
  },
  "P023": {
    "id": "P023",
    "name": "Rajesh Tiwari",
    "age": 55,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Type 2 Diabetes",
      "Peripheral Neuropathy"
    ],
    "medications": [
      {
        "name": "Pregabalin",
        "dosage": "75mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Metformin",
        "dosage": "1000mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Duloxetine",
        "dosage": "30mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "HbA1c",
        "value": "8.6",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "critical"
      },
      {
        "name": "Nerve conduction",
        "value": "Reduced velocity bilateral lower limbs",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-08",
    "ward": "Diabetes",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Symptomatic diabetic peripheral neuropathy. Burning pain in feet managed with Pregabalin and Duloxetine. Foot care education given. Podiatry referral made. Glycaemic control needs improvement."
  },
  "P024": {
    "id": "P024",
    "name": "Asha Nambiar",
    "age": 37,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Epilepsy"
    ],
    "medications": [
      {
        "name": "Sodium",
        "dosage": "Valproate 500mg BD",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "EEG",
        "value": "Generalised spike-wave",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "MRI",
        "value": "Normal",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-01-18",
    "ward": "Neurology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Well-controlled epilepsy on Valproate. Last seizure 18 months ago. Driving restrictions discussed. Pre-conception counselling given as patient planning pregnancy. Folate supplementation started."
  },
  "P025": {
    "id": "P025",
    "name": "Dinesh Chopra",
    "age": 73,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Alzheimer's Disease",
      "Hypertension"
    ],
    "medications": [
      {
        "name": "Donepezil",
        "dosage": "10mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Ramipril",
        "dosage": "5mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "MMSE",
        "value": "16/30",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "BP",
        "value": "134/80",
        "unit": "mmHg",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-22",
    "ward": "Memory Clinic",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Moderate Alzheimer's disease. MMSE declining from 22 last year. BP well controlled. Carer support assessed. Memory clinic referral. Safeguarding assessment completed. Advanced care planning discussion initiated."
  },
  "P026": {
    "id": "P026",
    "name": "Shobha Agarwal",
    "age": 60,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Osteoporosis",
      "Vitamin D Deficiency"
    ],
    "medications": [
      {
        "name": "Alendronate",
        "dosage": "70mg weekly",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Calcium",
        "dosage": "1000mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Cholecalciferol",
        "dosage": "2000IU",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "DEXA",
        "value": "2.8",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Vitamin D",
        "value": "18",
        "unit": "ng/mL",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-04",
    "ward": "Rheumatology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Severe osteoporosis. Prior fragility fracture of wrist. Vitamin D deficient. Bisphosphonate therapy initiated. Calcium and Vitamin D supplementation optimised. Falls risk assessment performed."
  },
  "P027": {
    "id": "P027",
    "name": "Anil Saxena",
    "age": 44,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "HIV/AIDS"
    ],
    "medications": [
      {
        "name": "Biktarvy",
        "dosage": "(Bictegravir/TAF/FTC)",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "CD4",
        "value": "520",
        "unit": "cells/mm3",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Viral Load",
        "value": "Undetectable",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-08",
    "ward": "Infectious Disease",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Patient on effective ART. Viral load undetectable and CD4 count stable. Annual sexually transmitted infection screen performed. Psychosocial support offered. Adherence to ART reinforced."
  },
  "P028": {
    "id": "P028",
    "name": "Chitra Nair",
    "age": 53,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Multiple Sclerosis"
    ],
    "medications": [
      {
        "name": "Glatiramer",
        "dosage": "acetate 20mg daily",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "MRI",
        "value": "2",
        "unit": "new T2 lesions",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "EDSS",
        "value": "3.5",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-01-30",
    "ward": "Neurology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Relapsing-remitting MS with new MRI activity. EDSS score worsening. Switching to higher efficacy therapy discussed. Neuropsychology referral for cognitive symptoms. Bladder symptoms noted."
  },
  "P029": {
    "id": "P029",
    "name": "Manoj Tiwari",
    "age": 48,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Psoriasis",
      "Psoriatic Arthritis"
    ],
    "medications": [
      {
        "name": "Methotrexate",
        "dosage": "20mg weekly",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Adalimumab",
        "dosage": "injection",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "PASI score",
        "value": "8",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "DAS28",
        "value": "3.9",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-06",
    "ward": "Rheumatology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Moderate psoriasis with active psoriatic arthritis. Initiating biologic therapy with Adalimumab. Baseline TB screen and hepatitis serology checked. Monitoring plan established."
  },
  "P030": {
    "id": "P030",
    "name": "Savitha Kumar",
    "age": 38,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Gestational Diabetes (Previous)"
    ],
    "medications": [
      {
        "name": "Metformin",
        "dosage": "500mg (preventative)",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "Fasting Glucose",
        "value": "98",
        "unit": "mg/dL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "HbA1c",
        "value": "5.9",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-14",
    "ward": "Endocrinology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Previous gestational diabetes. Currently not pregnant. Pre-diabetes screening. Fasting glucose borderline. Metformin for prevention. Annual HbA1c monitoring. Lifestyle intervention counselled."
  },
  "P031": {
    "id": "P031",
    "name": "Naresh Jain",
    "age": 65,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Bladder Cancer (Non-invasive)"
    ],
    "medications": [
      {
        "name": "BCG",
        "dosage": "intravesical therapy",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "Cystoscopy",
        "value": "Recurrence of Ta lesion",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-09",
    "ward": "Urology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Superficial bladder cancer, recurrence detected on surveillance cystoscopy. Transurethral resection planned. BCG maintenance therapy to continue. Urology follow-up every 3 months."
  },
  "P032": {
    "id": "P032",
    "name": "Manjula Pillai",
    "age": 70,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Type 2 Diabetes",
      "Cataract"
    ],
    "medications": [
      {
        "name": "Insulin",
        "dosage": "Glargine 30U",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Metformin",
        "dosage": "500mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "HbA1c",
        "value": "7.2",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "warning"
      },
      {
        "name": "Visual acuity",
        "value": "6/18",
        "unit": "both eyes",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-20",
    "ward": "Ophthalmology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Elderly patient with well-managed diabetes and bilateral cataracts reducing vision. Ophthalmology referral for cataract surgery. Diabetes well controlled. Annual diabetic eye review done."
  },
  "P033": {
    "id": "P033",
    "name": "Ramesh Bhat",
    "age": 41,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Anxiety Disorder",
      "IBS"
    ],
    "medications": [
      {
        "name": "Sertraline",
        "dosage": "50mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Mebeverine",
        "dosage": "135mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "Colonoscopy",
        "value": "Normal",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Stool cultures",
        "value": "Negative",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-26",
    "ward": "Gastroenterology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Irritable bowel syndrome with anxiety comorbidity. Psychological element of IBS discussed. Low-FODMAP diet referral. Cognitive behavioural therapy arranged. Mebeverine for symptom control."
  },
  "P034": {
    "id": "P034",
    "name": "Usha Patel",
    "age": 56,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Breast Cancer (Post-lumpectomy)"
    ],
    "medications": [
      {
        "name": "Tamoxifen",
        "dosage": "20mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "CA 15-3",
        "value": "18",
        "unit": "U/mL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Mammogram",
        "value": "No recurrence",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-02",
    "ward": "Oncology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Post-lumpectomy breast cancer surveillance. CA 15-3 within normal limits. Annual mammogram clear. Tamoxifen well tolerated. Bone density monitoring recommended due to tamoxifen use."
  },
  "P035": {
    "id": "P035",
    "name": "Ganesh Menon",
    "age": 59,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Hypertension",
      "Erectile Dysfunction"
    ],
    "medications": [
      {
        "name": "Telmisartan",
        "dosage": "80mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Sildenafil",
        "dosage": "50mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "BP",
        "value": "130/82",
        "unit": "mmHg",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Testosterone",
        "value": "310",
        "unit": "ng/dL",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-22",
    "ward": "Urology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "BP well controlled on ARB. Erectile dysfunction multi-factorial, likely vascular. Testosterone borderline low. Endocrinology referral considered. Lifestyle counselling given. Sildenafil well tolerated."
  },
  "P036": {
    "id": "P036",
    "name": "Hema Krishnan",
    "age": 43,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Fibromyalgia",
      "Depression"
    ],
    "medications": [
      {
        "name": "Duloxetine",
        "dosage": "60mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Amitriptyline",
        "dosage": "25mg (night)",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "Pain score",
        "value": "7/10",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "PHQ-9",
        "value": "14",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "FM score",
        "value": "22",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-05",
    "ward": "Pain Clinic",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Fibromyalgia with significant depressive symptoms. Multidisciplinary approach initiated. Pain management clinic referral. Duloxetine dose optimised. Gentle exercise programme started. Sleep hygiene advice given."
  },
  "P037": {
    "id": "P037",
    "name": "Vinod Mishra",
    "age": 77,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Parkinson's Disease",
      "BPH"
    ],
    "medications": [
      {
        "name": "Levodopa/Carbidopa",
        "dosage": "250/25mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Tamsulosin",
        "dosage": "0.4mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "UPDRS",
        "value": "38",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "PSA",
        "value": "4.1",
        "unit": "ng/mL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Uroflowmetry",
        "value": "Reduced",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-01",
    "ward": "Urology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Advanced Parkinson's with significant motor disability. Urinary symptoms from BPH. Tamsulosin caution due to orthostatic hypotension risk. Urology and Neurology co-management. Palliative care discussion initiated."
  },
  "P038": {
    "id": "P038",
    "name": "Lalita Devi",
    "age": 50,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Chronic Migraine",
      "Hypertension"
    ],
    "medications": [
      {
        "name": "Topiramate",
        "dosage": "50mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Propranolol",
        "dosage": "80mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "BP",
        "value": "128/78",
        "unit": "mmHg",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Neurological exam",
        "value": "Normal",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-18",
    "ward": "Neurology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Chronic migraine with cardiovascular risk. Propranolol serves dual purpose of migraine prophylaxis and BP control. Topiramate added for refractory cases. Mood monitoring due to Topiramate side effect risk."
  },
  "P039": {
    "id": "P039",
    "name": "Santosh Rao",
    "age": 63,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Colorectal Cancer (Stage 2)"
    ],
    "medications": [
      {
        "name": "Post-adjuvant",
        "dosage": "chemotherapy",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "CEA",
        "value": "2.1",
        "unit": "ng/mL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "CT",
        "value": "No recurrence",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Colonoscopy",
        "value": "Clear",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-07",
    "ward": "Oncology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Completed adjuvant FOLFOX chemotherapy 6 months ago. Surveillance CT and colonoscopy negative for recurrence. CEA within normal limits. Oncology follow-up every 6 months."
  },
  "P040": {
    "id": "P040",
    "name": "Bharati Joshi",
    "age": 47,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Chronic Pancreatitis",
      "Type 2 Diabetes"
    ],
    "medications": [
      {
        "name": "Pancreatic",
        "dosage": "enzyme supplements",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Insulin",
        "dosage": "Glargine 18U",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "Amylase",
        "value": "180",
        "unit": "U/L",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "HbA1c",
        "value": "8.8",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "critical"
      },
      {
        "name": "CT",
        "value": "Pancreatic calcifications",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-10",
    "ward": "Gastroenterology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Pancreatogenic diabetes secondary to chronic pancreatitis. HbA1c elevated. Insulin dose adjusted. Enzyme replacement optimised for malabsorption. Alcohol cessation reinforced. Pain management reviewed."
  },
  "P041": {
    "id": "P041",
    "name": "Kamal Verma",
    "age": 35,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Crohn's Disease"
    ],
    "medications": [
      {
        "name": "Azathioprine",
        "dosage": "150mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Infliximab",
        "dosage": "infusion",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "CRP",
        "value": "12",
        "unit": "mg/L",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Calprotectin",
        "value": "280",
        "unit": "mcg/g",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "MRI",
        "value": "Mild ileal activity",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-03",
    "ward": "Gastroenterology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Crohn's disease in partial remission. Mild ileal activity on MRI. Calprotectin mildly elevated. Infliximab levels checked. Dietary review with GI dietitian. Standard monitoring bloods satisfactory."
  },
  "P042": {
    "id": "P042",
    "name": "Jyoti Malhotra",
    "age": 64,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Glaucoma",
      "Hypertension"
    ],
    "medications": [
      {
        "name": "Latanoprost",
        "dosage": "eye drops",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Atenolol",
        "dosage": "50mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "IOP",
        "value": "24",
        "unit": "mmHg both eyes",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "BP",
        "value": "136/86",
        "unit": "mmHg",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-28",
    "ward": "Ophthalmology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Open-angle glaucoma with IOP not adequately controlled. Second eye drop Brimonidine added. Ophthalmology review in 6 weeks. Visual field testing stable. BP management reviewed."
  },
  "P043": {
    "id": "P043",
    "name": "Prakash Singh",
    "age": 58,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Chronic Back Pain",
      "Depression"
    ],
    "medications": [
      {
        "name": "Tramadol",
        "dosage": "50mg PRN",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Amitriptyline",
        "dosage": "25mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "MRI spine",
        "value": "4",
        "unit": "-L5 disc herniation",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "PHQ-9",
        "value": "11",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-15",
    "ward": "Psychiatry",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Chronic low back pain with L4-L5 disc herniation. Opioid use monitored carefully. Physiotherapy and pain clinic referral. Depression managed with Amitriptyline. Surgical opinion pending."
  },
  "P044": {
    "id": "P044",
    "name": "Mira Desai",
    "age": 31,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Ulcerative Colitis"
    ],
    "medications": [
      {
        "name": "Mesalazine",
        "dosage": "2.4g daily",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Prednisolone",
        "dosage": "20mg (reducing)",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "Calprotectin",
        "value": "850",
        "unit": "mcg/g",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Colonoscopy",
        "value": "Moderate-severe pancolitis",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-09",
    "ward": "Gastroenterology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Active moderate-to-severe UC. Prednisolone started for flare. Biological therapy assessment initiated. Nutritional status assessed. Hydration and electrolytes monitored. Stool cultures negative."
  },
  "P045": {
    "id": "P045",
    "name": "Rajan Krishnamurthy",
    "age": 72,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "CKD Stage 4",
      "Anaemia of CKD",
      "Hypertension"
    ],
    "medications": [
      {
        "name": "Erythropoietin",
        "dosage": "injection",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Amlodipine",
        "dosage": "10mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Calcium",
        "dosage": "carbonate",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "eGFR",
        "value": "22",
        "unit": "mL/min",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Hb",
        "value": "8.9",
        "unit": "g/dL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "PTH",
        "value": "180",
        "unit": "pg/mL",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-01-15",
    "ward": "Nephrology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Advanced CKD approaching dialysis threshold. Anaemia managed with ESA. Secondary hyperparathyroidism developing. Dialysis planning initiated. Vascular access assessment for AV fistula. Renal dietitian review."
  },
  "P046": {
    "id": "P046",
    "name": "Shanti Menon",
    "age": 68,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Atrial Fibrillation",
      "Hypertension"
    ],
    "medications": [
      {
        "name": "Rivaroxaban",
        "dosage": "20mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Bisoprolol",
        "dosage": "5mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Amlodipine",
        "dosage": "5mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "INR",
        "value": "/",
        "unit": "A (on NOAC)",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Heart rate",
        "value": "72",
        "unit": "bpm",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "BP",
        "value": "138/84",
        "unit": "mmHg",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-02-25",
    "ward": "Cardiology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Permanent AF managed with rate control. NOAC for stroke prevention. CHA2DS2-VASc score 4. BP moderately controlled. Echocardiogram shows mild left atrial enlargement. Annual cardiology review."
  },
  "P047": {
    "id": "P047",
    "name": "Renu Ahluwalia",
    "age": 44,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Polycythemia Vera"
    ],
    "medications": [
      {
        "name": "Hydroxyurea",
        "dosage": "500mg BD",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Aspirin",
        "dosage": "75mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "Hb",
        "value": "18.2",
        "unit": "g/dL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Hct",
        "value": "54",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "JAK2 mutation",
        "value": "Positive",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-06",
    "ward": "Haematology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Polycythemia vera with JAK2 mutation. Haematocrit above target despite Hydroxyurea. Phlebotomy performed. Venesection schedule adjusted. Splenic enlargement monitored. Thromboembolic risk discussed."
  },
  "P048": {
    "id": "P048",
    "name": "Suresh Nambiar",
    "age": 55,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Chronic Lymphocytic Leukaemia (CLL)",
      "Stage 1"
    ],
    "medications": [
      {
        "name": "Watch",
        "dosage": "and wait (no active treatment)",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "WBC",
        "value": "18000/",
        "unit": "mcL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Lymphocytes",
        "value": "14000/",
        "unit": "mcL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Flow cytometry",
        "value": "5",
        "unit": "+CD23+ B-cells",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-04",
    "ward": "Haematology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Early stage CLL on watch and wait strategy. No symptoms of disease progression. Lymphocyte count stable over past 6 months. Annual staging reassessment. Patient counselled on signs of progression."
  },
  "P049": {
    "id": "P049",
    "name": "Aruna Pillai",
    "age": 52,
    "gender": "Female",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Endometrial Cancer (Stage 1)"
    ],
    "medications": [
      {
        "name": "Post-hysterectomy",
        "dosage": "",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "no",
        "dosage": "adjuvant therapy",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "CA-125",
        "value": "12",
        "unit": "U/mL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "CT pelvis",
        "value": "No recurrence",
        "unit": "",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-04",
    "ward": "Oncology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Post-hysterectomy for Stage 1A endometrial cancer. No adjuvant therapy required. Surveillance CA-125 normal. CT pelvis clear. Weight management counselled as obesity is a risk factor for recurrence."
  },
  "P050": {
    "id": "P050",
    "name": "Balakrishnan Iyer",
    "age": 78,
    "gender": "Male",
    "bloodGroup": "Unknown",
    "diagnoses": [
      "Heart Failure with Reduced EF",
      "CKD Stage 3"
    ],
    "medications": [
      {
        "name": "Sacubitril/Valsartan",
        "dosage": "49/51mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Dapagliflozin",
        "dosage": "10mg",
        "frequency": "As prescribed",
        "since": "2023"
      },
      {
        "name": "Eplerenone",
        "dosage": "25mg",
        "frequency": "As prescribed",
        "since": "2023"
      }
    ],
    "labResults": [
      {
        "name": "BNP",
        "value": "680",
        "unit": "pg/mL",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "Echo",
        "value": "30",
        "unit": "%",
        "normalRange": "See protocol",
        "status": "normal"
      },
      {
        "name": "eGFR",
        "value": "40",
        "unit": "mL/min",
        "normalRange": "See protocol",
        "status": "normal"
      }
    ],
    "lastVisit": "2024-03-10",
    "ward": "Cardiology",
    "attendingDoctor": "Dr. Clinical AI",
    "notes": "Severe heart failure with reduced ejection fraction. Disease-modifying therapy optimised with HFrEF guideline-directed therapy. eGFR stable. Diuresis adequate. Cardiac rehabilitation referral. AICD/CRT evaluation pending."
  }
};

export function searchPatients(query: string): Patient[] {
  const q = query.toLowerCase();
  return Object.values(mockPatients).filter(
    (p) =>
      p.name.toLowerCase().includes(q) ||
      p.id.toLowerCase().includes(q) ||
      p.diagnoses.some((d) => d.toLowerCase().includes(q))
  );
}

export function getPatientById(id: string): Patient | undefined {
  return mockPatients[id.toUpperCase()];
}

export const API_BASE_URL = (
  window.location.hostname === 'localhost' || 
  window.location.hostname === '127.0.0.1' || 
  window.location.hostname.startsWith('192.168.')
) ? 'http://localhost:8000' : '';

export async function fetchAllPatients(): Promise<Patient[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/patients`);
    if (!response.ok) throw new Error('Failed to fetch patients');
    const data = await response.json();
    return data && data.length > 0 ? data : Object.values(mockPatients);
  } catch (error) {
    console.error('Error fetching patients:', error);
    return Object.values(mockPatients); // Fallback to mocks (now contains all 50)
  }
}
