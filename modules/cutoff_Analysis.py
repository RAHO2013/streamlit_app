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

    # Combine R1 and R2 remarks for heatmap analysis
    combined_remarks_analysis = aiqr2_data.groupby(['R1 Remarks', 'R2 Final Remarks']).size().reset_index(name='Count')

    # Tabs for analysis
    tab1, tab2, tab3, tab4 = st.tabs([
        "AIR Allotment Analysis",
        "Course and Category Analysis",
        "Remarks Analysis",
        "Comparison Analysis"
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

        # Format NEET AIR column for display without commas
        formatted_data = filtered_air_data.copy()
        formatted_data['NEET AIR'] = formatted_data['NEET AIR'].astype(str)
        st.dataframe(formatted_data)

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

        # Convert NEET AIR values to integers for display
        pivot_table = pivot_table.applymap(lambda x: int(x) if pd.notnull(x) and x != 0 else x)

        st.write(f"### Pivot Table: Maximum NEET AIR by Course and Category (Quota: {quota_filter})")
        st.dataframe(pivot_table)

    # Tab 3: Remarks Analysis
    with tab3:
        st.write("### Remarks Analysis")

        # Display combined remarks table
        st.write("#### Combined R1 and R2 Remarks Analysis Table")
        st.dataframe(combined_remarks_analysis)

        # Heatmap for combined remarks
        st.write("#### Heatmap: R1 to R2 Remarks Transition")
        pivot_data = combined_remarks_analysis.pivot(
            index='R1 Remarks', columns='R2 Final Remarks', values='Count'
        ).fillna(0)

        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(pivot_data, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5, ax=ax)
        ax.set_title("R1 to R2 Remarks Transition Heatmap", fontsize=16)
        ax.set_xlabel("R2 Final Remarks", fontsize=12)
        ax.set_ylabel("R1 Remarks", fontsize=12)
        st.pyplot(fig)

        # Export functionality
        st.write("#### Export Analysis Data")
        export_data = combined_remarks_analysis.to_csv(index=False)
        st.download_button(
            label="Download Combined Remarks Data as CSV",
            data=export_data,
            file_name="combined_remarks_analysis.csv",
            mime="text/csv"
        )

    # Tab 4: Comparison Analysis
    with tab4:
        st.write("### Comparison Analysis")

        # Add comparison filters
        st.sidebar.write("### Comparison Filters")
        compare_r1 = st.sidebar.multiselect("Select R1 Remarks to Compare:", aiqr2_data['R1 Remarks'].unique())
        compare_r2 = st.sidebar.multiselect("Select R2 Remarks to Compare:", aiqr2_data['R2 Final Remarks'].unique())
        compare_r1_quota = st.sidebar.multiselect("Select R1 Allotted Quota:", aiqr2_data['R1 Allotted Quota'].unique())
        compare_r1_course = st.sidebar.multiselect("Select R1 Course:", aiqr2_data['R1 Course'].unique())
        compare_r2_quota = st.sidebar.multiselect("Select R2 Final Allotted Quota:", aiqr2_data['R2 Final Allotted Quota'].unique())
        compare_r2_course = st.sidebar.multiselect("Select R2 Final Course:", aiqr2_data['R2 Final Course'].unique())
        compare_r2_category = st.sidebar.multiselect("Select R2 Final Alloted Category:", aiqr2_data['R2 Final Alloted Category'].unique())

        if any([compare_r1, compare_r2, compare_r1_quota, compare_r1_course, compare_r2_quota, compare_r2_course, compare_r2_category]):
            filtered_comparison_data = aiqr2_data[
                (aiqr2_data['R1 Remarks'].isin(compare_r1) if compare_r1 else True) &
                (aiqr2_data['R2 Final Remarks'].isin(compare_r2) if compare_r2 else True) &
                (aiqr2_data['R1 Allotted Quota'].isin(compare_r1_quota) if compare_r1_quota else True) &
                (aiqr2_data['R1 Course'].isin(compare_r1_course) if compare_r1_course else True) &
                (aiqr2_data['R2 Final Allotted Quota'].isin(compare_r2_quota) if compare_r2_quota else True) &
                (aiqr2_data['R2 Final Course'].isin(compare_r2_course) if compare_r2_course else True) &
                (aiqr2_data['R2 Final Alloted Category'].isin(compare_r2_category) if compare_r2_category else True)
            ]
            st.dataframe(filtered_comparison_data)

# Call the function to display the dashboard
display_cutoff_Analysis()
