import streamlit as st
import pandas as pd
from datetime import datetime

def render_staffing_tab(eid, db, get_data, is_adm):
    """
    Modular Staffing Tab for Event Workspace.
    Features: Staff Gallery, Role-based assignment, and Shift validation.
    """
    st.subheader("📋 Available Staff Gallery")

    # 1. FETCH DATA
    df_staff_db = get_data("Staff_Database")
    df_staffing = get_data("Event_Staffing")
    
    # Initialize empty state if table is new
    if df_staffing.empty or 'Event_ID' not in df_staffing.columns:
        df_staffing = pd.DataFrame(columns=['Event_ID', 'Staff_Name', 'Start_Time', 'End_Time', 'Payment_Status', 'Type'])

    # Get list of staff already assigned to this specific event
    assigned_names = df_staffing[df_staffing['Event_ID'].astype(str) == str(eid)]['Staff_Name'].tolist()

    if not df_staff_db.empty:
        # 2. STAFF GALLERY GRID
        card_grid = st.columns(2)
        
        for i, (idx, s_row) in enumerate(df_staff_db.iterrows()):
            name = s_row['Staff_Name']
            
            # --- 📞 PHONE CLEANING ---
            raw_phone = str(s_row.get('Phone', ''))
            clean_phone = raw_phone.split('.')[0].strip()
            # Re-add leading zero for Australian Mobile logic
            if len(clean_phone) == 9 and clean_phone.startswith('4'):
                clean_phone = "0" + clean_phone
            if clean_phone.lower() == "nan" or not clean_phone:
                clean_phone = None

            # --- ⭐ STAR RATING LOGIC ---
            try:
                num_stars = int(float(s_row.get('Rating', 0)))
            except (ValueError, TypeError):
                num_stars = 0
            star_display = "⭐" * num_stars if num_stars > 0 else "No Rating"

            with card_grid[i % 2]:
                with st.container(border=True):
                    h1, h2 = st.columns([3, 1])
                    h1.markdown(f"**{name}**")
                    h2.markdown("🟢 **Active**" if name in assigned_names else "⚪ **Idle**")
                    
                    if clean_phone:
                        st.markdown(f"📞 [ {clean_phone} ](tel:{clean_phone})")
                    else:
                        st.caption("📞 Phone: N/A")

                    st.caption(f"Rating: {star_display}")
                    st.write(f"🛠️ **Skills:** {s_row.get('Skills', 'N/A')}")
                    
                    # --- ACTION BUTTONS ---
                    if name in assigned_names:
                        if is_adm:
                            # Use unique key to avoid Streamlit Duplicate Widget ID error
                            if st.button(f"❌ Remove {name.split()[0]}", key=f"rem_{idx}_{eid}", use_container_width=True):
                                # Filter out the row and update table
                                df_staffing_updated = df_staffing[~((df_staffing['Event_ID'].astype(str) == str(eid)) & 
                                                                   (df_staffing['Staff_Name'] == name))]
                                if db.update_table("Event_Staffing", df_staffing_updated):
                                    st.cache_data.clear()
                                    st.rerun()
                    else:
                        with st.expander("➕ Assign to Event"):
                            with st.form(key=f"assign_f_{idx}_{eid}"):
                                c1, c2 = st.columns(2)
                                st_time_str = c1.text_input("Start", value="08:00")
                                en_time_str = c2.text_input("End", value="18:00")

                                # Shift duration warning
                                try:
                                    fmt = '%H:%M'
                                    t1 = datetime.strptime(st_time_str, fmt)
                                    t2 = datetime.strptime(en_time_str, fmt)
                                    delta = (t2 - t1).total_seconds() / 3600
                                    if delta < 0: delta += 24 
                                    if delta > 8:
                                        st.warning(f"⚠️ Long Shift: {delta:.1f} hrs")
                                except:
                                    pass

                                if st.form_submit_button("Confirm Assignment", use_container_width=True):
                                    new_entry = {
                                        "Event_ID": eid, "Staff_Name": name, 
                                        "Start_Time": st_time_str, "End_Time": en_time_str, 
                                        "Payment_Status": "Pending", "Type": "Standard"
                                    }
                                    if db.insert_row("Event_Staffing", new_entry):
                                        st.cache_data.clear()
                                        st.success(f"{name} added!")
                                        st.rerun()
    else:
        st.warning("No staff records found in Staff_Database.")

    st.divider()

    # 3. ADMIN QUICK ADD (SEARCHABLE)
    if is_adm:
        with st.expander("🔍 Search & Assign Staff"):
            with st.form("add_staff_form_quick", clear_on_submit=True):
                staff_options = df_staff_db['Staff_Name'].tolist() if not df_staff_db.empty else []
                sel_staff = st.selectbox("Select Staff Member", staff_options)
                
                col1, col2 = st.columns(2)
                s_time = col1.text_input("Start Time", value="08:00")
                e_time = col2.text_input("End Time", value="18:00")
                
                if st.form_submit_button("Assign to Event", use_container_width=True):
                    if sel_staff:
                        new_quick = {
                            "Event_ID": eid, "Staff_Name": sel_staff,
                            "Start_Time": s_time, "End_Time": e_time,
                            "Payment_Status": "Pending", "Type": "Standard"
                        }
                        if db.insert_row("Event_Staffing", new_quick):
                            st.cache_data.clear()
                            st.success(f"Added {sel_staff}!")
                            st.rerun()
    else:
        st.caption("🔒 Roster management is restricted to Admins.")