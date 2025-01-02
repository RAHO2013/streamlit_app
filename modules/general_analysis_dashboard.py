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

    # Tabs for Frequency Table and Graph
    tab1, tab2 = st.tabs(["Grouped Frequency Table", "Graph Visualization"])

    # Tab 1: Grouped Frequency Table
    with tab1:
        st.write("### Create a Grouped Frequency Table")

        # Select Column for Grouping
        group_column = st.selectbox("Select a Column to Group By:", options=data.columns)

        # Check if the column is numeric or categorical
        if pd.api.types.is_numeric_dtype(data[group_column]):
            # Numeric Column: Group into Ranges
            bin_size = st.slider("Select Bin Size:", min_value=1, max_value=50, value=10)
            data['Bins'] = pd.cut(data[group_column], 
                                  bins=range(int(data[group_column].min()), 
                                             int(data[group_column].max()) + bin_size, 
                                             bin_size), 
                                  right=False)
            grouped_data = data.groupby('Bins').size().reset_index(name='Count')
            grouped_data['Percentage'] = (grouped_data['Count'] / grouped_data['Count'].sum()) * 100
        else:
            # Categorical Column: Count occurrences
            grouped_data = data[group_column].value_counts().reset_index()
            grouped_data.columns = [group_column, 'Count']
            grouped_data['Percentage'] = (grouped_data['Count'] / grouped_data['Count'].sum()) * 100

        # Display Grouped Frequency Table
        st.write("### Grouped Frequency Table")
        st.dataframe(grouped_data)

        # Export Frequency Table
        st.write("### Download Frequency Table")
        frequency_csv = grouped_data.to_csv(index=False)
        st.download_button(
            label="Download Frequency Table as CSV",
            data=frequency_csv,
            file_name="grouped_frequency_table.csv",
            mime="text/csv"
        )

    # Tab 2: Graph Visualization
    with tab2:
        st.write("### Visualize Grouped Data")
        graph_type = st.selectbox("Select Graph Type:", options=["Bar Chart", "Pie Chart"])

        if graph_type == "Bar Chart":
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=grouped_data, x=grouped_data.columns[0], y='Count', ax=ax)
            ax.set_title("Bar Chart of Grouped Data", fontsize=16)
            ax.set_xlabel(grouped_data.columns[0], fontsize=12)
            ax.set_ylabel("Count", fontsize=12)
            st.pyplot(fig)

        elif graph_type == "Pie Chart":
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.pie(grouped_data['Count'], labels=grouped_data[grouped_data.columns[0]], autopct='%1.1f%%', startangle=90)
            ax.set_title("Pie Chart of Grouped Data", fontsize=16)
            st.pyplot(fig)


# Run the function
if __name__ == "__main__":
    display_general_analysis()
