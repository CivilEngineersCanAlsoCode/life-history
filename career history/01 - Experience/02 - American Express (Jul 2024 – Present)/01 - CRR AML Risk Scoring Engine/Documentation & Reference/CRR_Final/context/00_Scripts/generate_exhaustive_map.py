
import os
import re

context_root = '/Users/satvikjain/Downloads/Projects/CRR_Final/context'
output_file = '/Users/satvikjain/Downloads/Projects/CRR_Final/Backlog/Step0_Process_Map.md'

ignore_dirs = ['.tmp', '.git', '__pycache__', 'venv', 'node_modules', 'archived', '.system_generated']
ignore_files = ['.DS_Store']

def get_file_description(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)
    
    if ext in ['.md', '.txt', '.sql', '.ddl', '.csv', '.json', '.js', '.py', '.html']:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read first non-empty lines
                lines = [line.strip() for line in f.readlines() if line.strip()]
                if not lines:
                    return "Empty file"
                
                # Try to find a header or significant start
                header = lines[0]
                if header.startswith('#'):
                     return header.lstrip('#').strip()
                return f"Text file. Starts with: {header[:50]}..."
        except Exception:
            return "Could not read content"
            
    elif ext == '.pdf':
        return "PDF Document (Content inferred from filename)"
    elif ext in ['.png', '.jpg', '.jpeg', '.gif']:
        return "Image File"
    elif ext in ['.xlsx', '.xls']:
        return "Excel Spreadsheet"
    elif ext in ['.zip', '.tar', '.gz']:
        return "Archive File"
    elif ext == '.rtf':
        return "Rich Text Format"
    
    return "Binary/Unknown Format"

def generate_map():
    with open(output_file, 'w') as out:
        out.write("# Step 0: Exhaustive Context File Map\n\n")
        out.write("**Generated:** 2026-01-21\n")
        out.write("**Scope:** All files in `context/` recursively.\n\n")
        out.write("---\n\n")
        
        for root, dirs, files in os.walk(context_root):
            # Filtering
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            # Calculate relative path and depth
            rel_path = os.path.relpath(root, context_root)
            if rel_path == '.':
                rel_path = "Root (context/)"
                depth = 0
            else:
                depth = rel_path.count(os.sep) + 1
            
            # Write Header
            indent = "#" * (min(depth + 2, 6))
            out.write(f"{indent} 📂 {rel_path}\n\n")
            
            if not files:
                out.write("*No files in this directory.*\n\n")
                continue
                
            # Table Header
            out.write("| File Name | Type | Key Information / Content Preview |\n")
            out.write("|-----------|------|-----------------------------------|\n")
            
            for file in sorted(files):
                if file in ignore_files or file.startswith('.'):
                    continue
                    
                full_path = os.path.join(root, file)
                desc = get_file_description(full_path)
                ext = os.path.splitext(file)[1]
                
                # Escape pipes in description
                desc = desc.replace('|', '\|')
                
                out.write(f"| **{file}** | {ext} | {desc} |\n")
            
            out.write("\n")

if __name__ == "__main__":
    generate_map()
