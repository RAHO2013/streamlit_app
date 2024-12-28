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
                Student_Orders=('Student Order', lambda x: format_ranges(sorted(x.dropna().astype(int).tolist())))
            ).reset_index()

            # Add a helper column for group rankings
            def assign_group_ranks(data):
                data = data.sort_values('Student_Orders', key=lambda x: x.str.split('-').str[0].astype(int))
                data['Helper_Group'] = (data['Student_Orders']
                                        .str.split('-')
                                        .str[0]
                                        .astype(int)
                                        .diff()
                                        .fillna(0)
                                        .gt(1)
                                        .cumsum() + 1)
                return data

            summary_table = assign_group_ranks(summary_table)

            # Tabs for displaying data
            tab1, tab2, tab3 = st.tabs([
                "Merged Data",
                "State, Program, Type with Student Orders",
                "Validation"
            ])

            # Tab 1: Merged Data
            with tab1:
                st.write("### Merged Data")
                st.dataframe(merged_data)

            # Tab 2: Summary Table
            with tab2:
                st.write("### State, Program, Type with Student Orders and Helper Groups")
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

        except Exception as e:
            st.error(f"An error occurred while processing the uploaded file: {e}")
    else:
        st.info("Please upload an Excel file for comparison.")

def format_ranges(lst):
    """Format a list of integers into range strings."""
    if not lst:
        return ""
    ranges = []
    start = lst[0]
    for i in range(1, len(lst)):
        if lst[i] != lst[i - 1] + 1:
            end = lst[i - 1]
            ranges.append(f"{start}" if start == end else f"{start}-{end}")
            start = lst[i]
    ranges.append(f"{start}" if start == lst[-1] else f"{start}-{lst[-1]}")
    return ", ".join(ranges)
