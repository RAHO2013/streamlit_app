import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def display_general_analysis():
    st.title("General Data Analysis Dashboard")

    # Step 1: File Upload
    uploaded_file = st.file_uploader("Upload your file (CSV or Excel):", type=['csv', 'xlsx'])

    if not uploaded_file:
        st.info("Please upload a file to get started.")
        return

    # Step 2: Load the File
    try:
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        st.success("File uploaded successfully!")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return

    # Display the dataset
    st.write("### Uploaded Dataset")
    st.dataframe(data)

    # Tabs for Analysis, Pivot Table, and Frequency Table
    tab1, tab2, tab3 = st.tabs(["Graph Analysis", "Pivot Table", "Grouped Frequency Table"])

    # Tab 1: Graph Analysis
    with tab1:
        st.write("### Select Graph Type and Plot")
        numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
        categorical_columns = data.select_dtypes(include=['object', 'category']).columns.tolist()
        all_columns = data.columns.tolist()

        if not numeric_columns:
            st.warning("No numeric columns detected. Plotting might not work.")
            return

        # User Selection for Filters
        with st.expander("Select Filters"):
            filters = {}
            for col in all_columns:
                unique_values = data[col].unique()
                if len(unique_values) <= 50:
                    selected_values = st.multiselect(f"Filter {col}:", options=unique_values, default=unique_values)
                    if selected_values and len(selected_values) < len(unique_values):
                        filters[col] = selected_values

        # Apply Filters
        filtered_data = data.copy()
        for col, selected_values in filters.items():
            filtered_data = filtered_data[filtered_data[col].isin(selected_values)]

        # Select Graph Type
        graph_type = st.selectbox("Select Graph Type:", options=["Scatter Plot", "Line Plot", "Bar Chart", "Histogram"])
        x_axis = st.selectbox("Select X-Axis:", options=all_columns)
        y_axis = st.selectbox("Select Y-Axis:", options=numeric_columns if numeric_columns else [None], index=0)

        # Generate Selected Graph
        if graph_type == "Scatter Plot":
            hue = st.selectbox("Select Hue (Color):", options=all_columns + [None], index=len(all_columns))
            style = st.selectbox("Select Style (Shape):", options=all_columns + [None], index=len(all_columns))

            fig, ax = plt.subplots(figsize=(12, 8))
            sns.scatterplot(
                data=filtered_data,
                x=x_axis,
                y=y_axis,
                hue=hue if hue else None,
                style=style if style else None,
                ax=ax,
                s=50  # Marker size
            )
            st.pyplot(fig)

        elif graph_type == "Line Plot":
            fig, ax = plt.subplots(figsize=(12, 8))
            sns.lineplot(data=filtered_data, x=x_axis, y=y_axis, ax=ax)
            st.pyplot(fig)

        elif graph_type == "Bar Chart":
            fig, ax = plt.subplots(figsize=(12, 8))
            sns.barplot(data=filtered_data, x=x_axis, y=y_axis, ax=ax)
            st.pyplot(fig)

        elif graph_type == "Histogram":
            fig, ax = plt.subplots(figsize=(12, 8))
            sns.histplot(data=filtered_data, x=x_axis, bins=20, kde=True, ax=ax)
            st.pyplot(fig)

    # Tab 2: Pivot Table
    with tab2:
        st.write("### Create a Pivot Table")

        rows = st.multiselect("Select Rows:", options=data.columns, default=[data.columns[0]])
        columns = st.multiselect("Select Columns:", options=data.columns, default=[])
        values = st.multiselect("Select Values (Numeric):", options=numeric_columns, default=numeric_columns[:1])
        aggfunc = st.selectbox("Select Aggregation Function:", options=["sum", "mean", "max", "min", "count"], index=0)

        if rows and values:
            pivot_table = pd.pivot_table(
                data,
                values=values,
                index=rows,
                columns=columns if columns else None,
                aggfunc=aggfunc,
                fill_value=0
            )
            st.write("### Generated Pivot Table")
            st.dataframe(pivot_table)

            pivot_csv = pivot_table.to_csv()
            st.download_button(
                label="Download Pivot Table as CSV",
                data=pivot_csv,
                file_name="pivot_table.csv",
                mime="text/csv"
            )

    # Tab 3: Grouped Frequency Table
    with tab3:
        st.write("### Create a Grouped Frequency Table")

        # Multiple column selection for grouping
        group_columns = st.multiselect("Select Rows for Grouping:", options=data.columns, default=[])

        if group_columns:
            # Handle numeric columns by creating bins
            binned_data = data.copy()
            bin_size = st.slider("Select Bin Size for Numeric Columns (if any):", min_value=1, max_value=50, value=10)
            for col in group_columns:
                if pd.api.types.is_numeric_dtype(data[col]):
                    binned_data[col] = pd.cut(
                        data[col],
                        bins=range(int(data[col].min()), int(data[col].max()) + bin_size, bin_size),
                        right=False
                    )

            # Group by selected columns
            grouped_data = binned_data.groupby(group_columns).size().reset_index(name='Count')
            grouped_data['Percentage'] = (grouped_data['Count'] / grouped_data['Count'].sum() * 100).round(2).astype(str) + '%'

            # Display Grouped Frequency Table
            st.write("### Grouped Frequency Table")
            st.dataframe(grouped_data)

            # Export Frequency Table
            frequency_csv = grouped_data.to_csv(index=False)
            st.download_button(
                label="Download Frequency Table as CSV",
                data=frequency_csv,
                file_name="grouped_frequency_table.csv",
                mime="text/csv"
            )

            # Visualize Grouped Data
            st.write("### Visualize Grouped Data")
            graph_type = st.selectbox("Select Graph Type for Frequency Data:", options=["Bar Chart", "Pie Chart"])

            if graph_type == "Bar Chart":
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(data=grouped_data, x=group_columns[0], y='Count', ax=ax)
                ax.set_title("Bar Chart of Grouped Data", fontsize=16)
                ax.set_xlabel(group_columns[0], fontsize=12)
                ax.set_ylabel("Count", fontsize=12)
                st.pyplot(fig)

            elif graph_type == "Pie Chart":
                if len(group_columns) == 1:
                    fig, ax = plt.subplots(figsize=(8, 8))
                    ax.pie(grouped_data['Count'], labels=grouped_data[group_columns[0]], autopct='%1.1f%%', startangle=90)
                    ax.set_title("Pie Chart of Grouped Data", fontsize=16)
                    st.pyplot(fig)
                else:
                    st.warning("Pie Chart only supports a single group column. Please select one column for grouping.")

        else:
            st.warning("Please select at least one column to group by.")


# Run the function
if __name__ == "__main__":
    display_general_analysis()
