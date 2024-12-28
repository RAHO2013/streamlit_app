import streamlit as st
import pandas as pd
import os

def display_order_creation():
    st.title("Order Creation Dashboard")

    # Path to the master file
    MASTER_FILE = os.path.join('data', 'MASTER EXCEL.xlsx')

    # Load MASTER EXCEL file
    if not os.path.exists(MASTER_FILE):
        st.error(f"Master file '{MASTER_FILE}' is missing in the 'data/' folder!")
        return

    master_sheet = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')

    # Normalize columns
    master_sheet['State'] = master_sheet['State'].str.strip().str.upper()
    master_sheet['Program'] = master_sheet['Program'].str.strip().str.upper()
    master_sheet['TYPE'] = master_sheet['TYPE'].astype(str).str.strip().str.upper()

    # Ensure necessary columns exist
    if {'State', 'Program', 'College Name', 'TYPE'}.issubset(master_sheet.columns):
        unique_states = master_sheet['State'].unique()

        # Tabs for Ranking and Orders
        tab1, tab2, tab3 = st.tabs([
            "Ranking States",
            "Ranking Programs by Type",
            "Generate Order Table"
        ])

        # Ranking States
        with tab1:
            st.subheader("Rank States")
            state_ranking = {}
            for state in unique_states:
                rank = st.number_input(f"Rank for {state}", min_value=0, value=0)
                if rank > 0:
                    state_ranking[state] = rank
            st.write(state_ranking)

        # Ranking Programs by Type
        with tab2:
            st.subheader("Rank Programs by Type")
            all_programs = master_sheet[['TYPE', 'Program']].drop_duplicates()
            program_ranking = {}
            for _, row in all_programs.iterrows():
                program, program_type = row['Program'], row['TYPE']
                rank = st.number_input(f"Rank for {program} ({program_type})", min_value=0, value=0)
                if rank > 0:
                    program_ranking[(program, program_type)] = rank
            st.write(program_ranking)

        # Generate Ordered Table
        with tab3:
            st.subheader("Generate Order Table")
            # Logic for generating and displaying the order table
            st.write("Order creation logic goes here.")
