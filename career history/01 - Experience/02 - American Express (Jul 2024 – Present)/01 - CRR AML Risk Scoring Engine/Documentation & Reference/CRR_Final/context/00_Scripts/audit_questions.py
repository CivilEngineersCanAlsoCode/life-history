
import os

backlog_root = '/Users/satvikjain/Downloads/Projects/CRR_Final/Backlog'

def audit_questions():
    missing_files = []
    total_files = 0
    
    for root, dirs, files in os.walk(backlog_root):
        for file in files:
            if file.endswith('.md') and not file.startswith('Step0'):
                total_files += 1
                full_path = os.path.join(root, file)
                
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                    
                    if "## Discovery Questions" not in content:
                        missing_files.append(full_path)
                except Exception as e:
                    print(f"Error reading {file}: {e}")

    print(f"Total MD Files: {total_files}")
    print(f"Files Missing Questions: {len(missing_files)}")
    
    if missing_files:
        print("\n--- Missing Files List ---")
        for f in sorted(missing_files):
            # Print relative path for readability
            rel_path = os.path.relpath(f, backlog_root)
            print(rel_path)

if __name__ == "__main__":
    audit_questions()
