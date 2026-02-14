import streamlit as st
import pandas as pd
import re
from modules.ui_utils import render_mini_map

def render_overview_tab(eid, event_core, df_events, db, get_data, is_adm):
    # --- 1. SETUP & DATA PARSING ---
    is_multi_db = str(event_core.get('Is_Multi_Day', 'No')) == "Yes"
    
    try:
        start_dt = pd.to_datetime(event_core['Date'], dayfirst=True).date()
        end_val = event_core.get('End_Date')
        end_dt = pd.to_datetime(end_val, dayfirst=True).date() if pd.notna(end_val) else start_dt
    except:
        from datetime import datetime
        start_dt = end_dt = datetime.now().date()

    # --- 2. HEADER & CONTROL ROW ---
    col_h, col_edit = st.columns([3, 1])
    with col_h:
        st.subheader(f"📍 {event_core['Venue']} Dashboard")
    with col_edit:
        # Defaults to False so UI is read-only on load
        edit_mode = st.toggle("🔓 Edit Mode", value=False) if is_adm else False

    # --- 3. THE SPLIT DASHBOARD LAYOUT ---
    col_form, col_map = st.columns([1.6, 1.4], gap="medium")

    # --- LEFT COLUMN: CORE DATA ---
    with col_form:
        with st.container(border=True):
            # Checkbox outside form to trigger reactive enabling of End Date
            if edit_mode:
                is_multi = st.checkbox("Multi-Day Event", value=is_multi_db)
            else:
                is_multi = is_multi_db
                st.caption("📅 Multi-Day Event" if is_multi else "⏱️ Single Day Event")

            with st.form("overview_form_master", border=False):
                # Row 1: Date Range
                d1, d2 = st.columns(2)
                new_start = d1.date_input("Start Date", value=start_dt, disabled=not edit_mode)
                new_end = d2.date_input("End Date", value=end_dt, disabled=not (edit_mode and is_multi))

                # Row 2: Basic Info
                v1, v2 = st.columns(2)
                new_venue = v1.text_input("Venue Name", value=event_core['Venue'], disabled=not edit_mode)
                new_org = v2.text_input("Organiser", value=str(event_core.get('Organiser_Name', '')), disabled=not edit_mode)

                # Row 3: Extended Info
                new_address = st.text_area("Address", value=str(event_core.get('Address', '')), disabled=not edit_mode, height=100)
                new_notes = st.text_area("Internal Notes", value=str(event_core.get('Notes', '')), disabled=not edit_mode, height=115)

                # Row 4: Action
                if st.form_submit_button("💾 Save Changes", use_container_width=True, disabled=not edit_mode):
                    # Construct the updated row (Keep original ID!)
                    updated_row = event_core.to_dict() # Start with all original columns
                    updated_row.update({
                        "Venue": new_venue, 
                        "Date": new_start.strftime('%d/%m/%Y'), 
                        "End_Date": new_end.strftime('%d/%m/%Y'), 
                        "Is_Multi_Day": "Yes" if is_multi else "No", 
                        "Address": new_address, 
                        "Organiser_Name": new_org, 
                        "Notes": new_notes
                    })
                    
                    # Merge with Master Dataframe
                    df_updated = df_events[df_events['Event_ID'].astype(str) != str(eid)].copy()
                    df_updated = pd.concat([df_updated, pd.DataFrame([updated_row])], ignore_index=True)
                    
                    if db.update_table("Events", df_updated):
                        st.success("Changes Saved Successfully!")
                        st.cache_data.clear()
                        st.rerun()

    # --- RIGHT COLUMN: MAP & CONTACTS ---
    with col_map:
        with st.container(border=True):
            st.caption("🗺️ Interactive Site Map")
            # Calling your utility (ensure height= is supported in ui_utils.py)
            render_mini_map(event_core.get('Address', '')) 
            
            st.markdown("<div style='margin-top: 22px;'></div>", unsafe_allow_html=True)
            
            with st.popover("👥 Manage Event Contacts", use_container_width=True):
                with st.form("quick_add_contact"):
                    st.write("**Quick Add Contact**")
                    c_name = st.text_input("Name")
                    c_role = st.selectbox("Role", ["Manager", "Organizer", "Billing", "Staff"])
                    if st.form_submit_button("Save Contact", use_container_width=True):
                        if c_name:
                            new_c = {"Event_ID": eid, "Name": c_name, "Role": c_role}
                            if db.insert_row("Event_Contacts", new_c):
                                st.cache_data.clear(); st.rerun()
                
                st.divider()
                # Display mini-list of contacts
                df_con = get_data("Event_Contacts")
                current_contacts = df_con[df_con['Event_ID'].astype(str) == str(eid)] if not df_con.empty else pd.DataFrame()
                for _, row in current_contacts.iterrows():
                    st.caption(f"**{row['Role']}**: {row['Name']}")






# import streamlit as st
# import pandas as pd
# import re
# from modules.ui_utils import render_mini_map

# def render_overview_tab(eid, event_core, df_events, db, get_data, is_adm):
#     # --- 1. SETUP ---
#     is_multi_db = str(event_core.get('Is_Multi_Day', 'No')) == "Yes"
    
#     try:
#         start_dt = pd.to_datetime(event_core['Date'], dayfirst=True).date()
#         end_val = event_core.get('End_Date')
#         end_dt = pd.to_datetime(end_val, dayfirst=True).date() if pd.notna(end_val) else start_dt
#     except:
#         from datetime import datetime
#         start_dt = end_dt = datetime.now().date()

#     # --- 2. TOP ACTIONS (Add Contact & Edit Toggle) ---
#     col_ov_h, col_ov_act = st.columns([2, 1])
#     with col_ov_h: 
#         st.subheader("📍 Event Overview")

#     with col_ov_act:
#         # Default is False (Locked)
#         edit_mode = st.toggle("🔓 Edit Mode", value=False) if is_adm else False
        
#         with st.popover("➕ Add Contact", use_container_width=True):
#             with st.form("add_contact_form", clear_on_submit=True):
#                 c_name = st.text_input("Full Name*")
#                 c_role = st.selectbox("Role", ["Site Manager", "Organizer", "Billing", "Electrician", "Security"])
#                 c_phone = st.text_input("Phone Number")
#                 c_email = st.text_input("Email Address")
#                 if st.form_submit_button("💾 Save Contact", use_container_width=True):
#                     if c_name and "@" in c_email:
#                         new_c = {"Event_ID": eid, "Name": c_name, "Phone": c_phone, "Email": c_email, "Role": c_role}
#                         if db.insert_row("Event_Contacts", new_c):
#                             st.cache_data.clear(); st.rerun()

#     # --- 3. THE CORE FORM ---
#     # We use a container to wrap the form for better visual grouping
#     with st.container(border=True):
#         # We place the Multi-Day checkbox OUTSIDE the form only if Edit Mode is on 
#         # to allow the "End Date" to unlock without a full form save.
#         if edit_mode:
#             is_multi = st.checkbox("This is a Multi-Day Event", value=is_multi_db)
#         else:
#             is_multi = is_multi_db
#             st.info("💡 Toggle 'Edit Mode' above to modify event details.")

#         with st.form("edit_event_core"):
#             # Row 1: Dates (Side by Side)
#             d_col1, d_col2 = st.columns(2)
#             new_start = d_col1.date_input("Start Date", value=start_dt, disabled=not edit_mode)
#             new_end = d_col2.date_input("End Date", value=end_dt, disabled=not (edit_mode and is_multi))

#             # Row 2: Venue & Organiser
#             v_col1, v_col2 = st.columns(2)
#             new_venue = v_col1.text_input("Venue Name", value=event_core['Venue'], disabled=not edit_mode)
#             new_org = v_col2.text_input("Organiser", value=str(event_core.get('Organiser_Name', '')), disabled=not edit_mode)

#             # Row 3: Address (Full Width)
#             new_address = st.text_area("Event Address", value=str(event_core.get('Address', '')), disabled=not edit_mode, height=68)
            
#             # Row 4: Notes
#             new_notes = st.text_area("Internal Notes", value=str(event_core.get('Notes', '')), disabled=not edit_mode)

#             # Submit Button
#             if st.form_submit_button("💾 Save Changes", use_container_width=True, disabled=not edit_mode):
#                 updated_data = {
#                     "Venue": new_venue, 
#                     "Date": new_start.strftime('%d/%m/%Y'), 
#                     "End_Date": new_end.strftime('%d/%m/%Y'), 
#                     "Is_Multi_Day": "Yes" if is_multi else "No", 
#                     "Address": new_address, 
#                     "Organiser_Name": new_org, 
#                     "Notes": new_notes
#                 }
#                 if db.update_row("Events", {"Event_ID": eid}, updated_data):
#                     st.success("Changes Saved Successfully!")
#                     st.cache_data.clear()
#                     st.rerun()

#     # --- 4. CONTACT LIST ---
#     st.divider()
#     df_con = get_data("Event_Contacts")
#     current_contacts = df_con[df_con['Event_ID'].astype(str) == str(eid)] if not df_con.empty else pd.DataFrame()
    
#     if not current_contacts.empty:
#         st.caption("Registered Contacts")
#         # Displaying contacts in a more compact grid
#         c_cols = st.columns(2)
#         for i, (idx, row) in enumerate(current_contacts.iterrows()):
#             with c_cols[i % 2]:
#                 with st.expander(f"{row['Role']}: {row['Name']}"):
#                     st.write(f"📞 {row['Phone']}")
#                     st.write(f"📧 {row['Email']}")
#                     if is_adm and st.button("🗑️ Remove", key=f"del_{idx}"):
#                         if db.delete_row("Event_Contacts", {"id": row['id']}):
#                             st.cache_data.clear(); st.rerun()

#     # --- 5. MAP ONLY ---
#     render_mini_map(event_core.get('Address', ''))








# import streamlit as st
# import pandas as pd
# import re
# from modules.ui_utils import render_mini_map

# def render_overview_tab(eid, event_core, df_events, db, get_data, is_adm):
#     # --- 1. SETUP & DATA PARSING ---
#     is_multi_db = str(event_core.get('Is_Multi_Day', 'No')) == "Yes"
    
#     try:
#         start_dt = pd.to_datetime(event_core['Date'], dayfirst=True).date()
#         end_val = event_core.get('End_Date')
#         end_dt = pd.to_datetime(end_val, dayfirst=True).date() if pd.notna(end_val) else start_dt
#     except:
#         from datetime import datetime
#         start_dt = end_dt = datetime.now().date()

#     # --- 2. HEADER & CONTROL ROW ---
#     col_h, col_edit = st.columns([3, 1])
#     with col_h:
#         st.subheader(f"📍 {event_core['Venue']} Details")
#     with col_edit:
#         # Locked by default
#         edit_mode = st.toggle("🔓 Edit Mode", value=False) if is_adm else False

#     # --- 3. MAIN DASHBOARD LAYOUT (Side-by-Side) ---
#     col_form, col_map = st.columns([1.8, 1.2], gap="medium")

#     # --- LEFT COLUMN: THE DATA FORM ---
#     with col_form:
#         with st.container(border=True):
#             # Reactive Checkbox (Only if editing)
#             if edit_mode:
#                 is_multi = st.checkbox("Multi-Day Event", value=is_multi_db)
#             else:
#                 is_multi = is_multi_db
#                 if not is_multi: st.caption("⏱️ Single Day Event")

#             with st.form("overview_form_master", border=False):
#                 # Row 1: Dates
#                 d1, d2 = st.columns(2)
#                 new_start = d1.date_input("Start Date", value=start_dt, disabled=not edit_mode)
#                 new_end = d2.date_input("End Date", value=end_dt, disabled=not (edit_mode and is_multi))

#                 # Row 2: Venue & Organiser
#                 v1, v2 = st.columns(2)
#                 new_venue = v1.text_input("Venue Name", value=event_core['Venue'], disabled=not edit_mode)
#                 new_org = v2.text_input("Organiser", value=str(event_core.get('Organiser_Name', '')), disabled=not edit_mode)

#                 # Row 3: Address & Notes
#                 new_address = st.text_area("Address", value=str(event_core.get('Address', '')), disabled=not edit_mode, height=90)
#                 new_notes = st.text_area("Internal Notes", value=str(event_core.get('Notes', '')), disabled=not edit_mode, height=90)

#                 # Save Button
#                 save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True, disabled=not edit_mode)
                
#                 if save_btn:
#                     updated_data = {
#                         "Venue": new_venue, 
#                         "Date": new_start.strftime('%d/%m/%Y'), 
#                         "End_Date": new_end.strftime('%d/%m/%Y'), 
#                         "Is_Multi_Day": "Yes" if is_multi else "No", 
#                         "Address": new_address, 
#                         "Organiser_Name": new_org, 
#                         "Notes": new_notes
#                     }
#                     if db.update_row("Events", {"Event_ID": eid}, updated_data):
#                         st.success("Saved!"); st.cache_data.clear(); st.rerun()

#     # --- RIGHT COLUMN: MAP & CONTACTS ---
#     with col_map:
#         # Render the map in its own frame
#         with st.container(border=True):
#             st.caption("🗺️ Event Location")
#             render_mini_map(event_core.get('Address', ''))
        
#         # Contacts Popover moved here to keep header clean
#         with st.popover("👤 Manage Contacts", use_container_width=True):
#             # Quick Add Form
#             with st.form("quick_add_contact"):
#                 st.write("**Add Contact**")
#                 c_name = st.text_input("Name")
#                 c_role = st.selectbox("Role", ["Manager", "Organizer", "Billing", "Staff"])
#                 c_ph = st.text_input("Phone")
#                 if st.form_submit_button("Save Contact", use_container_width=True):
#                     if c_name:
#                         new_c = {"Event_ID": eid, "Name": c_name, "Phone": c_ph, "Role": c_role}
#                         if db.insert_row("Event_Contacts", new_c):
#                             st.cache_data.clear(); st.rerun()
            
#             # Contact List (Mini List)
#             st.divider()
#             df_con = get_data("Event_Contacts")
#             current_contacts = df_con[df_con['Event_ID'].astype(str) == str(eid)] if not df_con.empty else pd.DataFrame()
#             for _, row in current_contacts.iterrows():
#                 st.caption(f"**{row['Role']}**: {row['Name']} ({row.get('Phone', 'No PH')})")






















# import streamlit as st
# import pandas as pd
# import re
# from modules.ui_utils import render_mini_map

# def render_overview_tab(eid, event_core, df_events, db, get_data, is_adm):
#     """
#     Modular Overview Tab for Event Workspace.
#     """
#     # 1. Local Logic & Date Setup
#     is_multi = str(event_core.get('Is_Multi_Day', 'No')) == "Yes"
    
#     # Pre-processing dates for the date picker
#     try:
#         start_dt = pd.to_datetime(event_core['Date'], dayfirst=True)
#         end_val = event_core.get('End_Date')
#         if pd.isna(end_val) or end_val == "" or str(end_val).lower() == "none":
#             end_dt = start_dt
#         else:
#             end_dt = pd.to_datetime(end_val, dayfirst=True)
#     except:
#         from datetime import datetime
#         start_dt = end_dt = datetime.now()

#     col_ov_h, col_ov_ed = st.columns([3, 1])
#     with col_ov_h: 
#         st.subheader("📍 Core Event Details")
    
#     # 2. Access Check
#     edit_mode = False
#     if is_adm:
#         edit_mode = col_ov_ed.toggle("🔓 Edit Details", value=False)
#     else:
#         col_ov_ed.info("🔒 View Only")

#     # 3. The Core Details Form
#     with st.form("edit_core_details", border=True):
#         c1, c2 = st.columns(2)
#         with c1:
#             new_venue = st.text_input("Venue Name", value=event_core['Venue'], disabled=not edit_mode)
#             new_start = st.date_input("Start Date", value=start_dt.date(), disabled=not edit_mode)
#             new_multi = st.selectbox("Multi-Day Event?", ["Yes", "No"], 
#                                      index=0 if is_multi else 1, disabled=not edit_mode)
#             new_end = st.date_input("End Date", value=end_dt.date(), disabled=not (edit_mode and new_multi == "Yes"))
#         with c2:
#             new_address = st.text_area("Event Address", value=str(event_core.get('Address', '')), disabled=not edit_mode, height=68)
#             new_map = st.text_input("Maps Link", value=str(event_core.get('Maps_Link', '')), disabled=not edit_mode)
#             new_org = st.text_input("Organiser Name", value=str(event_core.get('Organiser_Name', '')), disabled=not edit_mode)
        
#         new_notes = st.text_area("Internal Notes", value=str(event_core.get('Notes', '')), disabled=not edit_mode)

#         save_btn = st.form_submit_button("💾 Save Core Changes", use_container_width=True, disabled=not edit_mode)

#         if save_btn and edit_mode:
#             updated_row = event_core.to_dict()
#             updated_row.update({
#                 "Venue": new_venue, 
#                 "Date": new_start.strftime('%d/%m/%Y'), 
#                 "End_Date": new_end.strftime('%d/%m/%Y'),
#                 "Is_Multi_Day": new_multi, 
#                 "Address": new_address, 
#                 "Maps_Link": new_map, 
#                 "Organiser_Name": new_org, 
#                 "Notes": new_notes, 
#                 "Last_Edited_By": st.session_state.get('user_name', 'Admin')
#             })
            
#             # Reconstruct the dataframe for update
#             df_events_updated = pd.concat([df_events[df_events['Event_ID'] != eid], pd.DataFrame([updated_row])], ignore_index=True)
            
#             if db.update_table("Events", df_events_updated):
#                 st.success("Details Updated!")
#                 st.rerun()

#     st.divider()
#     st.subheader("👥 Event Contacts")
    
#     df_con = get_data("Event_Contacts")
#     current_contacts = df_con[df_con['Event_ID'] == eid] if not df_con.empty else pd.DataFrame()
    
#     if not current_contacts.empty:
#         for idx, row in current_contacts.iterrows():
#             with st.expander(f"{row['Role']}: {row['Name']}"):
#                 st.write(f"📞 {row['Phone']} | 📧 {row['Email']}")
#                 st.write(f"💬 Preferred: {row.get('Preferred_Method', 'Not Specified')}")
                
#                 if is_adm and st.button("🗑️ Remove", key=f"del_{idx}"):
#                     df_con_updated = df_con.drop(idx)
#                     db.update_table("Event_Contacts", df_con_updated)
#                     st.rerun()

#     # --- ADD CONTACT WITH VALIDATION ---
#     with st.popover("➕ Add New Contact", use_container_width=True):
#         with st.form("add_contact_form", clear_on_submit=True):
#             r1c1, r1c2 = st.columns([2, 1])
#             c_name = r1c1.text_input("Full Name*")
#             c_role = r1c2.selectbox("Role", ["Site Manager", "Organizer", "Billing", "Electrician", "Security"])
            
#             r2c1, r2c2 = st.columns(2)
#             c_phone = r2c1.text_input("Phone Number*")
#             c_email = r2c2.text_input("Email Address*")
            
#             c_pref = st.radio("Preferred Contact Method", ["Phone", "Email", "WhatsApp"], horizontal=True)
            
#             if st.form_submit_button("💾 Save Contact", use_container_width=True):
#                 is_email = bool(re.match(r"[^@]+@[^@]+\.[^@]+", c_email))
#                 is_phone = len(re.sub(r'\D', '', c_phone)) >= 10
                
#                 if not (c_name and is_email and is_phone):
#                     st.error("Check Name, Email (@), and Phone (10 digits).")
#                 else:
#                     new_c = {
#                         "Event_ID": eid, "Name": c_name, "Phone": c_phone, 
#                         "Email": c_email, "Role": c_role, "Preferred_Method": c_pref
#                     }
#                     if db.insert_row("Event_Contacts", new_c):
#                         st.success(f"Added {c_name}!")
#                         st.rerun()

#     render_mini_map(event_core.get('Address', ''))
