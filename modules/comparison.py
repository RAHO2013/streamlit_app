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
            comparison_sheet['MAIN CODE'] = comparison_sheet['MCC College Code'].str.strip() + "_" + comparison_sheet['COURSE CODE'].str.strip()

            # Create MAIN CODE in the master sheet
            if {'MCC College Code', 'COURSE CODE'}.issubset(master_sheet.columns):
                master_sheet['MAIN CODE'] = master_sheet['MCC College Code'].astype(str).str.strip() + "_" + master_sheet['COURSE CODE'].astype(str).str.strip()

            # Merge data based on MAIN CODE
            merged_data = pd.merge(comparison_sheet, master_sheet, on='MAIN CODE', how='left', suffixes=('_uploaded', '_master'))

            # Combine State, Program, Type, and Student Orders into a single table
            summary_table = merged_data.groupby(['State', 'Program_uploaded', 'TYPE_uploaded']).agg(
                Options_Filled=('MAIN CODE', 'count'),
                Student_Order_Ranges=('Student Order', lambda x: split_ranges(sorted(x.dropna().astype(int).tolist())))
            ).reset_index()

            # Split Student Order ranges into separate columns and ensure they are numeric
            summary_table[['Student_Order_From', 'Student_Order_To']] = summary_table['Student_Order_Ranges'].str.extract(r'(\d+)-(\d+)', expand=True)
            summary_table['Student_Order_From'] = pd.to_numeric(summary_table['Student_Order_From'], errors='coerce')
            summary_table['Student_Order_To'] = pd.to_numeric(summary_table['Student_Order_To'], errors='coerce')

            # Fill missing 'To' values with the same as 'From' for better sorting and analysis
            summary_table['Student_Order_To'].fillna(summary_table['Student_Order_From'], inplace=True)

            # Sort the summary table by numeric columns for correct ascending order
            summary_table = summary_table.sort_values(by=['Student_Order_From', 'Student_Order_To']).reset_index(drop=True)

            # Create unique tables for State, Program, and Type
            unique_state_table = merged_data[['State']].drop_duplicates().reset_index(drop=True)
            unique_program_table = merged_data[['Program_uploaded']].drop_duplicates().reset_index(drop=True)
            unique_type_table = merged_data[['TYPE_uploaded']].drop_duplicates().reset_index(drop=True)

            # Tabs for displaying data
            tab1, tab2, tab3, tab4 = st.tabs([
                "Merged Data",
                "State, Program, Type with Student Orders",
                "Validation",
                "Unique Tables"
            ])

            # Tab 1: Merged Data
            with tab1:
                st.write("### Merged Data")
                st.dataframe(merged_data)

            # Tab 2: Summary Table
            with tab2:
                st.write("### State, Program, Type with Student Orders")
                st.dataframe(summary_table)

            # Tab 3: Validation
            with tab3:
                with st.expander("Unmatched Rows"):
                    st.write("### Unmatched Rows")
                    missing_in_master = comparison_sheet[~comparison_sheet['MAIN CODE'].isin(master_sheet['MAIN CODE'])]
                    missing_in_comparison = master_sheet[~master_sheet['MAIN CODE'].isin(comparison_sheet['MAIN CODE'])]

                    if not missing_in_master.empty:
                        st.write("### Rows in Uploaded File with Missing Matches in Master File")
                        st.dataframe(missing_in_master)

                    if not missing_in_comparison.empty:
                        st.write("### Rows in Master File with Missing Matches in Uploaded File")
                        st.dataframe(missing_in_comparison)

                with st.expander("Duplicates"):
                    st.write("### Duplicates")
                    duplicate_in_uploaded = comparison_sheet[comparison_sheet.duplicated(subset=['MAIN CODE'], keep=False)]
                    duplicate_in_master = master_sheet[master_sheet.duplicated(subset=['MAIN CODE'], keep=False)]

                    if not duplicate_in_uploaded.empty:
                        st.write("### Duplicate MAIN CODE Entries in Uploaded File")
                        st.dataframe(duplicate_in_uploaded)

                    if not duplicate_in_master.empty:
                        st.write("### Duplicate MAIN CODE Entries in Master File")
                        st.dataframe(duplicate_in_master)

                with st.expander("Missing Values"):
                    st.write("### Missing Values")
                    missing_values = merged_data[merged_data.isnull().any(axis=1)]

                    if not missing_values.empty:
                        st.write("### Rows with Missing Values in Merged Data")
                        st.dataframe(missing_values)
                    else:
                        st.success("No missing values found in the merged data!")

            # Tab 4: Unique Tables
            with tab4:
                with st.expander("Unique States"):
                    st.write("### Unique States")
                    st.dataframe(unique_state_table)

                with st.expander("Unique Programs"):
                    st.write("### Unique Programs")
                    st.dataframe(unique_program_table)

                with st.expander("Unique Types"):
                    st.write("### Unique Types")
                    st.dataframe(unique_type_table)

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
