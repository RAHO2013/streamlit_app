import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

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
        "Advanced Analytics"
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

        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        with col1:
            compare_r1 = st.multiselect(
                "Select R1 Remarks to Compare:",
                options=aiqr2_data['R1 Remarks'].unique(),
                default=None
            )

        filtered_data = aiqr2_data[aiqr2_data['R1 Remarks'].isin(compare_r1)] if compare_r1 else aiqr2_data

        with col2:
            compare_r2 = st.multiselect(
                "Select R2 Remarks to Compare:",
                options=filtered_data['R2 Final Remarks'].unique(),
                default=None
            )
            filtered_data = filtered_data[filtered_data['R2 Final Remarks'].isin(compare_r2)] if compare_r2 else filtered_data

        with col3:
            compare_r1_quota = st.multiselect(
                "Select R1 Allotted Quota:",
                options=filtered_data['R1 Allotted Quota'].unique(),
                default=None
            )
            filtered_data = filtered_data[filtered_data['R1 Allotted Quota'].isin(compare_r1_quota)] if compare_r1_quota else filtered_data

        with col4:
            compare_r1_course = st.multiselect(
                "Select R1 Course:",
                options=filtered_data['R1 Course'].unique(),
                default=None
            )
            filtered_data = filtered_data[filtered_data['R1 Course'].isin(compare_r1_course)] if compare_r1_course else filtered_data

        with col5:
            compare_r2_quota = st.multiselect(
                "Select R2 Final Allotted Quota:",
                options=filtered_data['R2 Final Allotted Quota'].unique(),
                default=None
            )
            filtered_data = filtered_data[filtered_data['R2 Final Allotted Quota'].isin(compare_r2_quota)] if compare_r2_quota else filtered_data

        with col6:
            compare_r2_course = st.multiselect(
                "Select R2 Final Course:",
                options=filtered_data['R2 Final Course'].unique(),
                default=None
            )
            filtered_data = filtered_data[filtered_data['R2 Final Course'].isin(compare_r2_course)] if compare_r2_course else filtered_data

        compare_r2_category = st.multiselect(
            "Select R2 Final Alloted Category:",
            options=filtered_data['R2 Final Alloted Category'].unique(),
            default=None
        )
        filtered_data = filtered_data[filtered_data['R2 Final Alloted Category'].isin(compare_r2_category)] if compare_r2_category else filtered_data

        air_range = st.slider("Select AIQ Rank Range:",
                              min_value=int(aiqr2_data['NEET AIR'].min()),
                              max_value=int(aiqr2_data['NEET AIR'].max()),
                              value=(int(aiqr2_data['NEET AIR'].min()), int(aiqr2_data['NEET AIR'].max())))
        filtered_data = filtered_data[(filtered_data['NEET AIR'] >= air_range[0]) & (filtered_data['NEET AIR'] <= air_range[1])]

        st.write("### Filtered Comparison Results Table")
        st.dataframe(filtered_data)

        st.write("### Filtered Comparison Results Scatter Plot")
        fig, ax = plt.subplots(figsize=(18, 12))
        sns.scatterplot(data=filtered_data, x='NEET AIR', y='R2 Final Course', hue='R2 Final Alloted Category', ax=ax)
        ax.set_title('Filtered Comparison: NEET AIR vs Course Allotments', fontsize=16)
        ax.set_xlabel('NEET AIR', fontsize=14)
        ax.set_ylabel('Course', fontsize=14)
        st.pyplot(fig)

    # Tab 4: Advanced Analytics
    with tab4:
        st.write("### Advanced Analytics")

        # Select columns dynamically
        st.write("#### Column Selection")
        all_columns = aiqr2_data.columns.tolist()
        
        # Select numeric columns for analysis
        numeric_columns = aiqr2_data.select_dtypes(include=['number']).columns.tolist()
        selected_numeric_columns = st.multiselect("Select Numerical Columns for Analysis:", numeric_columns, default=numeric_columns)

        # Select columns for filtering
        selected_filter_columns = st.multiselect("Select Columns to Filter By:", all_columns)
        
        # Dynamic filters for each selected column
        filter_conditions = {}
        for col in selected_filter_columns:
            unique_values = aiqr2_data[col].dropna().unique()
            selected_values = st.multiselect(f"Filter values for {col}:", unique_values, default=unique_values)
            filter_conditions[col] = selected_values

        # Apply filters to the data
        filtered_data = aiqr2_data.copy()
        for col, values in filter_conditions.items():
            filtered_data = filtered_data[filtered_data[col].isin(values)]

        # Display filtered data
        st.write("### Filtered Data")
        st.dataframe(filtered_data)

        # Statistical Summary
        st.write("#### Statistical Summary")
        if selected_numeric_columns:
            stats_summary = filtered_data[selected_numeric_columns].describe().T
            st.dataframe(stats_summary)

        # Correlation Analysis
        st.write("#### Correlation Analysis")
        if len(selected_numeric_columns) > 1:
            correlation_matrix = filtered_data[selected_numeric_columns].corr()
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
            ax.set_title("Correlation Matrix", fontsize=16)
            st.pyplot(fig)
        else:
            st.write("Not enough numerical columns for correlation analysis.")

        # Clustering Analysis
        st.write("#### Clustering Analysis (K-Means)")
        if selected_numeric_columns:
            clustering_data = filtered_data[selected_numeric_columns].dropna()
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(clustering_data)
            
            num_clusters = st.slider("Select Number of Clusters for K-Means:", min_value=2, max_value=10, value=3)
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            filtered_data['Cluster'] = kmeans.fit_predict(scaled_data)
            
            # Visualize Clusters
            st.write("### Clustered Data Visualization")
            if len(selected_numeric_columns) >= 2:
                x_axis = st.selectbox("Select X-axis for Cluster Plot:", selected_numeric_columns)
                y_axis = st.selectbox("Select Y-axis for Cluster Plot:", selected_numeric_columns)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.scatterplot(
                    data=filtered_data,
                    x=x_axis,
                    y=y_axis,
                    hue='Cluster',
                    palette='tab10',
                    ax=ax
                )
                ax.set_title(f"K-Means Clustering ({num_clusters} Clusters)", fontsize=16)
                ax.set_xlabel(x_axis, fontsize=14)
                ax.set_ylabel(y_axis, fontsize=14)
                st.pyplot(fig)
            else:
                st.write("Not enough numerical columns for clustering visualization.")
            
            # Download Clustered Data
            st.write("#### Export Clustered Data")
            export_clustered_data = filtered_data.to_csv(index=False)
            st.download_button(
                label="Download Clustered Data as CSV",
                data=export_clustered_data,
                file_name="clustered_data.csv",
                mime="text/csv"
            )

# Call the function to display the dashboard
display_cutoff_Analysis()
