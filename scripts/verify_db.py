import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from app.db import fetch_all

total   = fetch_all("SELECT COUNT(*) as c FROM requests")[0]["c"]
closed  = fetch_all("SELECT COUNT(*) as c FROM requests WHERE status='Closed'")[0]["c"]
open_c  = fetch_all("SELECT COUNT(*) as c FROM requests WHERE status='Open'")[0]["c"]
ai_ok   = fetch_all("SELECT COUNT(*) as c FROM requests WHERE override_count=0 AND status='Closed'")[0]["c"]
overrides = fetch_all("SELECT COUNT(*) as c FROM override_log")[0]["c"]
cats    = fetch_all("SELECT final_category, COUNT(*) as c FROM requests GROUP BY final_category ORDER BY c DESC")
accuracy = round((ai_ok / closed) * 100, 1) if closed else 0.0

print(f"Total: {total}  |  Open: {open_c}  |  Closed: {closed}")
print(f"AI Accuracy: {ai_ok}/{closed} = {accuracy}%")
print(f"Override log entries: {overrides}")
print("Category spread:")
for r in cats:
    print(f"  {r['final_category']}: {r['c']}")
