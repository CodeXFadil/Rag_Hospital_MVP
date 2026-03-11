"""
ui/app.py
Streamlit UI for the Hospital Patient Records RAG Assistant.
Run with: streamlit run ui/app.py
"""

import os
import sys
import streamlit as st

# Ensure project root is on path
ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"), override=False)

from agents.coordinator_agent import process_query
from rag.vector_store import build_vector_store

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hospital RAG Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
        background-color: #f8fafc;
    }

    /* Premium Main Header */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 2.5rem 3rem;
        border-radius: 20px;
        margin-bottom: 2.5rem;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }

    .main-header::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        background: radial-gradient(circle at top right, rgba(56, 189, 248, 0.15), transparent 50%);
        pointer-events: none;
    }

    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
        background: linear-gradient(to right, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .main-header p {
        margin: 0.75rem 0 0 0;
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* Cards & Components */
    .section-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.025);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        color: #0f172a;
    }

    .section-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.025);
    }

    .section-card h3 {
        font-size: 1.1rem;
        font-weight: 600;
        color: #0f172a;
        margin: 0 0 0.75rem 0;
    }

    /* Risk Flags */
    .risk-flag-red {
        background: linear-gradient(to right, #fef2f2, #fff1f2);
        border-left: 4px solid #ef4444;
        padding: 1rem 1.25rem;
        border-radius: 0 12px 12px 0;
        margin: 0.75rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .risk-flag-amber {
        background: linear-gradient(to right, #fffbeb, #fefce8);
        border-left: 4px solid #f59e0b;
        padding: 1rem 1.25rem;
        border-radius: 0 12px 12px 0;
        margin: 0.75rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .risk-flag-red strong { color: #991b1b; font-size: 1rem; }
    .risk-flag-red small { color: #b91c1c; font-size: 0.9rem; display: block; margin-top: 0.25rem;}
    .risk-flag-amber strong { color: #92400e; font-size: 1rem; }
    .risk-flag-amber small { color: #b45309; font-size: 0.9rem; display: block; margin-top: 0.25rem; }

    /* Badges */
    .intent-badge {
        display: inline-flex;
        align-items: center;
        background: #e0f2fe;
        color: #0369a1;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.35rem 0.75rem;
        border-radius: 9999px;
        margin-right: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border: 1px solid #bae6fd;
    }

    .patient-badge {
        background: #f3e8ff;
        color: #6b21a8;
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.4rem;
        border: 1px solid #e9d5ff;
    }

    /* Note Chunks */
    .note-chunk {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #3b82f6;
        padding: 1rem 1.25rem;
        border-radius: 0 12px 12px 0;
        margin: 0.75rem 0;
        font-size: 0.95rem;
        color: #334155;
        line-height: 1.5;
    }

    /* Chat Elements overrides */
    .stChatMessage {
        background-color: transparent !important;
        padding: 1rem 0;
    }
    
    [data-testid="stChatMessageAvatarUser"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
    
    [data-testid="stChatMessageAvatarAssistant"] {
        background-color: #0f172a !important;
        color: white !important;
    }

    /* General Button Styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: white;
        color: #334155;
        border: 1px solid #cbd5e1;
        justify-content: flex-start;
        text-align: left;
        padding: 0.5rem 1rem;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #f1f5f9;
        border-color: #94a3b8;
        color: #0f172a;
    }
    
</style>
""", unsafe_allow_html=True)


# ── Initialization ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Ensure vector store is initialized on first run
if "vs_initialized" not in st.session_state:
    chroma_path = os.path.join(ROOT, "chroma_db")
    if not os.path.exists(chroma_path):
        with st.spinner("Initialising vector store on first run (this takes ~60 seconds)…"):
            try:
                build_vector_store(force_rebuild=False)
                st.session_state["vs_initialized"] = True
            except Exception as e:
                st.warning(f"Could not auto-init vector store: {e}\nUse the sidebar button.")
    else:
        st.session_state["vs_initialized"] = True

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 Patient RAG Assistant")
    st.markdown("---")

    st.markdown("### 💡 Example Queries")
    example_queries = [
        "What medication is Rahul Sharma taking?",
        "Summarize patient P014.",
        "Which patients have HbA1c above 8?",
        "What concerns appear in Priya's doctor notes?",
        "Show lab results for Amit Kumar.",
        "Which patients have LDL above 150?",
        "Tell me about Rahul's diabetes condition.",
        "How bad is Rahul Sharma's blood sugar?",
    ]

    for i, eq in enumerate(example_queries):
        if st.button(f"💬 {eq}", key=f"ex_btn_{i}", use_container_width=True):
            st.session_state["example_triggered"] = eq

    st.markdown("---")

    st.markdown("### ⚙️ Vector Store")
    if st.button("🔄 Build / Refresh Index", use_container_width=True):
        with st.spinner("Building vector index from patient notes…"):
            try:
                build_vector_store(force_rebuild=True)
                st.success("✅ Index built successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<small style='color:#64748b'>Powered by ChromaDB + OpenRouter LLM<br>"
        "Router: LLM-based intent classifier<br>"
        "Model: meta-llama/llama-3-8b-instruct</small>",
        unsafe_allow_html=True,
    )

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>Hospital Patient Records Assistant</h1>
    <p>Multi-Agent RAG System · Hybrid Retrieval · Clinical Reasoning</p>
</div>
""", unsafe_allow_html=True)

# ── Helper to render assistant responses ──────────────────────────────────────
def render_assistant_response(result):
    """Renders the complex assistant response block correctly."""
    if result.get("error"):
        st.error(f"⚠️ {result['error']}")
        return

    intent = result.get("intent", {})
    patients = result.get("patients", [])
    notes = result.get("notes", [])
    risk_flags = result.get("risk_flags", [])
    llm_response = result.get("llm_response", "")

    # Intent badges
    if intent.get("intents"):
        intent_html = " ".join(
            f'<span class="intent-badge">{i.replace("_", " ")}</span>'
            for i in intent.get("intents", [])
        )
        st.markdown(f"<div style='margin-bottom:1rem;'>{intent_html}</div>", unsafe_allow_html=True)

    # Main response (LLM)
    if llm_response:
        st.markdown(
            f"<div class='section-card'><strong>Clinical Synthesis</strong><br><br>{llm_response.replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True,
        )

    # Risk flags
    if risk_flags:
        for flag in risk_flags:
            css_class = "risk-flag-red" if "🔴" in flag["flag"] else "risk-flag-amber"
            st.markdown(
                f"<div class='{css_class}'><strong>{flag['flag']}</strong><br>"
                f"<small>{flag['detail']}</small></div>",
                unsafe_allow_html=True,
            )

    # Patient Details Cards
    if patients:
        st.markdown("<h4 style='color:#334155; margin-top:1.5rem; margin-bottom:1rem;'>👤 Patient Profiles</h4>", unsafe_allow_html=True)
        for p in patients[:5]:
            with st.expander(f"**{p['name']}** · ID: {p['patient_id']} · Age: {p['age']} · {p['gender']}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Diagnoses**")
                    st.info(p["diagnoses"])
                    st.markdown("**Medications**")
                    st.info(p["medications"])
                with col2:
                    st.markdown("**Lab Results**")
                    st.info(p["lab_results"])
                    st.markdown("**Visit History**")
                    st.info(p["visit_history"])

    # Retrieved Notes
    if notes and any(n.get("score", 0) > 0.1 for n in notes):
        st.markdown("<h4 style='color:#334155; margin-top:1.5rem; margin-bottom:1rem;'>📄 Relevant Clinical Notes</h4>", unsafe_allow_html=True)
        for n in notes:
            if n.get("score", 0) > 0.1:
                score_pct = int(n["score"] * 100)
                st.markdown(
                    f"<div class='note-chunk'>"
                    f"<div style='margin-bottom:0.5rem;'>"
                    f"<span class='patient-badge'>{n['patient_id']} – {n['name']}</span> "
                    f"<small style='color:#64748b; font-weight:500;'>Match Relevance: {score_pct}%</small>"
                    f"</div>"
                    f"{n['text']}</div>",
                    unsafe_allow_html=True,
                )

# ── Chat rendering loop ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            render_assistant_response(msg["result"])

# ── Input processing ──────────────────────────────────────────────────────────
query = st.chat_input("🔍 Ask a clinical question (e.g. 'Summarize patient P014')...")

# If example was clicked in sidebar, use it as query
if "example_triggered" in st.session_state:
    query = st.session_state.pop("example_triggered")


if query:
    # 1. Append and render user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # 2. Process query and render assistant output
    with st.chat_message("assistant"):
        with st.spinner("🤖 Analyzing clinical query..."):
            result = process_query(query)
            st.session_state.messages.append({"role": "assistant", "result": result})
            render_assistant_response(result)
            st.rerun()

