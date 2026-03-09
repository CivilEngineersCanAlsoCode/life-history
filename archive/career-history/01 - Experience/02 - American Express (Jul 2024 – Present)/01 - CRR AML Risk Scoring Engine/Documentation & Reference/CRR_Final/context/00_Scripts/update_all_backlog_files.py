
import os
import glob
import re

# ==========================================
# 1. Traceability Matrix Data (Parsed manually to ensure accuracy)
# ==========================================
# Format: ID -> {Feature, Status, Percent, Comments}
matrix_data = {
    "12.1": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Target 26.3 for full Integration)"},
    "12.1.1": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Target 26.3 for full Integration)"},
    "12.1.2": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Target 26.3 for full Integration)"},
    "12.1.3": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Target 26.3 for full Integration)"},
    "12.1.4": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Target 26.3 for full Integration)"},
    "12.1.5": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Target 26.3 for full Integration)"},
    "12.2": {"Feature": "Change Request Workflow", "Status": "No", "Comments": "New Feature to be built for MCOs to submit/track changes. (Target PI 26.4)"},
    "12.2.1": {"Feature": "Change Request Workflow", "Status": "No", "Comments": "New Feature to be built for MCOs to submit/track changes."},
    "12.2.2": {"Feature": "Authorization", "Status": "No", "Comments": "Features related to IAM/Permissions are not yet implemented."},
    "12.2.3": {"Feature": "Authorization", "Status": "No", "Comments": "Features related to IAM/Permissions are not yet implemented."},
    "12.2.4": {"Feature": "Change Request Workflow", "Status": "No", "Comments": "New Feature to be built for MCOs to submit/track changes."},
    "12.2.5": {"Feature": "Change Request Workflow", "Status": "No", "Comments": "New Feature to be built for MCOs to submit/track changes."},
    "12.2.6": {"Feature": "Change Request Workflow", "Status": "No", "Comments": "New Feature to be built for MCOs to submit/track changes."},
    "12.2.7": {"Feature": "Change Request Workflow", "Status": "No", "Comments": "New Feature to be built for MCOs to submit/track changes."},
    "12.2.8": {"Feature": "Change Request Workflow", "Status": "No", "Comments": "New Feature to be built for MCOs to submit/track changes."},
    "12.2.9": {"Feature": "Change Request Workflow", "Status": "No", "Comments": "New Feature to be built for MCOs to submit/track changes."},
    "12.2.10": {"Feature": "Change Request Workflow", "Status": "No", "Comments": "New Feature to be built for MCOs to submit/track changes."},
    "12.2.11": {"Feature": "Change Request Workflow", "Status": "No", "Comments": "New Feature to be built for MCOs to submit/track changes."},
    "12.3": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Target 26.3)"},
    "12.3.1": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Target 26.3)"},
    "12.3.2": {"Feature": "Authorization", "Status": "No", "Comments": "Features related to IAM/Permissions are not yet implemented."},
    "12.3.3": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "Constraint/Warning logic for unsupported data combinations missing."},
    "12.3.4": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Target 26.3)"},
    "12.3.5": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Target 26.3)"},
    "12.3.6": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "Partially satisfied: Missing Center/Legal Entity/Product overrides."},
    "12.3.7": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "Partially satisfied: Missing Center/Legal Entity specific capability."},
    "12.3.8": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Target 26.3)"},
    "12.4": {"Feature": "Core Rule Execution Logic", "Status": "Yes", "Comments": "Managed by Rule Execution Team."},
    "12.4.1": {"Feature": "Core Rule Execution Logic", "Status": "Yes", "Comments": "Managed by Rule Execution Team."},
    "12.4.2": {"Feature": "DAM Integration", "Status": "No", "Comments": "Output to DAM for downstream consumption not built. (Target 26.3)"},
    "12.4.3": {"Feature": "CRR Manual Override", "Status": "No", "Comments": "New capability for manual risk overrides to be developed."},
    "12.4.4": {"Feature": "Risk Threshold Calculation", "Status": "Yes", "Comments": "Maps Risk Score to Risk Class."},
    "12.4.5": {"Feature": "CRR Risk Framework Configuration", "Status": "No", "Comments": "UI configuration for Prohibited/Very High flags missing."},
    "12.4.6": {"Feature": "CRR Risk Framework Configuration", "Status": "Yes", "Comments": "Configurable flags (Prohibited) on Risk Elements."},
    "12.5": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Rulesets)"},
    "12.5.1": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Rulesets)"},
    "12.6": {"Feature": "Asset Manager", "Status": "No", "Comments": "In Development (Integration Target 26.3)"},
    "12.6.1": {"Feature": "Asset Manager", "Status": "No", "Comments": "Partially satisfied: Missing Center/Market/Legal Entity/Product specific lists."},
    "12.6.2": {"Feature": "Fundamental Assessment", "Status": "No", "Comments": "Partially satisfied: Missing Center/Legal Entity overrides."},
    "12.6.3": {"Feature": "Asset Manager", "Status": "No", "Comments": "In Development (Integration Target 26.3)"},
    "12.6.4": {"Feature": "Authorization", "Status": "No", "Comments": "Features related to IAM/Permissions are not yet implemented."},
    "12.6.5": {"Feature": "Fundamental Assessment", "Status": "Yes", "Comments": "Configured via Y/N question sets."},
    "12.7": {"Feature": "Audit", "Status": "Yes", "Comments": "Tracks changes pushed to Production."},
    "12.7.1": {"Feature": "Audit", "Status": "Yes", "Comments": "Tracks changes pushed to Production."},
    "12.7.2": {"Feature": "Audit", "Status": "Yes", "Comments": "Tracks changes pushed to Production."},
    "12.7.3": {"Feature": "Audit", "Status": "Yes", "Comments": "Tracks changes pushed to Production."},
    "12.7.4": {"Feature": "Audit", "Status": "Yes", "Comments": "Tracks changes pushed to Production."},
    "12.8": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development (Simulation/Integration pending)"},
    "12.8.1": {"Feature": "Unified Sandbox Journey", "Status": "Yes", "Comments": "-"},
    "12.8.2": {"Feature": "Unified Sandbox Journey", "Status": "Yes", "Comments": "-"},
    "12.8.3": {"Feature": "Authorization", "Status": "No", "Comments": "Features related to IAM/Permissions are not yet implemented."},
    "12.8.4": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "Partially satisfied: Missing Center/Legal Entity/Product specific instances."},
    "12.8.5": {"Feature": "Unified Sandbox Journey", "Status": "Yes", "Comments": "-"},
    "12.8.6": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "Feature not developed yet."},
    "12.8.7": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "Feature not developed yet."},
    "12.8.8": {"Feature": "Unified Sandbox Journey", "Status": "Yes", "Comments": "-"},
    "12.8.9": {"Feature": "Unified Sandbox Journey", "Status": "Yes", "Comments": "-"},
    "12.8.10": {"Feature": "Unified Sandbox Journey", "Status": "Yes", "Comments": "-"},
    "12.8.11": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "In Development: Simulation on list update being built."},
    "12.8.12": {"Feature": "Unified Sandbox Journey", "Status": "Yes", "Comments": "-"},
    "12.8.13": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "Merge in-flight changes functionality missing."},
    "12.8.14": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "Impact calculation for risk threshold update not developed."},
    "12.8.15": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "SLA/Performance simulation not simulated/integrated."},
    "12.9": {"Feature": "Real-time Dashboards", "Status": "No", "Comments": "Partially built (UI only). Integration with DAM/Rule Exec pending."},
    "12.9.1": {"Feature": "Real-time Dashboards", "Status": "No", "Comments": "Partially built (UI only). Integration with DAM/Rule Exec pending."},
    "12.9.2": {"Feature": "Real-time Dashboards", "Status": "No", "Comments": "Partially built (UI only). Integration with DAM/Rule Exec pending."},
    "12.9.3": {"Feature": "Real-time Dashboards", "Status": "No", "Comments": "Feature functionality not available."},
    "12.9.4": {"Feature": "Authorization", "Status": "No", "Comments": "Features related to IAM/Permissions are not yet implemented."},
    "12.9.5": {"Feature": "Sandbox Dashboard", "Status": "No", "Comments": "UI completed, but integration missing."},
    "12.9.6": {"Feature": "Unified Sandbox Journey", "Status": "No", "Comments": "Change Summary UI built, but Export functionality missing."},
    "12.10": {"Feature": "Unified Sandbox Journey", "Status": "Yes", "Comments": "Atomic Promotion supported."},
    "12.10.1": {"Feature": "Unified Sandbox Journey", "Status": "Yes", "Comments": "Atomic Promotion supported."},
    "12.10.2": {"Feature": "Unified Sandbox Journey", "Status": "Yes", "Comments": "Atomic Promotion supported."},
    "12.11": {"Feature": "Certification / Attestation", "Status": "No", "Comments": "Prioritized for next year's roadmap (2027)."},
    "12.12": {"Feature": "AML Ecosystem Integration", "Status": "No", "Comments": "Integration endpoints not built (Target 26.3)."},
    "12.13": {"Feature": "GCIP Reporting", "Status": "No", "Comments": "Managed by Core Reporting Team of GCIP."},
    "12.14": {"Feature": "UI Enhancements", "Status": "Yes", "Comments": "Incremental UI improvements."},
    "12.15": {"Feature": "Customer 360 View", "Status": "No", "Comments": "Requirement not built yet (Target 2027)."},
    "12.16": {"Feature": "Triggers (Time/Event based)", "Status": "No", "Comments": "In Development by Rule Exec Team (Target 26.3)."},
    "12.17": {"Feature": "DAM Integration", "Status": "No", "Comments": "Data integration missing (Target 26.3)."},
    "12.18": {"Feature": "System Health Monitoring", "Status": "No", "Comments": "Performance dashboards missing (Target 26.5)."},
    "12.19": {"Feature": "AI/ML Model Ops", "Status": "No", "Comments": "No discussions yet (Target 2027)."},
    "12.20": {"Feature": "Smart Alert Manager", "Status": "No", "Comments": "Not developed yet (Target 2027)."},
    "12.21": {"Feature": "Authorization", "Status": "No", "Comments": "Features related to IAM/Permissions are not yet implemented (Blocking)."},
}

# ==========================================
# 2. System Behavior / Architecture Maps (The "Explanation")
# ==========================================

feature_descriptions = {
    "Unified Sandbox Journey": 
        "**System Behavior:** Users access the 'Sandbox' module via the React Frontend. When a new simulation is initialized, the backend (Python/Node) copies the active Production configuration (Rulesets, Weights, Multipliers) into a temporary 'Draft' schema in the database. Users then modify this draft configuration. The Rule Execution Engine (running in Simulation Mode) scores a sample population against this draft config to generate impact metrics.\n\n"
        "**User Journey:** Login -> Dashboard -> Sandbox -> 'Create New Simulation' -> Select Scope (Enterprise/Market) -> Modify Risk Weights -> Run Simulation -> View Impact -> Submit for Approval.",
    
    "Change Request Workflow":
        "**System Behavior:** A workflow engine (possibly integrated with an external ticketing system or custom-built) manages the lifecycle of configuration changes. While Atomic Promotion (12.10) handles the technical push, this feature manages the *governance*—tracking who requested the change, business justification, and multi-level approvals before the technical promotion is allowed.\n\n"
        "**User Journey:** User identifies gap -> Opens Change Request Form -> Selects Affected Attributes -> Enters Justification -> Submits -> Approver receives notification -> Approver approves -> Change is queued for Sandbox/Production.",
    
    "Asset Manager":
        "**System Behavior:** The Asset Manager acts as the CRUD interface for all Reference Data (Lists, Industry Codes, Country Scores). Data is stored in normalized relational tables. The UI provides filtering, bulk upload (Excel/CSV), and version history for these lists. Changes here propagate to the Rule Execution Engine via cache invalidation or batch updates.\n\n"
        "**User Journey:** Navigation -> Asset Manager -> Select List (e.g., 'High Risk Geographies') -> 'Edit' or 'Upload New Version' -> Validate Entries -> Save.",
    
    "Core Rule Execution Logic":
        "**System Behavior:** The central engine of the CRR platform. It consumes Customer Data (Profile, Transaction, KYC) and applies the active Ruleset Configuration. It calculates Risk Points = Weight * Multiplier for each element, sums them, and maps the total to a Risk Class (Low/Med/High). This runs both in Batch (monthly/daily) and Real-time (onboarding).\n\n"
        "**User Journey:** (Backend Process) No direct user interaction. Users view the *output* of this logic in the Customer 360 or Impact Analysis views.",

    "Authorization":
        "**System Behavior:** Identity and Access Management (IAM) is handled via the enterprise Identity Provider (IDP). The application enforces Role-Based Access Control (RBAC). Roles (e.g., 'Analyst', 'Approver', 'Admin') are mapped to specific API endpoints and UI components. This ensures users only see/edit what they are entitled to.\n\n"
        "**User Journey:** User logs in -> System validates Token -> Fetches Permissions -> UI renders enabled/disabled buttons based on permission set.",
    
    "DAM Integration":
        "**System Behavior:** Data Access Manager (DAM) serves as the integration layer. It acts as the data plumbing, fetching Customer Data from upstream systems (KYC, Transaction Lakes) and pushing generated Risk Ratings to downstream consumers (EDD, Investigations). It manages data lineage and quality checks.\n\n"
        "**User Journey:** (Backend Process) Operations teams monitor Data Ingestion Reports to ensure feed health.",

    "Real-time Dashboards":
        "**System Behavior:** Analytical dashboards rendered in the UI (likely using a charting library like Recharts or D3). They consume aggregated metrics from the Reporting Database/Data Warehouse. They provide drill-down capabilities from Enterprise -> Market -> Legal Entity views.\n\n"
        "**User Journey:** Dashboard -> Apply Filters (Date Range, Region) -> View Risk Distribution Pie Chart -> Drill down into 'High Risk' segment.",

    "Fundamental Assessment":
         "**System Behavior:** A specific sub-module of Asset Manager where users configure 'Fundamental Assessments'—typically Y/N question sets or simplified scorecards used for specific entity types. These are stored as structured JSON or relational rules that the engine parses during scoring.\n\n"
         "**User Journey:** Asset Manager -> Fundamental Assessment -> Select Questionnaire -> Add Question/Weight -> Save."
}

# Generic Fallback for missing features
default_description = "**System Behavior:** This requirement is handled by the core platform architecture, utilizing the standard React-Python stack. Specific behavior details are pending granular design."

# ==========================================
# 3. Mom Test Questions Generator
# ==========================================
def generate_questions(feature, req_id):
    base_questions = [
        "What is the single most expensive mistake a user could make here?",
        "How do you currently solve this problem manually (Excel? Email?)?",
    ]
    
    if "Sandbox" in feature:
        base_questions.append("If a simulation takes 4 hours, what do you do while waiting?")
    if "Asset Manager" in feature:
        base_questions.append("How frequently does this list data actually change? Daily? Yearly?")
    if "Authorization" in feature:
        base_questions.append("Who is the one person who should *never* have access to this?")
    if "Report" in feature:
        base_questions.append("What specific action do you take immediately after seeing this number?")
        
    return base_questions

# ==========================================
# 4. Main Update Logic
# ==========================================

root_dir = "Backlog"
files = glob.glob(f"{root_dir}/**/*.md", recursive=True)

for file_path in files:
    filename = os.path.basename(file_path)
    req_id = filename.replace(".md", "")
    
    # Defaults
    status = "Unknown"
    comments = "No status available."
    feature = "General"
    
    # Match ID
    matched = False
    
    # Exact match first
    if req_id in matrix_data:
        data = matrix_data[req_id]
        status = data["Status"]
        comments = data["Comments"]
        feature = data["Feature"]
        matched = True
    else:
        # Prefix match
        matches = [k for k in matrix_data.keys() if req_id.startswith(k)]
        if matches:
            matches.sort(key=len, reverse=True)
            parent_key = matches[0]
            data = matrix_data[parent_key]
            status = data["Status"]
            comments = data["Comments"]
            feature = data["Feature"]
            matched = True
            
    if not matched and "_Capability" not in req_id:
        continue # Skip files we can't map (or keep old behavior)

    # Prepare Content
    system_behavior = feature_descriptions.get(feature, default_description)
    questions = generate_questions(feature, req_id)
    
    # Read File
    with open(file_path, "r") as f:
        content = f.read()
        
    # Construct New Sections
    new_status_section = f"\n\n## Development Status\n\n**Status:** {status}\n**Comments:** {comments}\n"
    
    new_behavior_section = f"\n\n## System Behavior & User Journey\n\n{system_behavior}\n"
    
    new_question_section = f"\n\n## Business Questions (Mom Test)\n\nThese questions are designed to reveal hidden desires and operational realities:\n\n"
    for q in questions:
        new_question_section += f"- {q}\n"

    # Remove old sections if they exist to avoid duplication/clutter (simple text splitting)
    # We will just append to the end, but creating a delimiter is safer.
    # To keep it simple and robust: We will strip any previous "## Development Status" or "## Business Questions" from the content first.
    
    if "## Development Status" in content:
        content = content.split("## Development Status")[0]
    if "## System Behavior" in content:
        content = content.split("## System Behavior")[0]
    if "## Business Questions" in content:
        content = content.split("## Business Questions")[0]
        
    final_content = content.strip() + new_status_section + new_behavior_section + new_question_section
    
    with open(file_path, "w") as f:
        f.write(final_content)
        
print(f"Processed {len(files)} files.")
