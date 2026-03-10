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
load_dotenv(os.path.join(ROOT, ".env"))

from agents.coordinator_agent import process_query
from rag.vector_store import build_vector_store

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hospital Patient Records Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
    }

    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.8;
        font-size: 1rem;
    }

    .section-card {
        background: #f8fafd;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }

    .section-card h3 {
        font-size: 1rem;
        font-weight: 600;
        color: #1e3a5f;
        margin: 0 0 0.5rem 0;
    }

    .risk-flag-red {
        background: #fff1f2;
        border-left: 4px solid #ef4444;
        padding: 0.6rem 1rem;
        border-radius: 6px;
        margin: 0.4rem 0;
        font-size: 0.9rem;
    }

    .risk-flag-amber {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 0.6rem 1rem;
        border-radius: 6px;
        margin: 0.4rem 0;
        font-size: 0.9rem;
    }

    .intent-badge {
        display: inline-block;
        background: #dbeafe;
        color: #1d4ed8;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        margin-right: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .note-chunk {
        background: #f0fdf4;
        border-left: 3px solid #22c55e;
        padding: 0.6rem 1rem;
        border-radius: 6px;
        margin: 0.4rem 0;
        font-size: 0.88rem;
        color: #166534;
    }

    .patient-badge {
        background: #ede9fe;
        color: #5b21b6;
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.3rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s;
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #1e40af, #2563eb);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }

    .stTextArea textarea {
        border-radius: 10px !important;
        border: 1.5px solid #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        transition: border-color 0.2s;
    }

    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
    }

    div[data-testid="stSidebar"] {
        background: #0f2027;
    }

    div[data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)


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
        "Give me a summary of patient P012.",
        "Summarize patient P050.",
    ]

    for i, eq in enumerate(example_queries):
        if st.button(eq, key=f"ex_btn_{i}", use_container_width=True):
            st.session_state["prefill_query"] = eq

    st.markdown("---")

    # Vector store management
    st.markdown("### ⚙️ Vector Store")
    if st.button("🔄 Build / Refresh Index", use_container_width=True):
        with st.spinner("Building vector index from patient notes…"):
            try:
                build_vector_store(force_rebuild=True)
                st.success("✅ Index built successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown(
        "<small style='color:#94a3b8'>Powered by ChromaDB + OpenRouter LLM<br>"
        "Router: LLM-based intent classifier<br>"
        "Model: meta-llama/llama-3-8b-instruct</small>",
        unsafe_allow_html=True,
    )


# ── Main header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏥 Hospital Patient Records Assistant</h1>
    <p>Multi-Agent RAG System · Hybrid Structured + Semantic Retrieval · Clinical Reasoning</p>
</div>
""", unsafe_allow_html=True)


# ── Auto-initialise vector store on first run ──────────────────────────────────
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


# ── Query input ────────────────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill_query", "")

col_input, col_btn = st.columns([5, 1])
with col_input:
    query = st.text_area(
        "🔍 Enter your clinical query",
        value=prefill,
        height=80,
        placeholder="e.g. 'Summarize patient P014' or 'Which patients have HbA1c above 8?'",
        label_visibility="collapsed",
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.button("Ask →", use_container_width=True)


# ── Process & display ──────────────────────────────────────────────────────────
if submit and query.strip():
    with st.spinner("🤖 LLM routing → retrieval → synthesis…"):
        result = process_query(query.strip())

    # Error handling
    if result.get("error"):
        st.error(f"⚠️ {result['error']}")
        if "OPENROUTER_API_KEY" in result["error"]:
            st.info(
                "**Setup required:** Create a `.env` file in the project root with:\n"
                "```\nOPENROUTER_API_KEY=your_key_here\n```\n"
                "Get your key at [openrouter.ai](https://openrouter.ai)"
            )
        st.stop()

    intent = result.get("intent", {})
    patients = result.get("patients", [])
    notes = result.get("notes", [])
    risk_flags = result.get("risk_flags", [])
    llm_response = result.get("llm_response", "")

    # ── Intent badges ──────────────────────────────────────────────────────────
    intent_html = " ".join(
        f'<span class="intent-badge">{i.replace("_", " ")}</span>'
        for i in intent.get("intents", [])
    )
    st.markdown(f"<div style='margin-bottom:1rem;'>Detected: {intent_html}</div>", unsafe_allow_html=True)

    # ── Main response (LLM) ────────────────────────────────────────────────────
    if llm_response:
        st.markdown("### 📋 Clinical Response")
        st.markdown(
            f"<div class='section-card'>{llm_response.replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True,
        )

    # ── Risk flags ─────────────────────────────────────────────────────────────
    if risk_flags:
        st.markdown("### 🚨 Risk Indicators")
        for flag in risk_flags:
            css_class = "risk-flag-red" if "🔴" in flag["flag"] else "risk-flag-amber"
            st.markdown(
                f"<div class='{css_class}'><strong>{flag['flag']}</strong><br>"
                f"<small>{flag['detail']}</small></div>",
                unsafe_allow_html=True,
            )

    # ── Patient summary cards ──────────────────────────────────────────────────
    if patients:
        st.markdown("### 👤 Patient Summary")
        for p in patients[:5]:
            with st.expander(
                f"**{p['name']}** · {p['patient_id']} · Age {p['age']} · {p['gender']}",
                expanded=(len(patients) == 1),
            ):
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

    # ── Retrieved clinical notes ───────────────────────────────────────────────
    if notes and any(n.get("score", 0) > 0.1 for n in notes):
        st.markdown("### 📄 Retrieved Clinical Notes")
        for n in notes:
            if n.get("score", 0) > 0.1:
                score_pct = int(n["score"] * 100)
                st.markdown(
                    f"<div class='note-chunk'>"
                    f"<span class='patient-badge'>{n['patient_id']} – {n['name']}</span> "
                    f"<small style='color:#6b7280'>Relevance: {score_pct}%</small><br>"
                    f"{n['text']}</div>",
                    unsafe_allow_html=True,
                )

    # ── Debug expander ─────────────────────────────────────────────────────────
    with st.expander("🔧 Agent Debug Info", expanded=False):
        st.json({
            "routing": intent,
            "patients_found": len(patients),
            "notes_retrieved": len(notes),
            "risk_flags_raised": len(risk_flags),
        })

elif submit and not query.strip():
    st.warning("Please enter a query before submitting.")
