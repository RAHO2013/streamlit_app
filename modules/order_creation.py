import streamlit as st
import pandas as pd

def display_order_creation():
    st.title("Order Creation Dashboard")

    # Load MASTER EXCEL file
    MASTER_FILE = "data/MASTER EXCEL.xlsx"
    if not st.file_exists(MASTER_FILE):
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

        # Ranking Programs by TYPE
        with tab2:
            st.subheader("Rank Programs by Type")
            rank_tab1, rank_tab2 = st.tabs(["Assign Rankings", "View Entered Rankings"])

            with rank_tab1:
                all_programs = master_sheet[['TYPE', 'Program']].drop_duplicates()
                program_ranking = {}
                ranked_data = []

                for _, row in all_programs.iterrows():
                    program = row['Program']
                    program_type = row['TYPE']
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        rank = st.selectbox(
                            f"{program} ({program_type})",
                            options=[0] + [i for i in range(1, len(all_programs) + 1) if i not in program_ranking.values()],
                            key=f"program_{program}_{program_type}",
                        )
                    if rank > 0:
                        program_ranking[(program, program_type)] = rank
                        ranked_data.append({"Program": program, "TYPE": program_type, "Rank": rank})

            with rank_tab2:
                if ranked_data:
                    program_df = pd.DataFrame(ranked_data).sort_values("Rank")
                    program_df.index = range(1, len(program_df) + 1)
                    st.write("### Entered Program Rankings")
                    st.dataframe(program_df)
                else:
                    st.write("No programs ranked yet. Please assign ranks to display the table.")

        # Generate Ordered Table
        with tab3:
            st.subheader("Generate Order by Rankings")
            with st.expander("Select Columns to Display", expanded=True):
                default_columns = ['MAIN CODE', 'Program', 'TYPE', 'State', 'College Name', 'Program Rank', 'State Rank', 'Order Number']
                selected_columns = st.multiselect(
                    "Select columns:",
                    list(master_sheet.columns) + ['State Rank', 'Program Rank', 'Order Number'],
                    default=default_columns
                )

            if st.button("Generate Order Table"):
                master_sheet['State Rank'] = master_sheet['State'].map(state_ranking).fillna(0)
                master_sheet['Program Rank'] = master_sheet.apply(
                    lambda x: program_ranking.get((x['Program'], x['TYPE']), 0), axis=1
                )

                ordered_data = master_sheet.query("`State Rank` > 0 and `Program Rank` > 0").sort_values(
                    by=['Program Rank', 'State Rank']
                ).reset_index(drop=True)
                ordered_data['Order Number'] = range(1, len(ordered_data) + 1)

                if selected_columns:
                    st.write("### Ordered Table")
                    ordered_data.index = range(1, len(ordered_data) + 1)
                    st.dataframe(ordered_data[selected_columns])
                else:
                    st.warning("Please select at least one column to display the table.")
