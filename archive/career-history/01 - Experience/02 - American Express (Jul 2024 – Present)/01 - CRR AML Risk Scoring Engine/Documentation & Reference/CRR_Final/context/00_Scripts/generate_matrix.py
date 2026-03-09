
import json

def get_feature_mapping(req_id, description):
    # Mapping logic based on ID prefix
    if req_id.startswith("12.1.") or req_id == "12.1":
        return "Core Risk Framework", "A flexible, graph-based data model to define Risk Categories, Elements, and Hierarchies dynamically."
    
    if req_id.startswith("12.2.") or req_id == "12.2":
        return "Change Management Workflow", "Workflow engine to handle change requests (initiate, review, approve, deploy) with status tracking."
        
    if req_id.startswith("12.3.") or req_id == "12.3":
        return "Dynamic Rules Engine", "Configurable engine allowing business users to define/update risk elements, weights, and multipliers without code changes."
        
    if req_id.startswith("12.4.") or req_id == "12.4":
        return "Real-Time Scoring Service", "High-performance calculation engine that computes Risk Ratings for Customers/Entities based on active rules."
        
    if req_id.startswith("12.5.") or req_id == "12.5":
        return "Advanced Rule Builder", "UI-based logic builder supporting complex conditions (AND/OR/NOT/Grouping) for risk logic."
        
    if req_id.startswith("12.6.") or req_id == "12.6":
        return "Reference Data Manager", "Centralized management UI for Notable Lists, Fundamental Assessments, and other lookup data."
        
    if req_id.startswith("12.7.") or req_id == "12.7":
        return "Audit & Versioning System", "Immutable ledger tracking every change to configuration, data, and scores with 'Who, What, When' details."
        
    if req_id.startswith("12.8.") or req_id == "12.8":
        return "Sandbox Simulation Environment", "Isolated environment with production data copy to run parallel simulations of logic changes."
        
    if req_id.startswith("12.9.") or req_id == "12.9":
        return "Simulation Analytics Dashboard", "Visual analytics tools to compare 'Before vs After' risk distributions and impact analysis."
        
    if req_id.startswith("12.10.") or req_id == "12.10":
        return "Production Deployment Gate", "Automated pipeline with 2-step approval enforcement for promoting Sandbox changes to Production."
        
    if req_id.startswith("12.11.") or req_id == "12.11":
        return "Certification & Compliance Module", "Reporting tools for periodic attestation and regulatory compliance snapshots."
        
    if req_id.startswith("12.12.") or req_id == "12.12":
        return "Integration API Layer", "Standardized APIs (REST/Event-bus) for downstream consumption (KYC, AML) and upstream data ingestion."
        
    if req_id.startswith("12.13.") or req_id == "12.13":
        return "Enterprise Reporting Suite", "Comprehensive BI dashboards for Risk Distribution, Operational Metrics, and temporal analysis."
        
    if req_id.startswith("12.14.") or req_id == "12.14":
        return "CRR Configuration UI", "Frontend interface to visualize and manage the entire risk framework structure and market variations."
        
    if req_id.startswith("12.15.") or req_id == "12.15":
        return "Customer 360 Risk View", "Detailed view for a specific customer showing the 'Why' behind their score (Explainable AI)."
        
    if req_id.startswith("12.16.") or req_id == "12.16":
        return "Batch Rescoring Job", "Scheduled jobs to re-evaluate customer risk based on new data, profile changes, or framework updates."
        
    if req_id.startswith("12.17.") or req_id == "12.17":
        return "Data Quality & Ingestion Fabric", "Robust ETL pipelines ensuring data integrity, lineage, and availability for the scoring engine."
        
    if req_id.startswith("12.18.") or req_id == "12.18":
        return "System Health Monitoring", "Technical dashboards tracking SLA performance, data feed failures, and scoring latency."
        
    if req_id.startswith("12.19.") or req_id == "12.19":
        return "AI/ML Model Ops", "Infrastructure to support transition from rules-based to model-based scoring with explainability and bias monitoring."
        
    if req_id.startswith("12.20.") or req_id == "12.20":
        return "Smart Notification Service", "Event-driven alert system triggering emails/messages based on significant risk shifts or breaches."
        
    if req_id.startswith("12.21.") or req_id == "12.21":
        return "RBAC / IAM Integration", "Granular permission system integrated with enterprise Identity providers for function-level access control."
        
    return "General CRR Capability", "Core platform functionality."

with open('all_requirements.json', 'r') as f:
    reqs = json.load(f)

# Sort reqs by ID numerically if possible to keep order
# They are strings "12.1", "12.1.1", etc.
def sort_key(x):
    parts = x['id'].split('.')
    return [int(p) if p.isdigit() else p for p in parts]

reqs.sort(key=sort_key)

print("# Traceability Matrix: Business Requirements to Features")
print("")
print("| Req ID | Business Requirement Description | Proposed Feature / Solution | Feature Description |")
print("| :--- | :--- | :--- | :--- |")

for r in reqs:
    req_id = r['id']
    desc = r['description'].replace("\n", " ").replace("|", "\|") # Escape pipes
    
    feature_name, feature_desc = get_feature_mapping(req_id, desc)
    
    print(f"| {req_id} | {desc} | {feature_name} | {feature_desc} |")
