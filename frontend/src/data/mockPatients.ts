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
  P001: {
    id: "P001",
    name: "Rahul Sharma",
    age: 52,
    gender: "Male",
    bloodGroup: "B+",
    diagnoses: ["Type 2 Diabetes Mellitus", "Hypertension", "Dyslipidemia"],
    medications: [
      { name: "Metformin", dosage: "500 mg", frequency: "Twice daily", since: "2021-03" },
      { name: "Amlodipine", dosage: "5 mg", frequency: "Once daily", since: "2022-01" },
      { name: "Atorvastatin", dosage: "20 mg", frequency: "Once nightly", since: "2022-01" },
      { name: "Glimepiride", dosage: "2 mg", frequency: "Once daily", since: "2023-06" },
    ],
    labResults: [
      { name: "HbA1c", value: "9.2", unit: "%", normalRange: "< 7.0", status: "critical" },
      { name: "Blood Pressure", value: "148/92", unit: "mmHg", normalRange: "< 130/80", status: "warning" },
      { name: "Total Cholesterol", value: "210", unit: "mg/dL", normalRange: "< 200", status: "warning" },
      { name: "Fasting Glucose", value: "186", unit: "mg/dL", normalRange: "70–100", status: "critical" },
      { name: "eGFR", value: "68", unit: "mL/min", normalRange: "> 60", status: "normal" },
    ],
    lastVisit: "2025-02-14",
    ward: "Endocrinology OPD",
    attendingDoctor: "Dr. Priya Menon",
    notes: "Patient reports poor dietary compliance. Recommended diabetologist consultation and lifestyle modification program. Consider insulin initiation if HbA1c remains above 9 at next visit.",
  },
  P014: {
    id: "P014",
    name: "Anita Desai",
    age: 67,
    gender: "Female",
    bloodGroup: "O+",
    diagnoses: ["Chronic Kidney Disease Stage 3", "Anemia of Chronic Disease", "Hypertension"],
    medications: [
      { name: "Erythropoietin", dosage: "4000 IU", frequency: "3x/week SC", since: "2023-09" },
      { name: "Ferrous Sulfate", dosage: "325 mg", frequency: "Once daily", since: "2023-09" },
      { name: "Lisinopril", dosage: "10 mg", frequency: "Once daily", since: "2020-05" },
      { name: "Furosemide", dosage: "40 mg", frequency: "Once daily", since: "2024-01" },
    ],
    labResults: [
      { name: "Hemoglobin", value: "8.4", unit: "g/dL", normalRange: "12.0–16.0", status: "critical" },
      { name: "Creatinine", value: "2.1", unit: "mg/dL", normalRange: "0.5–1.1", status: "critical" },
      { name: "eGFR", value: "32", unit: "mL/min", normalRange: "> 60", status: "warning" },
      { name: "Blood Pressure", value: "138/86", unit: "mmHg", normalRange: "< 130/80", status: "warning" },
      { name: "Potassium", value: "4.8", unit: "mEq/L", normalRange: "3.5–5.0", status: "normal" },
    ],
    lastVisit: "2025-03-01",
    ward: "Nephrology OPD",
    attendingDoctor: "Dr. Kavitha Rao",
    notes: "CKD progression noted. Nephrology follow-up every 3 months. Dietary phosphorus and potassium restriction advised. Patient awaiting renal function reassessment.",
  },
  P022: {
    id: "P022",
    name: "Mohammed Al-Hassan",
    age: 44,
    gender: "Male",
    bloodGroup: "A+",
    diagnoses: ["Coronary Artery Disease", "Post-PTCA (2023)", "Hyperlipidemia"],
    medications: [
      { name: "Aspirin", dosage: "75 mg", frequency: "Once daily", since: "2023-04" },
      { name: "Clopidogrel", dosage: "75 mg", frequency: "Once daily", since: "2023-04" },
      { name: "Rosuvastatin", dosage: "40 mg", frequency: "Once nightly", since: "2023-04" },
      { name: "Metoprolol", dosage: "25 mg", frequency: "Twice daily", since: "2023-04" },
      { name: "Ramipril", dosage: "5 mg", frequency: "Once daily", since: "2023-04" },
    ],
    labResults: [
      { name: "LDL Cholesterol", value: "62", unit: "mg/dL", normalRange: "< 70 (post-CAD)", status: "normal" },
      { name: "HbA1c", value: "5.8", unit: "%", normalRange: "< 7.0", status: "normal" },
      { name: "Blood Pressure", value: "124/78", unit: "mmHg", normalRange: "< 130/80", status: "normal" },
      { name: "Troponin I", value: "0.01", unit: "ng/mL", normalRange: "< 0.04", status: "normal" },
      { name: "NT-proBNP", value: "180", unit: "pg/mL", normalRange: "< 300", status: "normal" },
    ],
    lastVisit: "2025-02-28",
    ward: "Cardiology OPD",
    attendingDoctor: "Dr. Arjun Nair",
    notes: "Good recovery post-PTCA. All parameters stable. Dual antiplatelet therapy to continue for 12 months total. Cardiac rehab program compliance good.",
  },
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

// Generates mock AI responses based on query
export function generateAIResponse(query: string): { text: string; patientId?: string } {
  const q = query.toLowerCase();

  // Check for patient name mentions
  for (const patient of Object.values(mockPatients)) {
    const firstName = patient.name.split(" ")[0].toLowerCase();
    const lastName = patient.name.split(" ").slice(-1)[0].toLowerCase();
    if (
      q.includes(firstName) ||
      q.includes(lastName) ||
      q.includes(patient.id.toLowerCase())
    ) {
      return {
        patientId: patient.id,
        text: generatePatientResponse(patient, query),
      };
    }
  }

  // HbA1c query
  if (q.includes("hba1c") && (q.includes("above") || q.includes("high") || q.includes("greater"))) {
    const elevated = Object.values(mockPatients).filter((p) =>
      p.labResults.some(
        (l) => l.name === "HbA1c" && l.status !== "normal"
      )
    );
    return {
      text: `## Patients with Elevated HbA1c\n\nThe following patients have HbA1c levels above the recommended threshold of **7.0%**:\n\n${elevated
        .map(
          (p) =>
            `- **${p.name}** (${p.id}) — HbA1c: **${p.labResults.find((l) => l.name === "HbA1c")?.value}%** ⚠️ ${p.labResults.find((l) => l.name === "HbA1c")?.status === "critical" ? "🔴 Critical" : "🟡 Elevated"}`
        )
        .join("\n")}\n\n> These patients may require medication adjustment or intensified lifestyle interventions. Please review their care plans.`,
    };
  }

  // Generic / unknown query
  return {
    text: `## Query Result\n\nI wasn't able to find a specific match for your query in the current patient records. Here's what I can help you with:\n\n- **Patient lookup** — Try "Summarize patient P001" or ask by patient name\n- **Lab queries** — E.g., "Which patients have HbA1c above 8?"\n- **Medication info** — E.g., "What medications is Rahul taking?"\n\nAvailable patients in the system: **${Object.values(mockPatients)
      .map((p) => `${p.name} (${p.id})`)
      .join(", ")}**`,
  };
}

function generatePatientResponse(patient: Patient, _query: string): string {
  const criticalLabs = patient.labResults.filter((l) => l.status === "critical");
  const warningLabs = patient.labResults.filter((l) => l.status === "warning");

  return `## Patient Summary — ${patient.name} (${patient.id})

### 👤 Patient Overview
**${patient.name}** is a **${patient.age}-year-old ${patient.gender}** (Blood Group: ${patient.bloodGroup}) currently under the care of **${patient.attendingDoctor}** in the **${patient.ward}**. Last visit recorded on **${patient.lastVisit}**.

### 🩺 Active Diagnoses
${patient.diagnoses.map((d) => `- ${d}`).join("\n")}

### 💊 Current Medications
${patient.medications
  .map((m) => `- **${m.name}** ${m.dosage} — ${m.frequency} *(since ${m.since})*`)
  .join("\n")}

### 🔬 Recent Lab Results
${patient.labResults
  .map(
    (l) =>
      `- **${l.name}**: ${l.value} ${l.unit} *(Normal: ${l.normalRange})* ${
        l.status === "critical" ? "🔴 Critical" : l.status === "warning" ? "🟡 Elevated" : "✅ Normal"
      }`
  )
  .join("\n")}

### 📋 Clinical Notes
${patient.notes}

### ⚠️ Risk Indicators
${
  criticalLabs.length > 0
    ? `**Critical values requiring immediate attention:** ${criticalLabs.map((l) => `${l.name} (${l.value} ${l.unit})`).join(", ")}`
    : ""
}
${
  warningLabs.length > 0
    ? `**Elevated values requiring monitoring:** ${warningLabs.map((l) => `${l.name} (${l.value} ${l.unit})`).join(", ")}`
    : ""
}
${criticalLabs.length === 0 && warningLabs.length === 0 ? "All lab values within normal range. ✅" : ""}`;
}
export const API_BASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';

export async function fetchAllPatients(): Promise<Patient[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/patients`);
    if (!response.ok) throw new Error('Failed to fetch patients');
    return await response.json();
  } catch (error) {
    console.error('Error fetching patients:', error);
    return Object.values(mockPatients); // Fallback to mocks
  }
}
