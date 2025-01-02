import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# General Analysis Functionality
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

    # Step 3: Detect Columns Dynamically
    numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
    categorical_columns = data.select_dtypes(include=['object', 'category']).columns.tolist()
    all_columns = data.columns.tolist()

    if not numeric_columns:
        st.warning("No numeric columns detected. Scatter plot might not work.")
        return

    # Step 4: User Selection for Filters and Plot
    st.write("### Filter and Customize Your Plot")
    with st.expander("Select Filters"):
        filters = {}
        for col in all_columns:
            unique_values = data[col].unique()
            if len(unique_values) <= 50:  # Limit to columns with fewer unique values for dropdowns
                selected_values = st.multiselect(f"Filter {col}:", options=unique_values, default=unique_values)
                if selected_values and len(selected_values) < len(unique_values):
                    filters[col] = selected_values

    # Apply Filters
    filtered_data = data.copy()
    for col, selected_values in filters.items():
        filtered_data = filtered_data[filtered_data[col].isin(selected_values)]

    # Step 5: Plot Customization Options
    st.write("### Customize Your Scatter Plot")
    x_axis = st.selectbox("Select X-Axis:", options=numeric_columns)
    y_axis = st.selectbox("Select Y-Axis:", options=numeric_columns)
    hue = st.selectbox("Select Hue (Color):", options=all_columns + [None], index=len(all_columns))
    style = st.selectbox("Select Style (Shape):", options=all_columns + [None], index=len(all_columns))

    # Step 6: Generate Scatter Plot
    st.write("### Scatter Plot")
    fig_width = st.slider("Adjust Figure Width:", min_value=8, max_value=30, value=12)
    fig_height = st.slider("Adjust Figure Height:", min_value=6, max_value=20, value=8)

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    sns.scatterplot(
        data=filtered_data,
        x=x_axis,
        y=y_axis,
        hue=hue if hue else None,
        style=style if style else None,
        ax=ax,
        s=50  # Marker size
    )

    # Add gridlines
    ax.grid(visible=True, which='both', axis='both', linestyle='--', linewidth=0.5, alpha=0.7)

    # Set titles and labels
    ax.set_title(f"{x_axis} vs {y_axis}", fontsize=16)
    ax.set_xlabel(x_axis, fontsize=12)
    ax.set_ylabel(y_axis, fontsize=12)

    # Adjust layout
    plt.tight_layout()
    st.pyplot(fig)

    # Step 7: Download Filtered Data
    st.write("### Download Filtered Data")
    filtered_csv = filtered_data.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=filtered_csv,
        file_name="filtered_data.csv",
        mime="text/csv"
    )

