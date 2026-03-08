
import os
import json

map_file = '/Users/satvikjain/Downloads/Projects/CRR_Final/.tmp/backlog_map.json'
# Updated input file for Batch 3A
questions_input_file = '/Users/satvikjain/Downloads/Projects/CRR_Final/.tmp/missing_batch3b.json'

def apply_questions():
    with open(questions_input_file, 'r') as f:
        questions_data = json.load(f)
        
    updated_count = 0
    
    # Handle list format (direct file paths)
    if isinstance(questions_data, list):
        for item in questions_data:
            file_path = item.get('file_path')
            questions = item.get('questions', [])
            
            if not file_path or not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
                continue
                
            with open(file_path, 'r') as f:
                content = f.read()
            
            if "## Discovery Questions" in content:
                continue
            
            new_section = "\n\n## Discovery Questions\n"
            for q in questions:
                new_section += f"{q}\n"
                
            with open(file_path, 'a') as f:
                f.write(new_section)
                
            updated_count += 1
            print(f"Updated {os.path.basename(file_path)}")

    # Handle dictionary format (Ref ID mapping - legacy support or fallback)
    elif isinstance(questions_data, dict):
        if not os.path.exists(map_file):
             print("Map file missing for dict mode!")
             return
             
        with open(map_file, 'r') as f:
            file_map = json.load(f)

        for ref_id, questions in questions_data.items():
            if ref_id in file_map:
                file_path = file_map[ref_id]
                
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if "## Discovery Questions" in content:
                    continue
                
                new_section = "\n\n## Discovery Questions\n"
                for q in questions:
                    new_section += f"- [ ] {q}\n"
                    
                with open(file_path, 'a') as f:
                    f.write(new_section)
                    
                updated_count += 1
                print(f"Updated {ref_id}")
            else:
                print(f"Warning: Ref ID {ref_id} not found in map.")
            
    print(f"Applying complete. Updated {updated_count} files.")

if __name__ == "__main__":
    apply_questions()
