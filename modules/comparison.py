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

    master_sheet = pd.read_excel(MASTER_FILE, sheet_name='Sheet1', dtype=str)

    # File upload section
    uploaded_file = st.file_uploader("Upload Comparison File (Excel)", type=["xlsx"])

    if uploaded_file:
        try:
            comparison_sheet = pd.read_excel(uploaded_file, sheet_name='Sheet1', dtype=str)

            # Rename columns in the uploaded file
            st.write("### Renaming Columns in Uploaded File")
            expected_columns = [
                "MCC College Code",
                "College Name",
                "COURSE CODE",
                "Program",
                "Quota",
                "TYPE",
                "Student Order"
            ]

            # Validate the uploaded file has enough columns
            if len(comparison_sheet.columns) < len(expected_columns):
                st.error("Uploaded file must have at least 7 columns.")
                return

            # Rename only the first 7 columns to match expected structure
            comparison_sheet.rename(columns=dict(zip(comparison_sheet.columns[:7], expected_columns)), inplace=True)

            # Ensure Student Order is numeric and starts at 1
            comparison_sheet['Student Order'] = pd.to_numeric(comparison_sheet['Student Order'], errors='coerce')
            if comparison_sheet['Student Order'].min() != 1:
                st.warning("'Student Order' should start from 1. Please check the uploaded file.")

            # Create MAIN CODE in the comparison file
            comparison_sheet['MAIN CODE'] = comparison_sheet['MCC College Code'].str.strip() + "_" + comparison_sheet['COURSE CODE'].str.strip()

            # Create MAIN CODE in the master sheet
            if {'MCC College Code', 'COURSE CODE'}.issubset(master_sheet.columns):
                master_sheet['MAIN CODE'] = master_sheet['MCC College Code'].astype(str).str.strip() + "_" + master_sheet['COURSE CODE'].astype(str).str.strip()

            # Merge data based on MAIN CODE
            merged_data = pd.merge(comparison_sheet, master_sheet, on='MAIN CODE', how='left', suffixes=('_uploaded', '_master'))

            # Tabs for validation and merged data display
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Merged Data",
                "Unmatched Rows",
                "Duplicates",
                "Missing Values",
                "Student Order Validation"
            ])

            # Tab 1: Display merged data
            with tab1:
                st.write("### Merged Table Based on MAIN CODE")
                st.dataframe(merged_data)

            # Tab 2: Check for unmatched rows
            with tab2:
                missing_in_master = comparison_sheet[~comparison_sheet['MAIN CODE'].isin(master_sheet['MAIN CODE'])]
                missing_in_comparison = master_sheet[~master_sheet['MAIN CODE'].isin(comparison_sheet['MAIN CODE'])]

                if not missing_in_master.empty:
                    st.write("### Rows in Uploaded File with Missing Matches in Master File")
                    st.dataframe(missing_in_master)

                if not missing_in_comparison.empty:
                    st.write("### Rows in Master File with Missing Matches in Uploaded File")
                    st.dataframe(missing_in_comparison)

            # Tab 3: Check for duplicates
            with tab3:
                duplicate_in_uploaded = comparison_sheet[comparison_sheet.duplicated(subset=['MAIN CODE'], keep=False)]
                duplicate_in_master = master_sheet[master_sheet.duplicated(subset=['MAIN CODE'], keep=False)]

                if not duplicate_in_uploaded.empty:
                    st.write("### Duplicate MAIN CODE Entries in Uploaded File")
                    st.dataframe(duplicate_in_uploaded)

                if not duplicate_in_master.empty:
                    st.write("### Duplicate MAIN CODE Entries in Master File")
                    st.dataframe(duplicate_in_master)

            # Tab 4: Check for missing values
            with tab4:
                missing_values = merged_data[merged_data.isnull().any(axis=1)]

                if not missing_values.empty:
                    st.write("### Rows with Missing Values in Merged Data")
                    st.dataframe(missing_values)
                else:
                    st.success("No missing values found in the merged data!")

            # Tab 5: Validate Student Order
            with tab5:
                if comparison_sheet['Student Order'].isnull().any():
                    st.write("### Invalid or Missing 'Student Order' Entries")
                    invalid_student_order = comparison_sheet[comparison_sheet['Student Order'].isnull()]
                    st.dataframe(invalid_student_order)
                else:
                    st.success("'Student Order' values are valid and properly formatted.")

        except Exception as e:
            st.error(f"An error occurred while processing the uploaded file: {e}")
    else:
        st.info("Please upload an Excel file for comparison.")
