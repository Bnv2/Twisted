import streamlit as st
import pandas as pd

def render_logistics_tab(eid, db, get_data, is_adm):
    """
    Modular Logistics Tab for Event Workspace.
    """
    st.subheader("🚛 Logistics & Setup Details")

    # 1. FETCH DATA
    # Ensure the table name matches your Supabase schema (e.g., "logistics_details")
    df_log = get_data("logistics_details")
    
    # 2. DATA PREPARATION
    if not df_log.empty and 'Event_ID' in df_log.columns:
        # Match eid against the column (ensuring type consistency)
        log_match = df_log[df_log['Event_ID'].astype(str) == str(eid)]
        curr_log = log_match.iloc[0] if not log_match.empty else {}
    else:
        curr_log = {}
        # Fallback empty dataframe with correct schema if table is missing/empty
        if df_log.empty or 'Event_ID' not in df_log.columns:
            df_log = pd.DataFrame(columns=['Event_ID', 'Setup_Type', 'Bump_In', 'Bump_Out', 'Parking', 'Log_Notes'])

    # 3. PERMISSIONS CHECK
    edit_log = False
    if is_adm:
        edit_log = st.toggle("🔓 Edit Logistics", key="log_edit_toggle", value=False)
    else:
        st.info("🔒 View Only: Logistics are managed by Admins.")

    # 4. LOGISTICS FORM
    with st.form("logistics_details_form", border=True):
        # Row 1: Times
        r1c1, r1c2 = st.columns(2)
        new_bump_in = r1c1.text_input("Bump In Time", value=str(curr_log.get("Bump_In", "08:00")), disabled=not edit_log)
        new_bump_out = r1c2.text_input("Bump Out Time", value=str(curr_log.get("Bump_Out", "18:00")), disabled=not edit_log)

        # Row 2: Setup & Parking
        r2c1, r2c2 = st.columns(2)
        setup_list = ["Marquee", "Food Truck", "Indoor", "Cart"]
        
        # Safely find the index for the selectbox
        current_val = curr_log.get("Setup_Type", "Food Truck")
        try:
            current_setup_idx = setup_list.index(current_val) if current_val in setup_list else 1
        except (ValueError, AttributeError):
            current_setup_idx = 1
        
        new_setup = r2c1.selectbox("Setup Type", setup_list, index=current_setup_idx, disabled=not edit_log)
        new_parking = r2c2.text_input("Parking Info", value=str(curr_log.get("Parking", "")), disabled=not edit_log)

        # Row 3: Notes
        new_log_notes = st.text_area("Logistics Notes", value=str(curr_log.get("Log_Notes", "")), disabled=not edit_log)

        # 5. SAVE LOGIC
        log_save_btn = st.form_submit_button("💾 Save Logistics", use_container_width=True, disabled=not edit_log)

        if log_save_btn and edit_log:
            new_log_row = {
                "Event_ID": eid, 
                "Setup_Type": new_setup, 
                "Bump_In": new_bump_in,
                "Bump_Out": new_bump_out, 
                "Parking": new_parking, 
                "Log_Notes": new_log_notes
            }
            
            # Filter out the existing record for this event and append the new version
            df_log_updated = df_log[df_log['Event_ID'].astype(str) != str(eid)].copy()
            df_log_updated = pd.concat([df_log_updated, pd.DataFrame([new_log_row])], ignore_index=True)
            
            # Use your Supabase wrapper to push the full updated table
            if db.update_table("logistics_details", df_log_updated):
                st.success("Logistics Updated!")
                st.cache_data.clear() # Force refresh for all users
                st.rerun()