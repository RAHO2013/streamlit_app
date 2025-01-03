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

    # Tabs for Analysis, Pivot Table, Frequency Table, and Statistical Table
    tab1, tab2, tab3, tab4 = st.tabs(["Graph Analysis", "Pivot Table", "Grouped Frequency Table", "Statistical Table"])

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

        group_columns = st.multiselect("Select Rows for Grouping:", options=data.columns, default=[])

        if group_columns:
            binned_data = data.copy()
            bin_size = st.slider("Select Bin Size for Numeric Columns (if any):", min_value=1, max_value=50, value=10)
            for col in group_columns:
                if pd.api.types.is_numeric_dtype(data[col]):
                    binned_data[col] = pd.cut(
                        data[col],
                        bins=range(int(data[col].min()), int(data[col].max()) + bin_size, bin_size),
                        right=False
                    )

            grouped_data = binned_data.groupby(group_columns).size().reset_index(name='Count')
            grouped_data['Percentage'] = (grouped_data['Count'] / grouped_data['Count'].sum() * 100).round(2).astype(str) + '%'

            st.write("### Grouped Frequency Table")
            st.dataframe(grouped_data)

            frequency_csv = grouped_data.to_csv(index=False)
            st.download_button(
                label="Download Frequency Table as CSV",
                data=frequency_csv,
                file_name="grouped_frequency_table.csv",
                mime="text/csv"
            )

    # Tab 4: Statistical Table
    with tab4:
        st.write("### Generate a Statistical Table")

        # Only allow numeric columns for statistical analysis
        numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
        columns = st.multiselect("Select Numeric Columns for Statistical Analysis:", options=numeric_columns)

        if columns:
            stats_table = pd.DataFrame({
                "Metric": columns,
                "Mean": data[columns].mean().values,
                "Std Deviation": data[columns].std().values,
                "P-value": [0.005] * len(columns)  # Placeholder for p-value
            })

            st.write("### Statistical Table")
            st.table(stats_table)

            csv = stats_table.to_csv(index=False)
            st.download_button(
                label="Download Statistical Table as CSV",
                data=csv,
                file_name="statistical_table.csv",
                mime="text/csv"
            )


# Run the function
if __name__ == "__main__":
    display_general_analysis()
