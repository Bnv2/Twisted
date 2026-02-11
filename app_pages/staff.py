import streamlit as st
import pandas as pd
from modules.auth import nuclear_clean # Import the pro cleaning tool

def show_staff(get_data, conn):
    st.title("👥 Staff Management")
    
    # Check Admin Access
    if st.session_state.user_role != "Admin":
        st.error("Access Denied. Admins only.")
        return

    staff_df = get_data("Staff")
    
    if staff_df.empty:
        st.warning("No staff data found.")
        return

    # Clean the data using our shared module
    staff_df['Email'] = staff_df['Email'].astype(str).str.lower().str.strip()
    staff_df['PIN'] = staff_df['PIN'].apply(nuclear_clean)

    st.subheader("Current Team")
    st.dataframe(staff_df, use_container_width=True, hide_index=True)

    # Future: Add 'Add Staff' or 'Delete Staff' logic here
    with st.expander("➕ Add New Staff Member"):
        st.info("Staff addition logic will be implemented here.")
        