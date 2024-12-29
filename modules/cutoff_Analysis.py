import streamlit as st
import pandas as pd
import os
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

    # Tabs for analysis
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "AIR Allotment Analysis",
        "Quota-wise Analysis",
        "Institute Preferences",
        "Course-wise Analysis",
        "Category Allotments",
        "Remarks Analysis"
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
        st.dataframe(filtered_air_data)

        # Graph
        fig, ax = plt.subplots()
        filtered_air_data['R1 Allotted Quota'].value_counts().plot(kind='bar', ax=ax)
        ax.set_title("Quota Distribution in Selected AIR Range")
        ax.set_xlabel("Quota")
        ax.set_ylabel("Count")
        st.pyplot(fig)

    # Tab 2: Quota-wise Analysis
    with tab2:
        st.write("### Quota-wise Analysis")

        quota_selection = st.selectbox("Select Round for Quota Analysis:", ["R1 Allotted Quota", "R2 Final Allotted Quota"])

        quota_counts = aiqr2_data[quota_selection].value_counts()
        st.write(f"### {quota_selection} Distribution")
        st.bar_chart(quota_counts)

    # Tab 3: Institute Preferences
    with tab3:
        st.write("### Institute Preferences")

        round_selection = st.selectbox("Select Round:", ["R1 Allotted Institute", "R2 Final Allotted Institute"])
        institute_counts = aiqr2_data[round_selection].value_counts()

        st.write(f"### {round_selection} Preferences")
        st.bar_chart(institute_counts)

    # Tab 4: Course-wise Analysis
    with tab4:
        st.write("### Course-wise Analysis")

        round_course_selection = st.selectbox("Select Round for Course Analysis:", ["R1 Course", "R2 Final Course"])
        course_counts = aiqr2_data[round_course_selection].value_counts()

        st.write(f"### {round_course_selection} Popularity")
        st.bar_chart(course_counts)

    # Tab 5: Category Allotments
    with tab5:
        st.write("### Category-based Allotments")

        category_selection = st.selectbox("Select Category Type:", ["R2 Final Alloted Category", "R2 candidate Category"])
        category_counts = aiqr2_data[category_selection].value_counts()

        st.write(f"### {category_selection} Distribution")
        st.bar_chart(category_counts)

    # Tab 6: Remarks Analysis
    with tab6:
        st.write("### Remarks Analysis")

        remarks_selection = st.selectbox("Select Remarks Type:", ["R1 Remarks", "R2 Final Remarks"])
        remarks_counts = aiqr2_data[remarks_selection].value_counts()

        st.write(f"### {remarks_selection} Distribution")
        st.bar_chart(remarks_counts)

# Call the function to display the dashboard
display_cutoff_Analysis()
