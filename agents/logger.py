import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app_debug.log")

def log_step(step_name, data):
    """Logs a specific step with a timestamp and formatted data."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"\n{'='*20} {step_name} ({timestamp}) {'='*20}\n"
    
    # Ensure data is stringified if it's a dict/list
    if isinstance(data, (dict, list)):
        import json
        formatted_data = json.dumps(data, indent=2)
    else:
        formatted_data = str(data)
        
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(header)
        f.write(formatted_data)
        f.write("\n")
    
    # Also print to console for real-time visibility
    print(f"[LOG][{step_name}] {formatted_data[:100]}...", flush=True)

def clear_logs():
    """Clears the log file."""
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
