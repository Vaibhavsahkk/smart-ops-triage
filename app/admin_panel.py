import streamlit as st
import os, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import execute, fetch_all
from config import CATEGORIES, PRIORITIES, TEAMS_MAP

st.set_page_config(page_title="Triage Admin Panel", page_icon="🔧", layout="wide")

# Custom CSS styling for premium look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Outfit:wght@400;600;800&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #020617 100%);
        font-family: 'Inter', sans-serif;
        color: #f8fafc;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        color: #ffffff;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    
    .gradient-title {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 5px;
        margin-top: -20px;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    
    /* Tabs styling */
    div[data-testid="stTabs"] button {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        color: #94a3b8 !important;
        border: none !important;
        padding: 10px 20px !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #a855f7 !important;
        border-bottom: 3px solid #a855f7 !important;
    }
    
    /* Sidebar custom styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.9) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Expander card styling */
    div[data-testid="stExpander"] {
        background: rgba(30, 41, 59, 0.4) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Custom buttons */
    .stButton > button {
        font-weight: 600 !important;
        border-radius: 8px !important;
        width: 100%;
        transition: all 0.2s ease !important;
        border: none !important;
    }
    
    /* Specialize save button dynamically */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button:hover {
        background: linear-gradient(90deg, #34d399 0%, #10b981 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }

    /* Specialize close button dynamically */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover {
        background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Metrics box */
    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    .metric-card-val {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        background: linear-gradient(90deg, #818cf8 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 5px;
    }
    .metric-card-lbl {
        color: #94a3b8;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="gradient-title">🔧 Triage Control Panel</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Review and override machine categorization, update priorities, and resolve open facilities tickets.</div>', unsafe_allow_html=True)

if 'reviewer' not in st.session_state:
    st.session_state.reviewer = "Admin"
st.session_state.reviewer = st.sidebar.text_input("Reviewer Name", value=st.session_state.reviewer)
reviewer = st.session_state.reviewer

tab1, tab2 = st.tabs(["📥 Open Tickets", "📊 Operational Insights"])

with tab1:
    rows = fetch_all("SELECT * FROM requests WHERE status='Open' ORDER BY submitted_at DESC")
    if not rows:
        st.info("No open tickets waiting for triage review.")
    for row in rows:
        # Beautiful expander header
        expander_title = f"🎫 {row['ticket_id']} | Suggested: {row['suggested_category']} ({int(row['suggested_confidence']*100)}%) | By {row['submitter']} | Site: {row['site']}"
        with st.expander(expander_title):
            st.markdown(f"**Issue Description:**")
            st.info(row['description'])
            
            st.markdown("##### Adjust Assignment & Routing")
            col1, col2, col3 = st.columns(3)
            with col1:
                default_cat = row['final_category'] if row['final_category'] in CATEGORIES else CATEGORIES[0]
                new_cat = st.selectbox("Override Category", CATEGORIES,
                                       index=CATEGORIES.index(default_cat),
                                       key=f"cat_{row['ticket_id']}")
            with col2:
                default_pri = row['final_priority'] if row['final_priority'] in PRIORITIES else PRIORITIES[1]
                new_pri = st.selectbox("Override Priority", PRIORITIES,
                                       index=PRIORITIES.index(default_pri),
                                       key=f"pri_{row['ticket_id']}")
            with col3:
                team_options = sorted(set(TEAMS_MAP.values()))
                default_team = row['final_team'] if row['final_team'] in team_options else team_options[0]
                new_team = st.selectbox("Override Team", team_options,
                                        index=team_options.index(default_team),
                                        key=f"team_{row['ticket_id']}")

            cols = st.columns([1, 1, 4])
            if cols[0].button("💾 Save Changes", key=f"save_{row['ticket_id']}"):
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                overrides = 0
                if new_cat != row['final_category']:
                    execute("INSERT INTO override_log (ticket_id, field_changed, old_value, new_value, reviewer, changed_at) VALUES (?, ?, ?, ?, ?, ?)",
                            (row['ticket_id'], 'category', row['final_category'], new_cat, reviewer, now))
                    overrides += 1
                if new_pri != row['final_priority']:
                    execute("INSERT INTO override_log (ticket_id, field_changed, old_value, new_value, reviewer, changed_at) VALUES (?, ?, ?, ?, ?, ?)",
                            (row['ticket_id'], 'priority', row['final_priority'], new_pri, reviewer, now))
                    overrides += 1
                if new_team != row['final_team']:
                    execute("INSERT INTO override_log (ticket_id, field_changed, old_value, new_value, reviewer, changed_at) VALUES (?, ?, ?, ?, ?, ?)",
                            (row['ticket_id'], 'team', row['final_team'], new_team, reviewer, now))
                    overrides += 1
                execute("UPDATE requests SET final_category=?, final_priority=?, final_team=?, override_count=override_count+? WHERE ticket_id=?",
                        (new_cat, new_pri, new_team, overrides, row['ticket_id']))
                st.success(f"Changes saved successfully. {overrides} fields overridden.")
                st.rerun()

            if cols[1].button("✅ Close Ticket", key=f"close_{row['ticket_id']}"):
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                execute("UPDATE requests SET status='Closed', closed_at=? WHERE ticket_id=?",
                        (now, row['ticket_id']))
                st.success("Ticket closed and archived.")
                st.rerun()

with tab2:
    total = fetch_all("SELECT COUNT(*) as c FROM requests")[0]['c']
    open_count = fetch_all("SELECT COUNT(*) as c FROM requests WHERE status='Open'")[0]['c']
    closed_count = total - open_count
    accuracy_count = fetch_all("SELECT COUNT(*) as c FROM requests WHERE override_count=0 AND status='Closed'")[0]['c']
    accuracy = f"{round((accuracy_count / closed_count) * 100, 1)}%" if closed_count else "N/A"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-card-lbl">Total Requests</div><div class="metric-card-val">{total}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-card-lbl">Open Tickets</div><div class="metric-card-val">{open_count}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-card-lbl">Closed Tickets</div><div class="metric-card-val">{closed_count}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-card-lbl">AI Accuracy Rate</div><div class="metric-card-val">{accuracy}</div></div>', unsafe_allow_html=True)
