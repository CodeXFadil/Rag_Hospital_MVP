
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
    results_file = "diagnostic_results.txt"
    with open(results_file, "w", encoding="utf-8") as f:
        f.write(f"Testing Query: {query}\n")
        f.write("="*30 + "\n")
        try:
            result = process_query(query)
            if result.get("error"):
                f.write(f"PIPELINE ERROR: {result['error']}\n")
            else:
                f.write("PIPELINE STATUS: SUCCESS\n\n")
                f.write("--- LLM RESPONSE ---\n")
                f.write(result.get("llm_response", "No response") + "\n\n")
                f.write("--- INTERNAL DATA ---\n")
                f.write(f"Intent: {result.get('intent', {}).get('primary_intent')}\n")
                f.write(f"Patients: {len(result.get('patients', []))}\n")
                f.write(f"Notes: {len(result.get('notes', []))}\n")
        except Exception as e:
            f.write(f"CRASHED: {e}\n")
            import traceback
            f.write(traceback.format_exc())
    
    print(f"Results written to {results_file}")

if __name__ == "__main__":
    diagnostic_test("Summarize patient P014.")
