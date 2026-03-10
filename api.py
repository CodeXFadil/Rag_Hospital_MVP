import os
import sys
import time

# Force unbuffered output so logs show up immediately on Render
def log(msg):
    print(f"{msg}", flush=True)

log("[API] Script initiated...")

# SQLite3 override for ChromaDB on Linux
if sys.platform.startswith('linux'):
    try:
        import pysqlite3
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
        log("[API] SQLite patch applied.")
    except Exception as e:
        log(f"[API] SQLite patch skipped: {e}")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Path setup
ROOT = os.path.dirname(__file__)
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

# Lazy-load the heavy stuff
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    log("[API] Application startup event triggered.")
    log(f"[API] Port: {os.environ.get('PORT', '8000')}")
    # We don't load the RAG here yet to ensure the port binds INSTANTLY.
    # The first request might be slow, but it's better than a timeout.
    log("[API] Server is now listening. RAG will lazy-load on first request.")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/chat")
async def chat_endpoint(request: QueryRequest):
    global rag_pipeline
    try:
        if rag_pipeline is None:
            log("[API] Lazy-loading RAG pipeline...")
            from agents.coordinator_agent import process_query
            rag_pipeline = process_query
            log("[API] RAG pipeline loaded.")
        
        result = rag_pipeline(request.query)
        return result
    except Exception as e:
        log(f"[API] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Render sets the PORT environment variable automatically
    port = int(os.environ.get("PORT", 8000))
    log(f"[API] Manual uvicorn start on port {port}...")
    uvicorn.run("api:app", host="0.0.0.0", port=port, log_level="info")

@app.post("/api/chat")
async def chat_endpoint(request: QueryRequest):
    try:
        # Pass the query to the RAG backend
        result = process_query(request.query)
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # uvicorn api:app --reload
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
