import streamlit as st
import pandas as pd
from datetime import datetime

# --- 📦 MODULAR IMPORTS ---
from app_pages.workspace_tabs.tab_overview import render_overview_tab
from app_pages.workspace_tabs.tab_logistics import render_logistics_tab
from app_pages.workspace_tabs.tab_reports import render_reports_tab
from app_pages.workspace_tabs.tab_staffing import render_staffing_tab
from app_pages.workspace_tabs.tab_sales import render_sales_tab

def show_event_workspace(eid, get_data, db):
    """
    MASTER CONTROLLER: show_event_workspace
    Handles data acquisition and tab routing.
    """
    # --- 🛡️ 1. DATA ACQUISITION ---
    # df_events = get_data("Events")
    df_events['Date'] = pd.to_datetime(df_events['Date'], errors='coerce')
    event_match = df_events[df_events['Event_ID'].astype(str) == str(eid)]
    
    if event_match.empty:
        st.error(f"Event ID {eid} not found."); return
    
    event_core = event_match.iloc[0].copy()
    is_adm = st.session_state.get('user_role') == "Admin"

    # # --- 📅 2. DATE LOGIC (Multi-Day Support) ---
    # try:
    #     start_dt = pd.to_datetime(event_core['Date'], dayfirst=True)
    #     end_val = event_core.get('End_Date')
    #     if pd.isna(end_val) or end_val == "" or str(end_val).lower() == "none":
    #         end_dt = start_dt
    #     else:
    #         end_dt = pd.to_datetime(end_val, dayfirst=True)
    #     date_range = pd.date_range(start=start_dt, end=end_dt).date.tolist()
    # except Exception as e:
    #     st.error(f"📅 Date Error: {e}")
    #     date_range = [datetime.now().date()]
    # --- 📅 2. DATE LOGIC (Updated for ISO Accuracy) ---
    try:
        start_dt = pd.to_datetime(event_core['Date'], errors='coerce') 
        
        end_val = event_core.get('End_Date')
        if pd.isna(end_val) or end_val == "" or str(end_val).lower() == "none":
            end_dt = start_dt
        else:
            end_dt = pd.to_datetime(end_val, errors='coerce')
    
        if pd.notna(start_dt) and pd.notna(end_dt):
            date_range = pd.date_range(start=start_dt, end=end_dt).date.tolist()
        else:
            date_range = [datetime.now().date()]
        
except Exception as e:
    st.error(f"📅 Date Error: {e}")
    date_range = [datetime.now().date()]

    # --- 🏗️ UI HEADER ---
    h1, h2 = st.columns([3, 1])
    h1.title(f"📂 {event_core['Venue']}")
    if h2.button("⬅️ Back to Home", use_container_width=True):
        st.session_state.page = "🏠 Home Dashboard"
        st.rerun()

    # --- 🗓️ DAILY SELECTOR ---
    selected_report_date = date_range[0]
    if len(date_range) > 1:
        selection = st.segmented_control(
            "Select Reporting Day", 
            options=date_range, 
            format_func=lambda x: x.strftime("%a, %d %b"), 
            default=date_range[0]
        )
        if selection: selected_report_date = selection

    # --- 📑 TAB DEFINITION ---
    tab_ov, tab_log, tab_rep, tab_staff, tab_sales = st.tabs([
        "📊 Overview", "🚛 Logistics", "📝 Daily Report", "👥 Staffing", "💰 Sales"
    ])
    
    # --- 🚀 MODULE ROUTING ---
    
    with tab_ov:
        render_overview_tab(eid, event_core, df_events, db, get_data, is_adm)

    with tab_log:
        render_logistics_tab(eid, db, get_data, is_adm)

    with tab_rep:
        render_reports_tab(eid, selected_report_date, db, get_data)

    with tab_staff:
        render_staffing_tab(eid, db, get_data, is_adm)

    with tab_sales:
        render_sales_tab(eid, selected_report_date, db, get_data)

# import streamlit as st
# import pandas as pd
# import re
# from datetime import datetime
# from modules.ui_utils import render_mini_map
# import time
# # from square.client import Client
# # from app_pages.event_workspace_tab5 import render_sales_tab

# def show_event_workspace(eid, get_data, db):
#     # --- 🛡️ 1. DATA ACQUISITION & SCHEMA MAPPING ---
#     df_events = get_data("Events")
#     event_match = df_events[df_events['Event_ID'] == eid]
    
#     if event_match.empty:
#         st.error(f"Event ID {eid} not found."); return
    
#     event_core = event_match.iloc[0].copy()
#     is_adm = st.session_state.get('user_role') == "Admin"

#     # --- 📅 2. DATE LOGIC (Multi-Day Support) ---
#     try:
#         # Ensure we handle various date formats gracefully
#         start_dt = pd.to_datetime(event_core['Date'], dayfirst=True)
#         end_val = event_core.get('End_Date')
        
#         if pd.isna(end_val) or end_val == "" or str(end_val).lower() == "none":
#             end_dt = start_dt
#         else:
#             end_dt = pd.to_datetime(end_val, dayfirst=True)
            
#         date_range = pd.date_range(start=start_dt, end=end_dt).date.tolist()
#     except Exception as e:
#         st.error(f"📅 Date Formatting Error: {e}")
#         date_range = [datetime.now().date()]

#     # --- 🏗️ UI HEADER ---
#     h1, h2 = st.columns([3, 1])
#     h1.title(f"📂 {event_core['Venue']}")
    
#     # Updated navigation to match your main.py page name
#     if h2.button("⬅️ Back to Home", use_container_width=True):
#         st.session_state.page = "🏠 Event Hub"
#         st.rerun()

#     # --- 🗓️ DAILY SELECTOR ---
#     selected_report_date = date_range[0]
#     if len(date_range) > 1:
#         selection = st.segmented_control(
#             "Select Reporting Day", 
#             options=date_range, 
#             format_func=lambda x: x.strftime("%a, %d %b"), 
#             default=date_range[0]
#         )
#         if selection: 
#             selected_report_date = selection

#     tab_ov, tab_log, tab_rep, tab_staff, tab_sales = st.tabs([
#         "📊 Overview", "🚛 Logistics", "📝 Daily Report", "👥 Staffing", "💰 Sales"
#     ])
    
#    # ==========================================
#     # 📊 TAB 1: OVERVIEW
#     # ==========================================
#     with tab_ov:
#         # 1. Local Variables
#         is_multi = str(event_core.get('Is_Multi_Day', 'No')) == "Yes"
        
#         col_ov_h, col_ov_ed = st.columns([3, 1])
#         with col_ov_h: 
#             st.subheader("📍 Core Event Details")
        
#         # 2. Access Check
#         edit_mode = False
#         if is_adm:
#             edit_mode = col_ov_ed.toggle("🔓 Edit Details", value=False)
#         else:
#             col_ov_ed.info("🔒 View Only")

#         # 3. The Core Details Form
#         with st.form("edit_core_details", border=True):
#             c1, c2 = st.columns(2)
#             with c1:
#                 new_venue = st.text_input("Venue Name", value=event_core['Venue'], disabled=not edit_mode)
#                 new_start = st.date_input("Start Date", value=start_dt.date(), disabled=not edit_mode)
#                 new_multi = st.selectbox("Multi-Day Event?", ["Yes", "No"], 
#                                          index=0 if is_multi else 1, disabled=not edit_mode)
#                 new_end = st.date_input("End Date", value=end_dt.date(), disabled=not (edit_mode and new_multi == "Yes"))
#             with c2:
#                 new_address = st.text_area("Event Address", value=str(event_core.get('Address', '')), disabled=not edit_mode, height=68)
#                 new_map = st.text_input("Maps Link", value=str(event_core.get('Maps_Link', '')), disabled=not edit_mode)
#                 new_org = st.text_input("Organiser Name", value=str(event_core.get('Organiser_Name', '')), disabled=not edit_mode)
            
#             new_notes = st.text_area("Internal Notes", value=str(event_core.get('Notes', '')), disabled=not edit_mode)

#             save_btn = st.form_submit_button("💾 Save Core Changes", use_container_width=True, disabled=not edit_mode)

#             if save_btn and edit_mode:
#                 updated_row = event_core.to_dict()
#                 updated_row.update({
#                     "Venue": new_venue, 
#                     "Date": new_start.strftime('%d/%m/%Y'), 
#                     "End_Date": new_end.strftime('%d/%m/%Y'),
#                     "Is_Multi_Day": new_multi, 
#                     "Address": new_address, 
#                     "Maps_Link": new_map, 
#                     "Organiser_Name": new_org, 
#                     "Notes": new_notes, 
#                     "Last_Edited_By": st.session_state.get('user_name', 'Admin')
#                 })
                
#                 # SUPABASE MIGRATION: Replace conn.update with db.update_table
#                 # We filter out the old row and add the updated one
#                 df_events_updated = pd.concat([df_events[df_events['Event_ID'] != eid], pd.DataFrame([updated_row])], ignore_index=True)
                
#                 if db.update_table("Events", df_events_updated):
#                     st.success("Details Updated!")
#                     st.rerun()

#         st.divider()
#         st.subheader("👥 Event Contacts")
        
#         df_con = get_data("Event_Contacts")
#         current_contacts = df_con[df_con['Event_ID'] == eid] if not df_con.empty else pd.DataFrame()
        
#         if not current_contacts.empty:
#             for idx, row in current_contacts.iterrows():
#                 with st.expander(f"{row['Role']}: {row['Name']}"):
#                     st.write(f"📞 {row['Phone']} | 📧 {row['Email']}")
#                     st.write(f"💬 Preferred: {row.get('Preferred_Method', 'Not Specified')}")
                    
#                     if is_adm and st.button("🗑️ Remove", key=f"del_{idx}"):
#                         # SUPABASE MIGRATION: Update table after dropping the contact row
#                         df_con_updated = df_con.drop(idx)
#                         db.update_table("Event_Contacts", df_con_updated)
#                         st.rerun()

#         # --- ADD CONTACT WITH VALIDATION ---
#         with st.popover("➕ Add New Contact", use_container_width=True):
#             with st.form("add_contact_form", clear_on_submit=True):
#                 r1c1, r1c2 = st.columns([2, 1])
#                 c_name = r1c1.text_input("Full Name*")
#                 c_role = r1c2.selectbox("Role", ["Site Manager", "Organizer", "Billing", "Electrician", "Security"])
                
#                 r2c1, r2c2 = st.columns(2)
#                 c_phone = r2c1.text_input("Phone Number*")
#                 c_email = r2c2.text_input("Email Address*")
                
#                 c_pref = st.radio("Preferred Contact Method", ["Phone", "Email", "WhatsApp"], horizontal=True)
                
#                 if st.form_submit_button("💾 Save Contact", use_container_width=True):
#                     is_email = bool(re.match(r"[^@]+@[^@]+\.[^@]+", c_email))
#                     is_phone = len(re.sub(r'\D', '', c_phone)) >= 10
                    
#                     if not (c_name and is_email and is_phone):
#                         st.error("Check Name, Email (@), and Phone (10 digits).")
#                     else:
#                         new_c = {
#                             "Event_ID": eid, "Name": c_name, "Phone": c_phone, 
#                             "Email": c_email, "Role": c_role, "Preferred_Method": c_pref
#                         }
#                         # SUPABASE MIGRATION: Using insert_row for new entries
#                         if db.insert_row("Event_Contacts", new_c):
#                             st.success(f"Added {c_name}!")
#                             st.rerun()

#         render_mini_map(event_core.get('Address', ''))

#     # ==========================================
#     # 🚛 TAB 2: LOGISTICS
#     # ==========================================
#     with tab_log:
#         st.subheader("🚛 Logistics & Setup Details")

#         # Use the name consistent with your database schema
#         df_log = get_data("logistics_details")
        
#         if not df_log.empty and 'Event_ID' in df_log.columns:
#             log_match = df_log[df_log['Event_ID'] == eid]
#             curr_log = log_match.iloc[0] if not log_match.empty else {}
#         else:
#             curr_log = {}
#             if df_log.empty or 'Event_ID' not in df_log.columns:
#                 df_log = pd.DataFrame(columns=['Event_ID', 'Setup_Type', 'Bump_In', 'Bump_Out', 'Parking', 'Log_Notes'])

#         # Admin Toggle
#         edit_log = False
#         if is_adm:
#             edit_log = st.toggle("🔓 Edit Logistics", key="log_edit_toggle", value=False)
#         else:
#             st.info("🔒 View Only: Logistics are managed by Admins.")

#         with st.form("logistics_details_form", border=True):
#             # Row 1: Bump In & Bump Out
#             r1c1, r1c2 = st.columns(2)
#             new_bump_in = r1c1.text_input("Bump In Time", value=str(curr_log.get("Bump_In", "08:00")), disabled=not edit_log)
#             new_bump_out = r1c2.text_input("Bump Out Time", value=str(curr_log.get("Bump_Out", "18:00")), disabled=not edit_log)

#             # Row 2: Setup Type & Parking
#             r2c1, r2c2 = st.columns(2)
#             setup_list = ["Marquee", "Food Truck", "Indoor", "Cart"]
#             try:
#                 current_val = curr_log.get("Setup_Type", "Food Truck")
#                 current_setup_idx = setup_list.index(current_val) if current_val in setup_list else 1
#             except (ValueError, AttributeError):
#                 current_setup_idx = 1
            
#             new_setup = r2c1.selectbox("Setup Type", setup_list, index=current_setup_idx, disabled=not edit_log)
#             new_parking = r2c2.text_input("Parking Info", value=str(curr_log.get("Parking", "")), disabled=not edit_log)

#             # Row 3: Full Width Notes
#             new_log_notes = st.text_area("Logistics Notes", value=str(curr_log.get("Log_Notes", "")), disabled=not edit_log)

#             # Submit Button
#             log_save_btn = st.form_submit_button("💾 Save Logistics", use_container_width=True, disabled=not edit_log)

#             if log_save_btn and edit_log:
#                 new_log_row = {
#                     "Event_ID": eid, 
#                     "Setup_Type": new_setup, 
#                     "Bump_In": new_bump_in,
#                     "Bump_Out": new_bump_out, 
#                     "Parking": new_parking, 
#                     "Log_Notes": new_log_notes
#                 }
                
#                 # SUPABASE MIGRATION: 
#                 # Filter old record out and concat the new one
#                 df_log_updated = df_log[df_log['Event_ID'] != eid].copy() if 'Event_ID' in df_log.columns else df_log.copy()
#                 df_log_updated = pd.concat([df_log_updated, pd.DataFrame([new_log_row])], ignore_index=True)
                
#                 # Update the "Logistics" table
#                 if db.update_table("Logistics", df_log_updated):
#                     st.success("Logistics Updated!")
#                     st.rerun()
#    # ==========================================
#     # 📝 TAB 3: DAILY REPORT
#     # ==========================================
#     with tab_rep:
#         rep_date_str = selected_report_date.strftime('%d/%m/%Y')
#         st.subheader(f"📝 Report: {selected_report_date.strftime('%A, %d %b')}")
        
#         df_rep = get_data("Event_Reports")
        
#         # --- CRITICAL: Normalize Column Names ---
#         df_rep.columns = [str(c).strip() for c in df_rep.columns]
        
#         # Filter for the specific event and date
#         if not df_rep.empty and 'Event_ID' in df_rep.columns:
#             day_match = df_rep[(df_rep['Event_ID'] == eid) & (df_rep['Report_Date'] == rep_date_str)]
#             curr_rep = day_match.iloc[0] if not day_match.empty else {}
#         else:
#             curr_rep = {}

#         # --- DATA CLEANING ---
#         raw_stalls = curr_rep.get("Other_Stalls", 0)
#         try:
#             clean_stalls = int(float(raw_stalls)) if pd.notna(raw_stalls) and str(raw_stalls).strip() != "" else 0
#         except (ValueError, TypeError):
#             clean_stalls = 0

#         # --- WEATHER SAFETY ---
#         weather_options = ["Sunny", "Cloudy", "Rainy", "Windy", "Heat"]
#         saved_weather = curr_rep.get("Weather", "Sunny")
#         w_index = weather_options.index(saved_weather) if saved_weather in weather_options else 0

#         with st.form("daily_rep"):
#             c1, c2 = st.columns(2)
#             weather = c1.selectbox("☀️ Weather", options=weather_options, index=w_index)
            
#             t_leave = c1.text_input("🚗 Time Leave House", value=curr_rep.get("Time_Leave", "06:00"))
#             t_reach = c1.text_input("📍 Time Reach Site", value=curr_rep.get("Time_Reach", "07:30"))
            
#             stalls = c2.number_input("🍟 Other Stalls", min_value=0, value=clean_stalls)
            
#             water = c2.toggle("🚰 Water Access?", value=(curr_rep.get("Water_Access") == "Yes"))
#             power = c2.toggle("🔌 Power Access?", value=(curr_rep.get("Power_Access") == "Yes"))
#             gen = st.text_area("✍️ General Comments", value=str(curr_rep.get("General_Comments", "")))
            
#             # The Save Button
#             save_btn = st.form_submit_button("💾 Save Daily Report", use_container_width=True)
            
#             if save_btn:
#                 new_report_row = {
#                     "Event_ID": eid, 
#                     "Report_Date": rep_date_str, 
#                     "Weather": weather,
#                     "Time_Leave": t_leave, 
#                     "Time_Reach": t_reach, 
#                     "Other_Stalls": stalls,
#                     "Water_Access": "Yes" if water else "No", 
#                     "Power_Access": "Yes" if power else "No",
#                     "General_Comments": gen
#                 }
                
#                 # SUPABASE MIGRATION: Logic to replace existing entry
#                 # Filter out the specific row if it exists (masking both ID and Date)
#                 if not df_rep.empty and 'Event_ID' in df_rep.columns:
#                     mask = (df_rep['Event_ID'] == eid) & (df_rep['Report_Date'] == rep_date_str)
#                     df_rep_updated = pd.concat([df_rep[~mask], pd.DataFrame([new_report_row])], ignore_index=True)
#                 else:
#                     df_rep_updated = pd.DataFrame([new_report_row])
                
#                 # Write back to Supabase
#                 if db.update_table("Event_Reports", df_rep_updated):
#                     st.cache_data.clear() 
#                     st.success(f"Report for {rep_date_str} Saved!")
#                     st.rerun()

#   # ==========================================
#     # 👥 TAB 4: STAFFING
#     # ==========================================
#     with tab_staff:
#         st.subheader("📋 Available Staff Gallery")

#         # FETCH DATA using Supabase/get_data
#         df_staff_db = get_data("Staff_Database")
#         df_staffing = get_data("Event_Staffing")
        
#         if df_staffing.empty or 'Event_ID' not in df_staffing.columns:
#             df_staffing = pd.DataFrame(columns=['Event_ID', 'Staff_Name', 'Start_Time', 'End_Time', 'Payment_Status', 'Type'])

#         assigned_names = df_staffing[df_staffing['Event_ID'] == eid]['Staff_Name'].tolist()

#         if not df_staff_db.empty:
#             card_grid = st.columns(2)
            
#             for i, (idx, s_row) in enumerate(df_staff_db.iterrows()):
#                 name = s_row['Staff_Name']
                
#                 # --- 📞 PHONE CLEANING ---
#                 raw_phone = str(s_row.get('Phone', ''))
#                 clean_phone = raw_phone.split('.')[0].strip()

#                 # Re-add leading zero for Aus Mobile
#                 if len(clean_phone) == 9 and clean_phone.startswith('4'):
#                     clean_phone = "0" + clean_phone

#                 if clean_phone.lower() == "nan" or not clean_phone:
#                     clean_phone = None

#                 # --- ⭐ STAR RATING LOGIC ---
#                 try:
#                     num_stars = int(float(s_row.get('Rating', 0)))
#                 except:
#                     num_stars = 0
#                 star_display = "⭐" * num_stars if num_stars > 0 else "No Rating"

#                 with card_grid[i % 2]:
#                     with st.container(border=True):
#                         h1, h2 = st.columns([3, 1])
#                         h1.markdown(f"**{name}**")
#                         h2.markdown("🟢 **Active**" if name in assigned_names else "⚪ **Idle**")
                        
#                         if clean_phone:
#                             st.markdown(f"📞 [ {clean_phone} ](tel:{clean_phone})")
#                         else:
#                             st.caption("📞 Phone: N/A")

#                         st.caption(f"Rating: {star_display}")
#                         st.write(f"🛠️ **Skills:** {s_row.get('Skills', 'N/A')}")
                        
#                         if name in assigned_names:
#                             if is_adm:
#                                 if st.button(f"❌ Remove {name.split()[0]}", key=f"rem_{idx}", use_container_width=True):
#                                     # SUPABASE MIGRATION: Filter out assigned staff
#                                     df_staffing_updated = df_staffing[~((df_staffing['Event_ID'] == eid) & (df_staffing['Staff_Name'] == name))]
#                                     if db.update_table("Event_Staffing", df_staffing_updated):
#                                         st.rerun()
#                         else:
#                             with st.expander("➕ Assign to Event"):
#                                 with st.form(key=f"assign_f_{idx}"):
#                                     c1, c2 = st.columns(2)
#                                     # Fallback defaults if logistics variables aren't locally available
#                                     st_time_str = c1.text_input("Start", value="08:00")
#                                     en_time_str = c2.text_input("End", value="18:00")

#                                     # --- ⚠️ 8-HOUR WARNING LOGIC ---
#                                     from datetime import datetime
#                                     try:
#                                         fmt = '%H:%M'
#                                         t1 = datetime.strptime(st_time_str, fmt)
#                                         t2 = datetime.strptime(en_time_str, fmt)
#                                         delta = (t2 - t1).total_seconds() / 3600
#                                         if delta < 0: delta += 24 
                                        
#                                         if delta > 8:
#                                             st.warning(f"⚠️ Long Shift: {delta:.1f} hrs")
#                                     except:
#                                         pass

#                                     if st.form_submit_button("Confirm Assignment", use_container_width=True):
#                                         new_entry = {
#                                             "Event_ID": eid, "Staff_Name": name, "Start_Time": st_time_str,
#                                             "End_Time": en_time_str, "Payment_Status": "Pending", "Type": "Standard"
#                                         }
#                                         # SUPABASE MIGRATION: 
#                                         if db.insert_row("Event_Staffing", new_entry):
#                                             st.success(f"{name} added!")
#                                             st.rerun()
#         else:
#             st.warning("No staff found in Staff_Database.")

#         st.divider()

#         # --- ➕ ADMIN QUICK ADD ---
#         if is_adm:
#             with st.expander("➕ Assign Staff Member (Search)"):
#                 with st.form("add_staff_form_quick", clear_on_submit=True):
#                     staff_options = df_staff_db['Staff_Name'].tolist() if not df_staff_db.empty else []
#                     sel_staff = st.selectbox("Select Staff", staff_options)
                    
#                     col1, col2 = st.columns(2)
#                     s_time = col1.text_input("Start Time", value="08:00")
#                     e_time = col2.text_input("End Time", value="18:00")
                    
#                     if st.form_submit_button("Assign to Event", use_container_width=True):
#                         if sel_staff:
#                             new_entry_quick = {
#                                 "Event_ID": eid, "Staff_Name": sel_staff,
#                                 "Start_Time": s_time, "End_Time": e_time,
#                                 "Payment_Status": "Pending", "Type": "Standard"
#                             }
#                             if db.insert_row("Event_Staffing", new_entry_quick):
#                                 st.success(f"Added {sel_staff}!")
#                                 st.rerun()
#         else:
#             st.caption("Only Admins can modify the roster.")
# # ==========================================
#     # 💰 TAB 5: SALES (Full Logic + Supabase)
#     # ==========================================
#     with tab_sales:
#         @st.cache_data(ttl=600)
#         def get_sales_data():
#             return db.read_table("event_sales")

#         df_master_events = get_data("Events") 
#         df_sales_dest = get_sales_data()

#         # Force column lowercase for reliability
#         if not df_sales_dest.empty:
#             df_sales_dest.columns = [str(c).lower().strip() for c in df_sales_dest.columns]
#         else:
#             df_sales_dest = pd.DataFrame(columns=['event_id', 'total_revenue', 'card_sales', 'cash_sales'])

#         # Get Event Info for Metrics
#         event_info = df_master_events[df_master_events['Event_ID'] == eid]
#         venue_name = event_info.iloc[0]['Venue'] if not event_info.empty else "Unknown"
#         is_multi = str(event_info.iloc[0].get('Is_Multi_Day', 'No')) == "Yes"
        
#         # METRICS
#         day_total = df_sales_dest[df_sales_dest['event_id'] == str(eid)]['total_revenue'].sum()
        
#         m_col1, m_col2 = st.columns(2)
#         m_col1.metric("Today's Gross", f"${day_total:,.2f}")
#         if is_multi:
#             # Shows total for this venue across all dates
#             m_col2.metric("Total for Venue", f"${day_total:,.2f}")
        
#         st.divider()

#         # --- FORM STATE ---
#         if "form_id" not in st.session_state: st.session_state.form_id = 0
#         if "fill_val" not in st.session_state: st.session_state.fill_val = 0.0

#         # --- THE FRAGMENT ---
#         @st.fragment
#         def render_sales_form():
#             st.subheader(f"📝 Sales Entry: {selected_report_date.strftime('%d/%m/%Y')}")
#             fid = st.session_state.form_id
            
#             # 1. TOTAL PAYMENTS
#             st.markdown("#### 1. Total Payments")
#             p1, p2 = st.columns(2)
#             v_card = p1.number_input("Card / Eftpos", min_value=0.0, step=1.0, key=f"eftpos_{fid}")
#             v_cash = p2.number_input("Cash", min_value=0.0, step=1.0, key=f"cash_{fid}")
            
#             t_gross = v_card + v_cash
#             st.markdown(f"### Gross Total: :green[${t_gross:,.2f}]")
#             st.divider()
            
#             # 2. CATEGORY INPUTS
#             st.markdown("#### 2. Categories")
#             c1, c2, c3, c4 = st.columns(4)
#             v_quick = c1.number_input("Quick", min_value=0.0, step=1.0, key=f"quick_{fid}")
#             v_food = c2.number_input("Food", min_value=0.0, step=1.0, key=f"food_{fid}")
#             v_drinks = c3.number_input("Drinks", min_value=0.0, step=1.0, key=f"drinks_{fid}")
#             v_uncat = c4.number_input("Uncategorised", min_value=0.0, step=1.0, value=st.session_state.fill_val, key=f"uncat_{fid}")
            
#             st.session_state.fill_val = v_uncat

#             # 3. BALANCING LOGIC
#             cat_sum = v_quick + v_food + v_drinks + v_uncat
#             diff = t_gross - cat_sum
            
#             st.divider()
            
#             if abs(diff) > 0.01:
#                 b_col1, b_col2 = st.columns([2, 1])
#                 b_col1.warning(f"⚠️ **Remaining to balance: ${diff:,.2f}**")
#                 if diff > 0:
#                     if b_col2.button(f"Auto-Fill ${diff:,.0f}", use_container_width=True):
#                         st.session_state.fill_val = float(v_uncat + diff)
#                         st.rerun(scope="fragment")
#             else:
#                 st.success("✅ Totals Balance Perfectly!")

#             # 4. SAVE LOGIC
#             if round(t_gross, 2) == round(cat_sum, 2) and t_gross > 0:
#                 if st.button("💾 Save Sales Record", use_container_width=True, type="primary"):
#                     new_row = {
#                         "event_id": str(eid),
#                         "card_sales": float(v_card),
#                         "cash_sales": float(v_cash),
#                         "total_revenue": float(t_gross),
#                         "opening_float": 0.0, # Adjust if you want to add float inputs
#                         "closing_float": 0.0
#                     }
                    
#                     # NOTE: If your Supabase has columns for Quick/Food/Drinks, 
#                     # add them to the dictionary above!
                    
#                     try:
#                         if db.insert_row("event_sales", new_row):
#                             st.session_state.form_id += 1
#                             st.session_state.fill_val = 0.0
#                             st.cache_data.clear() 
#                             st.success("✅ Saved!")
#                             time.sleep(1)
#                             st.rerun() 
#                     except Exception as e:
#                         st.error(f"Error: {e}")

#         # EXECUTE
#         render_sales_form()
# # # ==========================================
# #     # 💰 TAB 5: SALES (Final KeyError Fix)
# #     # ==========================================
# #     with tab_sales:
# #         @st.cache_data(ttl=600)
# #         def get_sales_data():
# #             return db.read_table("event_sales")

# #         df_master_events = get_data("Events") 
# #         df_sales_dest = get_sales_data()

# #         # --- 🛡️ THE FIX: Force Case-Insensitivity ---
# #         if not df_sales_dest.empty:
# #             # Force all column names to lowercase to match your SQL schema
# #             df_sales_dest.columns = [str(c).lower().strip() for c in df_sales_dest.columns]
# #         else:
# #             # Fallback for empty table so the app doesn't crash
# #             df_sales_dest = pd.DataFrame(columns=['event_id', 'total_revenue', 'card_sales', 'cash_sales', 'created_at'])

# #         # Safety Check: Ensure 'event_id' actually exists now
# #         if 'event_id' not in df_sales_dest.columns:
# #             st.error(f"🚨 Table 'event_sales' found, but column 'event_id' is missing. Columns: {list(df_sales_dest.columns)}")
# #             st.stop()

# #         # Fetch Event Info from Master
# #         event_match = df_master_events[df_master_events['Event_ID'] == eid]
# #         venue_name = event_match.iloc[0]['Venue'] if not event_match.empty else "Unknown"
        
# #         # METRICS
# #         day_total = df_sales_dest[df_sales_dest['event_id'] == str(eid)]['total_revenue'].sum()
        
# #         m_col1, m_col2 = st.columns(2)
# #         m_col1.metric("Today's Gross", f"${day_total:,.2f}")
        
# #         st.divider()

# #         # --- REST OF THE TAB (FORM & FRAGMENT) ---
# #         if "form_id" not in st.session_state: st.session_state.form_id = 0

# #         @st.fragment
# #         def render_sales_form():
# #             st.subheader(f"📝 Sales Entry: {selected_report_date.strftime('%d/%m/%Y')}")
# #             fid = st.session_state.form_id
            
# #             with st.container(border=True):
# #                 p1, p2 = st.columns(2)
# #                 v_card = p1.number_input("Card Sales", min_value=0.0, step=1.0, key=f"card_{fid}")
# #                 v_cash = p2.number_input("Cash Sales", min_value=0.0, step=1.0, key=f"cash_{fid}")
                
# #                 t_rev = v_card + v_cash
# #                 st.markdown(f"### Total: :green[${t_rev:,.2f}]")

# #                 if t_rev > 0:
# #                     if st.button("💾 Save to Supabase", use_container_width=True, type="primary"):
# #                         new_row = {
# #                             "event_id": str(eid),
# #                             "card_sales": float(v_card),
# #                             "cash_sales": float(v_cash),
# #                             "total_revenue": float(t_rev),
# #                             "opening_float": 0.0,
# #                             "closing_float": 0.0
# #                         }
# #                         if db.insert_row("event_sales", new_row):
# #                             st.session_state.form_id += 1
# #                             st.cache_data.clear()
# #                             st.success("Saved!")
# #                             st.rerun()

# #         render_sales_form() 
# # # ==========================================
#   #   # 💰 TAB 5: SALES (Schema Aligned)
#   #   # ==========================================
#   #   with tab_sales:
#   #       @st.cache_data(ttl=600)
#   #       def get_sales_data():
#   #           return db.read_table("event_sales") # Table is lowercase in SQL

#   #       df_sales_dest = get_sales_data()
        
#   #       # --- 🛡️ Schema Mapping & Safety ---
#   #       if not df_sales_dest.empty:
#   #           df_sales_dest.columns = [str(c).strip() for c in df_sales_dest.columns]
#   #       else:
#   #           df_sales_dest = pd.DataFrame(columns=['event_id', 'total_revenue', 'card_sales', 'cash_sales'])

#   #       # Logic Mapping:
#   #       # 'Event_ID' -> 'event_id'
#   #       # 'Total_Gross_Sales' -> 'total_revenue'
#   #       # 'Eftpos' -> 'card_sales'
#   #       # 'Cash' -> 'cash_sales'

#   #       event_info = df_master_events[df_master_events['Event_ID'] == eid]
#   #       venue_name = event_info.iloc[0]['Venue'] if not event_info.empty else "Unknown"
#   #       is_multi = str(event_info.iloc[0].get('Is_Multi_Day', 'No')) == "Yes"
        
#   #       # METRICS (Updated to use lowercase snake_case columns)
#   #       day_total = 0.0
#   #       if not df_sales_dest.empty:
#   #           day_total = df_sales_dest[df_sales_dest['event_id'] == str(eid)]['total_revenue'].sum()
        
#   #       m_col1, m_col2 = st.columns(2)
#   #       m_col1.metric("Today's Gross", f"${day_total:,.2f}")
        
#   #       st.divider()

#   #       # 2. FORM STATE
#   #       if "form_id" not in st.session_state: st.session_state.form_id = 0
#   #       if "fill_val" not in st.session_state: st.session_state.fill_val = 0.0

#   #       # 3. THE FRAGMENT
#   #       @st.fragment
#   #       def render_sales_form():
#   #           st.subheader(f"📝 Sales Entry: {selected_report_date.strftime('%d/%m/%Y')}")
#   #           fid = st.session_state.form_id
            
#   #           st.markdown("#### 1. Total Payments")
#   #           p1, p2 = st.columns(2)
#   #           v_card = p1.number_input("Card / Eftpos", min_value=0.0, step=1.0, key=f"card_{fid}")
#   #           v_cash = p2.number_input("Cash", min_value=0.0, step=1.0, key=f"cash_{fid}")
            
#   #           t_gross = v_card + v_cash
#   #           st.markdown(f"### Gross Total: :green[${t_gross:,.2f}]")
            
#   #           # --- SAVE LOGIC ---
#   #           if t_gross > 0:
#   #               if st.button("💾 Save Sales Record", use_container_width=True, type="primary"):
#   #                   # Mapping to your SQL schema columns exactly
#   #                   new_row = {
#   #                       "event_id": str(eid), 
#   #                       "card_sales": v_card, 
#   #                       "cash_sales": v_cash,
#   #                       "total_revenue": t_gross,
#   #                       "opening_float": 0.0, # Placeholder based on your SQL
#   #                       "closing_float": 0.0  # Placeholder based on your SQL
#   #                   }
#   #                   try:
#   #                       if db.insert_row("event_sales", new_row):
#   #                           st.session_state.form_id += 1
#   #                           st.cache_data.clear() 
#   #                           st.success("✅ Sales Saved!")
#   #                           time.sleep(1)
#   #                           st.rerun() 
#   #                   except Exception as e:
#   #                       st.error(f"Error: {e}")

#   #       render_sales_form()

   
