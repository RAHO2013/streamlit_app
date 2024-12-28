import pandas as pd
import os

# Define the path to the MASTER EXCEL file
MASTER_FILE = os.path.join("data", "MASTER EXCEL.xlsx")

def load_master_sheet():
    if not os.path.exists(MASTER_FILE):
        raise FileNotFoundError(f"Master file '{MASTER_FILE}' is missing in the 'data/' folder!")
    
    # Load the master sheet
    master_sheet = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')

    # Normalize columns
    master_sheet['State'] = master_sheet['State'].str.strip().str.upper()
    master_sheet['Program'] = master_sheet['Program'].str.strip().str.upper()
    master_sheet['TYPE'] = master_sheet['TYPE'].astype(str).str.strip().str.upper()

    # Create MAIN CODE column
    if {'MCC College Code', 'COURSE CODE'}.issubset(master_sheet.columns):
        master_sheet['MAIN CODE'] = master_sheet['MCC College Code'].astype(str) + "_" + master_sheet['COURSE CODE'].astype(str)

    return master_sheet
