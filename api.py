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
        start_time = time.time()
        log("[WARMUP] V3.3: Pre-loading RAG components...")
        
        log("[WARMUP] Importing coordinator_agent...")
        from agents.coordinator_agent import process_query
        log("[WARMUP] coordinator_agent imported.")
        
        rag_pipeline = process_query
        
        log("[WARMUP] Initializing SentenceTransformer model...")
        from rag.retriever import _get_model
        _get_model() # Trigger actual loading
        log("[WARMUP] SentenceTransformer model loaded.")
        
        log(f"[WARMUP] RAG completely ready in {time.time() - start_time:.2f}s")
    except Exception as e:
        log(f"[WARMUP] Error during background loading: {e}")
        import traceback
        log(traceback.format_exc())
    finally:
        is_warming_up = False

@app.on_event("startup")
async def startup_event():
    log("[API] V3.3 LIVE: Application startup event triggered.")
    log(f"[API] Port: {os.environ.get('PORT', '8000')}")
    # Start background loading immediately
    threading.Thread(target=warmup_task, daemon=True).start()
    log("[API] Server is now listening. V3.3 Warmup initiated.")

@app.get("/")
def read_root():
    return {
        "message": "Hospital RAG API is running",
        "version": "3.3",
        "endpoints": ["/health", "/api/chat (POST)"]
    }

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "version": "3.3",
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

        result = rag_pipeline(request.query)
        if isinstance(result, dict) and result.get("error"):
            log(f"[API] Backend error: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        log(f"[API] Successfully processed query.")
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
