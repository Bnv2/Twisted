import streamlit as st
import pandas as pd

def show_logs(get_data, conn):
    st.title("📦 Inventory & Logistics Logs")
    
    # Load all relevant logistics data
    df_log = get_data("Logistics_Details")
    df_inv = get_data("Inventory_Logs") # Assuming this exists in your sheets

    tabs = st.tabs(["🚛 Delivery Logs", "📦 Stock Levels"])

    with tabs[0]:
        if not df_log.empty:
            st.dataframe(df_log, use_container_width=True)
        else:
            st.info("No logistics logs recorded yet.")

    with tabs[1]:
        st.write("Stock tracking dashboard coming soon.")
        