import streamlit as st
import os, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import execute, fetch_all
from config import CATEGORIES, PRIORITIES, TEAMS_MAP

st.set_page_config(page_title="Triage Control — Facilities Ops", page_icon="⬡", layout="wide")

PRIORITY_COLORS = {
    'Critical': ('#ff4444', 'rgba(255,68,68,0.12)'),
    'High':     ('#f59e0b', 'rgba(245,158,11,0.12)'),
    'Medium':   ('#3b82f6', 'rgba(59,130,246,0.12)'),
    'Low':      ('#10b981', 'rgba(16,185,129,0.12)'),
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', system-ui, sans-serif !important;
    background: #0a0908 !important;
    color: #d8d0c4 !important;
}

/* ── Noise overlay ── */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
    pointer-events: none; z-index: 0; opacity: 0.7;
}

#MainMenu, footer, header { display: none !important; }
.block-container { padding: 0 2.5rem 3rem !important; max-width: 100% !important; }

/* ── Top nav bar ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 22px 0 0; margin-bottom: 36px;
    border-bottom: 1px solid #1a1714; padding-bottom: 22px;
}
.topbar-brand { display: flex; align-items: center; gap: 10px; }
.topbar-hex {
    width: 28px; height: 28px; background: #d4a017;
    clip-path: polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%);
}
.topbar-name {
    font-size: 0.78rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #5a5248;
}
.topbar-pills { display: flex; gap: 8px; }
.pill {
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; padding: 5px 14px; border-radius: 100px;
}
.pill-open   { color: #f59e0b; background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.2); }
.pill-closed { color: #10b981; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); }

/* ── Page title ── */
.page-title { margin-bottom: 32px; }
.page-eyebrow {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.2em;
    text-transform: uppercase; color: #d4a017; margin-bottom: 8px;
}
.page-h1 {
    font-size: 2rem; font-weight: 700; letter-spacing: -0.025em;
    color: #f0ebe0; line-height: 1.1;
}

/* ── Stat cards ── */
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 36px; }
.stat-card {
    background: #0f0d0b; border: 1px solid #1a1714; border-radius: 14px;
    padding: 22px 24px; position: relative; overflow: hidden;
    transition: border-color 0.2s;
}
.stat-card:hover { border-color: #2a2520; }
.stat-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.stat-total::before  { background: linear-gradient(90deg, #d4a017, transparent); }
.stat-open::before   { background: linear-gradient(90deg, #f59e0b, transparent); }
.stat-closed::before { background: linear-gradient(90deg, #10b981, transparent); }
.stat-ai::before     { background: linear-gradient(90deg, #3b82f6, transparent); }
.stat-label {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #3a3530; margin-bottom: 10px;
}
.stat-value {
    font-size: 2.4rem; font-weight: 700; letter-spacing: -0.03em;
    line-height: 1; color: #f0ebe0;
}
.stat-sub { font-size: 0.75rem; color: #3a3530; margin-top: 6px; }

/* ── Tab strip ── */
div[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid #1a1714 !important;
    gap: 0 !important; background: transparent !important;
    margin-bottom: 24px;
}
div[data-testid="stTabs"] button[role="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important; font-weight: 600 !important;
    letter-spacing: 0.05em !important; color: #3a3530 !important;
    padding: 10px 20px !important; border: none !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important; border-radius: 0 !important;
    transition: all 0.15s !important;
}
div[data-testid="stTabs"] button[role="tab"]:hover { color: #8a7e70 !important; }
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #d4a017 !important;
    border-bottom: 2px solid #d4a017 !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0a0908 !important;
    border-right: 1px solid #1a1714 !important;
    padding: 28px 20px !important;
}
section[data-testid="stSidebar"] label {
    font-size: 0.68rem !important; font-weight: 700 !important;
    letter-spacing: 0.12em !important; text-transform: uppercase !important;
    color: #3a3530 !important;
}
section[data-testid="stSidebar"] input {
    background: #0f0d0b !important; border: 1px solid #1a1714 !important;
    border-radius: 8px !important; color: #d8d0c4 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Ticket expander ── */
div[data-testid="stExpander"] {
    background: #0f0d0b !important;
    border: 1px solid #1a1714 !important;
    border-radius: 12px !important; margin-bottom: 8px !important;
    box-shadow: none !important;
    transition: border-color 0.2s !important;
    overflow: hidden !important;
}
div[data-testid="stExpander"]:hover { border-color: #2a2520 !important; }
div[data-testid="stExpander"] summary {
    font-size: 0.82rem !important; font-weight: 500 !important;
    color: #8a7e70 !important; padding: 14px 18px !important;
    font-family: 'DM Mono', monospace !important;
}
div[data-testid="stExpander"] summary:hover { color: #d8d0c4 !important; }

/* ── Inputs inside expander ── */
div[data-testid="stExpander"] label {
    font-size: 0.68rem !important; font-weight: 700 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    color: #3a3530 !important;
}
div[data-testid="stExpander"] .stSelectbox > div > div {
    background: #0a0908 !important; border: 1px solid #1a1714 !important;
    border-radius: 8px !important; color: #d8d0c4 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.88rem !important;
}
div[data-testid="stExpander"] .stTextArea textarea {
    background: #0a0908 !important; border: 1px solid #1a1714 !important;
    border-radius: 8px !important; color: #8a7e70 !important;
    font-family: 'DM Mono', monospace !important; font-size: 0.78rem !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important; font-weight: 700 !important;
    letter-spacing: 0.06em !important; text-transform: uppercase !important;
    border-radius: 8px !important; border: none !important;
    padding: 10px 18px !important; width: 100% !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button {
    background: rgba(212,160,23,0.12) !important;
    color: #d4a017 !important;
    border: 1px solid rgba(212,160,23,0.25) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button:hover {
    background: rgba(212,160,23,0.2) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button {
    background: rgba(16,185,129,0.1) !important;
    color: #10b981 !important;
    border: 1px solid rgba(16,185,129,0.2) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button:hover {
    background: rgba(16,185,129,0.18) !important;
    transform: translateY(-1px) !important;
}

/* ── Alert override ── */
div[data-testid="stAlert"] {
    border-radius: 8px !important; font-size: 0.82rem !important;
    font-family: 'DM Sans', sans-serif !important;
    border: none !important;
    background: rgba(212,160,23,0.07) !important;
    color: #d4a017 !important;
}

/* ── Info box (description) ── */
div[data-testid="stInfo"] {
    background: #0a0908 !important; border: 1px solid #1a1714 !important;
    border-radius: 8px !important; color: #8a7e70 !important;
    font-size: 0.88rem !important; font-family: 'DM Sans', sans-serif !important;
}

/* ── Priority badge ── */
.p-badge {
    display: inline-block;
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; padding: 3px 10px; border-radius: 100px;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2520; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Data ──
total = fetch_all("SELECT COUNT(*) as c FROM requests")[0]['c']
open_count = fetch_all("SELECT COUNT(*) as c FROM requests WHERE status='Open'")[0]['c']
closed_count = total - open_count
accuracy_count = fetch_all("SELECT COUNT(*) as c FROM requests WHERE override_count=0 AND status='Closed'")[0]['c']
accuracy = f"{round((accuracy_count / closed_count) * 100, 1)}%" if closed_count else "—"

# ── Sidebar ──
if 'reviewer' not in st.session_state:
    st.session_state.reviewer = "Admin"
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.session_state.reviewer = st.sidebar.text_input("Reviewer Identity", value=st.session_state.reviewer)
reviewer = st.session_state.reviewer

st.sidebar.markdown("<hr style='border-color:#1a1714;margin:20px 0'>", unsafe_allow_html=True)
st.sidebar.markdown(f"""
<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#3a3530;margin-bottom:14px;">Queue Summary</div>
<div style="display:flex;flex-direction:column;gap:8px;">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <span style="font-size:0.82rem;color:#5a5248;">Open</span>
    <span style="font-size:0.82rem;font-weight:600;color:#f59e0b;">{open_count}</span>
  </div>
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <span style="font-size:0.82rem;color:#5a5248;">Closed</span>
    <span style="font-size:0.82rem;font-weight:600;color:#10b981;">{closed_count}</span>
  </div>
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <span style="font-size:0.82rem;color:#5a5248;">AI Accuracy</span>
    <span style="font-size:0.82rem;font-weight:600;color:#3b82f6;">{accuracy}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Top bar ──
st.markdown(f"""
<div class="topbar">
  <div class="topbar-brand">
    <div class="topbar-hex"></div>
    <span class="topbar-name">Facilities Ops · Control</span>
  </div>
  <div class="topbar-pills">
    <span class="pill pill-open">{open_count} Open</span>
    <span class="pill pill-closed">{closed_count} Closed</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stat cards ──
st.markdown(f"""
<div class="stats-row">
  <div class="stat-card stat-total">
    <div class="stat-label">Total Requests</div>
    <div class="stat-value">{total}</div>
    <div class="stat-sub">All time submissions</div>
  </div>
  <div class="stat-card stat-open">
    <div class="stat-label">Open Queue</div>
    <div class="stat-value">{open_count}</div>
    <div class="stat-sub">Awaiting resolution</div>
  </div>
  <div class="stat-card stat-closed">
    <div class="stat-label">Resolved</div>
    <div class="stat-value">{closed_count}</div>
    <div class="stat-sub">Successfully closed</div>
  </div>
  <div class="stat-card stat-ai">
    <div class="stat-label">AI Accuracy</div>
    <div class="stat-value">{accuracy}</div>
    <div class="stat-sub">Closed without override</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Page title ──
st.markdown("""
<div class="page-title">
  <div class="page-eyebrow">Operations Dashboard</div>
  <div class="page-h1">Triage Control Center</div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──
tab1, tab2 = st.tabs(["Open Tickets", "Operational Insights"])

with tab1:
    rows = fetch_all("SELECT * FROM requests WHERE status='Open' ORDER BY submitted_at DESC")
    if not rows:
        st.markdown("""
        <div style="text-align:center;padding:60px 0;color:#3a3530;font-size:0.9rem;">
            No open tickets — the queue is clear.
        </div>
        """, unsafe_allow_html=True)
    for row in rows:
        prio = row['suggested_priority']
        pcolor, pbg = PRIORITY_COLORS.get(prio, ('#d4a017', 'rgba(212,160,23,0.12)'))
        badge = f'<span class="p-badge" style="color:{pcolor};background:{pbg};">{prio}</span>'
        conf = int(row['suggested_confidence'] * 100)
        header = (
            f"{row['ticket_id']}  ·  {row['suggested_category']}  {conf}%  "
            f"·  {row['submitter']}  ·  {row['site']}"
        )
        with st.expander(header):
            st.markdown(f"**Description**")
            st.info(row['description'])
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown(f"**Override Assignment**")
            col1, col2, col3 = st.columns(3)
            with col1:
                default_cat = row['final_category'] if row['final_category'] in CATEGORIES else CATEGORIES[0]
                new_cat = st.selectbox("Category", CATEGORIES,
                                       index=CATEGORIES.index(default_cat),
                                       key=f"cat_{row['ticket_id']}")
            with col2:
                default_pri = row['final_priority'] if row['final_priority'] in PRIORITIES else PRIORITIES[1]
                new_pri = st.selectbox("Priority", PRIORITIES,
                                       index=PRIORITIES.index(default_pri),
                                       key=f"pri_{row['ticket_id']}")
            with col3:
                team_options = sorted(set(TEAMS_MAP.values()))
                default_team = row['final_team'] if row['final_team'] in team_options else team_options[0]
                new_team = st.selectbox("Team", team_options,
                                        index=team_options.index(default_team),
                                        key=f"team_{row['ticket_id']}")

            cols = st.columns([1, 1, 4])
            if cols[0].button("Save Changes", key=f"save_{row['ticket_id']}"):
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                overrides = 0
                for field, old, new in [('category', row['final_category'], new_cat),
                                         ('priority',  row['final_priority'],  new_pri),
                                         ('team',      row['final_team'],      new_team)]:
                    if old != new:
                        execute("INSERT INTO override_log (ticket_id,field_changed,old_value,new_value,reviewer,changed_at) VALUES (?,?,?,?,?,?)",
                                (row['ticket_id'], field, old, new, reviewer, now))
                        overrides += 1
                execute("UPDATE requests SET final_category=?,final_priority=?,final_team=?,override_count=override_count+? WHERE ticket_id=?",
                        (new_cat, new_pri, new_team, overrides, row['ticket_id']))
                st.success(f"{overrides} field(s) overridden and saved.")
                st.rerun()

            if cols[1].button("Close Ticket", key=f"close_{row['ticket_id']}"):
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                execute("UPDATE requests SET status='Closed', closed_at=? WHERE ticket_id=?",
                        (now, row['ticket_id']))
                st.success("Ticket closed.")
                st.rerun()

with tab2:
    cat_rows = fetch_all("SELECT final_category, COUNT(*) as c FROM requests GROUP BY final_category ORDER BY c DESC")
    pri_rows = fetch_all("SELECT final_priority, COUNT(*) as c FROM requests GROUP BY final_priority ORDER BY c DESC")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;
                    color:#3a3530;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid #1a1714;">
            By Category
        </div>""", unsafe_allow_html=True)
        for r in cat_rows:
            pct = round(r['c'] / total * 100) if total else 0
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        padding:10px 0;border-bottom:1px solid #0f0d0b;">
              <span style="font-size:0.85rem;color:#8a7e70;">{r['final_category']}</span>
              <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:80px;height:3px;background:#1a1714;border-radius:3px;overflow:hidden;">
                  <div style="width:{pct}%;height:100%;background:#d4a017;border-radius:3px;"></div>
                </div>
                <span style="font-size:0.78rem;font-weight:600;color:#5a5248;width:26px;text-align:right;">{r['c']}</span>
              </div>
            </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;
                    color:#3a3530;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid #1a1714;">
            By Priority
        </div>""", unsafe_allow_html=True)
        for r in pri_rows:
            pct = round(r['c'] / total * 100) if total else 0
            pcolor, _ = PRIORITY_COLORS.get(r['final_priority'], ('#d4a017', ''))
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        padding:10px 0;border-bottom:1px solid #0f0d0b;">
              <span style="font-size:0.85rem;color:#8a7e70;">{r['final_priority']}</span>
              <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:80px;height:3px;background:#1a1714;border-radius:3px;overflow:hidden;">
                  <div style="width:{pct}%;height:100%;background:{pcolor};border-radius:3px;"></div>
                </div>
                <span style="font-size:0.78rem;font-weight:600;color:#5a5248;width:26px;text-align:right;">{r['c']}</span>
              </div>
            </div>""", unsafe_allow_html=True)
