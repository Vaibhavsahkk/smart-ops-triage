import streamlit as st
import os, sys, uuid
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import execute
from app.triage_engine import triage
from app.notifier import notify
from config import SITES, BUILDINGS

st.set_page_config(page_title="Submit Facilities Request", page_icon="🏢", layout="centered")

# Custom CSS styling for premium look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Outfit:wght@400;600;800&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #111827 50%, #070a0f 100%);
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        color: #ffffff;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    
    .gradient-title {
        background: linear-gradient(90deg, #4f46e5 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
        margin-top: -20px;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 30px;
    }
    
    div[data-testid="stForm"] {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 35px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-family: 'Outfit', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4) !important;
        width: 100%;
        margin-top: 10px;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.6) !important;
    }
    
    .result-card {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
        border: 1px solid rgba(124, 58, 237, 0.3);
        border-radius: 15px;
        padding: 25px;
        margin-top: 25px;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.15);
    }
    
    .result-title {
        font-family: 'Outfit', sans-serif;
        color: #a78bfa;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 15px;
        border-bottom: 1px solid rgba(124, 58, 237, 0.2);
        padding-bottom: 8px;
    }
    
    .metric-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
        font-size: 1rem;
    }
    .metric-label {
        color: #94a3b8;
        font-weight: 500;
    }
    .metric-value {
        color: #f1f5f9;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="gradient-title">🏢 Smart Facilities Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Submit facilities issues and watch our triage system instantly classify & route them.</div>', unsafe_allow_html=True)

with st.form("request_form"):
    name = st.text_input("Your Name *")
    col1, col2 = st.columns(2)
    with col1:
        site = st.selectbox("Site *", SITES)
    with col2:
        building = st.selectbox("Building *", BUILDINGS)
    description = st.text_area("Describe the issue *", placeholder="E.g., The AC unit is leaking water in Room 302 and the room is starting to flood...", height=120)
    submitted = st.form_submit_button("Submit Request")

if submitted:
    if not name.strip() or not description.strip():
        st.error("Please fill in all required fields.")
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
        
        st.success(f"Request submitted! Your ticket ID is {ticket_id}")
        
        # HTML Custom Card for auto-triage details
        st.markdown(f"""
        <div class="result-card">
            <div class="result-title">⚡ Auto-Triage Engine Results</div>
            <div class="metric-row">
                <span class="metric-label">Suggested Category</span>
                <span class="metric-value">{result['category']} (Confidence: {int(result['confidence']*100)}%)</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Predicted Priority</span>
                <span class="metric-value">{result['priority']}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Assigned Team</span>
                <span class="metric-value">{result['team']}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Target SLA</span>
                <span class="metric-value">{result['sla_hours']} Hours</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Execution Time</span>
                <span class="metric-value">{result['triage_time_ms']} ms</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
