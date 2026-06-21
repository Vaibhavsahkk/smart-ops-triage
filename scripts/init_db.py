import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

from app.db import execute

execute("""
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT UNIQUE,
    submitter TEXT,
    site TEXT,
    building TEXT,
    description TEXT,
    suggested_category TEXT,
    suggested_confidence REAL,
    final_category TEXT,
    suggested_priority TEXT,
    final_priority TEXT,
    suggested_team TEXT,
    final_team TEXT,
    status TEXT DEFAULT 'Open',
    submitted_at TEXT,
    closed_at TEXT,
    triage_time_ms REAL,
    override_count INTEGER DEFAULT 0,
    notification_sent INTEGER DEFAULT 0
)
""")

execute("""
CREATE TABLE IF NOT EXISTS override_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT,
    field_changed TEXT,
    old_value TEXT,
    new_value TEXT,
    reviewer TEXT,
    changed_at TEXT
)
""")

print("Database initialized at data/triage.db")
