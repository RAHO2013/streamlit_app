import streamlit as st
from utils.utils import load_master_sheet


st.title("Order Creation Dashboard")

try:
    master_sheet = load_master_sheet()
    
    # Ensure necessary columns exist
    if {'State', 'Program', 'College Name', 'TYPE'}.issubset(master_sheet.columns):
        unique_states = master_sheet['State'].unique()

        # Tabs for Ranking and Orders
        tab1, tab2, tab3 = st.tabs(["Ranking States", "Ranking Programs by Type", "Generate Order Table"])

        # Ranking States
        with tab1:
            st.subheader("Rank States")
            state_ranking = {}
            for state in unique_states:
                rank = st.number_input(f"Rank for {state}", min_value=0, value=0)
                if rank > 0:
                    state_ranking[state] = rank
            
            st.write("State Rankings:")
            st.write(state_ranking)

        # Ranking Programs by TYPE
        with tab2:
            st.subheader("Rank Programs by Type")
            all_programs = master_sheet[['TYPE', 'Program']].drop_duplicates()
            program_ranking = {}
            for _, row in all_programs.iterrows():
                program, program_type = row['Program'], row['TYPE']
                rank = st.number_input(f"Rank for {program} ({program_type})", min_value=0, value=0)
                if rank > 0:
                    program_ranking[(program, program_type)] = rank
            
            st.write("Program Rankings:")
            st.write(program_ranking)

        # Generate Ordered Table
        with tab3:
            st.subheader("Generate Order Table")
            master_sheet['State Rank'] = master_sheet['State'].map(state_ranking).fillna(0)
            master_sheet['Program Rank'] = master_sheet.apply(
                lambda x: program_ranking.get((x['Program'], x['TYPE']), 0), axis=1
            )
            ordered_data = master_sheet.query("State Rank > 0 and Program Rank > 0").sort_values(
                by=['Program Rank', 'State Rank']
            ).reset_index(drop=True)
            ordered_data['Order Number'] = range(1, len(ordered_data) + 1)
            st.dataframe(ordered_data)

except Exception as e:
    st.error(f"Error: {e}")
