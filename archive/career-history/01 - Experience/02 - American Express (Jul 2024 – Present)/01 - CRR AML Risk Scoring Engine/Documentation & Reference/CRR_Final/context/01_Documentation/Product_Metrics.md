# Product Metrics for CRR Platform

These metrics are designed to measure the success of the new CRR platform, specifically targeting the gaps identified in the Legacy System (Speed, Safety, Transparency).

## 1. North Star Metric: Time from Concept to Production

| Metric | Definition | Why it matters |
| :--- | :--- | :--- |
| **Time to Market** | End-to-end duration from a business requirement to the rule being active in Production. | **Agility.** Reduces the cycle time from weeks/months to hours, allowing rapid response to regulatory changes (e.g. Russia Sanctions). |

### Detailed Calculation Methodology
*   **Formula:** $T_{production} - T_{concept}$
    *   $T_{concept}$: Timestamp of Jira Ticket Creation / Email Request.
    *   $T_{production}$: Timestamp of Rule Activation in Production Logic.
*   **Legacy Monitor (Baseline):**
    *   Track `Jira Created Date` vs `Jira Closed Date` for "Rule Change" tickets.
    *   *Note:* Often includes "Waiting for Dev" states which should be counted as friction.
*   **New System Monitor:**
    *   Audit Trail: `Draft Created Timestamp` vs `Promotion Approval Timestamp`.
    *   Measure the time spent in "Simulation" vs "Approval Queue".
*   **Value Calculation:**
    *   $\text{Value} = \text{Avg Legacy Time (Weeks)} - \text{Avg New Time (Hours)}$

---

## 2. Operational Efficiency Metrics

| Metric | Definition | Why it matters |
| :--- | :--- | :--- |
| **Configuration Setup Time** | Average time to create a new Risk Assessment or update a Centralized List. | Solves the "Addenda maintenance nightmare". drastically reducing manual data entry effort. |
| **Simulation Turnaround Time** | Average time to score N million customers in a Sandbox. | Addressing the "5-hour wait" friction. Users shouldn't wait overnight to see results. |
| **Reuse Rate** | % of Risk Elements/Lists inherited vs. created from scratch. | Measures if users are using the new "Center/Legal Entity" inheritance instead of the broken "Copy-Paste" pattern. |

### Detailed Calculation Methodology

#### A. Configuration Setup Time
*   **Formula:** Time spent by a user in the UI/File editing to set up a specific list or rule.
*   **Legacy Monitor:**
    *   Hard to track systemically. Proxy: Number of Addenda Files uploaded * 30 mins per file.
*   **New System Monitor:**
    *   UI Session Logs: Time from `Open Asset Manager` to `Save Successful`.
*   **Value Calculation:**
    *   $\text{Efficiency Gain} = (\text{Old Manual Hours} - \text{New UI Minutes}) \times \text{Hourly Rate of Risk Analyst}$

#### B. Simulation Turnaround Time
*   **Formula:** $T_{completion} - T_{submission}$
*   **Legacy Monitor:**
    *   Batch Logs: Check start/end time of ad-hoc SQL runs or batch estimation jobs. (Reference Benchmark: 5 Hours).
*   **New System Monitor:**
    *   Job Scheduler Logs: Duration of distributed Spark/Python scoring jobs. (Target: < 2 Hours).
*   **Value Calculation:**
    *   $\text{Productivity} = \text{Saved Wait Time} \times \text{Number of Simulations per Year}$

---

## 3. System Reliability: Onboarding & Real-Time

| Metric | Definition | Why it matters |
| :--- | :--- | :--- |
| **Onboarding API Latency** | P99 Latency for Pre-Booking Risk Score (Go2 Integration). | **Risk Avoidance.** Blocks bad actors *before* card issuance (vs T+1 detection). |
| **Data Ingestion Lag** | Time difference between event occurrence (e.g. Geo Change) and Scoring. | Ensures "Real-time" scoring is actually real-time, preventing exposure gaps. |
| **Sandbox Success Rate** | % of Simulations that complete successfully without crashing. | Legacy system had frequent silent failures ("Black Hole"). New system ensures stability. |

### Detailed Calculation Methodology

#### A. Onboarding API Latency
*   **Formula:** P99 Latency of the `POST /score-customer` endpoint.
*   **Legacy Monitor:**
    *   N/A (Did not exist). Metric starts at "Infinity" (Risk was blind until T+1).
*   **New System Monitor:**
    *   APM Tools (Datadog/Splunk): Track `response_time` for the Onboarding API.
*   **Value Calculation:**
    *   $\text{Value} = \text{Blocked Bad Actors} \times \text{Avg Fraud Cost per User}$

#### B. Data Ingestion Lag
*   **Formula:** $T_{scoring} - T_{event\_occurrence}$
*   **Legacy Monitor:**
    *   Compare `Event Timestamp` vs `Scoring Timestamp` (Standardized to 7 PM MST batch). Top lag: 24h.
*   **New System Monitor:**
    *   Event Stream Lag: Kafka/Queue processing lag.
*   **Value Calculation:**
    *   $\text{Exposure Reduction} = \text{Avg Legacy Lag (Hours)} - \text{New Event Lag (Seconds)}$

---

## 4. Cost Efficiency: Reducing False Positives

| Metric | Definition | Why it matters |
| :--- | :--- | :--- |
| **False Positive Reduction** | Reduction in High Risk customers generated solely by "Hierarchy Max Contagion". | **Direct Financial Savings.** Drastically reduces volume of unnecessary EDD Reviews. |
| **FIU/MCO Hours Saved** | Estimated man-hours saved per month due to fewer investigations. | Direct impact on operational salaries/overhead. |

### Detailed Calculation Methodology

#### A. False Positive Reduction (Hierarchy Contagion)
*   **Formula:**
    *   $Count_{LegacyHigh} = \text{Customers High Risk via Max Logic}$
    *   $Count_{NewHigh} = \text{Customers High Risk via New Granular Logic}$
    *   $\Delta_{FalsePositives} = Count_{LegacyHigh} - Count_{NewHigh}$
*   **Monitor:**
    *   Scenario Test: Run the *same* population through New Logic vs Legacy Logic.
*   **Value Calculation (Financial):**
    *   $\text{Reviews Saved} = \Delta_{FalsePositives} \times \% \text{Typically Triggering EDD}$
    *   $\text{Cost Savings} = \text{Reviews Saved} \times \text{Avg Hours per Review} \times \text{Investigator Hourly Rate}$

---

## 5. Risk Governance: Decommissioning & Safety

| Metric | Definition | Why it matters |
| :--- | :--- | :--- |
| **Unsimulated Changes** | % of Production changes that were *not* simulated in Sandbox first. | **Target: 0%**. Closing the "Direct-to-Prod" loophole prevents accidental mass-failures. |
| **Audit Traceability Score** | % of Production configs linked to a Change Request. | Eliminates "Mystery Scores". Every score can be explained by a specific approved CR. |
| **Decommissioning Rate** | % of Non-Core Legacy modules retired. | Leaner architecture = Lower Cloud Bills & Easier Maintenance. |

### Detailed Calculation Methodology

#### A. Unsimulated Changes
*   **Formula:** % of Production Configuration Versions that have NO linked Simulation ID.
*   **Legacy Monitor:**
    *   Count of "Addenda File Uploads" or "SQL Updates" directly to Prod DB. (Likely 100% for Lists).
*   **New System Monitor:**
    *   Database Constraint: Ensure every `Production_Config_Row` has a foreign key to `Approved_Change_Request_ID` which links to `Simulation_ID`.
*   **Value Calculation:**
    *   **Compliance Value:** 100% Audit Coverage. (Binary: Compliant vs Non-Compliant).

#### B. Decommissioning Rate
*   **Formula:** $\frac{\text{Retired Lines of Code}}{\text{Total Legacy Codebase}} \times 100$
*   **Target:** 100% of "Review Scheduling" and "Case Management" code removed from CRR engine.
*   **Value:** Reduced infrastructure compute cost (Cloud Bill) and maintenance overhead.
