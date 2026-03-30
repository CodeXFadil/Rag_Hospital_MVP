import os
import sys
import time

# Apply SQLite patch BEFORE anything else
try:
    from patch_sqlite import apply_patch
    apply_patch()
except Exception as e:
    print(f"[API] Failed to import/apply patch: {e}", flush=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Force unbuffered output so logs show up immediately on Render
def log(msg):
    print(f"{msg}", flush=True)

log("[API] Script initiated...")

# Path setup
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
load_dotenv(os.path.join(ROOT, ".env"))

app = FastAPI(title="Hospital Structured Retrieval API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

# Entry point for the coordinator
from agents.coordinator_agent import process_query
rag_pipeline = process_query

@app.on_event("startup")
async def startup_event():
    log("[API] V1.0 LEAN: Application startup event triggered.")
    log(f"[API] Port: {os.environ.get('PORT', '8000')}")
    log("[API] Server is now listening. Ready for structured queries.")

@app.get("/")
def read_root():
    return {
        "message": "Hospital Structured Retrieval API is running",
        "version": "1.0-LEAN",
        "endpoints": ["/health", "/api/chat (POST)", "/api/patients (GET)"]
    }

@app.get("/health")
def health():
    import os
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_debug.log")
    return {
        "status": "ok", 
        "version": "1.0-lean",
        "ready": True,
        "logging_active": True,
        "log_size_bytes": os.path.getsize(log_file) if os.path.exists(log_file) else 0
    }

@app.post("/api/clear-logs")
def clear_logs_endpoint():
    from agents.logger import clear_logs
    clear_logs()
    return {"status": "logs cleared"}

@app.post("/api/chat")
async def chat_endpoint(request: QueryRequest):
    log(f"[API] Received query: {request.query[:50]}...")
    
    try:
        t_process_start = time.time()
        result = rag_pipeline(request.query)
        
        if isinstance(result, dict) and result.get("error"):
            log(f"[API] Backend error: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Add server-side overhead timing
        if isinstance(result, dict) and "timings" in result:
            result["timings"]["server_total"] = round(time.time() - t_process_start, 3)
            log(f"[API] Timings: {result['timings']}")

        log(f"[API] Successfully processed query in {time.time() - t_process_start:.2f}s")
        return result
    except Exception as e:
        log(f"[API] Exception during chat: {e}")
        import traceback
        log(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patients")
def get_patients_endpoint():
    """
    Returns all patients directly from the structured SQLite database.
    """
    from agents.patient_data_agent import get_all_patients
    
    # 1. Fetch from database using SQLAlchemy models
    patients_from_db = get_all_patients()
    patients_list = []
    
    for p in patients_from_db:
        # Map flat SQL columns to the nested structure the frontend expects
        patients_list.append({
            "id": str(p["patient_id"]),
            "name": p["name"],
            "age": int(p["age"]),
            "gender": p["gender"],
            "bloodGroup": "Unknown",
            "diagnoses": [d.strip() for d in str(p.get("diagnoses", "")).split(",") if d.strip()],
            "medications": [
                {"name": m.split()[0], "dosage": " ".join(m.split()[1:]), "frequency": "As prescribed", "since": "2024"}
                for m in str(p.get("medications", "")).split(",") if m.strip()
            ],
            "labResults": [
                {"name": l.split(":")[0].strip(), "value": l.split(":")[1].strip(), "unit": "", "status": "normal"}
                for l in str(p.get("lab_results", "")).split(",") if ":" in l
            ],
            "lastVisit": "2024",
            "ward": "General Ward",
            "attendingDoctor": "Dr. Clinical AI",
            "notes": p.get("doctor_notes", "")
        })
        
    return patients_list

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    log(f"[API] Starting uvicorn on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    log(f"[API] Starting uvicorn on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
