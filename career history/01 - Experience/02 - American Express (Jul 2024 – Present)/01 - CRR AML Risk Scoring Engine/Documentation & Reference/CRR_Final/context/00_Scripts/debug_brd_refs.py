
import pandas as pd

excel_path = '/Users/satvikjain/Downloads/Projects/CRR_Final/context/CRR - American Express/Business Requirements/CRR_Business Requirements Document.xlsx'
sheet_name = 'BRD - Customer Risk Rating'

def find_header_row(file_path, sheet_name):
    # Same logic as before
    df_scan = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=20)
    for idx, row in df_scan.iterrows():
        row_str = row.astype(str).str.lower().tolist()
        if any('crr capability' in x for x in row_str) and any('brd ref' in x for x in row_str):
            return idx
    return 1

# Read with specific converters or dtype to try and preserve string format (though Excel often gives float)
header_idx = find_header_row(excel_path, sheet_name)
df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_idx, dtype={'BRD Ref #': str})

print("--- BRD Refs Found ---")
for index, row in df.iterrows():
    if pd.notna(row.get('CRR Capability')):
        print(f"Ref: '{row.get('BRD Ref #')}' - Cap: {row.get('CRR Capability')}")
