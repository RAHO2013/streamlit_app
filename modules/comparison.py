import streamlit as st
import pandas as pd
import os

def display_comparison():
    st.title("Order Comparison Dashboard")

    # Path to the master file
    MASTER_FILE = os.path.join('data', 'MASTER EXCEL.xlsx')

    if not os.path.exists(MASTER_FILE):
        st.error(f"Master file '{MASTER_FILE}' is missing in the 'data/' folder!")
        return

    master_sheet = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')

    # File upload section
    uploaded_file = st.file_uploader("Upload Comparison File (Excel)", type=["xlsx"])

    if uploaded_file:
        try:
            comparison_sheet = pd.read_excel(uploaded_file, sheet_name='Sheet1')

            # Allow the user to rename columns in the uploaded file
            st.write("### Rename Columns in Uploaded File")
            current_columns = comparison_sheet.columns.tolist()
            renamed_columns = {}

            for column in current_columns:
                new_name = st.text_input(f"Rename column '{column}' to:", column)
                renamed_columns[column] = new_name

            # Apply renamed columns
            comparison_sheet.rename(columns=renamed_columns, inplace=True)

            # Ensure necessary columns exist
            if not {'Institute Name', 'Program Name'}.issubset(comparison_sheet.columns):
                st.error("Comparison file must contain 'Institute Name' and 'Program Name' columns after renaming.")
                return

            # Create MAIN CODE column in comparison file
            comparison_sheet['MAIN CODE'] = comparison_sheet['Institute Name'].astype(str) + "_" + comparison_sheet['Program Name'].astype(str)

            # Create MAIN CODE column in master sheet
            if {'MCC College Code', 'COURSE CODE'}.issubset(master_sheet.columns):
                master_sheet['MAIN CODE'] = master_sheet['MCC College Code'].astype(str) + "_" + master_sheet['COURSE CODE'].astype(str)

            # Find mismatches
            missing_in_comparison = set(master_sheet['MAIN CODE']) - set(comparison_sheet['MAIN CODE'])
            missing_in_master = set(comparison_sheet['MAIN CODE']) - set(master_sheet['MAIN CODE'])

            # Display results
            st.write("### MAIN CODE Missing in Comparison File")
            missing_comparison_df = pd.DataFrame(list(missing_in_comparison), columns=["MAIN CODE"])
            missing_comparison_df.index = range(1, len(missing_comparison_df) + 1)
            st.dataframe(missing_comparison_df)

            st.write("### MAIN CODE Missing in Master File")
            missing_master_df = pd.DataFrame(list(missing_in_master), columns=["MAIN CODE"])
            missing_master_df.index = range(1, len(missing_master_df) + 1)
            st.dataframe(missing_master_df)

        except Exception as e:
            st.error(f"An error occurred while processing the uploaded file: {e}")
    else:
        st.info("Please upload an Excel file for comparison.")
