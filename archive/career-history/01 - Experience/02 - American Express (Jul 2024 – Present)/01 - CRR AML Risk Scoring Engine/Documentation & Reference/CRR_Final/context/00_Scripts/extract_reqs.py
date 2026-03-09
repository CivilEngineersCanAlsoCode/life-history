
import os
import json

backlog_dir = "/Users/satvikjain/Downloads/Projects/CRR_Final/Backlog"
requirements = []

# Walk through the directory
for root, dirs, files in os.walk(backlog_dir):
    for file in files:
        if file.endswith(".md"):
            path = os.path.join(root, file)
            
            # Skip Step0_Process_Map.md or similar unless relevant
            if "Step0" in file:
                continue
                
            try:
                with open(path, "r") as f:
                    content = f.read()
                    
                # Extract simple metadata mapping
                # Assuming filename is ID like 12.1.1.md -> ID: 12.1.1
                name_parts = file.replace(".md", "").split("_")
                req_id = name_parts[0] # e.g., 12.1.1 or 12.1
                
                # Determine type
                req_type = "Capability" if "Capability" in file else "Requirement"
                
                # Extract Description (dumb extraction: text after ## Description or ## Business Requirement)
                description = ""
                lines = content.split('\n')
                capture = False
                for line in lines:
                    if line.startswith("## Description") or line.startswith("## Business Requirement"):
                        capture = True
                        continue
                    if line.startswith("## ") and capture: # Stop at next header
                        capture = False
                        break
                    if capture and line.strip():
                        description += line.strip() + " "
                
                requirements.append({
                    "id": req_id,
                    "type": req_type,
                    "description": description.strip(),
                    "path": path
                })
            except Exception as e:
                print(f"Error reading {file}: {e}")

# Sort by ID roughly
requirements.sort(key=lambda x: x['id'])

print(json.dumps(requirements, indent=2))
