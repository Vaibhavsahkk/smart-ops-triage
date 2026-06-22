import streamlit as st
import os, sys, uuid
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import execute
from app.triage_engine import triage
from app.notifier import notify
from config import SITES, BUILDINGS

st.set_page_config(
    page_title="Facilities Request Portal",
    page_icon="assets/favicon.png" if os.path.exists("assets/favicon.png") else None,
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    background: #F1F5F9 !important;
    color: #0F172A !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Top navigation bar ── */
.topnav {
    background: #0F172A;
    padding: 0 40px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
.topnav-brand {
    display: flex;
    align-items: center;
    gap: 10px;
}
.topnav-dot {
    width: 8px;
    height: 8px;
    background: #3B82F6;
    border-radius: 50%;
}
.topnav-name {
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #F8FAFC;
}
.topnav-sub {
    font-size: 0.72rem;
    font-weight: 400;
    color: #64748B;
    margin-left: 4px;
}
.topnav-badge {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    padding: 4px 12px;
    background: rgba(59,130,246,0.15);
    color: #93C5FD;
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 100px;
}

/* ── Page wrapper ── */
.page-wrap {
    max-width: 680px;
    margin: 0 auto;
    padding: 48px 24px 80px;
}

/* ── Page header ── */
.page-header {
    margin-bottom: 36px;
}
.page-eyebrow {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #3B82F6;
    margin-bottom: 10px;
}
.page-title {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #0F172A;
    line-height: 1.15;
    margin-bottom: 10px;
}
.page-desc {
    font-size: 0.92rem;
    color: #64748B;
    line-height: 1.65;
    font-weight: 400;
}

/* ── Info strip ── */
.info-strip {
    display: flex;
    gap: 20px;
    margin-bottom: 28px;
    padding: 14px 20px;
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 10px;
}
.info-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.8rem;
    color: #1E40AF;
    font-weight: 500;
}
.info-dot {
    width: 6px;
    height: 6px;
    background: #3B82F6;
    border-radius: 50%;
    flex-shrink: 0;
}

/* ── Form card ── */
div[data-testid="stForm"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    padding: 36px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 8px 24px rgba(0,0,0,0.06) !important;
}

/* ── Section label inside form ── */
.form-section {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #94A3B8;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #F1F5F9;
}

/* ── Field labels ── */
label, .stTextInput label, .stTextArea label, .stSelectbox label {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    text-transform: none !important;
    color: #374151 !important;
    margin-bottom: 4px !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    background: #F8FAFC !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 10px !important;
    color: #0F172A !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    padding: 11px 14px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    background: #FFFFFF !important;
    outline: none !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #CBD5E1 !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #F8FAFC !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 10px !important;
    color: #0F172A !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
}
.stSelectbox > div > div:focus-within {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}

/* ── Submit button ── */
.stButton > button {
    background: #2563EB !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 13px 24px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.01em !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 1px 2px rgba(37,99,235,0.3), 0 4px 12px rgba(37,99,235,0.2) !important;
    margin-top: 8px !important;
}
.stButton > button:hover {
    background: #1D4ED8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 4px rgba(37,99,235,0.3), 0 8px 20px rgba(37,99,235,0.25) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
    background: #1E40AF !important;
}

/* ── Result ticket card ── */
.result-wrap {
    margin-top: 24px;
}
.result-header-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}
.result-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #64748B;
}
.ticket-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 8px 24px rgba(0,0,0,0.06);
}
.ticket-head {
    background: #0F172A;
    padding: 20px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.ticket-id-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 500;
    color: #94A3B8;
    letter-spacing: 0.06em;
}
.ticket-id-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem;
    font-weight: 500;
    color: #F8FAFC;
    letter-spacing: 0.04em;
}
.priority-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 100px;
}
.ticket-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
}
.ticket-cell {
    padding: 20px 28px;
    border-bottom: 1px solid #F1F5F9;
    border-right: 1px solid #F1F5F9;
}
.ticket-cell:nth-child(2n) {
    border-right: none;
}
.ticket-cell:nth-last-child(-n+2) {
    border-bottom: none;
}
.cell-key {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #94A3B8;
    margin-bottom: 6px;
}
.cell-val {
    font-size: 0.95rem;
    font-weight: 600;
    color: #0F172A;
}
.cell-val.mono {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #475569;
    font-weight: 400;
}
.conf-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
}
.conf-track {
    flex: 1;
    height: 6px;
    background: #F1F5F9;
    border-radius: 6px;
    overflow: hidden;
}
.conf-fill {
    height: 100%;
    border-radius: 6px;
    background: #3B82F6;
    transition: width 0.6s ease;
}
.conf-pct {
    font-size: 0.82rem;
    font-weight: 700;
    color: #2563EB;
    min-width: 36px;
}
.sla-pill {
    display: inline-flex;
    align-items: center;
    font-size: 0.82rem;
    font-weight: 600;
    color: #0369A1;
    background: #E0F2FE;
    border-radius: 6px;
    padding: 3px 10px;
}
.latency-badge {
    display: inline-flex;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 500;
    color: #059669;
    background: #ECFDF5;
    border-radius: 6px;
    padding: 3px 10px;
}
.success-strip {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 20px;
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 10px;
    margin-bottom: 20px;
    font-size: 0.84rem;
    font-weight: 500;
    color: #15803D;
}

/* ── Divider ── */
hr { border-color: #F1F5F9 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }

/* Streamlit alert override */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.84rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── Navigation bar ──────────────────────────────────────────────────────────
st.markdown("""
<div class="topnav">
  <div class="topnav-brand">
    <div class="topnav-dot"></div>
    <span class="topnav-name">FacilityOps</span>
    <span class="topnav-sub">/ Request Portal</span>
  </div>
  <span class="topnav-badge">AI Triage Active</span>
</div>
""", unsafe_allow_html=True)

# ── Page wrapper start ──────────────────────────────────────────────────────
st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

# ── Page header ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div class="page-eyebrow">Request Intake</div>
  <div class="page-title">Report a Facility Issue</div>
  <div class="page-desc">
    Submit your request below. The AI triage engine will instantly classify the issue,
    assign the correct team, and set a response SLA — no manual routing required.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Info strip ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="info-strip">
  <div class="info-item"><div class="info-dot"></div> Sub-1ms auto-categorization</div>
  <div class="info-item"><div class="info-dot"></div> 8 facility categories</div>
  <div class="info-item"><div class="info-dot"></div> Instant team routing</div>
</div>
""", unsafe_allow_html=True)

# ── Form ────────────────────────────────────────────────────────────────────
with st.form("request_form", clear_on_submit=False):
    st.markdown('<div class="form-section">Requestor Information</div>', unsafe_allow_html=True)
    name = st.text_input("Full Name", placeholder="e.g. Arjun Sharma")

    st.markdown('<div class="form-section" style="margin-top:20px;">Location</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        site = st.selectbox("Site", SITES)
    with col2:
        building = st.selectbox("Building", BUILDINGS)

    st.markdown('<div class="form-section" style="margin-top:20px;">Issue Details</div>', unsafe_allow_html=True)
    description = st.text_area(
        "Describe the Issue",
        placeholder="e.g. The AC unit in Room 201 stopped cooling completely. Temperature is rising and it is urgent.",
        height=120
    )
    submitted = st.form_submit_button("Submit Request")

# ── Result ──────────────────────────────────────────────────────────────────
if submitted:
    if not name.strip() or not description.strip():
        st.error("Full name and issue description are both required.")
    else:
        result = triage(description)
        ticket_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        execute("""
            INSERT INTO requests (
                ticket_id, submitter, site, building, description,
                suggested_category, suggested_confidence, final_category,
                suggested_priority, final_priority,
                suggested_team, final_team,
                submitted_at, triage_time_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ticket_id, name, site, building, description,
              result['category'], result['confidence'], result['category'],
              result['priority'], result['priority'],
              result['team'], result['team'],
              now, result['triage_time_ms']))

        notify(ticket_id, result['category'], result['priority'], result['team'], description)
        execute("UPDATE requests SET notification_sent=1 WHERE ticket_id=?", (ticket_id,))

        PRIORITY_STYLES = {
            'Critical': ('color:#DC2626;background:#FEF2F2;border:1px solid #FECACA;', 'Critical'),
            'High':     ('color:#D97706;background:#FFFBEB;border:1px solid #FDE68A;', 'High'),
            'Medium':   ('color:#2563EB;background:#EFF6FF;border:1px solid #BFDBFE;', 'Medium'),
            'Low':      ('color:#059669;background:#ECFDF5;border:1px solid #A7F3D0;', 'Low'),
        }
        prio = result['priority']
        chip_style, chip_label = PRIORITY_STYLES.get(prio, ('color:#2563EB;background:#EFF6FF;border:1px solid #BFDBFE;', prio))
        conf_pct = int(result['confidence'] * 100)

        sla = result['sla_hours']
        lat = result['triage_time_ms']

        st.markdown(f"""
        <div class="result-wrap">
          <div class="success-strip">
            Request submitted — ticket {ticket_id} has been created and the team has been notified.
          </div>
          <div class="result-header-bar">
            <span class="result-label">Triage Result</span>
            <span class="priority-chip" style="{chip_style}">{chip_label} Priority</span>
          </div>
          <div class="ticket-card">
            <div class="ticket-head">
              <div>
                <div class="ticket-id-label">Ticket ID</div>
                <div class="ticket-id-val">{ticket_id}</div>
              </div>
              <div style="text-align:right;">
                <div class="ticket-id-label">Submitted</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#94A3B8;">{now[:16]}</div>
              </div>
            </div>
            <div class="ticket-grid">
              <div class="ticket-cell">
                <div class="cell-key">Category</div>
                <div class="cell-val">{result['category']}</div>
              </div>
              <div class="ticket-cell">
                <div class="cell-key">Assigned Team</div>
                <div class="cell-val">{result['team']}</div>
              </div>
              <div class="ticket-cell">
                <div class="cell-key">AI Confidence</div>
                <div class="cell-val">
                  <div class="conf-wrap">
                    <div class="conf-track"><div class="conf-fill" style="width:{conf_pct}%;"></div></div>
                    <span class="conf-pct">{conf_pct}%</span>
                  </div>
                </div>
              </div>
              <div class="ticket-cell">
                <div class="cell-key">SLA Window</div>
                <div class="cell-val"><span class="sla-pill">{sla} hours</span></div>
              </div>
              <div class="ticket-cell" style="border-bottom:none;border-right:1px solid #F1F5F9;">
                <div class="cell-key">Location</div>
                <div class="cell-val">{site} / {building}</div>
              </div>
              <div class="ticket-cell" style="border-bottom:none;">
                <div class="cell-key">Engine Latency</div>
                <div class="cell-val"><span class="latency-badge">{lat} ms</span></div>
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
