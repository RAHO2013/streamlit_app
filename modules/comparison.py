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

            # Assign ranks for State and Program
            def assign_state_program_ranks(df):
                df = df.sort_values(by='Student Order')
                df['Rank'] = (df['MAIN CODE'] != df['MAIN CODE'].shift()).cumsum()
                return df

            merged_data = merged_data.groupby('State', group_keys=False).apply(assign_state_program_ranks)
            merged_data = merged_data.groupby('Program_uploaded', group_keys=False).apply(assign_state_program_ranks)

            # Tabs for validation and dashboard
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Merged Data",
                "Validation",
                "State Opted",
                "Program Opted",
                "Type Opted"
            ])

            # Tab 1: Display merged data
            with tab1:
                st.write("### Merged Table Based on MAIN CODE")
                st.dataframe(merged_data)

            # Tab 2: Validation (Dropdowns)
            with tab2:
                st.write("### Validation")

            # Tab 3: State Opted
            with tab3:
                st.write("### State Opted")
                state_opted = merged_data.groupby('State').apply(
                    lambda x: pd.Series({
                        'Options_Filled': x['MAIN CODE'].nunique(),
                        'Student_Orders': format_ranges(sorted(x['Student Order'].dropna().astype(int).tolist())),
                        'Ranks': ', '.join(map(str, x['Rank'].unique()))
                    })
                ).reset_index()
                state_opted['Student_Orders'] = state_opted['Student_Orders'].apply(lambda x: ', '.join(x))
                st.dataframe(state_opted)

            # Tab 4: Program Opted
            with tab4:
                st.write("### Program Opted")
                program_opted = merged_data.groupby('Program_uploaded').apply(
                    lambda x: pd.Series({
                        'Options_Filled': x['MAIN CODE'].nunique(),
                        'Student_Orders': format_ranges(sorted(x['Student Order'].dropna().astype(int).tolist())),
                        'Ranks': ', '.join(map(str, x['Rank'].unique()))
                    })
                ).reset_index()
                program_opted['Student_Orders'] = program_opted['Student_Orders'].apply(lambda x: ', '.join(x))
                st.dataframe(program_opted)

            # Tab 5: Type Opted
            with tab5:
                st.write("### Type Opted")
                type_opted = merged_data.groupby('TYPE_uploaded').apply(
                    lambda x: pd.Series({
                        'Options_Filled': x['MAIN CODE'].nunique(),
                        'Student_Orders': format_ranges(sorted(x['Student Order'].dropna().astype(int).tolist()))
                    })
                ).reset_index()
                type_opted['Student_Orders'] = type_opted['Student_Orders'].apply(lambda x: ', '.join(x))
                st.dataframe(type_opted)

        except Exception as e:
            st.error(f"An error occurred while processing the uploaded file: {e}")
    else:
        st.info("Please upload an Excel file for comparison.")

def format_ranges(lst):
    """Format a list of integers into range strings."""
    if not lst:
        return []
    ranges = []
    start = lst[0]
    for i in range(1, len(lst)):
        if lst[i] != lst[i - 1] + 1:
            end = lst[i - 1]
            ranges.append(f"{start}" if start == end else f"{start}-{end}")
            start = lst[i]
    ranges.append(f"{start}" if start == lst[-1] else f"{start}-{lst[-1]}")
    return ranges
