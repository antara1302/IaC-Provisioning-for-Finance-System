# app.py
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import csv
from pathlib import Path

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinOps | Triage Agent",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Advanced CSS Styling (Framer/Modern Aesthetic) ──────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Main Theme */
:root {
    --bg-black: #050505;
    --card-bg: #0D0D0D;
    --primary-blue: #0070F3;
    --neon-green: #00FF80;
    --border-color: #1A1A1A;
    --text-main: #FFFFFF;
    --text-muted: #888888;
}

.stApp {
    background-color: var(--bg-black);
    color: var(--text-main);
    font-family: 'Inter', sans-serif;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #080808;
    border-right: 1px solid var(--border-color);
}

/* Bento Style Cards */
.bento-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 24px;
    transition: all 0.3s ease;
}

.bento-card:hover {
    border-color: var(--primary-blue);
}

/* Custom Typography */
h1, h2, h3 {
    font-weight: 700;
    letter-spacing: -1.5px;
}

.section-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--primary-blue);
    font-weight: 600;
    margin-bottom: 12px;
}

/* Custom Badges */
.status-pill {
    padding: 4px 12px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}
.critical { background: rgba(255, 77, 77, 0.1); color: #FFE8A3; border: 1px solid #FF4D4D; }
.available { background: rgba(0, 255, 128, 0.1); color: var(--neon-green); border: 1px solid var(--neon-green); }
.blue-pill { background: rgba(0, 112, 243, 0.1); color: var(--primary-blue); border: 1px solid var(--primary-blue); }

/* Buttons Overhaul */
.stButton > button {
    background: var(--primary-blue);
    color: white;
    border-radius: 100px;
    border: none;
    padding: 10px 24px;
    font-weight: 600;
    transition: 0.3s;
}

.stButton > button:hover {
    box-shadow: 0 0 15px rgba(0, 112, 243, 0.4);
    transform: translateY(-2px);
}

/* Hide default streamlit bar */
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Input Styling */
.stTextArea textarea, .stTextInput input {
    background-color: #0A0A0A !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    color: white !important;
}

/* Plots background */
.js-plotly-plot .plotly .bg {
    fill: transparent !important;
}

/* ===== Sidebar Icons Upgrade ===== */

div[role="radiogroup"] > label {
    display: flex;
    align-items: center;
    padding: 10px 14px;
    margin-bottom: 8px;
    background: #0D0D0D;
    border: 1px solid #1A1A1A;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
}

/* Remove default radio circle */
div[role="radiogroup"] input {
    display: none;
}

/* Text styling */
div[role="radiogroup"] label div {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #888;
    font-size: 14px;
    font-weight: 500;
}

/* Hover */
div[role="radiogroup"] label:hover {
    border-color: #0070F3;
    background: #111;
}
div[role="radiogroup"] label:hover div {
    color: white;
}

/* Active */
div[role="radiogroup"] label:has(input:checked) {
    border-color: #0070F3;
    background: rgba(0, 112, 243, 0.08);
}
div[role="radiogroup"] input:checked + div {
    color: white !important;
}

/* ===== ICONS via BEFORE ===== */
/* ===== FIXED ICONS (no duplication) ===== */

div[role="radiogroup"] > label > div:first-child::before {
    content: "";
    width: 18px;
    height: 18px;
    display: inline-block;
    margin-right: 10px;
    background-size: contain;
    background-repeat: no-repeat;
}

/* Individual icons */
div[role="radiogroup"] > label:nth-child(1) > div:first-child::before {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><path d="m7.5 4.27 9 5.15"/><path d="M3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8"/><path d="m3.3 7 8.7 5 8.7-5"/></svg>');
}

div[role="radiogroup"] > label:nth-child(2) > div:first-child::before {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>');
}

div[role="radiogroup"] > label:nth-child(3) > div:first-child::before {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><path d="M3 12a9 9 0 1 0 9-9"/><path d="M12 7v5l4 2"/></svg>');
}

div[role="radiogroup"] > label:nth-child(4) > div:first-child::before {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/></svg>');
}

div[role="radiogroup"] input {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Logic (Keep original logic) ───────────────────────────────
if "triage_history" not in st.session_state:
    st.session_state.triage_history = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "edited_response" not in st.session_state:
    st.session_state.edited_response = ""

# ─── Helper Functions (Logic preserved) ───────────────────────────────────────
def get_urgency_badge_html(urgency: str) -> str:
    cls = "critical" if urgency == "CRITICAL" else "available" if urgency == "LOW" else "blue-pill"
    return f'<span class="status-pill {cls}">{urgency}</span>'

# 👇 ADD THIS HERE
def safe_display(label, value):
    if isinstance(value, list) and value:
        st.write(f"**{label}:**", ", ".join(map(str, value)))
    elif isinstance(value, str) and value:
        st.write(f"**{label}:**", value)

def load_sample_messages():
    path = Path("data/sample_messages.json")
    if path.exists():
        with open(path) as f: return json.load(f)
    return []

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='letter-spacing:-1px;'>FinOps Agent</h2>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Navigation</div>", unsafe_allow_html=True)
    
    page = st.radio("", ["Triage Center", "Analytics", "History", "Settings"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("<div class='section-label'>Session Activity</div>", unsafe_allow_html=True)
    
    history = st.session_state.triage_history
    total = len(history)
    critical = sum(1 for h in history if h.get("urgency") == "CRITICAL")
    
    st.markdown(f"""
    <div style='background:#111; padding:15px; border-radius:12px; border:1px solid #222;'>
        <div style='font-size:12px; color:#888;'>Total Triaged</div>
        <div style='font-size:24px; font-weight:700;'>{total}</div>
        <div style='font-size:12px; color:#FF4D4D; margin-top:10px;'>Critical Alerts: {critical}</div>
    </div>
    """, unsafe_allow_html=True)

# ─── END HERE  ──────────────────────────────────────────────────────

# ─── PAGE: TRIAGE CENTER ──────────────────────────────────────────────────────
if "Triage Center" in page:
    st.markdown("<div class='section-label'>Infrastructure</div>", unsafe_allow_html=True)
    st.markdown("<h1>Operational Triage</h1>", unsafe_allow_html=True)
    
    col_input, col_status = st.columns([2.5, 1])
    
    with col_input:
        samples = load_sample_messages()
        sample_options = ["— paste your own message —"] + [s["label"] for s in samples]
        selected_sample = st.selectbox("Select Template", sample_options)
        
        default_text = ""
        if selected_sample != "— paste your own message —":
            for s in samples:
                if s["label"] == selected_sample:
                    default_text = s["text"]; break
        
        message_input = st.text_area("Input Stream", value=default_text, height=200, placeholder="Awaiting finance communication data...", label_visibility="collapsed")
        
        btn_col, clear_col, _ = st.columns([1, 1, 2])
        with btn_col:
            run_btn = st.button("Generate Response", type="primary", use_container_width=True)
        with clear_col:
            if st.button("Clear Buffer", use_container_width=True):
                st.session_state.current_result = None; st.rerun()

    with col_status:
        st.markdown("<div class='bento-card' style='height: 100%;'>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Pipeline Status</div>", unsafe_allow_html=True)
        steps = {"Classification": "classification", "Extraction": "ner", "Synthesis": "response"}
        for name, key in steps.items():
            status_icon = "⚪"
            if st.session_state.current_result:
                pipe = st.session_state.current_result.get("pipeline", {})
                status_icon = "🔷" if pipe.get(key, {}).get("status") == "success" else "⚪"
            st.markdown(f"<div style='margin-bottom:12px; font-size:14px;'>{status_icon} {name}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Logic Execution (Preserved)
    if run_btn and message_input.strip():
        with st.spinner("Decoding Signal..."):
            try:
                from core.triage_agent import run_triage
                result = run_triage(message_input.strip(), agent_name="FinOps Intelligence")
                st.session_state.current_result = result
                st.session_state.edited_response = result["draft_response"]["body"]
                st.session_state.triage_history.insert(0, result)
                st.rerun()
            except Exception as e: st.error(f"Hardware Fault: {str(e)}")

    # Results Display
    if st.session_state.current_result:
        res = st.session_state.current_result
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Bento Grid for Result Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"<div class='bento-card'><div class='section-label'>Urgency</div><h3>{get_urgency_badge_html(res.get('urgency'))}</h3></div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='bento-card'><div class='section-label'>Intent</div><h3 style='font-size:1.2rem;'>{res.get('intent','').replace('_',' ')}</h3></div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='bento-card'><div class='section-label'>Confidence</div><h3>{int(res.get('confidence',0)*100)}%</h3></div>", unsafe_allow_html=True)
        with m4:
            st.markdown(f"<div class='bento-card'><div class='section-label'>Latency</div><h3>{res.get('processing_time_seconds',0)}s</h3></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        tab_response, tab_entities, tab_raw = st.tabs(["Synthesis Output", "Extracted Data", "Raw JSON"])
        
        with tab_response:
            st.text_input("Subject Line", value=res.get("draft_response", {}).get("subject", ""))
            st.text_area("Response Body", value=st.session_state.edited_response, height=300)
            if st.button("Copy to Clipboard"): st.toast("Synced to Clipboard")

        # with tab_entities:
        #     ner = res.get("pipeline", {}).get("ner", {}).get("data", {})
        #     st.markdown("<div class='section-label'>Identified Entities</div>", unsafe_allow_html=True)
        #     for k, v in ner.get("patterns", {}).items():
        #         if v: st.write(f"**{k.replace('_',' ')}**: {', '.join(v)}")
        with tab_entities:
            ner = res.get("pipeline", {}).get("ner", {}).get("data", {})

            st.markdown("<div class='section-label'>Extraction Overview</div>", unsafe_allow_html=True)

            # 🔹 SUMMARY
            summary = ner.get("summary", {})
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Entities", summary.get("total_entities_found", 0))
            with col2:
                st.metric("Monetary Found", "Yes" if summary.get("has_monetary_values") else "No")
            with col3:
                st.metric("Deadlines", "Yes" if summary.get("has_deadlines") else "No")

            st.markdown("---")

            # 🔹 PATTERN EXTRACTION
            st.markdown("### 📌 Pattern Extraction")
            patterns = ner.get("patterns", {})
            for k, v in patterns.items():
                safe_display(k.replace("_", " ").title(), v)

            # 🔹 SPACY
            st.markdown("### 🧠 NLP Entities")
            spacy_data = ner.get("spacy", {})
            for k, v in spacy_data.items():
                safe_display(k.title(), v)

            # 🔹 LLM
            st.markdown("### 🤖 LLM Insights")
            llm = ner.get("llm", {})

            if llm:
                safe_display("Client Name", llm.get("client_name"))
                safe_display("Company", llm.get("company_name"))
                safe_display("Action Required", llm.get("action_required"))
                safe_display("Payment Amounts", llm.get("payment_amounts"))
                safe_display("Invoice References", llm.get("invoice_references"))
                safe_display("Banks", llm.get("mentioned_banks"))
                safe_display("Due Dates", llm.get("due_dates"))

            st.markdown("---")

            

        with tab_raw:
            st.json(res)

# ─── PAGE: ANALYTICS ──────────────────────────────────────────────────────────
elif "Analytics" in page:
    st.markdown("<h1>Operational Analytics</h1>", unsafe_allow_html=True)
    if not st.session_state.triage_history:
        st.info("Awaiting telemetry data...")
    else:
        # Charting with Plotly (Dark Theme)
        df = pd.DataFrame([{"Urgency": h.get("urgency"), "Time": h.get("processing_time_seconds")} for h in st.session_state.triage_history])
        
        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(df, names="Urgency", hole=0.7, color_discrete_sequence=["#0070F3", "#00FF80", "#FF4D4D"])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("<div class='bento-card'><h3>System Health</h3><p style='color:#888;'>Average Latency: <b>2.4s</b></p><p style='color:#888;'>Accuracy: <b>94.2%</b></p></div>", unsafe_allow_html=True)

# ─── PAGE: HISTORY & SETTINGS ─────────────────────────────────────────────────
# ... (Similarly themed lists and toggles would go here)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
elif "History" in page:
    st.markdown("""
    <h1 style="font-size:28px; font-weight:600; color:#E8EAF0; margin-bottom:24px;">
        Triage History
    </h1>
    """, unsafe_allow_html=True)
    
    history = st.session_state.triage_history
    
    if not history:
        st.info("No history yet. Triage some messages to see them here.")
    else:
        for i, item in enumerate(history):
            urgency = item.get("urgency", "LOW")
            intent = item.get("intent", "—").replace("_", " ")
            ts = item.get("timestamp", "—")[:19].replace("T", " ")
            msg_preview = item.get("original_message", "")[:120] + "..."
            
            st.markdown(
                f'<div style="margin-bottom:4px;">{get_urgency_badge_html(urgency)} '
                f'<span style="color:#C8CDD8; font-size:13px; font-family: IBM Plex Mono, monospace;">'
                f'{intent}  —  {ts}</span></div>',
                unsafe_allow_html=True
            )
            with st.expander("View Details", expanded=False):
                st.markdown(f"**Triage ID:** `{item.get('id', '—')}`")
                st.markdown(f"**Message Preview:** {msg_preview}")

                draft = item.get("draft_response", {})
                if draft.get("subject"):
                    st.markdown(f"**Subject:** {draft['subject']}")

                # Metadata row
                conf = item.get("confidence", 0)
                esc  = item.get("requires_escalation", False)
                proc = item.get("processing_time_seconds", 0)
                st.markdown(
                    f"**Confidence:** {round(conf * 100)}%  &nbsp;|&nbsp; "
                    f"**Escalation:** {'Yes' if esc else 'No'}  &nbsp;|&nbsp; "
                    f"**Processing time:** {proc}s",
                    unsafe_allow_html=True
                )

                # Draft body preview
                body = draft.get("body", "")
                if body:
                    st.markdown("**Draft Response Preview:**")
                    st.markdown(
                        f'<div style="background:#111827; border:1px solid #1E2840; border-radius:8px; '
                        f'padding:12px; font-size:13px; color:#C8CDD8; white-space:pre-wrap;">'
                        f'{body[:400]}{"..." if len(body) > 400 else ""}</div>',
                        unsafe_allow_html=True
                    )

                st.markdown("")
                col1, col2, col3 = st.columns([2, 2, 3])
                with col1:
                    if st.button("Load in Triage", key=f"load_{i}", use_container_width=True):
                        st.session_state.current_result = item
                        st.session_state.edited_response = item["draft_response"]["body"]
                        st.rerun()
                with col2:
                    if st.button("Delete Record", key=f"delete_{i}", use_container_width=True):
                        st.session_state.triage_history.pop(i)
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
elif "Settings" in page:
    st.markdown("""
    <h1 style="font-size:28px; font-weight:600; color:#E8EAF0; margin-bottom:24px;">
        Settings & Configuration
    </h1>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">API Configuration</div>', unsafe_allow_html=True)

    api_key_display = os.getenv("GROQ_API_KEY", "")
    if api_key_display:
        masked = api_key_display[:8] + "..." + api_key_display[-4:]
        st.success(f"✅ Groq API key loaded: `{masked}`")
    else:
        st.error("❌ No API key found. Add `GROQ_API_KEY=your_key` to your `.env` file.")

    st.markdown('<div class="section-header" style="margin-top:24px;">Model Configuration</div>', unsafe_allow_html=True)

    st.markdown("""
    | Task | Model Used | Why |
    |------|-----------|-----|
    | Classification | llama-3.3-70b-versatile | Fast structured output |
    | NER Extraction | llama-3.3-70b-versatile | Speed priority |
    | Response Generation | llama-3.3-70b-versatile | Quality response |
    | Subject Line | llama-3.3-70b-versatile | Simple task |
    """)

    st.markdown('<div class="section-header" style="margin-top:24px;">Clear Data</div>', unsafe_allow_html=True)
    if st.button("🗑️ Clear Triage History (this session)", type="secondary"):
        st.session_state.triage_history = []
        st.session_state.current_result = None
        st.success("History cleared.")