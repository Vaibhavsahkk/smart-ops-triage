import os, sys, uuid, random
from datetime import datetime, timedelta
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

from faker import Faker
from app.db import execute
from app.triage_engine import triage
from config import SITES, BUILDINGS

fake = Faker()
random.seed(42)

SAMPLE_DESCRIPTIONS = [
    "AC not working in conference room",
    "Light flickering in corridor",
    "Water leak under sink urgent",
    "Broken chair needs replacement",
    "Power outlet not working at desk",
    "Setup projector for meeting tomorrow",
    "Bulb fused in cabin",
    "Pipe leaking flooding the room emergency",
    "Wall paint scratch near elevator",
    "Temperature too hot climate issue",
    "Toilet flush broken",
    "Furniture moving needed",
    "Electrical shock from socket danger",
    "Minor cosmetic damage on wall",
    "AC stopped cooling completely",
    "Humidity too high in lab",
    "Lamp not turning on at workstation",
    "Cabinet door broken",
    "Drain blocked in restroom",
    "Conference room paint chipped"
]

for i in range(60):
    desc = random.choice(SAMPLE_DESCRIPTIONS)
    r = triage(desc)
    tid = f"REQ-{uuid.uuid4().hex[:8].upper()}"
    # Vary submitted_at across last 60 days for realistic time-series
    days_ago = random.randint(0, 60)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    submitted_at = (datetime.now() - timedelta(days=days_ago, hours=hours, minutes=minutes)).strftime('%Y-%m-%d %H:%M:%S')

    execute("""
        INSERT INTO requests (
            ticket_id, submitter, site, building, description,
            suggested_category, suggested_confidence, final_category,
            suggested_priority, final_priority,
            suggested_team, final_team,
            submitted_at, triage_time_ms, notification_sent
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (tid, fake.name(), random.choice(SITES), random.choice(BUILDINGS), desc,
          r['category'], r['confidence'], r['category'],
          r['priority'], r['priority'],
          r['team'], r['team'],
          submitted_at, r['triage_time_ms']))

print("Seeded 60 sample requests with varied timestamps.")
