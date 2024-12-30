import streamlit as st
import pandas as pd
import os

def display_master_data():
    st.title("Master Data Overview")

    MASTER_FILE = "data/MASTER EXCEL.xlsx"

    @st.cache_data
    def load_master_file():
        if os.path.exists(MASTER_FILE):
            data = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')
            return data
        else:
            st.error("Master file not found.")
            return None

    master_sheet = load_master_file()

    if master_sheet is not None:
        # Adjust the index to start from 1
        master_sheet.index = master_sheet.index + 1

        # Allow the user to reorder columns with a unique key
        all_columns = master_sheet.columns.tolist()
        reordered_columns = st.multiselect(
            "Reorder columns:",
            options=all_columns,
            default=all_columns,
            key=f"reorder_columns_{st.session_state.get('page', 'master_data')}"  # Unique key per session state
        )

        if reordered_columns:
            reordered_data = master_sheet[reordered_columns]

            # Display the reordered table
            numeric_columns = reordered_data.select_dtypes(include=['int64', 'float64']).columns
            st.write("### Reordered Master Sheet")
            st.dataframe(reordered_data.style.format({col: "{:.0f}" for col in numeric_columns}))
        else:
            st.warning("Please select at least one column to display.")

# Call the function to display the data
display_master_data()
