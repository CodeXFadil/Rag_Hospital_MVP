# 🏥 Hospital Patient Records RAG Assistant

A multi-agent, hybrid RAG (Retrieval-Augmented Generation) AI assistant for querying hospital patient records in natural language.

Built with **ChromaDB** (vector search), **sentence-transformers** (embeddings), **OpenRouter LLM** (meta-llama/llama-3-8b-instruct), and **Streamlit** UI.

---

## Architecture

```
User Query
    ↓
Router Agent  (intent classification)
    ↓
Patient Data Agent     +    Clinical Notes RAG Agent
(structured CSV/pandas)     (ChromaDB semantic search)
    ↓                              ↓
Clinical Reasoning Agent  (rule-based risk flags)
    ↓
Coordinator Agent  →  OpenRouter LLM  →  Final Response
```

---

## Project Structure

```
Medical Rag MVP/
├── data/
│   └── patients.csv          # 50 synthetic patient records
├── agents/
│   ├── router_agent.py       # Intent classification & routing
│   ├── patient_data_agent.py # Structured CSV retrieval
│   ├── notes_agent.py        # Semantic notes retrieval
│   ├── clinical_reasoning_agent.py  # Rule-based risk analysis
│   └── coordinator_agent.py  # Orchestration + LLM synthesis
├── rag/
│   ├── vector_store.py       # ChromaDB ingestion & embedding
│   └── retriever.py          # Semantic similarity retrieval
├── ui/
│   └── app.py                # Streamlit web interface
├── chroma_db/                # Auto-created vector database (gitignored)
├── .env.example              # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd "Medical Rag MVP"
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure OpenRouter API Key

Copy the example env file and add your key:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Get your API key at [openrouter.ai](https://openrouter.ai) — free tier available.

### 4. Build the vector store (first-time only)

```bash
python rag/vector_store.py
```

This embeds all 50 patient doctor notes into ChromaDB locally. Takes ~30–60 seconds.

---

## Running the Application

```bash
streamlit run ui/app.py
```

Open your browser at: **http://localhost:8501**

The app auto-builds the vector store on first launch if it doesn't exist.

---

## Example Queries

| Query | Type |
|---|---|
| `What medication is Rahul Sharma taking?` | Medication lookup |
| `Summarize patient P014.` | Patient summary |
| `Which patients have HbA1c above 8?` | Abnormal lab detection |
| `What concerns appear in Priya's doctor notes?` | Clinical notes search |
| `Show lab results for Amit Kumar.` | Lab query |
| `Which patients have LDL above 150?` | Threshold filtering |

---

## Clinical Risk Rules

The system automatically flags:

| Condition | Threshold | Flag |
|---|---|---|
| HbA1c | > 7% | Uncontrolled Diabetes |
| HbA1c | > 8% | Severely Uncontrolled |
| Systolic BP | > 140 mmHg | Hypertension Risk |
| Systolic BP | > 160 mmHg | Severe Hypertension |
| LDL | > 130 mg/dL | Elevated Cholesterol |
| eGFR | < 60 mL/min | Reduced Kidney Function |
| eGFR | < 30 mL/min | Severely Reduced Kidney |
| Haemoglobin | < 10 g/dL | Anaemia |
| TSH | > 5 mIU/L | Possible Hypothyroidism |
| BNP | > 400 pg/mL | Heart Failure Risk |

---

## Technology Stack

- **LLM**: [OpenRouter](https://openrouter.ai) — `meta-llama/llama-3-8b-instruct` (temperature=0)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (runs locally)
- **Vector DB**: [ChromaDB](https://www.trychroma.com/) (persistent local storage)
- **Data**: pandas + synthetic CSV dataset (50 patients)
- **UI**: [Streamlit](https://streamlit.io)
- **Environment**: python-dotenv

---

## Notes

- All data is synthetic. Do not use with real patient records without proper compliance review.
- The `.env` file and `chroma_db/` directory are gitignored for security.
- Temperature is set to 0 to minimise hallucinations.
