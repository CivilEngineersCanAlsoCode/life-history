
import pandas as pd

file_path = '/Users/satvikjain/Downloads/Projects/CRR_Final/context/CRR - American Express/Business Requirements/CRR_Business Requirements Document.xlsx'
sheet_name = 'BRD - Customer Risk Rating'

print(f"Reading file: {file_path}, Sheet: {sheet_name}")

try:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    print("\n--- Columns ---")
    for col in df.columns:
        print(col)
        
    print("\n--- First 10 Rows (to handle header offset) ---")
    print(df.head(10).to_string())
    
    # Try to find the specific columns user mentioned
    # Sometimes header is on row 2 or 3
    
except Exception as e:
    print(f"Error: {e}")
