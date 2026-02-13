import streamlit as st
import pandas as pd

def show_history(get_data, db):
    st.title("📜 Historic Archives")
    st.caption("Full event history and financial statistics")

    # Fetch data from Supabase modules
    df = get_data("Events")
    df_fin = get_data("Event_Financials")

    if df.empty:
        st.warning("No historic data available."); return

    # --- 📊 STATISTICS SECTION ---
    if not df_fin.empty:
        # Note: In your Supabase SQL, the column is 'total_revenue' 
        # based on Table 8 or calculated fields.
        rev_col = 'total_revenue' if 'total_revenue' in df_fin.columns else 'Total_Sales'
        
        if rev_col in df_fin.columns:
            total_revenue = pd.to_numeric(df_fin[rev_col], errors='coerce').sum()
            st.metric("Total Historic Revenue", f"${total_revenue:,.2f}")
        else:
            st.metric("Total Historic Revenue", "$0.00", help="Revenue column not found")

    # --- 🗂️ DATA TABLE ---
    st.write("### Raw Archive Data")
    # We display the events dataframe. 
    # Streamlit's st.dataframe handles the display perfectly.
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Space for future charts
    if not df_fin.empty:
        st.info("💡 Pro Tip: You can now add Plotly charts here to track revenue trends over time.")
# import streamlit as st
# import pandas as pd

# def show_history(get_data, conn):
#     st.title("📜 Historic Archives")
#     st.caption("Full event history and financial statistics")

#     df = get_data("Events")
#     df_fin = get_data("Event_Financials")

#     if df.empty:
#         st.warning("No historic data available."); return

#     # Statistics Section for Admin
#     if not df_fin.empty:
#         total_revenue = df_fin['Total_Sales'].sum() if 'Total_Sales' in df_fin.columns else 0
#         st.metric("Total Historic Revenue", f"${total_revenue:,.2f}")

#     # Search and Full Table
#     st.dataframe(df, use_container_width=True)
    
#     # You can add Plotly charts here later for "Revenue per Venue"
    
