import os
import sys
import time
import threading

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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    log(f"[API] Starting uvicorn on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
