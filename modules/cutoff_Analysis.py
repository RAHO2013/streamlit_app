import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import textwrap
import plotly.express as px

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
        "Interactive Plotly Graphs"
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

        # Create scatter plot
        fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
        sns.scatterplot(
            data=filtered_data,
            x='NEET AIR',
            y=y_axis_column,
            hue=hue_column,
            style=style_column,
            ax=ax,
            s=50
        )
        ax.grid(visible=True, which='both', axis='x', linestyle='--', linewidth=0.7, alpha=0.5)
        ax.set_title(f"Filtered Comparison: NEET AIR vs {y_axis_column}", fontsize=14)
        ax.set_xlabel('NEET AIR', fontsize=14)
        ax.set_ylabel(y_axis_column, fontsize=14)
        ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)
        st.pyplot(fig)

    # Tab 4: Interactive Plotly Graphs
    with tab4:
        # Plotly Scatter Plot
        st.write("#### Plotly Scatter Plot: Filtered Data")
        fig = px.scatter(
            filtered_data,
            x='NEET AIR',
            y=y_axis_column,
            color=hue_column,
            symbol=style_column,
            title=f"Filtered Comparison: NEET AIR vs {y_axis_column}",
            hover_data=filtered_data.columns
        )
        fig.update_traces(marker=dict(size=10))
        fig.update_layout(xaxis_title="NEET AIR", yaxis_title=y_axis_column)
        st.plotly_chart(fig)

# Call the function to display the dashboard
display_cutoff_Analysis()
