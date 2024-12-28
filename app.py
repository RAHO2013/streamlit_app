import streamlit as st
import pandas as pd
import os

# Sidebar Navigation
def navigate():
    st.sidebar.title("Navigation")
    return st.sidebar.radio(
        "Select a page:",
        ["Order Creation", "Order Creation with Excel", "Order Comparison", "Fee Checking"]
    )

# Main App Logic
def main():
    st.set_page_config(page_title="ETERNALS", layout="wide")

    # Load MASTER EXCEL file
    MASTER_FILE = "data/MASTER EXCEL.xlsx"
    if not os.path.exists(MASTER_FILE):
        st.error(f"Master file '{MASTER_FILE}' is missing in the project folder!")
        return

    # Load and preprocess master_sheet
    master_sheet = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')
    master_sheet['State'] = master_sheet['State'].str.strip().str.upper()
    master_sheet['Program'] = master_sheet['Program'].str.strip().str.upper()
    master_sheet['TYPE'] = master_sheet['TYPE'].astype(str).str.strip().str.upper()
    if {'MCC College Code', 'COURSE CODE'}.issubset(master_sheet.columns):
        master_sheet['MAIN CODE'] = master_sheet['MCC College Code'].astype(str) + "_" + master_sheet['COURSE CODE'].astype(str)

    # Navigation
    page = navigate()

    # Page Routing with master_sheet passed
    if page == "Order Creation":
        from modules.order_creation import display_order_creation
        display_order_creation(master_sheet)  # Pass master_sheet
    elif page == "Order Creation with Excel":
        from modules.excel_ranking import display_excel_ranking
        display_excel_ranking(master_sheet)  # Pass master_sheet
    elif page == "Order Comparison":
        from modules.comparison import display_comparison
        display_comparison(master_sheet)  # Pass master_sheet
    elif page == "Fee Checking":
        from modules.fee_checking import display_fee_checking
        display_fee_checking(master_sheet)  # Pass master_sheet

if __name__ == "__main__":
    main()
