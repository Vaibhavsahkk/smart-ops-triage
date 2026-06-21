import streamlit as st
import os, sys, uuid
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import execute
from app.triage_engine import triage
from app.notifier import notify
from config import SITES, BUILDINGS

st.set_page_config(page_title="Facilities Request Portal", page_icon="⬡", layout="centered")

PRIORITY_COLORS = {
    'Critical': ('#ff4444', '#3d0f0f'),
    'High':     ('#f59e0b', '#2d1f00'),
    'Medium':   ('#3b82f6', '#0d1f3d'),
    'Low':      ('#10b981', '#0d2d22'),
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', system-ui, sans-serif !important;
    background: #0c0c0c !important;
    color: #e8e3d8 !important;
}

/* ── Animated noise texture background ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.6;
}

/* ── Subtle gold glow orb ── */
.stApp::after {
    content: '';
    position: fixed;
    width: 600px;
    height: 600px;
    top: -200px;
    right: -200px;
    background: radial-gradient(circle, rgba(212,160,23,0.06) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { display: none !important; }
.block-container { padding-top: 0 !important; padding-bottom: 40px !important; }

/* ── Top wordmark bar ── */
.wordmark {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 28px 0 0 0;
    margin-bottom: 52px;
}
.wordmark-hex {
    width: 36px;
    height: 36px;
    background: #d4a017;
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    flex-shrink: 0;
}
.wordmark-text {
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7a7065;
}
.wordmark-divider {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #2a2520 0%, transparent 100%);
    margin-left: 16px;
}

/* ── Hero heading ── */
.hero {
    margin-bottom: 44px;
}
.hero-eyebrow {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #d4a017;
    margin-bottom: 12px;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 700;
    line-height: 1.08;
    letter-spacing: -0.03em;
    color: #f0ebe0;
    margin-bottom: 14px;
}
.hero-title span {
    color: #d4a017;
}
.hero-body {
    font-size: 0.95rem;
    line-height: 1.65;
    color: #5a5248;
    max-width: 480px;
    font-weight: 400;
}

/* ── Form wrapper ── */
div[data-testid="stForm"] {
    background: #141210 !important;
    border: 1px solid #232018 !important;
    border-radius: 16px !important;
    padding: 36px !important;
    box-shadow:
        0 0 0 1px rgba(212,160,23,0.04),
        0 24px 48px rgba(0,0,0,0.6),
        inset 0 1px 0 rgba(255,255,255,0.03) !important;
}

/* ── Field labels ── */
label, .stTextInput label, .stTextArea label, .stSelectbox label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #4a453f !important;
    margin-bottom: 6px !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    background: #0c0c0c !important;
    border: 1px solid #2a2520 !important;
    border-radius: 10px !important;
    color: #e8e3d8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 12px 16px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #d4a017 !important;
    box-shadow: 0 0 0 3px rgba(212,160,23,0.08) !important;
    outline: none !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #3a3530 !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #0c0c0c !important;
    border: 1px solid #2a2520 !important;
    border-radius: 10px !important;
    color: #e8e3d8 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stSelectbox > div > div:hover {
    border-color: #3a3530 !important;
}

/* ── Submit button ── */
.stButton > button {
    background: #d4a017 !important;
    color: #0c0c0c !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 13px 24px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.04em !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 1px 0 rgba(255,255,255,0.12) inset, 0 4px 16px rgba(212,160,23,0.2) !important;
    margin-top: 8px !important;
}
.stButton > button:hover {
    background: #e6b020 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 1px 0 rgba(255,255,255,0.15) inset, 0 8px 24px rgba(212,160,23,0.3) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Success banner ── */
div[data-testid="stAlert"][data-baseweb="notification"] {
    background: rgba(212,160,23,0.06) !important;
    border: 1px solid rgba(212,160,23,0.2) !important;
    border-radius: 10px !important;
    color: #d4a017 !important;
}

/* ── Ticket result card ── */
.ticket-card {
    margin-top: 32px;
    background: #0f0e0c;
    border: 1px solid #232018;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 24px 48px rgba(0,0,0,0.5);
}
.ticket-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 24px;
    border-bottom: 1px solid #1a1814;
}
.ticket-id {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    color: #5a5248;
    letter-spacing: 0.06em;
}
.ticket-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 100px;
}
.ticket-body {
    padding: 0;
}
.ticket-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 15px 24px;
    border-bottom: 1px solid #141210;
    transition: background 0.15s;
}
.ticket-row:last-child { border-bottom: none; }
.ticket-row:hover { background: rgba(255,255,255,0.015); }
.ticket-key {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #3a3530;
}
.ticket-val {
    font-size: 0.92rem;
    font-weight: 500;
    color: #d0c8ba;
    font-family: 'DM Sans', sans-serif;
}
.ticket-val.mono {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    color: #5a5248;
}
.conf-bar-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
}
.conf-bar {
    height: 4px;
    border-radius: 4px;
    background: #1a1814;
    width: 80px;
    overflow: hidden;
}
.conf-fill {
    height: 100%;
    border-radius: 4px;
    background: #d4a017;
}
.section-rule {
    height: 1px;
    background: #1a1814;
    margin: 0 24px;
}

/* ── Divider ── */
hr { border-color: #1a1814 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2520; border-radius: 4px; }

</style>
""", unsafe_allow_html=True)

# ── Wordmark ──
st.markdown("""
<div class="wordmark">
    <div class="wordmark-hex"></div>
    <span class="wordmark-text">Facilities Operations</span>
    <div class="wordmark-divider"></div>
</div>
""", unsafe_allow_html=True)

# ── Hero ──
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Request Intake Portal</div>
    <div class="hero-title">Report an issue.<br><span>Get routed in seconds.</span></div>
    <div class="hero-body">
        Our triage engine reads your description and instantly classifies the issue,
        assigns a team, and sets an SLA — no paperwork, no waiting.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Form ──
with st.form("request_form", clear_on_submit=False):
    name = st.text_input("Your Full Name")
    col1, col2 = st.columns(2)
    with col1:
        site = st.selectbox("Site Location", SITES)
    with col2:
        building = st.selectbox("Building", BUILDINGS)
    description = st.text_area(
        "Describe the Issue",
        placeholder="e.g. The AC unit stopped cooling completely in Room 201 — the room temperature is rising fast.",
        height=110
    )
    submitted = st.form_submit_button("Submit Request →")

# ── Result ──
if submitted:
    if not name.strip() or not description.strip():
        st.error("Name and issue description are both required.")
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

        prio = result['priority']
        badge_color, badge_bg = PRIORITY_COLORS.get(prio, ('#d4a017', '#2d1f00'))
        conf_pct = int(result['confidence'] * 100)

        st.markdown(f"""
        <div class="ticket-card">
            <div class="ticket-header">
                <span class="ticket-id">{ticket_id}</span>
                <span class="ticket-badge" style="color:{badge_color};background:{badge_bg};">
                    ● {prio} Priority
                </span>
            </div>
            <div class="ticket-body">
                <div class="ticket-row">
                    <span class="ticket-key">Category</span>
                    <span class="ticket-val">{result['category']}</span>
                </div>
                <div class="ticket-row">
                    <span class="ticket-key">Confidence</span>
                    <span class="ticket-val">
                        <span class="conf-bar-wrap">
                            <span class="conf-bar"><span class="conf-fill" style="width:{conf_pct}%;"></span></span>
                            {conf_pct}%
                        </span>
                    </span>
                </div>
                <div class="ticket-row">
                    <span class="ticket-key">Assigned Team</span>
                    <span class="ticket-val">{result['team']}</span>
                </div>
                <div class="ticket-row">
                    <span class="ticket-key">SLA Window</span>
                    <span class="ticket-val">{result['sla_hours']} hours</span>
                </div>
                <div class="ticket-row">
                    <span class="ticket-key">Engine Latency</span>
                    <span class="ticket-val mono">{result['triage_time_ms']} ms</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
