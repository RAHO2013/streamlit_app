import streamlit as st

# Sidebar Navigation
def navigate():
    st.sidebar.title("Navigation")

    # Home Page as a separate section
    with st.sidebar.expander("🏠 Home", expanded=False):
        if st.button("Home"):
            st.session_state.page = "home"

    # Data Management Expander
    with st.sidebar.expander("📊 Data Management", expanded=False):
        if st.button("Master Data"):
            st.session_state.page = "master_data"


    # Rankings
    with st.sidebar.expander("🏆 Rankings ", expanded=False):
        if st.button("Order Creation with Excel"):
            st.session_state.page = "excel_ranking"
        if st.button("Order Creation"):
            st.session_state.page = "order_creation"
            
    # Comparison Expander
    with st.sidebar.expander("⚙️ Comparison", expanded=False):
        if st.button("Order Comparison"):
            st.session_state.page = "order_comparison"

    # Fee Management Expander
    with st.sidebar.expander("💸 Fee Management", expanded=False):
        if st.button("Fee Checking"):
            st.session_state.page = "fee_checking"

# Run the selected page
def run_page():
    if 'page' not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.page == "home":
        from modules.home import display_home
        display_home()
    elif st.session_state.page == "master_data":
        from modules.master_data import display_master_data
        display_master_data()
    elif st.session_state.page == "order_creation":
        from modules.order_creation import display_order_creation
        display_order_creation()
    elif st.session_state.page == "excel_ranking":
        from modules.excel_ranking import display_excel_ranking
        display_excel_ranking()
    elif st.session_state.page == "order_comparison":
        from modules.comparison import display_comparison
        display_comparison()
    elif st.session_state.page == "fee_checking":
        from modules.fee_checking import display_fee_checking
        display_fee_checking()

# Main app logic
def main():
    st.set_page_config(page_title="ETERNALS", layout="wide")
    navigate()
    run_page()

if __name__ == "__main__":
    main()
