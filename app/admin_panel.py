import streamlit as st
import os, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import execute, fetch_all
from config import CATEGORIES, PRIORITIES, TEAMS_MAP

st.set_page_config(
    page_title="Triage Control Center — FacilityOps",
    layout="wide",
    initial_sidebar_state="expanded",
)

PCFG = {
    'Critical': ('#DC2626', '#FEF2F2', '#FECACA'),
    'High':     ('#D97706', '#FFFBEB', '#FDE68A'),
    'Medium':   ('#2563EB', '#EFF6FF', '#BFDBFE'),
    'Low':      ('#059669', '#ECFDF5', '#A7F3D0'),
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    font-family: 'Inter', system-ui, sans-serif !important;
    background: #F1F5F9 !important;
    color: #0F172A !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }
.block-container { padding: 0 40px 64px !important; max-width: 100% !important; }

/* topbar */
.topbar {
    background: #0F172A;
    padding: 0 40px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    margin-left: -40px;
    margin-right: -40px;
}
.tb-brand { display:flex; align-items:center; gap:12px; }
.tb-dot { width:8px; height:8px; background:#3B82F6; border-radius:50%; }
.tb-name { font-size:0.95rem; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; color:#F8FAFC; }
.tb-sub  { font-size:0.8125rem; color:#64748B; margin-left:4px; }
.tb-pills { display:flex; gap:10px; align-items:center; }
.tb-pill {
    font-size:0.75rem; font-weight:600; letter-spacing:0.04em;
    padding:6px 14px; border-radius:100px;
}
.tb-open   { color:#FBBF24; background:rgba(251,191,36,0.15); border:1px solid rgba(251,191,36,0.3); }
.tb-closed { color:#34D399; background:rgba(52,211,153,0.15); border:1px solid rgba(52,211,153,0.3); }

/* main layout */
.main-wrap { padding: 0; }

/* stat cards */
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:24px; margin-bottom:32px; }
.kpi-card {
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:12px;
    padding:24px;
    position:relative;
    overflow:hidden;
    box-shadow:0 1px 3px 0 rgba(0,0,0,0.05), 0 1px 2px 0 rgba(0,0,0,0.03);
    transition:all 0.2s ease;
}
.kpi-card:hover { box-shadow:0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.025); transform: translateY(-1px); }
.kpi-card::before {
    content:'';
    position:absolute;
    top:0; left:0; right:0;
    height:4px;
    border-radius:12px 12px 0 0;
}
.kpi-blue::before  { background:#3B82F6; }
.kpi-amber::before { background:#F59E0B; }
.kpi-green::before { background:#10B981; }
.kpi-indigo::before{ background:#6366F1; }
.kpi-label {
    font-size:0.75rem; font-weight:600; letter-spacing:0.05em;
    text-transform:uppercase; color:#64748B; margin-bottom:8px;
}
.kpi-value {
    font-size:2.0rem; font-weight:700; letter-spacing:-0.02em;
    color:#0F172A; line-height:1.25; font-variant-numeric: tabular-nums;
}
.kpi-sub { font-size:0.75rem; color:#64748B; margin-top:6px; font-weight:400; }

/* page section title */
.section-title {
    font-size:0.875rem; font-weight:600; letter-spacing:0.02em;
    text-transform:none; color:#334155;
    margin-bottom:20px; padding-bottom:12px;
    border-bottom:1px solid #E2E8F0;
}

/* ticket row cards */
.tkt-card {
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:12px;
    margin-bottom:12px;
    overflow:hidden;
    box-shadow:0 1px 2px rgba(0,0,0,0.04);
    transition:all 0.2s ease;
}
.tkt-card:hover { box-shadow:0 4px 12px rgba(0,0,0,0.08); border-color:#CBD5E1; }
.p-chip {
    display:inline-flex; align-items:center;
    font-size:0.75rem; font-weight:600; letter-spacing:0.02em;
    text-transform:uppercase; padding:4px 12px; border-radius:100px;
}
.conf-bar {
    display:inline-block; width:60px; height:6px;
    background:#F1F5F9; border-radius:5px; overflow:hidden;
    vertical-align:middle; margin-right:6px;
}
.conf-fill { height:100%; border-radius:5px; background:#3B82F6; }

/* insights table */
.ins-row {
    display:flex; align-items:center; justify-content:space-between;
    padding:12px 0; border-bottom:1px solid #F1F5F9;
}
.ins-row:last-child { border-bottom:none; }
.ins-label { font-size:0.875rem; color:#475569; }
.ins-bar-wrap { display:flex; align-items:center; gap:12px; }
.ins-bar { width:120px; height:6px; background:#F1F5F9; border-radius:5px; overflow:hidden; }
.ins-fill { height:100%; border-radius:5px; }
.ins-count { font-size:0.875rem; font-weight:600; color:#0F172A; min-width:24px; text-align:right; }

/* sidebar */
section[data-testid="stSidebar"] {
    background:#FFFFFF !important;
    border-right:1px solid #E2E8F0 !important;
}
section[data-testid="stSidebar"] label {
    font-size:0.75rem !important; font-weight:600 !important;
    letter-spacing:0.05em !important; text-transform:uppercase !important;
    color:#64748B !important;
}
section[data-testid="stSidebar"] input {
    background:#F8FAFC !important; border:1px solid #E2E8F0 !important;
    border-radius:8px !important; color:#0F172A !important;
    font-family:'Inter',sans-serif !important;
    padding: 8px 12px !important;
}

/* expander */
div[data-testid="stExpander"] {
    background:#FFFFFF !important;
    border:1px solid #E2E8F0 !important;
    border-radius:12px !important;
    margin-bottom:12px !important;
    box-shadow:0 1px 2px rgba(0,0,0,0.04) !important;
    overflow:hidden !important;
}
div[data-testid="stExpander"] summary {
    font-size:0.875rem !important; font-weight:500 !important;
    color:#1E293B !important; padding:16px 24px !important;
    font-family:'Inter', sans-serif !important;
}
div[data-testid="stExpander"] summary:hover { color:#0F172A !important; }
div[data-testid="stExpander"] label {
    font-size:0.75rem !important; font-weight:600 !important;
    letter-spacing:0.05em !important; text-transform:uppercase !important;
    color:#64748B !important;
}
div[data-testid="stExpander"] .stSelectbox > div > div {
    background:#F8FAFC !important; border:1px solid #E2E8F0 !important;
    border-radius:8px !important; color:#0F172A !important;
    font-family:'Inter',sans-serif !important; font-size:0.875rem !important;
}
div[data-testid="stExpander"] .stTextArea textarea {
    background:#F8FAFC !important; border:1px solid #E2E8F0 !important;
    border-radius:8px !important; color:#475569 !important;
    font-family:'JetBrains Mono',monospace !important; font-size:0.8125rem !important;
    line-height: 1.5 !important;
}

/* buttons */
.stButton > button {
    font-family:'Inter',sans-serif !important;
    font-size:0.8125rem !important; font-weight:600 !important;
    border-radius:8px !important; border:none !important;
    padding:10px 18px !important; width:100% !important;
    transition:all 0.15s ease !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button {
    background:#EFF6FF !important; color:#2563EB !important;
    border:1px solid #BFDBFE !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button:hover {
    background:#DBEAFE !important; transform:translateY(-1px) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button {
    background:#F0FDF4 !important; color:#059669 !important;
    border:1px solid #A7F3D0 !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button:hover {
    background:#DCFCE7 !important; transform:translateY(-1px) !important;
}

div[data-testid="stAlert"] {
    border-radius:8px !important; font-size:0.82rem !important;
    font-family:'Inter',sans-serif !important;
}
div[data-testid="stInfo"] {
    background:#F8FAFC !important; border:1px solid #E2E8F0 !important;
    border-radius:8px !important; color:#475569 !important;
    font-size:0.88rem !important; font-family:'Inter',sans-serif !important;
}

::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#CBD5E1; border-radius:4px; }
</style>
""", unsafe_allow_html=True)

# ── Data ────────────────────────────────────────────────────────────────────
total      = fetch_all("SELECT COUNT(*) as c FROM requests")[0]['c']
open_count = fetch_all("SELECT COUNT(*) as c FROM requests WHERE status='Open'")[0]['c']
closed_count = total - open_count
ai_ok      = fetch_all("SELECT COUNT(*) as c FROM requests WHERE override_count=0 AND status='Closed'")[0]['c']
accuracy   = f"{round((ai_ok/closed_count)*100,1)}%" if closed_count else "--"
override_total = fetch_all("SELECT COUNT(*) as c FROM override_log")[0]['c']

# ── Sidebar ─────────────────────────────────────────────────────────────────
if 'reviewer' not in st.session_state:
    st.session_state.reviewer = "Admin"
st.sidebar.markdown("""
<div style="padding:16px 0 4px;">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#94A3B8;margin-bottom:16px;">
    Reviewer Identity
  </div>
</div>""", unsafe_allow_html=True)
st.session_state.reviewer = st.sidebar.text_input("Name", value=st.session_state.reviewer, label_visibility="collapsed")
reviewer = st.session_state.reviewer

st.sidebar.markdown(f"""
<div style="margin-top:24px;padding:16px;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#94A3B8;margin-bottom:14px;">Queue Summary</div>
  <div style="display:flex;flex-direction:column;gap:10px;">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:0.83rem;color:#64748B;font-weight:500;">Open</span>
      <span style="font-size:0.83rem;font-weight:700;color:#D97706;background:#FFFBEB;padding:2px 10px;border-radius:6px;">{open_count}</span>
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:0.83rem;color:#64748B;font-weight:500;">Closed</span>
      <span style="font-size:0.83rem;font-weight:700;color:#059669;background:#ECFDF5;padding:2px 10px;border-radius:6px;">{closed_count}</span>
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:0.83rem;color:#64748B;font-weight:500;">AI Accuracy</span>
      <span style="font-size:0.83rem;font-weight:700;color:#2563EB;background:#EFF6FF;padding:2px 10px;border-radius:6px;">{accuracy}</span>
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:0.83rem;color:#64748B;font-weight:500;">Overrides</span>
      <span style="font-size:0.83rem;font-weight:700;color:#6366F1;background:#EEF2FF;padding:2px 10px;border-radius:6px;">{override_total}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Topbar ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
  <div class="tb-brand">
    <div class="tb-dot"></div>
    <span class="tb-name">FacilityOps</span>
    <span class="tb-sub">/ Triage Control</span>
  </div>
  <div class="tb-pills">
    <span class="tb-pill tb-open">{open_count} Open</span>
    <span class="tb-pill tb-closed">{closed_count} Closed</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Spacer ──────────────────────────────────────────────────────────────────
st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

# ── KPI Cards ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card kpi-blue">
    <div class="kpi-label">Total Requests</div>
    <div class="kpi-value">{total}</div>
    <div class="kpi-sub">All time submissions</div>
  </div>
  <div class="kpi-card kpi-amber">
    <div class="kpi-label">Open Queue</div>
    <div class="kpi-value">{open_count}</div>
    <div class="kpi-sub">Pending resolution</div>
  </div>
  <div class="kpi-card kpi-green">
    <div class="kpi-label">AI Accuracy</div>
    <div class="kpi-value">{accuracy}</div>
    <div class="kpi-sub">Closed without override</div>
  </div>
  <div class="kpi-card kpi-indigo">
    <div class="kpi-label">Override Events</div>
    <div class="kpi-value">{override_total}</div>
    <div class="kpi-sub">Reviewer corrections</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Open Tickets", "Operational Insights"])

with tab1:
    rows = fetch_all("SELECT * FROM requests WHERE status='Open' ORDER BY submitted_at DESC")

    if not rows:
        st.markdown("""
        <div style="text-align:center;padding:60px;background:#FFFFFF;border:1px solid #E2E8F0;border-radius:14px;color:#94A3B8;font-size:0.9rem;">
            No open tickets in the queue.
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="section-title">{len(rows)} Open Ticket{"s" if len(rows)!=1 else ""}</div>', unsafe_allow_html=True)

    for row in rows:
        prio = row['suggested_priority']
        fc, bg, bd = PCFG.get(prio, ('#2563EB','#EFF6FF','#BFDBFE'))
        conf = int(row['suggested_confidence'] * 100)
        header = f"{row['ticket_id']}  ·  {row['suggested_category']}  {conf}%  ·  {row['submitter']}  ·  {row['site']}"

        with st.expander(header):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
              <span class="p-chip" style="color:{fc};background:{bg};border:1px solid {bd};">{prio}</span>
              <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#94A3B8;">{row['submitted_at']}</span>
            </div>""", unsafe_allow_html=True)

            st.info(row['description'])
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#94A3B8;margin-bottom:10px;">Override Assignment</div>', unsafe_allow_html=True)

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
                st.success(f"{overrides} field(s) saved.")
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
    team_rows = fetch_all("SELECT final_team, COUNT(*) as c FROM requests GROUP BY final_team ORDER BY c DESC")

    cat_col, pri_col = st.columns(2)

    CAT_COLORS = ['#3B82F6','#6366F1','#8B5CF6','#EC4899','#F59E0B','#10B981','#EF4444','#14B8A6']

    with cat_col:
        cat_html = '<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:14px;padding:22px 24px;box-shadow:0 1px 3px rgba(0,0,0,0.04);"><div class="section-title">Tickets by Category</div>'
        for i, r in enumerate(cat_rows):
            pct = round(r['c'] / total * 100) if total else 0
            color = CAT_COLORS[i % len(CAT_COLORS)]
            cat_html += f'<div class="ins-row"><span class="ins-label">{r["final_category"]}</span><div class="ins-bar-wrap"><div class="ins-bar"><div class="ins-fill" style="width:{pct}%;background:{color};"></div></div><span class="ins-count">{r["c"]}</span></div></div>'
        cat_html += "</div>"
        st.markdown(cat_html, unsafe_allow_html=True)

    with pri_col:
        pri_html = '<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:14px;padding:22px 24px;box-shadow:0 1px 3px rgba(0,0,0,0.04);"><div class="section-title">Tickets by Priority</div>'
        for r in pri_rows:
            pct = round(r['c'] / total * 100) if total else 0
            fc, _, _ = PCFG.get(r['final_priority'], ('#3B82F6','',''))
            pri_html += f'<div class="ins-row"><span class="ins-label">{r["final_priority"]}</span><div class="ins-bar-wrap"><div class="ins-bar"><div class="ins-fill" style="width:{pct}%;background:{fc};"></div></div><span class="ins-count">{r["c"]}</span></div></div>'
        pri_html += "</div>"
        st.markdown(pri_html, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Team workload card
    team_html = '<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:14px;padding:22px 24px;box-shadow:0 1px 3px rgba(0,0,0,0.04);"><div class="section-title">Workload by Team</div>'
    for r in team_rows:
        pct = round(r['c'] / total * 100) if total else 0
        team_html += f'<div class="ins-row"><span class="ins-label">{r["final_team"]}</span><div class="ins-bar-wrap"><div class="ins-bar" style="width:160px;"><div class="ins-fill" style="width:{pct}%;background:#6366F1;"></div></div><span class="ins-count">{r["c"]}</span></div></div>'
    team_html += "</div>"
    st.markdown(team_html, unsafe_allow_html=True)
