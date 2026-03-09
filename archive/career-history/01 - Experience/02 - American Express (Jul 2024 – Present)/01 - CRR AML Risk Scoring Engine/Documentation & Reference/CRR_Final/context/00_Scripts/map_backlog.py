
import os
import json

backlog_root = '/Users/satvikjain/Downloads/Projects/CRR_Final/Backlog'
output_file = '/Users/satvikjain/Downloads/Projects/CRR_Final/.tmp/backlog_map.json'

def map_files():
    file_map = {}
    
    for root, dirs, files in os.walk(backlog_root):
        for file in files:
            if file.endswith('.md'):
                # Handle ID extraction
                # e.g. "12.1_Capability.md" -> "12.1"
                # "12.1.1.md" -> "12.1.1"
                
                name_part = os.path.splitext(file)[0]
                
                if '_Capability' in name_part:
                    # e.g. 12.1_Capability
                    key = name_part.split('_')[0]
                else:
                    key = name_part
                
                full_path = os.path.join(root, file)
                file_map[key] = full_path
                
    with open(output_file, 'w') as f:
        json.dump(file_map, f, indent=2)
        
    print(f"Mapped {len(file_map)} files to {output_file}")

if __name__ == "__main__":
    map_files()
