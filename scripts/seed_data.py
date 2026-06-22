import os, sys, uuid, random
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

from faker import Faker
from app.db import execute, fetch_all
from app.triage_engine import triage
from config import SITES, BUILDINGS, CATEGORIES, PRIORITIES, TEAMS_MAP

fake = Faker()
random.seed(99)

# ── Diverse descriptions spanning all 8 categories ──────────────────────────
DESCRIPTIONS = [
    # HVAC (6)
    "AC unit stopped cooling completely in Room 201 — temperature rising fast",
    "Chiller making loud noise and not maintaining temperature in server room",
    "Air conditioning vent blocked, office getting very warm",
    "HVAC system keeps shutting down on Floor 3, urgent cooling issue",
    "Cooling tower leaking refrigerant, needs immediate check",
    "Ventilation fan motor broken in cafeteria — very stuffy",
    # Electrical (6)
    "Power outlet sparking at desk near window — electrical shock risk",
    "Main breaker tripped twice today, entire wing on backup",
    "Multiple sockets not working in conference room B2",
    "Electrical fuse blown in server cabinet, equipment down",
    "Wire exposed near reception area — safety hazard",
    "UPS unit failed, power backup for lab equipment gone",
    # Plumbing (6)
    "Water leak under sink in 2nd floor restroom — flooding starting",
    "Pipe burst near boiler room, water everywhere, emergency",
    "Toilet flush broken in executive washroom",
    "Drain completely blocked in ground floor kitchen",
    "Tap dripping constantly in pantry, wasting water",
    "Sink water pressure very low on 4th floor",
    # Lighting (5)
    "Light bulb fused in main corridor near elevator bank",
    "LED panel flickering badly in open-plan office area",
    "Lamp not turning on at workstation Row C",
    "Entire staircase lighting dark — safety concern",
    "Conference room A1 lights dim and buzzing",
    # Furniture (5)
    "Broken chair armrest in Manager cabin 302",
    "Standing desk hydraulic lift stuck, cannot adjust height",
    "Cabinet door hinge snapped, files falling out",
    "Reception sofa torn and needs upholstery replacement",
    "Desk drawer jammed shut with documents inside",
    # Painting (4)
    "Large scratch on wall near elevator lobby, very visible",
    "Paint peeling off ceiling in storage room — cosmetic issue",
    "Wall stain near water cooler, unsightly for visitors",
    "Minor scuff marks on corridor walls near loading bay",
    # Climate Control (4)
    "Humidity extremely high in laboratory — equipment risk",
    "Room too cold due to climate control override, staff complaining",
    "Ventilation system not responding to thermostat settings",
    "Temperature too hot on 5th floor, climate system unresponsive",
    # Event Support (4)
    "Projector in boardroom not connecting to laptop via HDMI",
    "Meeting room B setup needed for all-hands event tomorrow",
    "Conference system microphone not working for executive meeting",
    "Event setup required for product launch in Hall A next week",
]

# ── Helper ───────────────────────────────────────────────────────────────────
def rand_dt(days_back_max=365):
    d = random.randint(1, days_back_max)
    h = random.randint(0, 23)
    m = random.randint(0, 59)
    return (datetime.now() - timedelta(days=d, hours=h, minutes=m)).strftime('%Y-%m-%d %H:%M:%S')

def rand_close_dt(submitted_at, hours_offset_max=72):
    base = datetime.strptime(submitted_at, '%Y-%m-%d %H:%M:%S')
    offset = random.randint(1, hours_offset_max)
    return (base + timedelta(hours=offset)).strftime('%Y-%m-%d %H:%M:%S')

# ── Shuffle descriptions for variety ─────────────────────────────────────────
pool = DESCRIPTIONS * 2          # 80 items → sample 75
random.shuffle(pool)
pool = pool[:75]

tickets_inserted = 0

# ─────────────────────────────────────────────────────────────────────────────
# BLOCK A: 25 closed tickets — AI correct, zero overrides  (AI accuracy WIN)
# ─────────────────────────────────────────────────────────────────────────────
for i in range(25):
    desc = pool[i]
    r = triage(desc)
    tid = f"REQ-{uuid.uuid4().hex[:8].upper()}"
    sub = rand_dt(300)
    clo = rand_close_dt(sub, 48)

    execute("""
        INSERT INTO requests (
            ticket_id, submitter, site, building, description,
            suggested_category, suggested_confidence, final_category,
            suggested_priority, final_priority,
            suggested_team, final_team,
            status, submitted_at, closed_at, triage_time_ms,
            override_count, notification_sent
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tid, fake.name(), random.choice(SITES), random.choice(BUILDINGS), desc,
        r['category'], r['confidence'], r['category'],
        r['priority'], r['priority'],
        r['team'], r['team'],
        'Closed', sub, clo, r['triage_time_ms'], 0, 1
    ))
    tickets_inserted += 1

# ─────────────────────────────────────────────────────────────────────────────
# BLOCK B: 10 closed tickets — reviewer overrode category/priority (AI MISS)
# ─────────────────────────────────────────────────────────────────────────────
OVERRIDE_PAIRS = [
    # (description, corrected_category, corrected_priority)
    ("Desk area uncomfortable due to cold air from vent", "Climate Control", "Medium"),
    ("Pipe rattling loudly inside wall — not a leak", "Plumbing", "Low"),
    ("Power LED on server rack is off, no shutdown observed", "Electrical", "Low"),
    ("Broken leg on conference table", "Furniture", "Medium"),
    ("Paint fumes in corridor after maintenance visit", "Painting", "High"),
    ("Event room chairs need rearranging before board meeting", "Event Support", "Low"),
    ("Water cooler not dispensing — needs technician", "Plumbing", "Medium"),
    ("Flickering screen on projector during presentations", "Event Support", "Medium"),
    ("Cabinet not locking properly — security concern", "Furniture", "High"),
    ("Room humidifier unit broken, air very dry", "Climate Control", "Low"),
]

reviewer_names = ["Arjun Singh", "Priya Mehta", "Rohan Verma", "Sneha Kapoor"]

for i, (desc, correct_cat, correct_pri) in enumerate(OVERRIDE_PAIRS):
    r = triage(desc)
    tid = f"REQ-{uuid.uuid4().hex[:8].upper()}"
    sub = rand_dt(200)
    clo = rand_close_dt(sub, 36)
    now_str = rand_close_dt(sub, 5)   # reviewer acted early
    reviewer = random.choice(reviewer_names)
    correct_team = TEAMS_MAP.get(correct_cat, 'Team-General')

    row_id = execute("""
        INSERT INTO requests (
            ticket_id, submitter, site, building, description,
            suggested_category, suggested_confidence, final_category,
            suggested_priority, final_priority,
            suggested_team, final_team,
            status, submitted_at, closed_at, triage_time_ms,
            override_count, notification_sent
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tid, fake.name(), random.choice(SITES), random.choice(BUILDINGS), desc,
        r['category'], r['confidence'], correct_cat,
        r['priority'], correct_pri,
        r['team'], correct_team,
        'Closed', sub, clo, r['triage_time_ms'], 2, 1
    ))

    # Log overrides
    if r['category'] != correct_cat:
        execute("""
            INSERT INTO override_log (ticket_id, field_changed, old_value, new_value, reviewer, changed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tid, 'category', r['category'], correct_cat, reviewer, now_str))

    if r['priority'] != correct_pri:
        execute("""
            INSERT INTO override_log (ticket_id, field_changed, old_value, new_value, reviewer, changed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tid, 'priority', r['priority'], correct_pri, reviewer, now_str))

    tickets_inserted += 1

# ─────────────────────────────────────────────────────────────────────────────
# BLOCK C: 15 open tickets — active queue (varied, recent)
# ─────────────────────────────────────────────────────────────────────────────
for i in range(25, 40):
    desc = pool[i]
    r = triage(desc)
    tid = f"REQ-{uuid.uuid4().hex[:8].upper()}"
    sub = rand_dt(30)   # recent — last 30 days

    execute("""
        INSERT INTO requests (
            ticket_id, submitter, site, building, description,
            suggested_category, suggested_confidence, final_category,
            suggested_priority, final_priority,
            suggested_team, final_team,
            status, submitted_at, triage_time_ms,
            override_count, notification_sent
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tid, fake.name(), random.choice(SITES), random.choice(BUILDINGS), desc,
        r['category'], r['confidence'], r['category'],
        r['priority'], r['priority'],
        r['team'], r['team'],
        'Open', sub, r['triage_time_ms'], 0, 1
    ))
    tickets_inserted += 1

total_closed = 35
ai_wins = 25
accuracy = round(ai_wins / total_closed * 100, 1)
print(f"[OK] Seeded {tickets_inserted} tickets:")
print(f"     25 closed - AI correct (no overrides)")
print(f"     10 closed - reviewer overrode (logged in override_log)")
print(f"     15 open   - active queue")
print(f"     Simulated AI Accuracy: {accuracy}%  ({ai_wins}/{total_closed} closed without override)")
