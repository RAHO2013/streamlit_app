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
            expected_columns = [
                "MCC College Code",
                "College Name",
                "COURSE CODE",
                "Program",
                "Quota",
                "TYPE",
                "Student Order"
            ]

            comparison_sheet.rename(columns=dict(zip(comparison_sheet.columns[:7], expected_columns)), inplace=True)

            # Ensure Student Order is numeric and sorted
            comparison_sheet['Student Order'] = pd.to_numeric(comparison_sheet['Student Order'], errors='coerce')
            comparison_sheet.sort_values(by='Student Order', inplace=True)

            # Create MAIN CODE in the comparison file
            comparison_sheet['MAIN CODE'] = comparison_sheet['MCC College Code'].str.strip() + "_" + comparison_sheet['COURSE CODE'].str.strip()

            # Create MAIN CODE in the master sheet
            if {'MCC College Code', 'COURSE CODE'}.issubset(master_sheet.columns):
                master_sheet['MAIN CODE'] = master_sheet['MCC College Code'].astype(str).str.strip() + "_" + master_sheet['COURSE CODE'].astype(str).str.strip()

            # Merge data based on MAIN CODE
            merged_data = pd.merge(comparison_sheet, master_sheet, on='MAIN CODE', how='left', suffixes=('_uploaded', '_master'))

            # Function to assign contiguous ranks
            def assign_ranks(group):
                group = group.sort_values('Student Order')
                group['Rank'] = (group['Student Order'].diff() > 1).cumsum() + 1
                return group

            # Tabs for display
            tab1, tab2, tab3, tab4 = st.tabs(["Merged Data", "State Opted", "Program Opted", "Type Opted"])

            # Tab 1: Merged Data
            with tab1:
                st.write("### Merged Data")
                st.dataframe(merged_data)

            # Tab 2: State Opted
            with tab2:
                st.write("### State Opted")
                state_grouped = merged_data.groupby('State', group_keys=False).apply(assign_ranks)
                state_summary = state_grouped.groupby(['State', 'Rank']).agg(
                    Options_Filled=('MAIN CODE', 'count'),
                    Student_Orders=('Student Order', lambda x: format_ranges(sorted(x.dropna().tolist())))
                ).reset_index()
                st.dataframe(state_summary)

            # Tab 3: Program Opted
            with tab3:
                st.write("### Program Opted")
                program_grouped = merged_data.groupby('Program_uploaded', group_keys=False).apply(assign_ranks)
                program_summary = program_grouped.groupby(['Program_uploaded', 'Rank']).agg(
                    Options_Filled=('MAIN CODE', 'count'),
                    Student_Orders=('Student Order', lambda x: format_ranges(sorted(x.dropna().tolist())))
                ).reset_index()
                st.dataframe(program_summary)

            # Tab 4: Type Opted
            with tab4:
                st.write("### Type Opted")
                type_summary = merged_data.groupby('TYPE_uploaded').agg(
                    Options_Filled=('MAIN CODE', 'count'),
                    Student_Orders=('Student Order', lambda x: format_ranges(sorted(x.dropna().tolist())))
                ).reset_index()
                st.dataframe(type_summary)

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
