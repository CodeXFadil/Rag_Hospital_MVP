import os
import sys
import time
import threading

# PRE-EMPTIVE IMPORTS: Ensure these are in the namespace before secondary AI libraries load
try:
    import torch
    import torch.nn as nn
    print(f"[API] Torch {torch.__version__} initialized pre-emptively.", flush=True)
except Exception as e:
    print(f"[API] Pre-emptive torch import skipped: {e}", flush=True)

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

app = FastAPI(title="Hospital RAG Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

# Lazy-load the heavy stuff with background warmup
rag_pipeline = None
is_warming_up = False

def warmup_task():
    global rag_pipeline, is_warming_up
    is_warming_up = True
    try:
        import gc
        start_time = time.time()
        log("[WARMUP] V3.5 ULTRA-LITE: Starting optimized sequence...")
        
        log("[WARMUP] Importing coordinator_agent...")
        from agents.coordinator_agent import process_query
        rag_pipeline = process_query
        
        # Force GC to clear import overhead
        gc.collect()
        
        log("[WARMUP] Triggering first-time model load...")
        from rag.retriever import _get_model
        _get_model() 
        
        gc.collect()
        log("[WARMUP] SentenceTransformer loaded and memory cleared.")
        
        log("[WARMUP] Triggering ChromaDB initialization...")
        from rag.retriever import _get_collection
        _get_collection()
        
        gc.collect()
        log("[WARMUP] ChromaDB initialized.")
        
        log(f"[WARMUP] V3.9: RAG completely ready in {time.time() - start_time:.2f}s")
    except Exception as e:
        log(f"[WARMUP] Error during V3.9 warmup: {e}")
        import traceback
        log(traceback.format_exc())
    finally:
        is_warming_up = False

@app.on_event("startup")
async def startup_event():
    log("[API] V3.9 LIVE: Application startup event triggered.")
    log(f"[API] Port: {os.environ.get('PORT', '8000')}")
    # Start background loading immediately
    threading.Thread(target=warmup_task, daemon=True).start()
    log("[API] Server is now listening. V3.9 Initializing...")

@app.get("/")
def read_root():
    return {
        "message": "Hospital RAG API is running (Optimized for Railway)",
        "version": "3.9",
        "endpoints": ["/health", "/api/chat (POST)"]
    }

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "version": "3.9",
        "rag_ready": rag_pipeline is not None,
        "warming_up": is_warming_up
    }

@app.post("/api/chat")
async def chat_endpoint(request: QueryRequest):
    global rag_pipeline
    log(f"[API] Received query: {request.query[:50]}...")
    
    try:
        # Wait for warmup if it's still running (up to 30s to avoid Render timeout)
        wait_start = time.time()
        while rag_pipeline is None and is_warming_up and (time.time() - wait_start < 25):
            log("[API] Warmup in progress, waiting...")
            time.sleep(2)
            
        if rag_pipeline is None:
            if is_warming_up:
                raise HTTPException(status_code=503, detail="AI is still warming up. Please try again in a few seconds.")
            else:
                log("[API] RAG was never loaded. Attempting emergency load...")
                from agents.coordinator_agent import process_query
                rag_pipeline = process_query

        t_process_start = time.time()
        result = rag_pipeline(request.query)
        t_process_end = time.time()
        
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
    Returns a list of all patients formatted for the React frontend.
    This parses the semi-structured CSV data into clean JSON.
    """
    from agents.patient_data_agent import get_all_patients
    from agents.clinical_reasoning_agent import RULES
    import re
    
    patients_from_db = get_all_patients()
    patients_list = []
    
    for row in patients_from_db:
        p_id = str(row["patient_id"])
        
        # 1. Parse Medications
        med_list = []
        raw_meds = str(row.get("medications", ""))
        for m in raw_meds.split(","):
            m = m.strip()
            if m:
                # Heuristic: split name and dosage
                parts = m.split(" ")
                name = parts[0]
                dosage = " ".join(parts[1:]) if len(parts) > 1 else ""
                med_list.append({
                    "name": name,
                    "dosage": dosage,
                    "frequency": "As prescribed",
                    "since": "2023"
                })
        
        # 2. Parse Lab Results
        lab_list = []
        raw_labs = str(row.get("lab_results", ""))
        # Split by comma (e.g., "HbA1c: 8.2%, BP: 145/90 mmHg")
        for l_item in raw_labs.split(","):
            l_item = l_item.strip()
            if ":" in l_item:
                name_val = l_item.split(":", 1)
                name = name_val[0].strip()
                val_unit = name_val[1].strip()
                
                # Split value and unit (e.g. "8.2%", "145/90 mmHg")
                v_match = re.search(r"([0-9\./]+)\s*(.*)", val_unit)
                value = v_match.group(1) if v_match else val_unit
                unit = v_match.group(2) if v_match else ""
                
                # Status determination using clinical rules
                status = "normal"
                for rule in RULES:
                    if rule["marker"] in name or name in rule["marker"]:
                        try:
                            # Rule pattern might be specific like BP systolic
                            r_match = re.search(rule["pattern"], l_item, re.IGNORECASE)
                            if r_match:
                                r_val = float(r_match.group(1))
                                triggered = (
                                    (rule["condition"] == "above" and r_val > rule["threshold"]) or
                                    (rule["condition"] == "below" and r_val < rule["threshold"])
                                )
                                if triggered:
                                    status = "critical" if "🔴" in rule["flag"] else "warning"
                        except:
                            pass
                
                lab_list.append({
                    "name": name,
                    "value": value,
                    "unit": unit,
                    "normalRange": "See protocol",
                    "status": status
                })
        
        # 3. Parse Metadata (Ward, Doctor from visit history or general)
        vh = str(row.get("visit_history", ""))
        last_visit = vh.split(";")[-1].split(":")[0].strip() if vh else "2024"
        ward = vh.split(":")[-1].strip() if ":" in vh else "General OPD"
        
        patients_list.append({
            "id": p_id,
            "name": row["name"],
            "age": int(row["age"]),
            "gender": row["gender"],
            "bloodGroup": "Unknown", # Not in CSV
            "diagnoses": [d.strip() for d in str(row["diagnoses"]).split(",")],
            "medications": med_list,
            "labResults": lab_list,
            "lastVisit": last_visit,
            "ward": ward,
            "attendingDoctor": "Dr. Clinical AI",
            "notes": row["doctor_notes"]
        })
        
    return patients_list

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    log(f"[API] Starting uvicorn on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
