import os
import sys

# ── Entry Point Telemetry & Linux Fix ──────────────────────────────────────────
print("[API] Starting Hospital RAG Assistant API...")

# SQLite3 override for ChromaDB on Linux (Render/Streamlit Cloud)
if sys.platform.startswith('linux'):
    try:
        __import__('pysqlite3')
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
        print("[API] Successfully applied pysqlite3-binary patch for Linux.")
    except ImportError:
        print("[API] Warning: pysqlite3-binary not found. ChromaDB might fail on old Linux kernels.")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure project root is on path
ROOT = os.path.dirname(__file__)
sys.path.insert(0, ROOT)

print("[API] Loading environment and agents...")
load_dotenv(os.path.join(ROOT, ".env"), override=False)

from agents.coordinator_agent import process_query
from rag.vector_store import build_vector_store
print("[API] Agent modules loaded successfully.")

app = FastAPI(title="Hospital RAG Assistant API")

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.on_event("startup")
def startup_event():
    print("[API] Running startup procedures...")
    # Initialize vector store if not present
    chroma_path = os.path.join(ROOT, "chroma_db")
    if not os.path.exists(chroma_path):
        print("[API] Initializing pre-built vector store bounds...")
        try:
            build_vector_store(force_rebuild=False)
        except Exception as e:
            print(f"[API] Error: Could not auto-init vector store: {e}")
    else:
        print("[API] Pre-built chroma_db found. Skipping rebuild.")
    print("[API] Startup complete. Server ready.")

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
