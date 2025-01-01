import streamlit as st
import pandas as pd
import os
import seaborn as sns
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
    aiqr2_data['NEET AIR'] = pd.to_numeric(aiqr2_data['NEET AIR'], errors='coerce')
    aiqr2_data['NEET AIR'] = aiqr2_data['NEET AIR'].apply(lambda x: int(x) if pd.notnull(x) else '-')

    # Collapse AFMS-related remarks
    aiqr2_data['R2 Final Remarks'] = aiqr2_data['R2 Final Remarks'].replace(
        to_replace=r'Fresh Allotted in 2nd Round\( AFMS Rank : \d+ \)',
        value='Fresh Allotted in 2nd Round (AFMS)',
        regex=True
    )

    # Replace '-' in R1 Remarks with 'R1 Not Allotted'
    aiqr2_data['R1 Remarks'] = aiqr2_data['R1 Remarks'].replace('-', 'R1 Not Allotted')

    # Tabs for analysis
    tab1, tab2, tab3, tab4 = st.tabs([
        "Course and Category Analysis",
        "Remarks Analysis",
        "Comparison Analysis",
        "Scatter Plot"
    ])

    # Tab 3: Comparison Analysis
    with tab3:
        st.write("### Comparison Analysis")

        # Create 3-by-row layout for filters
        all_columns = aiqr2_data.columns.tolist()
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)
        col7, col8, col9 = st.columns(3)

        filtered_data = aiqr2_data.copy()

        with col1:
            selected_col1 = st.selectbox("Select Column 1 for Filter:", all_columns, key="filter1")
            values_col1 = st.multiselect(f"Filter values for {selected_col1}:", aiqr2_data[selected_col1].unique(), key="multiselect1")
            if values_col1:
                filtered_data = filtered_data[filtered_data[selected_col1].isin(values_col1)]

        with col2:
            selected_col2 = st.selectbox("Select Column 2 for Filter:", all_columns, key="filter2")
            values_col2 = st.multiselect(f"Filter values for {selected_col2}:", aiqr2_data[selected_col2].unique(), key="multiselect2")
            if values_col2:
                filtered_data = filtered_data[filtered_data[selected_col2].isin(values_col2)]

        with col3:
            selected_col3 = st.selectbox("Select Column 3 for Filter:", all_columns, key="filter3")
            values_col3 = st.multiselect(f"Filter values for {selected_col3}:", aiqr2_data[selected_col3].unique(), key="multiselect3")
            if values_col3:
                filtered_data = filtered_data[filtered_data[selected_col3].isin(values_col3)]

        with col4:
            selected_col4 = st.selectbox("Select Column 4 for Filter:", all_columns, key="filter4")
            values_col4 = st.multiselect(f"Filter values for {selected_col4}:", aiqr2_data[selected_col4].unique(), key="multiselect4")
            if values_col4:
                filtered_data = filtered_data[filtered_data[selected_col4].isin(values_col4)]

        with col5:
            selected_col5 = st.selectbox("Select Column 5 for Filter:", all_columns, key="filter5")
            values_col5 = st.multiselect(f"Filter values for {selected_col5}:", aiqr2_data[selected_col5].unique(), key="multiselect5")
            if values_col5:
                filtered_data = filtered_data[filtered_data[selected_col5].isin(values_col5)]

        with col6:
            selected_col6 = st.selectbox("Select Column 6 for Filter:", all_columns, key="filter6")
            values_col6 = st.multiselect(f"Filter values for {selected_col6}:", aiqr2_data[selected_col6].unique(), key="multiselect6")
            if values_col6:
                filtered_data = filtered_data[filtered_data[selected_col6].isin(values_col6)]

        with col7:
            selected_col7 = st.selectbox("Select Column 7 for Filter:", all_columns, key="filter7")
            values_col7 = st.multiselect(f"Filter values for {selected_col7}:", aiqr2_data[selected_col7].unique(), key="multiselect7")
            if values_col7:
                filtered_data = filtered_data[filtered_data[selected_col7].isin(values_col7)]

        with col8:
            selected_col8 = st.selectbox("Select Column 8 for Filter:", all_columns, key="filter8")
            values_col8 = st.multiselect(f"Filter values for {selected_col8}:", aiqr2_data[selected_col8].unique(), key="multiselect8")
            if values_col8:
                filtered_data = filtered_data[filtered_data[selected_col8].isin(values_col8)]

        with col9:
            selected_col9 = st.selectbox("Select Column 9 for Filter:", all_columns, key="filter9")
            values_col9 = st.multiselect(f"Filter values for {selected_col9}:", aiqr2_data[selected_col9].unique(), key="multiselect9")
            if values_col9:
                filtered_data = filtered_data[filtered_data[selected_col9].isin(values_col9)]

        # Display filtered data
        st.write("### Filtered Data")
        st.dataframe(filtered_data)

    # Tab 4: Scatter Plot
    with tab4:
        st.write("### Scatter Plot")

        # Allow user to select columns for scatter plot
        scatter_x = st.selectbox("Select X-axis:", all_columns, key="scatter_x")
        scatter_y = st.selectbox("Select Y-axis:", all_columns, key="scatter_y")
        scatter_hue = st.selectbox("Select Hue (Optional):", [None] + all_columns, key="scatter_hue")

        # Scatter Plot
        st.write("### Scatter Plot")
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.scatterplot(
            data=filtered_data,
            x=scatter_x,
            y=scatter_y,
            hue=scatter_hue if scatter_hue else None,
            ax=ax
        )
        ax.set_title(f"Scatter Plot: {scatter_x} vs {scatter_y}", fontsize=16)
        ax.set_xlabel(scatter_x, fontsize=14)
        ax.set_ylabel(scatter_y, fontsize=14)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Move legend outside
        st.pyplot(fig)


# Call the function to display the dashboard
display_cutoff_Analysis()
