import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure project root is on path
ROOT = os.path.dirname(__file__)
sys.path.insert(0, ROOT)

load_dotenv(os.path.join(ROOT, ".env"), override=False)

from agents.coordinator_agent import process_query
from rag.vector_store import build_vector_store

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
    # Initialize vector store if not present
    chroma_path = os.path.join(ROOT, "chroma_db")
    if not os.path.exists(chroma_path):
        print("Initializing vector store bounds...")
        try:
            build_vector_store(force_rebuild=False)
        except Exception as e:
            print(f"Warning: Could not auto-init vector store: {e}")

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
