import os
import json
import traceback
from agents.router_agent import classify_intent

query = "Find patients over 60 with HbA1c > 8 and on Metformin."
try:
    result = classify_intent(query)
    print("\nFINAL RESULT:")
    print(json.dumps(result, indent=4))
except Exception:
    traceback.print_exc()
