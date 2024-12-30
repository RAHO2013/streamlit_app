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

            # Clean and process Student Order to handle unexpected formats
            comparison_sheet['Student Order'] = comparison_sheet['Student Order'].str.replace(',', '').astype(float, errors='ignore')
            comparison_sheet['Student Order'] = pd.to_numeric(comparison_sheet['Student Order'], errors='coerce')
            comparison_sheet.sort_values(by='Student Order', inplace=True)

            # Create MAIN CODE in the comparison file
            comparison_sheet['MAIN CODE'] = comparison_sheet['MCC College Code'].str.strip() + "_" + comparison_sheet['COURSE CODE'].str.strip() + "_" + comparison_sheet['Quota'].str.strip()

            # Create MAIN CODE in the master sheet
            if {'MCC College Code', 'COURSE CODE'}.issubset(master_sheet.columns):
                master_sheet['MAIN CODE'] = master_sheet['MCC College Code'].astype(str).str.strip() + "_" + master_sheet['COURSE CODE'].astype(str).str.strip() + "_" + master_sheet['Quota'].astype(str).str.strip()

            # Merge data based on MAIN CODE
            merged_data = pd.merge(comparison_sheet, master_sheet, on='MAIN CODE', how='left', suffixes=('_uploaded', '_master'))

            # Extract Fee and Cutoff data
            fee_cutoff_table = merged_data[[
                'College Name_master', 'Program_uploaded', 'TYPE_uploaded', 'Student Order', 'Fees', 'OC CUTOFF', 'EWS CUTOFF', 'OBC CUTOFF', 'SC CUTOFF', 'ST CUTOFF', 'SERVICE YEARS'
            ]].dropna(how='all').reset_index(drop=True)

            # Convert Fees to numeric for proper sorting
            fee_cutoff_table['Fees'] = pd.to_numeric(fee_cutoff_table['Fees'], errors='coerce')

            # Tabs for displaying data
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Merged Data",
                "State, Program, Type with Student Orders",
                "Validation",
                "Unique Tables",
                "Fee and Cutoff Data"
            ])

            # Tab 1: Merged Data
            with tab1:
                st.write("### Merged Data")
                st.dataframe(merged_data)

            # Tab 2: Fee and Cutoff Data
            with tab5:
                st.write("### Fee and Cutoff Data")

                # Dropdown to filter Fee and Cutoff data
                selected_column = st.selectbox(
                    "Select Fee or Cutoff to Display:",
                    options=['OC CUTOFF', 'EWS CUTOFF', 'OBC CUTOFF', 'SC CUTOFF', 'ST CUTOFF', 'SERVICE YEARS'],
                    index=0
                )

                filtered_fee_cutoff_table = fee_cutoff_table[[
                    'College Name_master', 'Program_uploaded', 'TYPE_uploaded', 'Student Order', 'Fees', selected_column
                ]].rename(columns={
                    'College Name_master': 'College Name',
                    'Program_uploaded': 'Program',
                    'TYPE_uploaded': 'Type'
                })

                # Sort the table by Fees and Student Order
                filtered_fee_cutoff_table = filtered_fee_cutoff_table.sort_values(
                    by=['Fees', 'Student Order'], ascending=True, na_position='last'
                )

                st.dataframe(filtered_fee_cutoff_table.style.format({
                    'Fees': "{:.0f}",
                    selected_column: "{:.0f}" if selected_column != 'SERVICE YEARS' else "{}"
                }))

        except Exception as e:
            st.error(f"An error occurred while processing the uploaded file: {e}")
    else:
        st.info("Please upload an Excel file for comparison.")

def split_ranges(lst):
    """Split a list of integers into start and end ranges."""
    if not lst:
        return ""
    ranges = []
    start = lst[0]
    for i in range(1, len(lst)):
        if lst[i] != lst[i - 1] + 1:
            end = lst[i - 1]
            ranges.append(f"{start}-{end}" if start != end else f"{start}")
            start = lst[i]
    ranges.append(f"{start}-{lst[-1]}" if start != lst[-1] else f"{start}")
    return ", ".join(ranges)
