
import sys
import os
import json

# Ensure project root is on path
ROOT = os.getcwd()
sys.path.insert(0, ROOT)

# Force reload of the agent to ensure we aren't using cached bytecode
import importlib
import agents.coordinator_agent
importlib.reload(agents.coordinator_agent)
from agents.coordinator_agent import process_query

def diagnostic_test(query):
    print(f"\n{'='*20}")
    print(f"Testing Query: {query}")
    print(f"{'='*20}")
    try:
        result = process_query(query)
        if result.get("error"):
            print(f"PIPELINE ERROR RETURNED: {result['error']}")
        else:
            print("PIPELINE STATUS: SUCCESS")
            print("\n--- LLM RESPONSE OVERVIEW ---")
            print(result.get("llm_response", "NO LLM RESPONSE FOUND"))
            print("\n--- DATA OVERVIEW ---")
            print(f"Patients Found: {len(result.get('patients', []))}")
            print(f"Notes Found: {len(result.get('notes', []))}")
            print(f"Risk Flags: {len(result.get('risk_flags', []))}")
    except Exception as e:
        print(f"CRASHED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # The user specifically requested this query
    diagnostic_test("Summarize patient P014.")
