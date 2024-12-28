import streamlit as st

# Sidebar Navigation
def navigate():
    st.sidebar.title("Navigation")
    return st.sidebar.radio(
        "Select a page:",
        ["Home", "Master Data", "Order Creation", "Order Creation with Excel", "Order Comparison", "Fee Checking"]
    )

# Run the selected page
def run_page(page):
    if page == "Home":
        from modules.home import display_home  # Updated path
        display_home()
    elif page == "Master Data":
        from modules.master_data import display_master_data  # Updated path
        display_master_data()
    elif page == "Order Creation":
        from modules.order_creation import display_order_creation  # Updated path
        display_order_creation()
    elif page == "Order Creation with Excel":
        from modules.excel_ranking import display_excel_ranking  # Updated path
        display_excel_ranking()
    elif page == "Order Comparison":
        from modules.comparison import display_comparison  # Updated path
        display_comparison()
    elif page == "Fee Checking":
        from modules.fee_checking import display_fee_checking  # Updated path
        display_fee_checking()

# Main app logic
def main():
    st.set_page_config(page_title="ETERNALS", layout="wide")
    page = navigate()
    run_page(page)

if __name__ == "__main__":
    main()
