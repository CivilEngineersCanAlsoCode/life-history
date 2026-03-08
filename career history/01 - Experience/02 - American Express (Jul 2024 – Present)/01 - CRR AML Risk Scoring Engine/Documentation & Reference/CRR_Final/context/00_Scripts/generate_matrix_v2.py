
import json

# Load requirements
with open('all_requirements.json', 'r') as f:
    reqs = json.load(f)

# Sort reqs
def sort_key(x):
    parts = x['id'].split('.')
    return [int(p) if p.isdigit() else p for p in parts]
reqs.sort(key=sort_key)

def get_raw_feature_details(req_id, description):
    feature = "Unified Sandbox Journey"
    status = "Yes"
    comments = "-"

    # --- Authorization Features ---
    auth_ids = [
        "12.2.2", "12.2.3", "12.3.2", "12.6.4", "12.8.3", 
        "12.9.4", "12.13.5", "12.14.4", "12.21", "12.21.1"
    ]
    if req_id in auth_ids or req_id.startswith("12.21"):
        return "Authorization", "No", "Features related to IAM/Permissions are not yet implemented."

    # --- Change Request Workflow ---
    if req_id.startswith("12.2.") or req_id == "12.2":
        return "Change Request Workflow", "No", "New Feature to be built for MCOs to submit/track changes."
    
    # --- 12.3 Updates ---
    if req_id == "12.3.3":
        return "Unified Sandbox Journey", "No", "Constraint/Warning logic for unsupported data combinations missing."
    if req_id == "12.3.6":
        return "Unified Sandbox Journey", "No", "Partially satisfied: Missing Center/Legal Entity/Product overrides."
    if req_id == "12.3.7":
        return "Unified Sandbox Journey", "No", "Partially satisfied: Missing Center/Legal Entity specific capability."

    # --- 12.4 Risk Scoring ---
    if req_id == "12.4.2":
        return "DAM Integration", "No", "Output to DAM for downstream consumption not built."
    if req_id == "12.4.3":
         return "CRR Manual Override", "No", "New capability for manual risk overrides to be developed."
    if req_id == "12.4.4":
        return "Risk Threshold Calculation", "Yes", "Maps Risk Score to Risk Class."
    if req_id == "12.4.5":
        return "CRR Risk Framework Configuration", "No", "UI configuration for Prohibited/Very High flags missing."
    if req_id == "12.4.6":
        return "CRR Risk Framework Configuration", "Yes", "Configurable flags (Prohibited) on Risk Elements."

    # --- 12.6 Lists ---
    if req_id == "12.6.1":
        return "Asset Manager", "No", "Partially satisfied: Missing Center/Market/Legal Entity/Product specific lists."
    if req_id == "12.6.2":
        return "Fundamental Assessment", "No", "Partially satisfied: Missing Center/Legal Entity overrides."
    if req_id == "12.6.5":
        return "Fundamental Assessment", "Yes", "-"

    # --- 12.7 Audit ---
    if req_id.startswith("12.7.") or req_id == "12.7":
        return "Audit", "Yes", "Tracks changes pushed to Production."

    # --- 12.8 Sandbox ---
    if req_id == "12.8.4":
        return "Unified Sandbox Journey", "No", "Partially satisfied: Missing Center/Legal Entity/Product specific instances."
    if req_id in ["12.8.6", "12.8.7"]:
        return "Unified Sandbox Journey", "No", "Feature not developed yet."
    if req_id == "12.8.11":
        return "Unified Sandbox Journey", "No", "In Development: Simulation on list update being built."
    if req_id == "12.8.13":
        return "Unified Sandbox Journey", "No", "Merge in-flight changes functionality missing."
    if req_id == "12.8.14":
        return "Unified Sandbox Journey", "No", "Impact calculation for risk threshold update not developed."
    if req_id == "12.8.15":
        return "Unified Sandbox Journey", "No", "SLA/Performance simulation not simulated/integrated."

    # --- 12.9 Analysis -> Real-time Dashboards ---
    if req_id == "12.9" or req_id == "12.9.1" or req_id == "12.9.2":
        return "Real-time Dashboards", "No", "Partially built (UI only). Integration with DAM/Rule Exec pending."
    if req_id == "12.9.3":
        return "Real-time Dashboards", "No", "Feature functionality not available."
    if req_id == "12.9.5":
        return "Sandbox Dashboard", "No", "UI completed, but integration missing."
    if req_id == "12.9.6":
        return "Unified Sandbox Journey", "No", "Change Summary UI built, but Export functionality missing."

    # --- 12.10 Promotion ---
    if req_id.startswith("12.10.") or req_id == "12.10":
        return "Unified Sandbox Journey", "Yes", "Atomic Promotion supported."

    # --- 12.11 Certification ---
    if req_id.startswith("12.11.") or req_id == "12.11":
        return "Certification / Attestation", "No", "Prioritized for next year's roadmap."

    # --- 12.12 Integration ---
    if req_id.startswith("12.12.") or req_id == "12.12":
        return "AML Ecosystem Integration", "No", "Integration endpoints not built."

    # --- 12.13 Reporting ---
    if req_id.startswith("12.13.") or req_id == "12.13":
        return "GCIP Reporting", "No", "Managed by Core Reporting Team of GCIP."

    # --- 12.14 UI Enhancements ---
    if req_id == "12.14" or req_id == "12.14.1":
        return "UI Enhancements", "Yes", "Incremental UI improvements."
    if req_id == "12.14.2":
        return "UI Enhancements", "No", "Designed but not developed."
    if req_id == "12.14.3":
        return "UI Enhancements", "No", "Not developed."
    if req_id == "12.14.5":
        return "Change Request Workflow", "No", "Feature not developed."

    # --- 12.15 Customer View ---
    if req_id.startswith("12.15.") or req_id == "12.15":
        return "Customer 360 View", "No", "Requirement not built yet."

    # --- 12.16 Rescoring ---
    if req_id == "12.16" or req_id == "12.16.1":
         return "Triggers (Time/Event based)", "No", "In Development by Rule Exec Team (Target 26.3)."
    if req_id == "12.16.2":
         return "Triggers (Rule Change based)", "No", "In Development by Rule Exec Team (Target 26.3)."

    # --- 12.17 Data ---
    if req_id.startswith("12.17.") or req_id == "12.17":
        return "DAM Integration", "No", "Data integration missing."

    # --- 12.18 Performance ---
    if req_id.startswith("12.18.") or req_id == "12.18":
        if "DAM" in description:
             return "DAM Reporting", "No", "DAM Reporting missing."
        return "System Health Monitoring", "No", "Performance dashboards missing."

    # --- 12.19 AI/ML ---
    if req_id.startswith("12.19.") or req_id == "12.19":
        return "AI/ML Model Ops", "No", "No discussions yet."

    # --- 12.20 Notifications ---
    if req_id.startswith("12.20.") or req_id == "12.20":
        return "Smart Alert Manager", "No", "Not developed yet."

    # --- Specific "Done" Items (Based on User Inputs) ---
    # 12.10 Promotion (User confirmed Done)
    if req_id.startswith("12.10.") or req_id == "12.10":
        return "Unified Sandbox Journey", "Yes", "Atomic Promotion supported."
    # 12.8.8, 12.8.9, 12.8.10 (User confirmed Done)
    if req_id in ["12.8.8", "12.8.9", "12.8.10", "12.8.12", "12.8.1", "12.8.2", "12.8.5"]: 
         return "Unified Sandbox Journey", "Yes", "-"
    # 12.14 (UI) - some parts done
    if req_id in ["12.14", "12.14.1"]:
        return "UI Enhancements", "Yes", "Incremental UI improvements."
    # 12.6.5 (User confirmed Done)
    if req_id == "12.6.5":
        return "Fundamental Assessment", "Yes", "-"
    # 12.7 Audit (User confirmed Done)
    if req_id.startswith("12.7.") or req_id == "12.7":
        return "Audit", "Yes", "Tracks changes pushed to Production."

    # Generic Fallbacks
    # Unified Sandbox Journey is STARTED in 26.1, Target 26.3 for Core Integrations. Currently "No" (Incomplete).
    if req_id.startswith("12.1.") or req_id == "12.1":
        return "Unified Sandbox Journey", "No", "In Development (Target 26.3 for full Integration)"
    if req_id.startswith("12.3.") or req_id == "12.3":
        return "Unified Sandbox Journey", "No", "In Development (Target 26.3)"
    if req_id.startswith("12.5.") or req_id == "12.5":
        return "Unified Sandbox Journey", "No", "In Development (Rulesets)"
    if req_id.startswith("12.8.") or req_id == "12.8":
        return "Unified Sandbox Journey", "No", "In Development (Simulation/Integration pending)"

    # Other Fallbacks
    if req_id.startswith("12.4.") or req_id == "12.4":
        return "Core Rule Execution Logic", "Yes", "Managed by Rule Execution Team."
    if req_id.startswith("12.6.") or req_id == "12.6":
        return "Asset Manager", "No", "In Development (Integration Target 26.3)"
    if req_id.startswith("12.14.") or req_id == "12.14": 
        return "UI Enhancements", "Yes", "-"

    return feature, status, comments

def get_feature_details(req_id, description):
    feature, status, comments = get_raw_feature_details(req_id, description)
    # Calculate Percentage
    percentage = 0
    if status == "Yes":
        percentage = 100
    elif "Partially satisfied" in comments or "In Development" in comments or "Partially built" in comments:
        percentage = 50
    else:
        percentage = 0
    return feature, status, comments, percentage

print("# Traceability Matrix: Business Requirements to Features & Status")
print("")
print("| Req ID | Business Requirement Description | Existing Feature / Solution | Status | % Completed | Comments / Gaps |")
print("| :--- | :--- | :--- | :--- | :--- | :--- |")

total_reqs = 0
total_score = 0

for r in reqs:
    req_id = r['id']
    desc = r['description'].replace("\n", " ").replace("|", "\|")
    feature, status, comment, pct = get_feature_details(req_id, desc)
    print(f"| {req_id} | {desc} | {feature} | {status} | {pct}% | {comment} |")
    total_reqs += 1
    total_score += pct

weighted_completion = (total_score / (total_reqs * 100)) * 100 if total_reqs > 0 else 0

print("")
print("## Executive Summary: PI Prioritization & Roadmap")
print("")
print(f"**Weighted Overall Project Completion:** {weighted_completion:.1f}%")
print("")
print("### Recommended PI Prioritization (2026)")
print("Based on current development status (Unified Sandbox started 26.1) and target integration date (26.3).")
print("")
print("#### **PI 26.1 & 26.2: Core Foundation (Build Phase)**")
print("- **Goal:** Complete UI/UX for Sandbox, Asset Manager, and Fundamental Assessment.")
print("- **Focus Areas (Rule Configuration Team):**")
print("  - **Unified Sandbox Journey:** Complete Rules Config, Risk Framework UI, and Simulation UI containers.")
print("  - **Asset Manager:** Complete Reference List management screens.")
print("  - **Fundamental Assessment:** Complete UI and integration hooks.")
print("  - **Structure:** Ensure 'In Development' items reach 'Partially Satisfied' (UI Done) status.")
print("")
print("#### **PI 26.1 - 26.3: Parallel Track (Rule Execution Team)**")
print("- **Goal:** Automated Rescoring & Triggers (Critical for Production).")
print("- **Focus Areas:**")
print("  - **Event-Based Triggers:** Rescore on DAM Events (Geo/Data changes).")
print("  - **Time-Based Triggers:** Monthly rescoring for Time-sensitive elements.")
print("  - **Rule-Change Triggers:** Automated population rescoring upon Sandbox Promotion.")
print("")
print("#### **PI 26.3: Integration Milestone (Target Delivery)**")
print("- **Goal:** End-to-end connectivity. Ensure Sandbox can actually run simulations.")
print("- **Priority 1 (Critical):**")
print("  - **IAM & Authorization (12.21):** Implement permission model (Blocking dependency).")
print("  - **Integrations (12.4.2, 12.17):** DAM Integration (In/Out) and Rule Execution Engine connectivity.")
print("  - **Asset Manager Integration:** Connect UI to backend/DB.")
print("- **Priority 2 (High):**")
print("  - **Sandbox Reporting:** Implement Sandbox-specific dashboards.")
print("")
print("#### **PI 26.4: Refinement & Advanced Workflows**")
print("- **Goal:** Operational efficiency and gap closure.")
print("- **Focus Areas:**")
print("  - **Change Request Workflow:** Develop MCO workflow for formal Production promotion.")
print("  - **Overrides Gap Closure:** Implement Center/Legal Entity/Product specific overrides.")
print("  - **Sandbox Refinements:** Merge Logic, Impact Checks.")
print("")
print("#### **PI 26.5: Stability & Prep for 2027**")
print("- **Goal:** Production hardening and future-proofing.")
print("- **Focus Areas:**")
print("  - **Performance/SLA Tuning:** Ensure simulations run within time limits.")
print("  - **UI Enhancements:** Final polish.")
print("  - **Pre-work for 2027:** Architecture planning for AI/ML and Customer 360.")
print("")
print("### 2027 Strategic Roadmap")
print("- **Certification & Attestation:** Periodic attestation workflows.")
print("- **Advanced Analytics:** AI/ML Ops and Smart Alert Manager.")
print("- **Customer 360:** Explainability and Deep-dive views.")


