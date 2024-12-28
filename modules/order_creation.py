import streamlit as st
import pandas as pd
import os  # Import os for file existence checks

def display_order_creation():
    st.title("Order Creation Dashboard")

    # Load MASTER EXCEL file
    MASTER_FILE = "data/MASTER EXCEL.xlsx"
    if not os.path.exists(MASTER_FILE):  # Use os.path.exists instead of st.file_exists
        st.error(f"Master file '{MASTER_FILE}' is missing in the project folder!")
        return

    master_sheet = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')

    # Normalize `State`, `Program`, and `TYPE` columns
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
            rank_tab1, rank_tab2 = st.tabs(["Assign Rankings", "View Entered Rankings"])

            with rank_tab1:
                state_ranking = {}
                ranked_data = []

                for state in unique_states:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        rank = st.selectbox(
                            state,
                            options=[0] + [i for i in range(1, len(unique_states) + 1) if i not in state_ranking.values()],
                            key=f"state_{state}",
                        )
                    if rank > 0:
                        state_ranking[state] = rank
                        ranked_data.append({"State": state, "Rank": rank})

            with rank_tab2:
                if ranked_data:
                    state_df = pd.DataFrame(ranked_data).sort_values("Rank")
                    state_df.index = range(1, len(state_df) + 1)
                    st.write("### Entered State Rankings")
                    st.dataframe(state_df)
                else:
                    st.write("No states ranked yet. Please assign ranks to display the table.")

        # Generate Ordered Table (Additional tabs and logic go here if required)
