import os, sys, smtplib, requests
from email.mime.text import MIMEText
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EMAIL_FROM, EMAIL_APP_PASSWORD, TEAMS_WEBHOOK_URL

def send_email(to_email: str, subject: str, body: str) -> bool:
    if not EMAIL_FROM or not EMAIL_APP_PASSWORD:
        print(f"[EMAIL SKIPPED] To: {to_email} | Subject: {subject}")
        return False
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(EMAIL_FROM, EMAIL_APP_PASSWORD)
            s.send_message(msg)
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

def send_teams(message: str) -> bool:
    if not TEAMS_WEBHOOK_URL:
        print(f"[TEAMS SKIPPED] {message[:120]}")
        return False
    try:
        r = requests.post(TEAMS_WEBHOOK_URL, json={'text': message}, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[TEAMS ERROR] {e}")
        return False

def notify(ticket_id: str, category: str, priority: str, team: str, description: str) -> bool:
    subject = f"[{priority}] New Facilities Request: {ticket_id}"
    body = f"""A new facilities request has been auto-triaged.

Ticket ID: {ticket_id}
Category: {category}
Priority: {priority}
Assigned Team: {team}

Description:
{description}

This is an automated notification from the Smart Triage System.
"""
    email_ok = send_email(f"{team.lower()}@example.com", subject, body)
    teams_ok = send_teams(f"{subject}\nTeam: {team}\nDescription: {description[:200]}")
    return email_ok or teams_ok
