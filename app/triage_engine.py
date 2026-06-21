import os, sys, re, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CATEGORIES, PRIORITIES, TEAMS_MAP, SLA_MAP

# Keywords must match as whole words (e.g. 'ac' should NOT match inside 'replacement')
CATEGORY_KEYWORDS = {
    'HVAC': ['ac', 'air conditioning', 'cooling', 'heating', 'ventilation', 'chiller', 'temperature'],
    'Electrical': ['power', 'electricity', 'outlet', 'socket', 'wire', 'breaker', 'fuse', 'shock'],
    'Plumbing': ['water', 'leak', 'pipe', 'drain', 'toilet', 'sink', 'tap', 'flooding'],
    'Furniture': ['chair', 'desk', 'table', 'cabinet', 'furniture', 'broken seat'],
    'Lighting': ['light', 'bulb', 'lamp', 'flicker', 'dark', 'led', 'dim'],
    'Painting': ['paint', 'wall', 'scratch', 'mark', 'stain'],
    'Climate Control': ['humidity', 'too cold', 'too hot', 'climate', 'ventilation'],
    'Event Support': ['event', 'setup', 'meeting', 'projector', 'conference']
}

PRIORITY_KEYWORDS = {
    'Critical': ['emergency', 'urgent', 'fire', 'flood', 'shock', 'gas', 'shut down', 'danger'],
    'High': ['not working', 'broken', 'failed', 'major', 'severe', 'stuck'],
    'Medium': ['issue', 'problem', 'slow', 'partial'],
    'Low': ['minor', 'small', 'cosmetic', 'whenever']
}


def _match(keyword: str, text: str) -> bool:
    """Word-boundary safe keyword match. Handles multi-word phrases too."""
    pattern = r'\b' + re.escape(keyword) + r'\b'
    return bool(re.search(pattern, text))


def categorize(description: str) -> tuple:
    text = description.lower()
    scores = {cat: 0 for cat in CATEGORIES}
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if _match(kw, text):
                scores[cat] += 1
    best = max(scores, key=scores.get)
    total = sum(scores.values())
    if total == 0:
        return 'Furniture', 0.0
    confidence = round(scores[best] / total, 2)
    return best, confidence


def predict_priority(description: str) -> str:
    text = description.lower()
    for prio in ['Critical', 'High', 'Medium', 'Low']:
        for kw in PRIORITY_KEYWORDS[prio]:
            if _match(kw, text):
                return prio
    return 'Medium'


def route_team(category: str) -> str:
    return TEAMS_MAP.get(category, 'Team-General')


def triage(description: str) -> dict:
    if not description or not isinstance(description, str):
        description = ""
    start = time.perf_counter()
    category, confidence = categorize(description)
    priority = predict_priority(description)
    team = route_team(category)
    sla_hours = SLA_MAP[priority]
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    return {
        'category': category,
        'confidence': confidence,
        'priority': priority,
        'team': team,
        'sla_hours': sla_hours,
        'triage_time_ms': duration_ms
    }
