# FINAL LOOM SCRIPT: Smart Facilities Request Triage System
**Presenter:** Vaibhav Kumar | **Target:** 5 Minutes | **Style:** Read directly from screen

---

> **BEFORE YOU HIT RECORD — DO THIS:**
> - Terminal 1: `streamlit run app/user_form.py --server.port 8501` (File: [app/user_form.py](file:///d:/GFD%28PROJECT-2%29/app/user_form.py))
> - Terminal 2: `streamlit run app/admin_panel.py --server.port 8502` (File: [app/admin_panel.py](file:///d:/GFD%28PROJECT-2%29/app/admin_panel.py))
> - Browser Tab 1: `localhost:8502` (Admin Panel - KPI cards visible)
> - Browser Tab 2: `localhost:8501` (Employee Portal - empty form)
> - VS Code: Open [config.py](file:///d:/GFD%28PROJECT-2%29/config.py), [app/triage_engine.py](file:///d:/GFD%28PROJECT-2%29/app/triage_engine.py), [scripts/init_db.py](file:///d:/GFD%28PROJECT-2%29/scripts/init_db.py), [app/notifier.py](file:///d:/GFD%28PROJECT-2%29/app/notifier.py)
> - GitHub: Open commit history page in a browser tab
> - Ensure VS Code Explorer sidebar is collapsed, but ready to open with Ctrl+B

---

## SCENE 1 - INTRODUCTION [00:00 - 00:15]

**SCREEN:** Browser, Tab 1: `localhost:8502` Admin Panel - KPI cards fully visible, no scrolling. Do not click anything.

**SPEAK:**

Hi, my name is Vaibhav Kumar.
Today, I want to walk you through a project I am really proud of:
the Smart Facilities Request Triage System.
I built this to solve a real-world operational problem,
and I will show you the live application, the code, the architecture,
and the engineering decisions behind every layer.

---

## SCENE 2 - THE PROBLEM [00:15 - 00:40]

**SCREEN:** Stay on Admin Panel. Slowly move your cursor over each of the four KPI cards (Total Requests, Open Queue, AI Accuracy, Override Events) as you name them.

**SPEAK:**

In large organizations, offices, campuses, manufacturing plants,
when something breaks, an employee sends an email or fills out a form.
Then a coordinator has to manually read it,
figure out if it is an HVAC issue or a plumbing issue,
decide how urgent it is, and route it to the right maintenance team.
At hundreds of sites and thousands of requests per week,
that manual step is the bottleneck.
I automated that entire middle layer.

---

## SCENE 3 - ARCHITECTURE OVERVIEW [00:40 - 01:10]

**SCREEN:** Switch to VS Code → [config.py](file:///d:/GFD%28PROJECT-2%29/config.py). Scroll slowly so `CATEGORIES`, `TEAMS_MAP`, and `SLA_MAP` are visible one by one.

**SPEAK:**

Everything in this project is driven by a central configuration file.
You can see eight facility categories defined here:
HVAC, Electrical, Plumbing, Lighting, Furniture, and more.
Each category maps to a maintenance team in this dictionary.
And each priority level maps to an SLA window:
eight hours for Critical, all the way to seventy-two hours for Low.

The flow is simple.
An employee submits a free-text description through a portal.
That text hits a triage engine written in pure Python.
The engine categorizes the request, assigns a priority, routes it to the correct team,
and writes a structured ticket to a SQLite database.
A notification goes out to email and Microsoft Teams.
On the admin side, a reviewer can inspect, override, and close tickets.
And the override data flows into a Power BI analytics dashboard.

---

## SCENE 4 - PROJECT STRUCTURE [01:10 - 01:25]

**SCREEN:** VS Code → open the Explorer sidebar (Ctrl+B). Hover your cursor over each folder as you name it: `app`, `scripts`, `automation`, `data`, `docs`. Collapse the sidebar again when finished.

**SPEAK:**

The project is cleanly organized.
The `app` folder holds the two Streamlit interfaces and the triage engine.
`scripts` handles database setup, demo data generation, and CSV exports.
`automation` has a Windows batch script for scheduled exports.
`data` holds the SQLite database and CSV outputs.
And `docs` contains the Power BI DAX guide.
Every module has exactly one responsibility. Nothing overlaps.

---

## SCENE 5 - LIVE DEMO [01:25 - 02:05]

**SCREEN:** Switch to Browser → Tab 2: `localhost:8501` Employee Portal. Fill in the form live as you speak:

1. Click into "Full Name" → type `Arjun Sharma`
2. Select Site → `Site-B`
3. Select Building → `Bldg-2`
4. Click into "Describe the Issue" → type `Water leak under the sink in the 2nd floor restroom, flooding is starting`
5. Click **Submit Request**
6. *(Pause 1 second for the result card to appear)*
7. Scroll down slightly to show the result card, and hover your cursor over the confidence bar, then the SLA pill, and finally the latency badge.

**SPEAK:**

Let me show you the application live.

*(type Full Name: "Arjun Sharma")*

I am submitting as an employee reporting a facility issue.

*(select Site-B, Bldg-2)*

The description I will type is:
"Water leak under the sink in the 2nd floor restroom, flooding is starting."

*(type description and click Submit Request)*

*(pause 1 second)*

The engine processed that in under one millisecond.
It categorized the issue as Plumbing, matched on keywords like water, leak, and flooding.
Priority is High. The assigned team is Team-Plumbing. SLA is twenty-four hours.

*(hover over confidence bar, SLA pill, latency badge)*

The confidence score tells us how certain the engine is.
The latency badge confirms the sub-millisecond speed.

---

## SCENE 6 - CODE WALKTHROUGH: TRIAGE ENGINE [02:05 - 02:55]

**SCREEN:** Switch to VS Code → [app/triage_engine.py](file:///d:/GFD%28PROJECT-2%29/app/triage_engine.py). Perform the following scrolls and highlights:

1. Highlight `_match()` function (lines 25–28).
2. Scroll to `categorize()` function (lines 31–43) and highlight it.
3. Scroll to `predict_priority()` function (lines 46–52) and highlight it.
4. Scroll to `triage()` function (lines 59–75) and highlight it.

**SPEAK:**

This is the heart of the system, seventy-six lines of Python.

The most important design decision is this `_match` function.
It uses word-boundary regex, these backslash-b anchors.
Without this, the word "replacement" would falsely trigger an HVAC match
because it contains the letters "ac."
One regex pattern eliminates an entire class of false positives.

*(scroll to categorize and highlight)*

The `categorize` function scores all eight categories by counting keyword hits.
It returns the winner and a confidence ratio.
If nothing matches at all, it falls back to the general category with zero confidence.
which signals the admin to manually review.

*(scroll to predict_priority and highlight)*

Priority prediction scans in severity order: Critical first, then High, Medium, Low.
First match wins.
This guarantees that the word "emergency" will always outrank the word "minor,"
even if both appear in the same description.

*(scroll to triage and highlight)*

And this is the orchestrator.
It calls all three functions, measures the execution time using `perf_counter`,
and returns a clean dictionary.
That latency number feeds into Power BI so the system monitors its own performance.

---

## SCENE 7 - SCHEMA DESIGN [02:55 - 03:15]

**SCREEN:** Switch to VS Code → [scripts/init_db.py](file:///d:/GFD%28PROJECT-2%29/scripts/init_db.py). Scroll to the `CREATE TABLE requests` block. Highlight the `suggested_category` and `final_category` lines.

**SPEAK:**

The database schema has one key design insight.
Every field stores both what the AI predicted and what the human decided.
`suggested_category` is what the engine chose.
`final_category` is what the reviewer confirmed or corrected.
When a ticket is closed with zero overrides — those two values match —
that counts as an AI win.
This dual-column design is what makes the seventy-one percent accuracy metric possible
with a single query, no joins.

The `override_log` table records every individual correction:
field changed, old value, new value, reviewer name, and timestamp. That is the full audit trail.

---

## SCENE 8 - NOTIFICATION DESIGN [03:15 - 03:30]

**SCREEN:** Switch to VS Code → [app/notifier.py](file:///d:/GFD%28PROJECT-2%29/app/notifier.py). Highlight the `if not EMAIL_FROM` guard clause at the top.

**SPEAK:**

The notification layer sends to Gmail SMTP and Microsoft Teams webhooks.
The critical design choice here is fail-silent.
If credentials are not configured, it logs a skip trace and continues.
The core pipeline — triage, database write, ticket creation — is never blocked
by a notification failure.
That is a deliberate reliability decision.

---

## SCENE 9 - ADMIN OVERRIDE AND AUDIT TRAIL [03:30 - 03:55]

**SCREEN:** Switch to Browser → Tab 1: `localhost:8502` Admin Panel. Click the expander on the ticket you just submitted. Change the Priority dropdown from "High" to "Critical." Click **Save Changes**.

**SPEAK:**

Back on the admin panel — here is the ticket I just submitted.
The reviewer sees the AI suggestion and can override it.

*(change Priority to Critical)*

I am changing priority to Critical. Active flooding is an emergency.

*(click Save Changes)*

That override is now written to the audit log.
This data serves two purposes.
First, compliance — every human correction is traceable.
Second, machine learning — these corrections become labeled training data
for eventually replacing the keyword engine with a proper text classifier.
The architecture was designed with that transition in mind.

---

## SCENE 10 - OPERATIONAL INSIGHTS [03:55 - 04:10]

**SCREEN:** On Admin Panel → click **Operational Insights** tab. Ensure the bar charts for category distribution and priority breakdown are visible.

**SPEAK:**

The Operational Insights tab shows real-time category distribution,
priority breakdown, and team workload — all computed live from the database.
Beyond this, there is a five-page Power BI dashboard
with twelve DAX measures covering AI accuracy analysis,
SLA compliance tracking, and team workload over time.

---

## SCENE 11 - COMMIT HISTORY [04:10 - 04:35]

**SCREEN:** Switch to Browser → GitHub commit history page. Scroll slowly through the commits.

**SPEAK:**

The commit history shows how the project evolved.
The first commit delivers the complete working system.
Then a UI overhaul, followed by bug fixes from a code review session.
Then a major refactor to the current professional light theme.
Then documentation — the Power BI DAX guide, README screenshots, the demo script.
Every commit uses conventional prefixes (feat, fix, refactor, docs)
so the history is readable at a glance.

On code quality — the triage engine, the database layer, and the notifier
have zero cross-dependencies.
All configuration is centralized in one file.
There are no magic strings anywhere in the business logic.
The system is readable, maintainable, and each module is independently replaceable.

---

## SCENE 12 - CLOSING [04:35 - 05:00]

**SCREEN:** Switch to Browser → Tab 1: `localhost:8502` Admin Panel. Back to KPI cards, no scrolling. Do not click anything.

**SPEAK:**

To close — this system takes a plain English facility request,
classifies it across eight categories,
assigns the correct priority and team,
sends notifications,
and logs every human correction for compliance and future ML training.
All of this in under one millisecond.

The honest limitations I acknowledge — SQLite is not production-scale,
there is no authentication yet, and unit tests are the next thing I would add.
But the architecture is built so every one of those has a clear upgrade path.

Thank you for watching.
I am happy to go deeper on any part of the code, the architecture,
or the engineering decisions behind this project.

---

## TIMING SUMMARY

| Scene | Time | Duration | Screen Action |
|---|---|---|---|
| 1. Introduction | 00:00–00:15 | 15s | Browser: Admin Panel KPIs |
| 2. The Problem | 00:15–00:40 | 25s | Browser: Hover over KPI cards |
| 3. Architecture | 00:40–01:10 | 30s | VS Code: Scroll config.py |
| 4. Project Structure | 01:10–01:25 | 15s | VS Code: Hover Explorer sidebar |
| 5. Live Demo | 01:25–02:05 | 40s | Browser: Submit request on Employee Portal |
| 6. Triage Engine Code | 02:05–02:55 | 50s | VS Code: Scroll triage_engine.py functions |
| 7. Schema Design | 02:55–03:15 | 20s | VS Code: init_db.py, highlight suggested/final |
| 8. Notification Design | 03:15–03:30 | 15s | VS Code: notifier.py, highlight guard clause |
| 9. Admin Override | 03:30–03:55 | 25s | Browser: Override ticket, click Save Changes |
| 10. Operational Insights | 03:55–04:10 | 15s | Browser: Insights tab charts |
| 11. Commit History | 04:10–04:35 | 25s | Browser: GitHub commits list |
| 12. Closing | 04:35–05:00 | 25s | Browser: Admin Panel KPI cards |
| **TOTAL** | | **5:00** | |
