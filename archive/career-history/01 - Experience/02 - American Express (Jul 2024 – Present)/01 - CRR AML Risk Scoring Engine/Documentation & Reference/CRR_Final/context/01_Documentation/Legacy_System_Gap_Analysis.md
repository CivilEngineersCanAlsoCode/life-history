# Legacy System Gap Analysis

## 1. Architecture & Scalability Gaps
### The "Copy-Paste" Assessment Trap (Lack of Inheritance)
**Legacy Behavior:**
In the old system, Risk Assessments were configured by "Scope" (e.g., Enterprise). When a new scope was needed (e.g., India Market), the users had to **copy** the Enterprise assessment.
**The Gap:**
Crucially, this "Copy" action duplicated **everything**—Risk Elements, Categories, and Rule Sets were recreated with **new unique IDs**. There was no parent-child relationship or "inheritance".
**Impact:**
- **Zero Scalability:** To make a global update (e.g., "Add a new Sanctions Rule"), the Business team had to manually apply the change to *every single* Market Assessment individually.
- **Drift:** Over time, Market assessments drifted unintentionally from the Enterprise standard because keeping them in sync was a manual nightmare.

## 2. Configuration & Flexibility Gaps
### The "Addenda" Workaround vs. Fundamental Assessment
**Legacy Behavior:**
"Fundamental Assessment" (FA) logic was hardcoded to only support **Geography**. It could not handle other keys like Industry, Occupation, Structure, or Product.
**The Gap:**
To score these other attributes, users were forced to use a generic "Addenda" file method (Multiplier Type Option 3).
- Users manually created CSV files mapping `Attribute Name -> Multiplier`.
- Users uploaded these files for *every* data point that wasn't Geo.
**Impact:**
- **Maintenance Nightmare:** Changing a risk weight meant locating and updating dozens of static "Addenda" files manually.
- **Error Prone:** No validation on the file content; a typo in the attribute name meant the rule simply didn't fire.

### Non-Configurable Data Point Combinations
**Legacy Behavior:**
Data points were rigid. If Business wanted to trigger a rule based on a new combination (e.g., `Country + Product Type`), it often failed because the underlying compute logic didn't support that specific tuple.
**The Gap:**
**Tech Dependency:** Business had to raise a ticket with the Technology team to code support for new data point combinations.
**Impact:**
- Slow Time-to-Market for new risk rules.

## 3. Safety & Governance Gaps (High Risk)
### Direct-to-Production Updates (No Sandbox)
**Legacy Behavior:**
While Rules had some approval process, **Centralized Lists** and **Fundamental Assessments** did not have a safe testing lifecycle.
**The Gap:**
- **List Updates:** Changing a value in a Centralized List (e.g., adding a country to High Risk) applied directly to Production.
- **No Impact Analysis:** There was *no* ability to run a Sandbox Simulation on a List change or FA change before it went live.
- **Missing Approvals:** Lists lacked the 2-step approval rigor found elsewhere.
**Impact:**
- **Production Incidents:** A bad list update could immediately mis-score customers in Production with no warning.

## 4. Operational & Usability Gaps
### "The Sandbox Black Hole"
**Legacy Behavior:**
Once a simulation was submitted, the user lost all control and visibility.
**The Gaps:**
1.  **No Cancellation:** Users could not stop a run, even if they realized a mistake 1 minute later. They had to wait.
2.  **No Progress Bar:** "Complete darkness." Users didn't know if it was 1% or 99% done.
3.  **Silent Failures:** If the backend failed/crashed, no notification was sent. Users waited indefinitely until they manually pinged Tech Support to check logs.
**Impact:**
- Wasted time and frustration. Blind reliance on Tech teams for basic status updates.

### File Management Chaos
**Legacy Behavior:**
The system handled file uploads (for lists/addenda) poorly.
**The Gap:**
- **Dynamic IDs:** Every time a file was re-uploaded (even with identical content), the system assigned a **new File ID**.
- **Rule Association:** Use had to update *every rule* that referenced that file to point to the new File ID.
**Impact:**
- A simple list update became a multi-step configuration tasks involving updating multiple rules just to link the new file version.

## 5. Traceability & Reporting Gaps

### Manual Tracing
**Legacy Behavior:**
To figure out "Why did Customer X's score change?", analysts had to manually perform a "Risk Scoring Matrix" analysis.
**The Gap:**
- **Blind Simulations & No Parallelism:** Users couldn't see what changed. Also, the system simply **could not run parallel sandboxes**. If Analyst A was running a geo simulation, Analyst B had to wait.
**Impact:**
- Extremely slow audit response times.

## 6. Functional & Logic Gaps (Business Logic)
### The "Daily Delta" Latency
**Legacy Behavior:**
Scoring was a batch process running daily at **7 PM MST**.
**The Gap:**
- **No Real-Time Scoring:** If a customer's geography changed at 9 AM, their risk score was wrong for 10+ hours.
- **Onboarding Risk Gap:** Customers were only scored *after* card issuance. There was **no Pre-Booking Risk Check** (via Go2 onboarding platform). Bad actors could get a card before being flagged.

### Hierarchy "Contagion" (False Positives)
**Legacy Behavior:**
Risk Logic used an aggressive "Max" function. If *one* account in a hierarchy was High Risk, **all** accounts and the Customer became High Risk.
**The Gap:**
- **Over-Conservative Scoring:** This created a massive volume of "False Positive" High Risk customers who were actually safe but linked to one flagged entity.
- **Cost Impact:** This flooded the Financial Investigation Unit (FIU) and MCOs with unnecessary Enhanced Due Diligence (EDD) reviews.
**Impact:**
- **Direct Financial Loss:** Wasted salary hours of investigators creating and closing reviews for low-risk customers.

## 7. Architecture Bloat
**Legacy Behavior:**
The legacy platform tried to do everything: Scoring + Review Scheduling + Review Processing.
**The Gap:**
- **Non-Core Bloat:** The CRR engine was overloaded with workflow capabilities (Review Processing) that should belong to a Case Management system, not a Calculation Engine.
**Impact:**
- Performance degradation and inability to scale the core scoring logic.
