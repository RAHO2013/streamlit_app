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
        "Scatter Plot Dashboard"
    ])

    # Tab 1: Course and Category Analysis
    with tab1:
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

    # Tab 2: Remarks Analysis
    with tab2:
        st.write("### Remarks Analysis")

        # Display combined remarks table
        combined_remarks_analysis = aiqr2_data.groupby(['R1 Remarks', 'R2 Final Remarks']).size().reset_index(name='Count')
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

    # Tab 3: Comparison Analysis
    with tab3:
        st.write("### Comparison Analysis")

        # Create filters
        col1, col2, col3 = st.columns(3)

        filtered_data = aiqr2_data.copy()

        with col1:
            compare_r1 = st.multiselect(
                "Select R1 Remarks to Compare:",
                options=aiqr2_data['R1 Remarks'].unique(),
                default=None
            )
            if compare_r1:
                filtered_data = filtered_data[filtered_data['R1 Remarks'].isin(compare_r1)]

        with col2:
            compare_r2 = st.multiselect(
                "Select R2 Remarks to Compare:",
                options=aiqr2_data['R2 Final Remarks'].unique(),
                default=None
            )
            if compare_r2:
                filtered_data = filtered_data[filtered_data['R2 Final Remarks'].isin(compare_r2)]

        with col3:
            air_range = st.slider(
                "Select AIQ Rank Range:",
                min_value=int(aiqr2_data['NEET AIR'].min()),
                max_value=int(aiqr2_data['NEET AIR'].max()),
                value=(int(aiqr2_data['NEET AIR'].min()), int(aiqr2_data['NEET AIR'].max()))
            )
            filtered_data = filtered_data[(filtered_data['NEET AIR'] >= air_range[0]) & (filtered_data['NEET AIR'] <= air_range[1])]

        # Display filtered data
        st.write("### Filtered Data")
        st.dataframe(filtered_data)

    # Tab 4: Scatter Plot Dashboard
    with tab4:
        st.write("### Scatter Plot Dashboard")

        # Create filters
        st.write("#### Select Filters for the Scatter Plot")
        scatter_filters = {}
        for column in aiqr2_data.columns:
            unique_values = aiqr2_data[column].dropna().unique()
            selected_values = st.multiselect(f"Filter {column}:", unique_values, default=unique_values)
            scatter_filters[column] = selected_values

        # Apply filters
        scatter_data = aiqr2_data.copy()
        for col, values in scatter_filters.items():
            scatter_data = scatter_data[scatter_data[col].isin(values)]

        # Scatter plot settings
        st.write("#### Customize Scatter Plot")
        scatter_x = st.selectbox("Select X-axis:", aiqr2_data.columns)
        scatter_y = st.selectbox("Select Y-axis:", aiqr2_data.columns)
        scatter_hue = st.selectbox("Select Hue (Optional):", [None] + list(aiqr2_data.columns))

        # Scatter plot visualization
        st.write("### Scatter Plot")
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.scatterplot(
            data=scatter_data,
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
