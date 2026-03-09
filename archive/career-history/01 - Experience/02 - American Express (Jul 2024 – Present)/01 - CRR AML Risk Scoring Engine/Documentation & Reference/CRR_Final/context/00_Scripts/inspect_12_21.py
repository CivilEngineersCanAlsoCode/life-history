
import pandas as pd

excel_path = '/Users/satvikjain/Downloads/Projects/CRR_Final/context/CRR - American Express/Business Requirements/CRR_Business Requirements Document.xlsx'
sheet_name = 'BRD - Customer Risk Rating'

def find_header_row(file_path, sheet_name):
    df_scan = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=20)
    for idx, row in df_scan.iterrows():
        row_str = row.astype(str).str.lower().tolist()
        if any('crr capability' in x for x in row_str) and any('brd ref' in x for x in row_str):
            return idx
    return 1

def main():
    header_idx = find_header_row(excel_path, sheet_name)
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_idx, dtype={'BRD Ref #': str})
    
    # Strip whitespace
    df.columns = df.columns.str.strip()
    
    # Find 12.21
    row = df[df['BRD Ref #'] == '12.21']
    if not row.empty:
        print("--- 12.21 Additional Details ---")
        print(row.iloc[0]['Additional Details (Sub-Requirements)'])
    else:
        print("12.21 not found")

if __name__ == "__main__":
    main()
