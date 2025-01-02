import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import textwrap


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
    tab1, tab2, tab3 = st.tabs([
        "Course and Category Analysis",
        "Remarks Analysis",
        "Comparison Analysis"
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

        fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
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
        
        # Dynamic filtering
        filtered_data = aiqr2_data.copy()
        filter_columns = st.multiselect("Select Columns to Filter:", options=aiqr2_data.columns)

        # Display active filters
        active_filters = []
        for column in filter_columns:
            if aiqr2_data[column].dtype == 'object':
                unique_values = filtered_data[column].unique()
                selected_values = st.multiselect(f"Filter values in {column}:", options=unique_values)
                if selected_values:
                    filtered_data = filtered_data[filtered_data[column].isin(selected_values)]
                    active_filters.append(f"{column}: {', '.join(map(str, selected_values))}")
            elif pd.api.types.is_numeric_dtype(aiqr2_data[column]):
                min_val, max_val = st.slider(
                    f"Select range for {column}:",
                    min_value=float(filtered_data[column].min()),
                    max_value=float(filtered_data[column].max()),
                    value=(float(filtered_data[column].min()), float(filtered_data[column].max()))
                )
                filtered_data = filtered_data[(filtered_data[column] >= min_val) & (filtered_data[column] <= max_val)]
                active_filters.append(f"{column}: {min_val} to {max_val}")

        # Scatter plot customization
        st.write("### Customize Scatter Plot")
        y_axis_column = st.selectbox("Select Y-Axis:", options=aiqr2_data.columns, index=aiqr2_data.columns.get_loc('R2 Final Course'))
        hue_column = st.selectbox("Select Hue (Color):", options=aiqr2_data.columns, index=aiqr2_data.columns.get_loc('R2 Final Alloted Category'))
        style_column = st.selectbox("Select Style (Shape):", options=aiqr2_data.columns, index=aiqr2_data.columns.get_loc('R2 Final Allotted Quota'))

        # Function to wrap long text
        def wrap_text(text, width=40):
            return "\n".join(textwrap.wrap(text, width))

        # Shorten Y-axis labels (abbreviate if needed)
        filtered_data[y_axis_column] = filtered_data[y_axis_column].apply(
            lambda x: wrap_text(str(x), width=30)
        )

        # Define fig_width and calculate dynamic fig_height
        fig_width = 30  # Further increased width for the figure
        unique_y_values = filtered_data[y_axis_column].nunique()
        base_height = 3  # Base height for compact layout
        increment_per_label = 0.3  # Increment per label
        fig_height = max(base_height, base_height + unique_y_values * increment_per_label)

        # Create scatter plot with adjusted width and height
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=150)
        sns.scatterplot(
            data=filtered_data,
            x='NEET AIR',
            y=y_axis_column,
            hue=hue_column,
            style=style_column,
            ax=ax,
            s=50  # Marker size
        )

        # Add gridlines
        ax.grid(visible=True, which='both', axis='x', linestyle='--', linewidth=0.7, alpha=0.5)

        # Explicitly set X-axis limits (optional, adjust based on your data range)
        ax.set_xlim(left=0, right=140000)  # Increase X-axis range if needed

        # Let Matplotlib decide the best X-axis ticks
        ax.xaxis.set_major_locator(plt.MaxNLocator(nbins='auto', integer=True))

        # Update title and axis labels
        ax.set_title(
            f"Filtered Comparison: NEET AIR vs {wrap_text(y_axis_column, width=30)}",
            fontsize=14, loc='center'
        )
        ax.set_xlabel('NEET AIR', fontsize=14)
        ax.set_ylabel(y_axis_column, fontsize=14)

        # Place legend outside the chart
        ax.legend(
            title=hue_column,
            bbox_to_anchor=(1.2, 1),
            loc='upper left',
            borderaxespad=0.
        )

        # Adjust layout
        plt.tight_layout()

        st.pyplot(fig)

        # Display filters below the chart
        st.write("### Active Filters:")
        if active_filters:
            st.markdown("\n".join([f"- **{wrap_text(filter, 50)}**" for filter in active_filters]))
        else:
            st.write("No filters applied")


# Call the function to display the dashboard
display_cutoff_Analysis()
