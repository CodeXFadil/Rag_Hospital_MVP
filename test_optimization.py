import os
import sys
import time

# Set up paths
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# Mock dependencies to avoid environment-specific errors (e.g. posthog in Python 3.8)
from unittest.mock import MagicMock

# Create mock data
MOCK_PATIENT = {
    "patient_id": "P001",
    "name": "Rahul Sharma",
    "age": 52,
    "gender": "Male",
    "diagnoses": "Type 2 Diabetes, Hypertension",
    "medications": "Metformin 500mg, Amlodipine 5mg",
    "lab_results": "HbA1c: 8.2%, BP: 145/90 mmHg, LDL: 142 mg/dL",
    "visit_history": "2023-10-12: Routine checkup"
}

MOCK_NOTES = [
    {"text": "Patient reports good compliance with Metformin.", "patient_id": "P001", "name": "Rahul Sharma", "score": 0.9}
]

# Apply mocks
import agents.patient_data_agent
agents.patient_data_agent.find_patient = MagicMock(return_value=[MOCK_PATIENT])
agents.patient_data_agent.find_patients_by_lab_threshold = MagicMock(return_value=[MOCK_PATIENT])

import agents.notes_agent
agents.notes_agent.get_relevant_notes = MagicMock(return_value=MOCK_NOTES)

import rag.retriever
rag.retriever.retrieve = MagicMock(return_value=MOCK_NOTES)

from agents.coordinator_agent import process_query

def test_query(query, log_file):
    log_file.write(f"\n--- Testing Query: {query} ---\n")
    start = time.time()
    result = process_query(query)
    end = time.time()
    
    if result.get("error"):
        log_file.write(f"Error: {result['error']}\n")
    else:
        log_file.write(f"Intent: {result['intent']['primary_intent']}\n")
        log_file.write(f"Response:\n{result['llm_response']}\n")
        log_file.write(f"Time Taken: {end-start:.2f}s\n")
    log_file.write("-" * 30 + "\n")

if __name__ == "__main__":
    with open("test_results.txt", "w", encoding="utf-8") as f:
        # Test 1: Population Query (Should NOT show generalized risk indicators)
        test_query("Which patients have HbA1c above 8?", f)
        
        # Test 2: Specific Risk Query (Should show risk indicators)
        test_query("Are there any risks for Rahul Sharma?", f)
        
        # Test 3: Summary Query (Should show risk indicators)
        test_query("Give me a summary for Rahul Sharma.", f)

        # Test 4: Medication Query (Should NOT show risk indicators)
        test_query("What medication is Rahul Sharma taking?", f)
        
    print("Tests completed. Results saved to test_results.txt")
