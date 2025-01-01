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

            if len(comparison_sheet.columns) < len(expected_columns):
                st.error("Uploaded file must have at least 7 columns.")
                return

            comparison_sheet.rename(columns=dict(zip(comparison_sheet.columns[:7], expected_columns)), inplace=True)

            # Clean and process Student Order
            comparison_sheet['Student Order'] = pd.to_numeric(comparison_sheet['Student Order'], errors='coerce')
            comparison_sheet.sort_values(by='Student Order', inplace=True)

            # Create MAIN CODE
            comparison_sheet['MAIN CODE'] = comparison_sheet['MCC College Code'].str.strip() + "_" + comparison_sheet['COURSE CODE'].str.strip() + "_" + comparison_sheet['Quota'].str.strip()
            master_sheet['MAIN CODE'] = master_sheet['MCC College Code'].str.strip() + "_" + master_sheet['COURSE CODE'].str.strip() + "_" + master_sheet['Quota'].str.strip()

            # Merge data based on MAIN CODE
            merged_data = pd.merge(comparison_sheet, master_sheet, on='MAIN CODE', how='left', suffixes=('_uploaded', '_master'))

            # Tabs for displaying data
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Merged Data",
                "State, Program, Type with Student Orders",
                "Validation",
                "Opted Tables",
                "Fee and Cutoff Data"
            ])

            with tab1:
                display_merged_data(merged_data)

            with tab2:
                display_summary_table(merged_data)

            with tab3:
                display_validation(comparison_sheet, master_sheet, merged_data)

            with tab4:
                display_opted_tables(merged_data)

            with tab5:
                display_fee_cutoff_data(merged_data)

        except Exception as e:
            st.error(f"An error occurred while processing the uploaded file: {e}")
    else:
        st.info("Please upload an Excel file for comparison.")

def display_merged_data(merged_data):
    st.write("### Merged Data")
    merged_data.index = range(1, len(merged_data) + 1)
    st.dataframe(merged_data)

def display_summary_table(merged_data):
    st.write("### State, Program, Type with Student Orders")
    summary_table = merged_data.groupby(['State', 'Program_uploaded', 'Quota_uploaded']).agg(
        Opted_Filled=('MAIN CODE', 'count'),
        Student_Order_Ranges=('Student Order', lambda x: split_ranges(sorted(x.dropna().astype(int).tolist())))
    ).reset_index()

    summary_table.insert(0, 'Student_Order_Ranges', summary_table.pop('Student_Order_Ranges'))
    summary_table['Student_Order_From'] = summary_table['Student_Order_Ranges'].str.extract(r'^([\d]+)', expand=False).astype(float)
    summary_table['Student_Order_To'] = summary_table['Student_Order_Ranges'].str.extract(r'([\d]+)$', expand=False).astype(float)
    summary_table['Student_Order_To'].fillna(summary_table['Student_Order_From'], inplace=True)

    summary_table = summary_table.sort_values(by=['Student_Order_From', 'Student_Order_To']).reset_index(drop=True)
    summary_table.index = range(1, len(summary_table) + 1)

    st.dataframe(summary_table)

def display_validation(comparison_sheet, master_sheet, merged_data):
    st.write("### Validation")
    with st.expander("Unmatched Rows"):
        missing_in_master = comparison_sheet[~comparison_sheet['MAIN CODE'].isin(master_sheet['MAIN CODE'])]
        missing_in_comparison = master_sheet[~master_sheet['MAIN CODE'].isin(comparison_sheet['MAIN CODE'])]

        if not missing_in_master.empty:
            st.write("### Rows in Uploaded File with Missing Matches in Master File")
            missing_in_master.index = range(1, len(missing_in_master) + 1)
            st.dataframe(missing_in_master)

        if not missing_in_comparison.empty:
            st.write("### Rows in Master File with Missing Matches in Uploaded File")
            missing_in_comparison.index = range(1, len(missing_in_comparison) + 1)
            st.dataframe(missing_in_comparison)

    with st.expander("Duplicates"):
        duplicate_in_uploaded = comparison_sheet[comparison_sheet.duplicated(subset=['MAIN CODE'], keep=False)]
        duplicate_in_master = master_sheet[master_sheet.duplicated(subset=['MAIN CODE'], keep=False)]

        if not duplicate_in_uploaded.empty:
            st.write("### Duplicate MAIN CODE Entries in Uploaded File")
            duplicate_in_uploaded.index = range(1, len(duplicate_in_uploaded) + 1)
            st.dataframe(duplicate_in_uploaded)

        if not duplicate_in_master.empty:
            st.write("### Duplicate MAIN CODE Entries in Master File")
            duplicate_in_master.index = range(1, len(duplicate_in_master) + 1)
            st.dataframe(duplicate_in_master)

    with st.expander("Missing Values"):
        missing_values = merged_data[merged_data.isnull().any(axis=1)]
        if not missing_values.empty:
            st.write("### Rows with Missing Values in Merged Data")
            missing_values.index = range(1, len(missing_values) + 1)
            st.dataframe(missing_values)
        else:
            st.success("No missing values found in the merged data!")

def display_opted_tables(merged_data):
    st.write("### Opted Tables")
    col1, col2 = st.columns(2)

    # Opted States
    with col1:
        st.subheader("Opted States")
        opted_state_table = merged_data.groupby('State').agg(
            Opted_Filled=('MAIN CODE', 'count')
        ).reset_index()

        first_occurrence = merged_data.loc[merged_data.groupby('State')['Student Order'].idxmin()]
        opted_state_table = opted_state_table.merge(
            first_occurrence[['State', 'Student Order']], on='State', how='left'
        )

        opted_state_table = opted_state_table.sort_values(by='Student Order').reset_index(drop=True)
        opted_state_table.insert(0, 'Order', range(1, len(opted_state_table) + 1))
        opted_state_table.drop(columns=['Student Order'], inplace=True)
        opted_state_table.index = range(1, len(opted_state_table) + 1)
        st.dataframe(opted_state_table)

    # Opted Programs
    with col2:
        st.subheader("Opted Programs")
        opted_program_table = merged_data.groupby(['Program_uploaded', 'TYPE_uploaded']).agg(
            Opted_Filled=('MAIN CODE', 'count')
        ).reset_index()

        first_occurrence = merged_data.loc[merged_data.groupby(['Program_uploaded', 'TYPE_uploaded'])['Student Order'].idxmin()]
        opted_program_table = opted_program_table.merge(
            first_occurrence[['Program_uploaded', 'TYPE_uploaded', 'Student Order']],
            on=['Program_uploaded', 'TYPE_uploaded'],
            how='left'
        )

        opted_program_table = opted_program_table.sort_values(by='Student Order').reset_index(drop=True)
        opted_program_table.insert(0, 'Order', range(1, len(opted_program_table) + 1))
        opted_program_table.drop(columns=['Student Order'], inplace=True)
        opted_program_table.index = range(1, len(opted_program_table) + 1)
        st.dataframe(opted_program_table)

    # Opted Types
    with col1:
        st.subheader("Opted Types")
        opted_type_table = merged_data.groupby('TYPE_uploaded').agg(
            Opted_Filled=('MAIN CODE', 'count')
        ).reset_index()

        first_occurrence = merged_data.loc[merged_data.groupby('TYPE_uploaded')['Student Order'].idxmin()]
        opted_type_table = opted_type_table.merge(
            first_occurrence[['TYPE_uploaded', 'Student Order']], on='TYPE_uploaded', how='left'
        )

        opted_type_table = opted_type_table.sort_values(by='Student Order').reset_index(drop=True)
        opted_type_table.insert(0, 'Order', range(1, len(opted_type_table) + 1))
        opted_type_table.drop(columns=['Student Order'], inplace=True)
        opted_type_table.index = range(1, len(opted_type_table) + 1)
        st.dataframe(opted_type_table)

    # Opted Course Types
    with col2:
        st.subheader("Opted Course Types")
        if 'COURSE TYPE' in merged_data.columns:
            opted_course_type_table = merged_data.groupby('COURSE TYPE').agg(
                Opted_Filled=('MAIN CODE', 'count')
            ).reset_index()

            first_occurrence = merged_data.loc[merged_data.groupby('COURSE TYPE')['Student Order'].idxmin()]
            opted_course_type_table = opted_course_type_table.merge(
