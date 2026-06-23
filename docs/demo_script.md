# Demo Script — Smart Facilities Request Triage System
**Presenter:** Vaibhav Kumar
**Target Audience:** Hiring Manager / Technical Recruiter / Engineering Manager
**Estimated Duration:** Exactly 2.5 minutes (150 seconds)
**Tone:** Confident, professional, clear, and direct.

---

## STEP 0 — QUICK PREPARATION (Do This Before Starting)

1. Launch the applications in your terminal from the project root:
   ```bash
   # Terminal 1: Launch Employee Portal
   streamlit run app/user_form.py --server.port 8501
   
   # Terminal 2: Launch Admin Control Center
   streamlit run app/admin_panel.py --server.port 8502
   ```
2. Open browser tabs:
   - Tab 1 → `http://localhost:8502` (Admin Panel — open to the "Open Tickets" tab)
   - Tab 2 → `http://localhost:8501` (Employee Portal)
3. Open `app/triage_engine.py` in VS Code to be ready for the code section.

---

## SEGMENT 1 — INTRODUCTION & PROBLEM [0:00 to 0:30]

> **ACTION:** Show the Admin Panel (`localhost:8502`) with the KPI cards visible at the top.

**SPEAK:**

"Hi, I am Vaibhav Kumar. Today, I'm showing you the Smart Facilities Request Triage System that I developed.

In large facilities—like offices or plants—handling maintenance requests is manually bottlenecked. An employee reports an issue, a coordinator reads it, determines the department, and forwards it. 

To automate this, I built an intelligent triage layer. It processes free-text descriptions, classifies them, prioritizes them, and routes them to the correct team in under a millisecond. Let's see how."

---

## SEGMENT 2 — INTAKE & DIRECT EMAIL/CHAT ROUTING [0:30 to 1:15]

> **ACTION:** Switch browser tab to the Employee Portal (`localhost:8501`).

**SPEAK:**

"This is the employee portal. If an employee reports a water issue—like typing: *'Water leakage in building 3 bathroom, floor is flooded'*—and hits submit, the engine processes it instantly.

The system reads the text and assigns it to 'Plumbing' with 'Medium' priority. It immediately logs the ticket and dispatches a notification via email, Slack, directly to the plumbing department (e.g., `team-plumbing@example.com`). 

If SMTP credentials or webhooks are active in production, the alert is sent instantly; otherwise, it logs a clean fallback trace to the terminal console so development is never blocked."

---

## SEGMENT 3 — ADMIN OVERRIDES & AUDIT TRAIL [1:15 to 1:55]

> **ACTION:** Switch to the Admin Panel (`localhost:8502`) and expand the first open ticket.

**SPEAK:**

"On the admin panel, coordinators see the active queue and metrics like our 71% AI accuracy—representing closed tickets resolved without human correction. 

If the automated system makes a mistake, the admin can manually override the category, priority, or team. 

Saving an override updates the ticket and logs a row in the `override_log` table. This provides a strict audit trail for compliance and builds a clean dataset for training future machine learning models."

---

## SEGMENT 4 — INSIGHTS & EXPLAINABLE CODE [1:55 to 2:30]

> **ACTION:** Click the "Operational Insights" tab, then briefly show `app/triage_engine.py` in VS Code.

**SPEAK:**

"The Operational Insights tab visualizes real-world data like category distributions and team workloads. 

Under the hood, the backend uses a deterministic python regex engine with word-boundary matching. This ensures the classification is explainable, fully auditable, and runs instantly in microseconds. 

This system guarantees that facility requests are resolved faster, routing is fully automated, and every decision is explainable. 

I am happy to dive deeper into the codebase or schema now."

---

## DELIVERY QUICK REFERENCE

| Time | Action | Speaking Focus |
|---|---|---|
| **0:00 - 0:30** | Show `localhost:8502` | Introduce yourself (Vaibhav Kumar) and the manual routing bottleneck. |
| **0:30 - 1:15** | Switch to `localhost:8501`, submit plumbing text | Explain classification and direct notification to plumbing/electrical via email/Slack/Teams. |
| **1:15 - 1:55** | Show `localhost:8502`, perform override | Explain the 71% accuracy stat and the compliance `override_log` audit trail. |
| **1:55 - 2:30** | Show Insights tab, then code in VS Code | Explain the regex engine's explainability and invite questions. |
