import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

def display_cutoff_Analysis():
    st.title("NEET AIQ Analysis Dashboard")

    # Load the AIQR2 Excel file
    file_path = os.path.join('data', 'AIQR2.xlsx')

    if not os.path.exists(file_path):
        st.error("AIQR2 file is missing in the 'data/' folder!")
        return

    # Load the data
    try:
        aiqr2_data = pd.read_excel(file_path, sheet_name='Sheet1')
    except Exception as e:
        st.error(f"Error loading the AIQR2 data: {e}")
        return

    # Clean and prepare data
    aiqr2_data.fillna("-", inplace=True)

    # Ensure NEET AIR is numeric for proper sorting and calculations
    aiqr2_data['NEET AIR'] = pd.to_numeric(aiqr2_data['NEET AIR'].str.replace(',', ''), errors='coerce')

    # Tabs for analysis
    tab1, tab2, tab3 = st.tabs([
        "AIR Allotment Analysis",
        "Course and Category Analysis",
        "Remarks Analysis"
    ])

    # Tab 1: AIR Allotment Analysis
    with tab1:
        st.write("### AIR Allotment Analysis")

        air_range = st.slider("Select AIR Range:", 
                              int(aiqr2_data['NEET AIR'].min()), 
                              int(aiqr2_data['NEET AIR'].max()), 
                              (int(aiqr2_data['NEET AIR'].min()), int(aiqr2_data['NEET AIR'].max())))

        filtered_air_data = aiqr2_data[(aiqr2_data['NEET AIR'] >= air_range[0]) & (aiqr2_data['NEET AIR'] <= air_range[1])]
        st.write(f"### AIR Range: {air_range[0]} - {air_range[1]}")
        st.dataframe(filtered_air_data)

        # Graph
        fig, ax = plt.subplots()
        filtered_air_data['R1 Allotted Quota'].value_counts().plot(kind='bar', ax=ax)
        ax.set_title("Quota Distribution in Selected AIR Range")
        ax.set_xlabel("Quota")
        ax.set_ylabel("Count")
        st.pyplot(fig)

    # Tab 2: Course and Category Analysis
    with tab2:
        st.write("### Course and Category Analysis")

        # Dropdown filters
        quota_filter = st.selectbox("Select Quota for Filtering:", aiqr2_data['R2 Final Allotted Quota'].unique())
        filtered_data = aiqr2_data[aiqr2_data['R2 Final Allotted Quota'] == quota_filter]

        category_order = ["Open", "EWS", "OBC", "SC", "ST"]
        remaining_categories = [cat for cat in filtered_data['R2 Final Alloted Category'].unique() if cat not in category_order]
        category_order += remaining_categories

        # Create a pivot table for max NEET AIR by R2 Final Course and R2 Final Alloted Category
        pivot_table = filtered_data.pivot_table(
            values='NEET AIR', 
            index='R2 Final Course', 
            columns='R2 Final Alloted Category', 
            aggfunc='max', 
            fill_value=0
        )

        # Reorder columns to match the category order
        pivot_table = pivot_table[[col for col in category_order if col in pivot_table.columns]]

        st.write(f"### Pivot Table: Maximum NEET AIR by Course and Category (Quota: {quota_filter})")
        st.dataframe(pivot_table)

    # Tab 3: Remarks Analysis
    with tab3:
        st.write("### Remarks Analysis")

        remarks_selection = st.selectbox("Select Remarks Type:", ["R1 Remarks", "R2 Final Remarks"])
        remarks_counts = aiqr2_data[remarks_selection].value_counts()

        st.write(f"### {remarks_selection} Distribution")
        st.bar_chart(remarks_counts)

# Call the function to display the dashboard
display_cutoff_Analysis()
