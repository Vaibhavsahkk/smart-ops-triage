import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Database
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'triage.db')

# Export
EXPORT_DIR = os.path.join(PROJECT_ROOT, 'data', 'exports')

# Sites and teams
SITES = ['Site-A', 'Site-B', 'Site-C']
BUILDINGS = ['Bldg-1', 'Bldg-2', 'Bldg-3', 'Bldg-4']
CATEGORIES = ['HVAC', 'Electrical', 'Plumbing', 'Furniture',
              'Lighting', 'Painting', 'Climate Control', 'Event Support']
PRIORITIES = ['Low', 'Medium', 'High', 'Critical']
TEAMS_MAP = {
    'HVAC': 'Team-HVAC',
    'Electrical': 'Team-Electrical',
    'Plumbing': 'Team-Plumbing',
    'Lighting': 'Team-Electrical',
    'Furniture': 'Team-General',
    'Painting': 'Team-General',
    'Climate Control': 'Team-HVAC',
    'Event Support': 'Team-General'
}
SLA_MAP = {'Low': 72, 'Medium': 48, 'High': 24, 'Critical': 8}

# Notification (leave empty to skip without errors)
EMAIL_FROM = ""
EMAIL_APP_PASSWORD = ""
TEAMS_WEBHOOK_URL = ""

# SLA on automation itself
AUTOMATION_SLA_MS = 5000  # target: triage under 5000 ms (5 sec)
