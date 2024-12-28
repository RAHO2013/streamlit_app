import streamlit as st
import pandas as pd
import os

def display_excel_ranking():
    st.title("Order Creation with Excel")

    # Path to the master file
    MASTER_FILE = os.path.join('data', 'MASTER EXCEL.xlsx')

    if not os.path.exists(MASTER_FILE):
        st.error(f"Master file '{MASTER_FILE}' is missing in the 'data/' folder!")
        return

    master_sheet = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')

    # File upload section
    uploaded_file = st.file_uploader("Upload Excel File (with Two Sheets)", type=["xlsx"])

    if uploaded_file:
        try:
            # Load both sheets
            state_data = pd.read_excel(uploaded_file, sheet_name='StateRanks')
            program_data = pd.read_excel(uploaded_file, sheet_name='ProgramRanks')

            # Validate State Sheet
            if not {'State', 'State Rank'}.issubset(state_data.columns):
                st.error("State sheet must contain 'State' and 'State Rank' columns.")
                return

            # Validate Program Sheet
            if not {'Program', 'Program Type', 'Program Rank'}.issubset(program_data.columns):
                st.error("Program sheet must contain 'Program', 'Program Type', and 'Program Rank' columns.")
                return

            # Map rankings
            master_sheet['State Rank'] = master_sheet['State'].map(state_data.set_index('State')['State Rank']).fillna(0)
            master_sheet['Program Rank'] = master_sheet.apply(
                lambda x: program_data.loc[
                    (program_data['Program'].str.upper() == x['Program'].upper()) &
                    (program_data['Program Type'].str.upper() == x['TYPE'].upper()),
                    'Program Rank'
                ].values[0] if ((program_data['Program'].str.upper() == x['Program'].upper()) &
                                (program_data['Program Type'].str.upper() == x['TYPE'].upper())).any() else 0,
                axis=1
            )

            # Generate ordered table
            ordered_data = master_sheet.query("`State Rank` > 0 and `Program Rank` > 0").sort_values(
                by=['Program Rank', 'State Rank']
            ).reset_index(drop=True)
            ordered_data['Order Number'] = range(1, len(ordered_data) + 1)

            # Collapsible section to select columns to display
            with st.expander("Select Columns to Display", expanded=True):
                st.write("### Choose the columns you want to include in the ordered table:")
                default_columns = ['MAIN CODE', 'Program', 'TYPE', 'State', 'College Name', 'Program Rank', 'State Rank', 'Order Number']
                selected_columns = st.multiselect(
                    "Select columns:",
                    list(master_sheet.columns) + ['State Rank', 'Program Rank', 'Order Number'],
                    default=default_columns
                )

            # Display ordered table
            if not selected_columns:
                st.warning("Please select at least one column to display the table.")
            else:
                st.write("### Ordered Table from Uploaded Excel")
                st.dataframe(ordered_data[selected_columns])
        except Exception as e:
            st.error(f"An error occurred while processing the uploaded file: {e}")
    else:
        st.info("Please upload an Excel file with two sheets: 'StateRanks' and 'ProgramRanks'.")
