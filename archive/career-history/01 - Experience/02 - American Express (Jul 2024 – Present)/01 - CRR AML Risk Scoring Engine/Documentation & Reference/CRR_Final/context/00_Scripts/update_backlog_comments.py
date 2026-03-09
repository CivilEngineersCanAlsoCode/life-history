
import os

# Define the updates logic mapped by ID prefix or exact ID
# Format: ID -> { "status": "...", "comments": "...", "questions": [...] }

updates_map = {
    # 12.2 Change Request
    "12.2": {
        "status": "Not Satisfied (Target PI 26.4)",
        "comments": "New Feature to be built for MCOs to submit/track changes.",
        "questions": [
            "Can you walk me through the last time a configuration change broke something in Production? How did you catch it?",
            "Who are the specific people (roles) that should *never* see the 'Promote to Production' button?",
            "Do you need a 'Draft' state for Change Requests where you can save work without submitting?"
        ]
    },
    # 12.3 Updates
    "12.3.3": {
        "status": "Not Satisfied",
        "comments": "Constraint/Warning logic for unsupported data combinations missing.",
        "questions": [
            "What specific data combinations (e.g. Country + Industry) are technically impossible for the Rule Execution Team to support?",
            "What should happen if a user tries to create this combination? Error message? Block? Warning?"
        ]
    },
    "12.3.6": {
        "status": "Partially Satisfied (Missing Center/Legal Entity/Product overrides)",
        "comments": "Currently supports Enterprise & Market overrides. Missing lower-level overrides.",
        "questions": [
            "How often do local compliance officers actually ask for a Center-specific override vs just applying the Enterprise rule?",
            "If a Center override conflicts with a Legal Entity override, which one wins?"
        ]
    },
    "12.3.7": {
         "status": "Partially Satisfied (Missing Center/Legal Entity support)",
         "comments": "Missing Center/Legal Entity specific capability.",
         "questions": [
            "Do you have a concrete example of a Risk Element that applies *only* to one specific Legal Entity and nowhere else?"
         ]
    },
    # 12.4 Risk Scoring
    "12.4.2": {
        "status": "Not Satisfied (Target PI 26.3)",
        "comments": "Output to Data Access Manager (DAM) for downstream consumption not yet built.",
        "questions": [
            "Who exactly consumes the Risk Rating downstream? (KYC? EDD?)",
            "What is the SLA for them receiving the score? Real-time or End-of-Day?"
        ]
    },
    "12.4.5": {
        "status": "Not Satisfied (UI Config Missing)",
        "comments": "UI configuration for Prohibited/Very High flags missing.",
        "questions": [
            "If the 'Very High' flag is set, does it trigger an immediate account freeze, or just a flag for manual review?",
            "Do these flags need to be visible on the main Customer Dashboard?"
        ]
    },
    # 12.6 Lists
    "12.6.1": {
        "status": "Partially Satisfied (Target PI 26.1/26.2)",
        "comments": "Missing Center/Market/Legal Entity/Product specific lists.",
        "questions": [
            "Do you have an example of a list designated for a specific Product that *must not* be visible to other Products?",
            "Who manages these local lists? Central team or Local Market officers?"
        ]
    },
    # 12.8 Sandbox
    "12.8.4": {
        "status": "Partially Satisfied (Target PI 26.4)",
        "comments": "Missing Center/Legal Entity/Product specific instances.",
        "questions": [
            "When you say 'Parallel Simulation', are these completely different scenarios (e.g., Geo vs Product) or iterations of the same scenario?",
            "Do you need to compare results across two different instances side-by-side?"
        ]
    },
    "12.8.13": {
        "status": "Not Satisfied (Target PI 26.4)",
        "comments": "Merge in-flight changes functionality missing.",
        "questions": [
            "If User A and User B both change the 'Geography' risk weights in parallel sandboxes, how should we decide whose change wins?",
            "Is 'Last Save Wins' acceptable, or do we need a complex conflict resolution UI?"
        ]
    },
    # 12.9 Reporting
    "12.9": {
        "status": "Not Satisfied (Target PI 26.3)",
        "comments": "Partially built (UI only). Integration with DAM/Rule Exec pending. Sandbox Reporting.",
        "questions": [
            "What is the *one* number you check every morning regarding Risk Distribution?",
            "Do you need to see the 'Before vs After' distribution graph *before* you hit the Submit button?"
        ]
    },
    # 12.11 Certification
    "12.11": {
        "status": "Not Satisfied (Target 2027)",
        "comments": "Prioritized for next year's roadmap.",
        "questions": [
            "Is this certification a regulatory requirement? If so, how are you doing it today? (Manually?)",
            "What is the frequency of this certification? Annual? Quarterly?"
        ]
    },
    # 12.13 Reporting
    "12.13": {
        "status": "Not Satisfied (Core Reporting Team)",
        "comments": "Managed by Core Reporting Team of GCIP.",
        "questions": [
            "Have you already briefed the GCIP Core Reporting Team on these requirements?",
            "Do we need to expose an API for them to fetch our data, or do they access the DB directly?"
        ]
    },
    # 12.16 Rescoring
    "12.16": {
        "status": "Not Satisfied (Target PI 26.1-26.3)",
        "comments": "In Development by Rule Exec Team (Parallel Track).",
        "questions": [
            "How quickly does a Geography corruption score update need to reflect in the Customer Risk Score? Real-time or End-of-Day?",
            "What happens if a rescore fails? Do we rollback or alert?"
        ]
    },
    # 12.20 Notifications
    "12.20": {
        "status": "Not Satisfied (Target 2027)",
        "comments": "Smart Alert Manager not developed yet.",
        "questions": [
            "Who determines the threshold for 'Significant Event'? Is it configurable per market?",
            "Do these alerts need to go to email, or just appear in the app?"
        ]
    },
    # 12.21 Authorization
    "12.21": {
        "status": "Not Satisfied (Target PI 26.3)",
        "comments": "Features related to IAM/Permissions are not yet implemented. Blocking Dependency.",
        "questions": [
            "What is the matrix of Roles vs Actions? (e.g. Can an 'Analyst' create a List but not Approve it?)",
            "Do we integrate with an existing IDP (like Active Directory) or is this custom?"
        ]
    }
}

# Helper to find closest match in map
def get_update_data(req_id):
    # Try exact match
    if req_id in updates_map:
        return updates_map[req_id]
    
    # Try prefix match (longest prefix wins)
    matches = []
    for key in updates_map:
        if req_id.startswith(key):
            matches.append(key)
    
    if matches:
        # Sort by length descending to get most specific match (e.g. 12.3.6 over 12.3)
        matches.sort(key=len, reverse=True)
        return updates_map[matches[0]]
    
    return None

import glob

root_dir = "Backlog"
files = glob.glob(f"{root_dir}/**/*.md", recursive=True)

for file_path in files:
    filename = os.path.basename(file_path)
    req_id = filename.replace(".md", "")
    
    # Skip non-ID files
    if not req_id.replace(".", "").isdigit():
        if "_Capability" not in req_id:
             continue
        # Process Capability files if needed, but usually we target specific IDs
    
    update_data = get_update_data(req_id)
    
    if update_data:
        print(f"Updating {file_path}...")
        
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check if sections already exist to avoid duplication
        if "## Development Status" not in content:
            new_section = f"\n\n## Development Status\n\n"
            new_section += f"**Status:** {update_data['status']}\n"
            new_section += f"**Comments:** {update_data['comments']}\n"
            
            new_section += f"\n## Business Questions (Mom Test)\n\n"
            new_section += "These questions are designed to reveal hidden desires and operational realities:\n\n"
            for q in update_data['questions']:
                new_section += f"- {q}\n"
                
            with open(file_path, "a") as f:
                f.write(new_section)

print("Update Complete.")
