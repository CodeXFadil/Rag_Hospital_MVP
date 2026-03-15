from agents.coordinator_agent import process_query
import json

test_queries = [
    "How many male patients are there?",
    "Find patients over 60 with HbA1c > 8.0",
    "Who is taking Metformin?",
    "Show me females under 40.",
    "Summarize Rahul Sharma's record."
]

print("=== SQL MIGRATION VERIFICATION ===\n")

for q in test_queries:
    print(f"Query: {q}")
    result = process_query(q)
    
    intent = result.get("intent", {})
    patient_count = len(result.get("patients", []))
    
    print(f"  Detected Intent: {intent.get('primary_intent')}")
    print(f"  Patients Found: {patient_count}")
    
    if patient_count > 0:
        found_names = [p['name'] for p in result['patients'][:3]]
        print(f"  Sample Results: {', '.join(found_names)}")
    
    print(f"  LLM Response: {result['llm_response'][:100]}...")
    print("-" * 50)
