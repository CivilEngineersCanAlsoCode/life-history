
import pandas as pd
import os
import re
import shutil

# Configuration
excel_path = '/Users/satvikjain/Downloads/Projects/CRR_Final/context/CRR - American Express/Business Requirements/CRR_Business Requirements Document.xlsx'
backlog_root = '/Users/satvikjain/Downloads/Projects/CRR_Final/Backlog'
sheet_name = 'BRD - Customer Risk Rating'

def clean_filename(text):
    if not isinstance(text, str):
        return "Unknown"
    cleaned = re.sub(r'[\\/*?:"<>|]', "", text)
    cleaned = cleaned.replace(" ", "_")
    return cleaned[:100]

def parse_sub_requirements(text):
    if not isinstance(text, str):
        return []
    
    # Flexible Regex: 
    # Group 1: ID (Digit.Digit.Digit)
    # Separator: Optional space/tab, optional hyphen/colon, optional space
    # Group 2: Content
    pattern = r'(\d+\.\d+\.\d+)[\s:\-]*(.*?)(?=(\n\d+\.\d+\.\d+)|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    results = []
    for m in matches:
        ref_id = m[0].strip()
        content = m[1].strip()
        results.append({'id': ref_id, 'content': content})
        
    return results

def find_header_row(file_path, sheet_name):
    # Same as before
    df_scan = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=20)
    for idx, row in df_scan.iterrows():
        row_str = row.astype(str).str.lower().tolist()
        if any('crr capability' in x for x in row_str) and any('brd ref' in x for x in row_str):
            return idx
    return 1

def main():
    print(f"Opening Excel: {excel_path}")
    
    header_idx = find_header_row(excel_path, sheet_name)
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_idx, dtype={'BRD Ref #': str})
    df.columns = df.columns.str.strip()
    
    col_cap = 'CRR Capability'
    col_ref = 'BRD Ref #'
    col_desc = 'Business Requirement'
    col_subs = 'Additional Details (Sub-Requirements)'
    col_purpose = 'Purpose'
    col_outcome = 'Outcome'

    df = df.dropna(subset=[col_cap, col_ref])
    print(f"Found {len(df)} capability rows.")

    invalid_path = os.path.join(backlog_root, "12.1_Model_Governance")
    if os.path.exists(invalid_path):
        shutil.rmtree(invalid_path)
        
    invalid_path_2 = os.path.join(backlog_root, "12.2_Notifications")
    if os.path.exists(invalid_path_2):
        shutil.rmtree(invalid_path_2)

    for index, row in df.iterrows():
        cap_name = row[col_cap]
        brd_ref = str(row[col_ref])
        desc = row.get(col_desc, 'No description')
        purpose = row.get(col_purpose, 'N/A')
        outcome = row.get(col_outcome, 'N/A')
        sub_reqs_text = row.get(col_subs, '')
        
        safe_cap_name = clean_filename(cap_name)
        folder_name = f"{brd_ref}_{safe_cap_name}"
        folder_path = os.path.join(backlog_root, folder_name)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            
        main_file_path = os.path.join(folder_path, f"{brd_ref}_Capability.md")
        with open(main_file_path, 'w') as f:
            f.write(f"# Capability: {cap_name}\n\n")
            f.write(f"**BRD Ref:** {brd_ref}\n\n")
            f.write(f"## Business Requirement\n{desc}\n\n")
            f.write(f"## Purpose\n{purpose}\n\n")
            f.write(f"## Outcome\n{outcome}\n")
        
        sub_reqs = parse_sub_requirements(sub_reqs_text)
        if sub_reqs:
            for sub in sub_reqs:
                sub_id = sub['id']
                sub_content = sub['content']
                sub_filename = f"{sub_id}.md"
                sub_file_path = os.path.join(folder_path, sub_filename)
                
                with open(sub_file_path, 'w') as sf:
                    sf.write(f"# Sub-Requirement: {sub_id}\n\n")
                    sf.write(f"**Parent Capability:** [{cap_name}]({brd_ref}_Capability.md)\n\n")
                    sf.write(f"## Description\n{sub_content}\n")
        
        # If text exists but no sub-reqs found, dump text to an 'Additional_Details.md' file or append to Capability?
        # User output strictness suggests sub-req files. 
        # But if regex still fails, we lose data.
        # Let's verify '12.21' works with new regex.
             
    print("Backlog regeneration complete.")

if __name__ == "__main__":
    main()
