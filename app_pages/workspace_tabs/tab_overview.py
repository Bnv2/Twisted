import streamlit as st
import pandas as pd
import numpy as np
from modules.ui_utils import render_mini_map

def render_overview_tab(eid, event_core, df_events, db, get_data, is_adm):
    # --- 1. SETUP & DATA PARSING ---
    # Handle boolean conversion for the checkbox safely
    is_multi_db = str(event_core.get('is_multi_day', 'No')).strip().lower() == "yes"
    
    try:
        # Standardize dates; handle empty or malformed strings
        start_dt = pd.to_datetime(event_core.get('date'), dayfirst=True, errors='coerce').date()
        end_val = event_core.get('end_date')
        if pd.isna(end_val) or str(end_val).strip() == "":
            end_dt = start_dt
        else:
            end_dt = pd.to_datetime(end_val, dayfirst=True, errors='coerce').date()
    except:
        from datetime import datetime
        start_dt = end_dt = datetime.now().date()

    # --- 2. HEADER & CONTROL ROW ---
    col_h, col_edit = st.columns([3, 1])
    with col_h:
        st.subheader(f"📍 {event_core.get('venue', 'Unknown Venue')} Dashboard")
    with col_edit:
        edit_mode = st.toggle("🔓 Edit Mode", value=False) if is_adm else False

    # --- 3. THE DASHBOARD LAYOUT ---
    col_form, col_map = st.columns([1.6, 1.4], gap="medium")

    with col_form:
        with st.container(border=True):
            is_multi = st.checkbox("Multi-Day Event", value=is_multi_db, disabled=not edit_mode)
            if not edit_mode:
                st.caption("📅 Multi-Day Event" if is_multi else "⏱️ Single Day Event")

            with st.form("overview_form_master", border=False):
                # Row 1: Date Inputs
                d1, d2 = st.columns(2)
                new_start = d1.date_input("Start Date", value=start_dt, disabled=not edit_mode)
                new_end = d2.date_input("End Date", value=end_dt, disabled=not (edit_mode and is_multi))

                # Row 2: Basic Details
                v1, v2 = st.columns(2)
                new_venue = v1.text_input("Venue Name", value=str(event_core.get('venue', '')), disabled=not edit_mode)
                new_org = v2.text_input("Organiser", value=str(event_core.get('organiser_name', '')), disabled=not edit_mode)

                # Row 3: Text Areas
                new_address = st.text_area("Address", value=str(event_core.get('address', '')), disabled=not edit_mode, height=100)
                new_notes = st.text_area("Internal Notes", value=str(event_core.get('notes', '')), disabled=not edit_mode, height=115)

                if st.form_submit_button("💾 Save Changes", use_container_width=True, disabled=not edit_mode):
                    with st.spinner("Updating Database..."):
                        # Data mapped exactly to your SQL lowercase schema
                        updated_row = {
                            "event_id": str(eid),
                            "venue": new_venue, 
                            "date": new_start.strftime('%Y-%m-%d'), 
                            "end_date": new_end.strftime('%Y-%m-%d'), 
                            "is_multi_day": "Yes" if is_multi else "No", 
                            "address": new_address, 
                            "organiser_name": new_org, 
                            "notes": new_notes
                        }
                        
                        try:
                            # Direct single-row upsert to prevent NaN/Full-table overwrite issues
                            db.client.table("events").upsert(updated_row, on_conflict="event_id").execute()
                            
                            st.cache_data.clear()
                            st.success("Database Updated Successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Update Failed: {str(e)}")

    with col_map:
        with st.container(border=True):
            st.caption("🗺️ Interactive Site Map")
            render_mini_map(str(event_core.get('address', ''))) 
            
            st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
            
            # --- CONTACTS SECTION ---
            with st.popover("👥 Manage Event Contacts", use_container_width=True):
                with st.form("quick_add_contact"):
                    st.write("**Add New Contact**")
                    c_name = st.text_input("Name")
                    c_role = st.selectbox("Role", ["Manager", "Organizer", "Staff", "Other"])
                    if st.form_submit_button("Save Contact", use_container_width=True):
                        if c_name:
                            new_c = {"event_id": str(eid), "name": c_name, "role": c_role}
                            db.client.table("event_contacts").insert(new_c).execute()
                            st.cache_data.clear()
                            st.rerun()
                
                st.divider()
                
                # --- FIXED: DEFENSIVE DATA FETCHING ---
                df_con = get_data("event_contacts")
                if not df_con.empty:
                    # Detect the ID column regardless of casing (event_id vs Event_ID)
                    actual_cols = df_con.columns.tolist()
                    id_col = next((c for c in actual_cols if c.lower() == 'event_id'), None)

                    if id_col:
                        # Filter for the specific event
                        current_contacts = df_con[df_con[id_col].astype(str).str.strip() == str(eid).strip()]
                        
                        if not current_contacts.empty:
                            for _, row in current_contacts.iterrows():
                                # Access data with case-insensitive fallbacks
                                role = row.get('role') or row.get('Role') or 'Staff'
                                name = row.get('name') or row.get('Name') or 'Unknown'
                                st.caption(f"**{role}**: {name}")
                        else:
                            st.caption("No contacts listed for this event.")
                    else:
                        st.warning(f"ID Column not found. Found: {actual_cols}")
                else:
                    st.caption("No contacts found.")
