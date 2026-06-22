# Power BI Dashboard — DAX Measures & Setup Guide

> Connect `data/exports/requests.csv`, `overrides.csv`, and `calendar.csv`.
> Set relationship: `calendar[Date]` → `requests[SubmittedDate]` (1:Many).

---

## Page 1 — Triage Performance Overview

**Purpose:** Executive KPI snapshot — volume, queue health, throughput.

### DAX Measures

```dax
-- 1. Total Requests
Total Requests = COUNTROWS(requests)

-- 2. Open Tickets
Open Tickets = CALCULATE(COUNTROWS(requests), requests[status] = "Open")

-- 3. Closed Tickets
Closed Tickets = CALCULATE(COUNTROWS(requests), requests[status] = "Closed")

-- 4. Resolution Rate %
Resolution Rate % =
    DIVIDE(
        CALCULATE(COUNTROWS(requests), requests[status] = "Closed"),
        COUNTROWS(requests),
        0
    ) * 100
```

**Visuals:**
- 4 KPI cards (Total, Open, Closed, Resolution Rate)
- Stacked bar: Tickets by `final_category`
- Donut: Split by `final_priority`

---

## Page 2 — AI Accuracy & Override Analysis ⭐

**Purpose:** The human-in-the-loop differentiator. Shows where the AI was right vs corrected.

### DAX Measures

```dax
-- 5. AI Accurate Closes (closed with zero overrides)
AI Accurate Closes =
    CALCULATE(
        COUNTROWS(requests),
        requests[status] = "Closed",
        requests[override_count] = 0
    )

-- 6. AI Accuracy %
AI Accuracy % =
    DIVIDE(
        CALCULATE(COUNTROWS(requests), requests[status] = "Closed", requests[override_count] = 0),
        CALCULATE(COUNTROWS(requests), requests[status] = "Closed"),
        0
    ) * 100

-- 7. Total Override Events
Total Override Events = COUNTROWS(overrides)

-- 8. Override Rate %
Override Rate % =
    DIVIDE(
        CALCULATE(COUNTROWS(requests), requests[status] = "Closed", requests[override_count] > 0),
        CALCULATE(COUNTROWS(requests), requests[status] = "Closed"),
        0
    ) * 100
```

**Visuals:**
- Gauge: AI Accuracy % (target line at 80%)
- Table: `overrides[ticket_id]`, `field_changed`, `old_value`, `new_value`, `reviewer`
- Bar: Override count by `field_changed` (category vs priority)
- Matrix: Category vs. override frequency heatmap

---

## Page 3 — Automation SLA Tracking

**Purpose:** Self-observability — did the triage engine meet its own SLA?

### DAX Measures

```dax
-- 9. Avg Triage Latency (ms)
Avg Triage Latency ms = AVERAGE(requests[triage_time_ms])

-- 10. SLA Breach Count (> 5000 ms threshold)
SLA Breach Count =
    CALCULATE(
        COUNTROWS(requests),
        requests[triage_time_ms] > 5000
    )

-- 11. SLA Compliance %
SLA Compliance % =
    DIVIDE(
        CALCULATE(COUNTROWS(requests), requests[triage_time_ms] <= 5000),
        COUNTROWS(requests),
        0
    ) * 100
```

**Visuals:**
- KPI card: Avg Triage Latency ms
- KPI card: SLA Compliance %
- Histogram / scatter: `triage_time_ms` distribution
- Line chart (time-series via calendar): Avg latency over time

---

## Page 4 — Workload by Team

**Purpose:** Identify team load balance and ticket backlog distribution.

### DAX Measures
*(Uses measures already defined above — no new measures needed)*

**Visuals:**
- Clustered bar: Open vs. Closed count by `final_team`
- Table: Team | Open | Closed | Avg Confidence %
- Line: New tickets per week by team (calendar relationship)
- Slicer: `final_team`, `site`, `building`

---

## Page 5 — Operational Health

**Purpose:** Rolling health view — ticket aging, confidence trends, submission patterns.

### DAX Measures

```dax
-- 12. Avg Confidence Score %
Avg Confidence % = AVERAGE(requests[suggested_confidence]) * 100
```

**Visuals:**
- Line chart: Tickets submitted per month (calendar time axis)
- Bar: Avg confidence score by category
- Scatter: Confidence score vs. override count (shows model weakness areas)
- Card: Total notifications sent (`SUM(requests[notification_sent])`)

---

## Relationship Setup

| From Table | From Column | To Table | To Column | Cardinality |
|---|---|---|---|---|
| `requests` | `SubmittedDate` | `calendar` | `Date` | Many → 1 |
| `overrides` | `ticket_id` | `requests` | `ticket_id` | Many → 1 |

---

## Summary: 12 DAX Measures Across 5 Pages

| # | Measure Name | Page |
|---|---|---|
| 1 | Total Requests | P1 |
| 2 | Open Tickets | P1 |
| 3 | Closed Tickets | P1 |
| 4 | Resolution Rate % | P1 |
| 5 | AI Accurate Closes | P2 |
| 6 | AI Accuracy % | P2 ⭐ |
| 7 | Total Override Events | P2 |
| 8 | Override Rate % | P2 |
| 9 | Avg Triage Latency ms | P3 |
| 10 | SLA Breach Count | P3 |
| 11 | SLA Compliance % | P3 |
| 12 | Avg Confidence % | P5 |
