import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
from app.db import get_connection
from config import EXPORT_DIR

os.makedirs(EXPORT_DIR, exist_ok=True)
conn = get_connection()

requests_df = pd.read_sql_query("SELECT * FROM requests", conn)
overrides_df = pd.read_sql_query("SELECT * FROM override_log", conn)

# Extract date portion for Calendar relationship
if not requests_df.empty:
    requests_df['SubmittedDate'] = pd.to_datetime(requests_df['submitted_at']).dt.date

requests_df.to_csv(os.path.join(EXPORT_DIR, 'requests.csv'), index=False)
overrides_df.to_csv(os.path.join(EXPORT_DIR, 'overrides.csv'), index=False)

conn.close()
print(f"Exported {len(requests_df)} requests + {len(overrides_df)} overrides to {EXPORT_DIR}")
