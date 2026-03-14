from agents.coordinator_agent import process_query
import json

test_queries = [
    "Find patients over 60 with HbA1c > 8 and on Metformin.",
    "Who has high blood pressure (BP > 160)?",
    "Show me males under 40.",
    "Which patients are taking Amlodipine?",
    "Summarize Rahul Sharma's status."
]

print("=== ADVANCED STRUCTURED QUERY VERIFICATION ===\n")

for q in test_queries:
    print(f"Query: {q}")
    result = process_query(q)
    intent = result.get("intent", {})
    entities = intent.get("entities", {})
    patient_count = len(result.get("patients", []))
    
    print(f"  Detected Intent: {intent.get('primary_intent')}")
    print(f"  Extracted Entities: {json.dumps(entities, indent=4)}")
    print(f"  Patients Found: {patient_count}")
    
    if patient_count > 0:
        found_names = [p['name'] for p in result['patients'][:3]]
        print(f"  Found (first 3): {', '.join(found_names)}")
    else:
        print("  No patients found for these exact criteria.")
    print("-" * 50)
