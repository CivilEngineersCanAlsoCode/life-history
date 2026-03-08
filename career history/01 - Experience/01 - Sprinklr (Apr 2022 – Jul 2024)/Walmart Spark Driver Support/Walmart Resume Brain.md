- Reduced time to value by 85%, built a GenAI powered Insight Assistant for automated root cause analysis and generated actionable insights
- Generated a $1.2M ARR opportunity by automating RCA for Walmart, creating a MVP for driver support using unsupervised learning models

---

**01 Context — What Was the Core Business Problem?**

Client: Walmart (Driver Support Ecosystem)

Situation:

- Thousands of drivers raising queries via call/chat
- Many unresolved issues escalated to Reddit, X (Twitter), etc.
- Support team working in silos
- No unified visibility of internal + public complaints
- Root cause identification took ~7 days

Impact:

Slow RCA → recurring issues → reputational risk → driver dissatisfaction → churn risk.

---

**02 Objective**

Build a system that:

- Unifies internal support + social data
- Automatically detects top recurring issues
- Identifies root cause clusters
- Predicts crisis probability
- Routes cases to correct Walmart teams
- Reduces time-to-insight drastically

North Goal:

End-of-day executive-ready issue summary.

---

**03 Data Architecture — What We Unified**

Two Primary Data Sources:

1️⃣ Internal Support Data

- Driver calls
- Chat logs
- Support tickets
- Provided by Walmart

2️⃣ Public Social Escalations

- Reddit, X, other platforms
- Drivers posting unresolved complaints
- Collected via Sprinklr Social Listening
- Keyword + image + executive tagging

Unification Method:

- SQL-based backend joins
- Common keys: User ID, timestamps
- Unified contact metric

Custom Metric Example:

Total Contacts =

Internal Support Messages + Public Escalations (same time window)

This created true ecosystem visibility.

---

**04 GenAI Insight Assistant — What We Built**

Built a GenAI-powered RCA engine on top of unified dataset.

Key Capabilities:

- L1 / L2 / L3 issue classification (custom for Walmart)
- Unsupervised clustering of complaints
- Automated summarisation
- Crisis probability scoring
- Top recurring themes detection

ML Approach:

- Unsupervised learning for clustering
- Pattern detection across text corpus
- Grouped semantically similar issues
- Identified hidden root causes

Earlier: Manual analysis (7 days)

Now: Automated insight summary (same day)

Time-to-Insight Improvement: 85%

---

**05 Workflow After RCA**

Insight Assistant Output:

- Top issues ranked
- Crisis likelihood
- Affected regions
- Driver volume impact

Then:

- Auto-create cases
- Route to relevant Walmart internal teams
- Enable faster resolution cycle

Shifted from reactive to proactive.

---

**06 My Role — Product Owner (End-to-End)**

I led:

- Problem framing
- Data unification logic
- Custom metric definitions
- L1/L2/L3 taxonomy design
- Insight Assistant product definition
- RCA workflow design
- POC execution

Collaborated with:

- Business team
- Sales team
- Data scientists
- Engineering

VP supported, but I drove execution.

---

**07 Business Impact**

Operational Impact:

- 85% reduction in time-to-insight
- Full visibility across support + public sentiment
- Structured issue taxonomy

Revenue Impact:

- POC converted into $1.2M ARR deal
- Positioned Sprinklr as AI-powered intelligence layer
- Expanded enterprise footprint

This wasn’t just analytics.

It became monetizable AI infrastructure.


