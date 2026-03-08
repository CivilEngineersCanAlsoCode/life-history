
import pandas as pd
import os
import re

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
    # Flexible Regex (Same as generator)
    pattern = r'(\d+\.\d+\.\d+)[\s:\-]*(.*?)(?=(\n\d+\.\d+\.\d+)|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    results = []
    for m in matches:
        ref_id = m[0].strip()
        content = m[1].strip()
        results.append({'id': ref_id, 'content': content})
    return results

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    # Normalize whitespace/newlines for rough comparison
    return re.sub(r'\s+', ' ', text).strip()

def check_file_content(path, expected_fragments):
    if not os.path.exists(path):
        return False, "File missing"
    
    with open(path, 'r') as f:
        content = f.read()
    
    normalized_content = normalize_text(content)
    missing = []
    for frag in expected_fragments:
        # Skip empty fragments
        if not frag or len(frag.strip()) < 5:
            continue
            
        norm_frag = normalize_text(frag)
        
        # Check presence
        if norm_frag not in normalized_content:
            # Try fuzzy check logic - exact match fails often due to markdown rendering (newlines/bullets)
            # Just check if first 20 chars match or something
            # Or split into words and check percentage overlap?
            # Keeping strict-ish for now:
            missing.append(frag[:50] + "...")
    
    if missing:
        return False, f"Missing content fragments: {missing}"
    return True, f"Found content match"

def find_header_row(file_path, sheet_name):
    df_scan = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=20)
    for idx, row in df_scan.iterrows():
        row_str = row.astype(str).str.lower().tolist()
        if any('crr capability' in x for x in row_str) and any('brd ref' in x for x in row_str):
            return idx
    return 1

def main():
    print("Starting verification (Revised Regex)...")
    header_idx = find_header_row(excel_path, sheet_name)
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_idx, dtype={'BRD Ref #': str})
    
    # Standardize columns
    df.columns = df.columns.str.strip()
    col_cap = 'CRR Capability'
    col_ref = 'BRD Ref #'
    col_desc = 'Business Requirement'
    col_subs = 'Additional Details (Sub-Requirements)'
    col_purpose = 'Purpose'
    col_outcome = 'Outcome'
    
    df = df.dropna(subset=[col_cap, col_ref])
    
    errors = []
    total_checks = 0
    passed_checks = 0
    
    for index, row in df.iterrows():
        cap_name = row[col_cap]
        brd_ref = str(row[col_ref])
        desc = row.get(col_desc, '')
        purpose = row.get(col_purpose, '')
        outcome = row.get(col_outcome, '')
        sub_reqs_text = row.get(col_subs, '')
        
        safe_cap_name = clean_filename(cap_name)
        folder_name = f"{brd_ref}_{safe_cap_name}"
        folder_path = os.path.join(backlog_root, folder_name)
        
        # 1. Check Main Capability File
        main_file = os.path.join(folder_path, f"{brd_ref}_Capability.md")
        to_check = [desc, purpose, outcome]
        to_check = [x for x in to_check if isinstance(x, str) and len(x) > 3 and x.lower() not in ['n/a', 'nan']]
        
        total_checks += 1
        ok, msg = check_file_content(main_file, to_check)
        if not ok:
            errors.append(f"CAPABILITY ERROR [{brd_ref}]: {msg}")
        else:
            passed_checks += 1
            
        # 2. Check Sub Requirements
        sub_reqs = parse_sub_requirements(sub_reqs_text)
        for sub in sub_reqs:
            sub_id = sub['id']
            sub_content = sub['content']
            sub_file = os.path.join(folder_path, f"{sub_id}.md")
            
            total_checks += 1
            ok, msg = check_file_content(sub_file, [sub_content])
            if not ok:
                 errors.append(f"SUB-REQ ERROR [{sub_id}]: {msg}")
            else:
                 passed_checks += 1
                 
        # 3. Check for missed content (Revised logic)
        covered_text = "".join([s['id'] + s['content'] for s in sub_reqs]) # Minimal concat
        if isinstance(sub_reqs_text, str):
            norm_original = re.sub(r'\s+', '', sub_reqs_text)
            norm_covered = re.sub(r'\s+', '', covered_text)
            # Remove digits/dots/separators to verify only text content
            clean_original = re.sub(r'[\d\.\-\:]', '', norm_original)
            clean_covered = re.sub(r'[\d\.\-\:]', '', norm_covered)
            
            diff = len(clean_original) - len(clean_covered)
            
            if diff > 50:
                 errors.append(f"POTENTIAL DATA LOSS [{brd_ref}]: ~{diff} chars of text uncaptured. Check if there are unnumbered sections.")

    print(f"Validation Summary: {passed_checks}/{total_checks} checks passed.")

    if not errors:
        print("VERIFICATION SUCCESS: All requirements match perfectly.")
    else:
        print(f"VERIFICATION FAILED: Found {len(errors)} issues.")
        for e in errors[:10]: # Limit output
            print(e)
            
if __name__ == "__main__":
    main()
