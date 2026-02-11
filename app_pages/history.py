import streamlit as st
import pandas as pd

def show_history(get_data, conn):
    st.title("📜 Historic Archives")
    st.caption("Full event history and financial statistics")

    df = get_data("Events")
    df_fin = get_data("Event_Financials")

    if df.empty:
        st.warning("No historic data available."); return

    # Statistics Section for Admin
    if not df_fin.empty:
        total_revenue = df_fin['Total_Sales'].sum() if 'Total_Sales' in df_fin.columns else 0
        st.metric("Total Historic Revenue", f"${total_revenue:,.2f}")

    # Search and Full Table
    st.dataframe(df, use_container_width=True)
    
    # You can add Plotly charts here later for "Revenue per Venue"
    