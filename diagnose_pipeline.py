
import sys
import os

# Ensure project root is on path
ROOT = os.getcwd()
sys.path.insert(0, ROOT)

from agents.coordinator_agent import process_query

def diagnostic_test(query):
    print(f"\nTesting Query: {query}")
    try:
        result = process_query(query)
        if result.get("error"):
            print(f"FAILED: {result['error']}")
        else:
            print("SUCCESS")
            # print(f"Intent: {result['intent']['primary_intent']}")
            # print(f"Response snippet: {result['llm_response'][:50]}...")
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    queries = [
        "What medication is Rahul Sharma taking?",
        "Summarize patient P014.",
        "Which patients have HbA1c above 8?",
        "Show me doctor notes for Amit Kumar"
    ]
    
    for q in queries:
        diagnostic_test(q)
