import streamlit as st
import pandas as pd
import re
from datetime import datetime
from modules.ui_utils import render_mini_map
import time
# from square.client import Client
# from app_pages.event_workspace_tab5 import render_sales_tab

def show_event_workspace(eid, get_data, conn):
    # --- 🛡️ 1. DATA ACQUISITION & SCHEMA MAPPING ---
    df_events = get_data("Events")
    event_match = df_events[df_events['Event_ID'] == eid]
    
    if event_match.empty:
        st.error(f"Event ID {eid} not found."); return
    
    event_core = event_match.iloc[0].copy()
    is_adm = st.session_state.get('user_role') == "Admin"

    # --- 📅 2. DATE LOGIC (Multi-Day Support) ---
    try:
        start_dt = pd.to_datetime(event_core['Date'], dayfirst=True)
        end_val = event_core.get('End_Date')
        if pd.isna(end_val) or end_val == "" or str(end_val).lower() == "none":
            end_dt = start_dt
        else:
            end_dt = pd.to_datetime(end_val, dayfirst=True)
        date_range = pd.date_range(start=start_dt, end=end_dt).date.tolist()
    except Exception as e:
        st.error(f"📅 Date Formatting Error: {e}")
        date_range = [datetime.now().date()]

    # --- 🏗️ UI HEADER ---
    h1, h2 = st.columns([3, 1])
    h1.title(f"📂 {event_core['Venue']}")
    if h2.button("⬅️ Back to Home", use_container_width=True):
        st.session_state.page = "🏠 Home Dashboard"; st.rerun()

    # --- 🗓️ DAILY SELECTOR ---
    selected_report_date = date_range[0]
    if len(date_range) > 1:
        selection = st.segmented_control("Select Reporting Day", options=date_range, 
                                         format_func=lambda x: x.strftime("%a, %d %b"), default=date_range[0])
        if selection: selected_report_date = selection

    tab_ov, tab_log, tab_rep, tab_staff, tab_sales = st.tabs(["📊 Overview", "🚛 Logistics", "📝 Daily Report", "👥 Staffing", "💰 Sales"])
    
    # ==========================================
    # 📊 TAB 1: OVERVIEW
    # ==========================================
    with tab_ov:
        # 1. Define variables at the top to avoid NameErrors
        is_multi = str(event_core.get('Is_Multi_Day', 'No')) == "Yes"
        
        col_ov_h, col_ov_ed = st.columns([3, 1])
        with col_ov_h: st.subheader("📍 Core Event Details")
        
        # 2. Access Check for the Toggle
        edit_mode = False
        if is_adm:
            edit_mode = col_ov_ed.toggle("🔓 Edit Details", value=False)
        else:
            col_ov_ed.info("🔒 View Only")

        # 3. The Core Details Form
        with st.form("edit_core_details", border=True):
            c1, c2 = st.columns(2)
            with c1:
                new_venue = st.text_input("Venue Name", value=event_core['Venue'], disabled=not edit_mode)
                new_start = st.date_input("Start Date", value=start_dt.date(), disabled=not edit_mode)
                new_multi = st.selectbox("Multi-Day Event?", ["Yes", "No"], 
                                         index=0 if is_multi else 1, disabled=not edit_mode)
                # Logic: Only enabled if Admin toggles Edit AND selects Yes for Multi-Day
                new_end = st.date_input("End Date", value=end_dt.date(), disabled=not (edit_mode and new_multi == "Yes"))
            with c2:
                new_address = st.text_area("Event Address", value=str(event_core.get('Address', '')), disabled=not edit_mode, height=68)
                new_map = st.text_input("Maps Link", value=str(event_core.get('Maps_Link', '')), disabled=not edit_mode)
                new_org = st.text_input("Organiser Name", value=str(event_core.get('Organiser_Name', '')), disabled=not edit_mode)
            
            new_notes = st.text_area("Internal Notes", value=str(event_core.get('Notes', '')), disabled=not edit_mode)

            # --- 🛡️ SUBMIT BUTTON LOGIC (Fixes "Missing Submit Button") ---
            # Button is always visible but only functional for Admin in edit mode
            save_btn = st.form_submit_button("💾 Save Core Changes", use_container_width=True, disabled=not edit_mode)

            if save_btn and edit_mode:
                updated_row = event_core.to_dict()
                updated_row.update({
                    "Venue": new_venue, "Date": new_start.strftime('%d/%m/%Y'), "End_Date": new_end.strftime('%d/%m/%Y'),
                    "Is_Multi_Day": new_multi, "Address": new_address, "Maps_Link": new_map, 
                    "Organiser_Name": new_org, "Notes": new_notes, "Last_Edited_By": st.session_state.get('user_name', 'Admin')
                })
                df_events = pd.concat([df_events[df_events['Event_ID'] != eid], pd.DataFrame([updated_row])], ignore_index=True)
                conn.update(worksheet="Events", data=df_events)
                st.success("Details Updated!"); st.rerun()

        st.divider()
        st.subheader("👥 Event Contacts")
        
        # Display existing contacts
        df_con = get_data("Event_Contacts")
        current_contacts = df_con[df_con['Event_ID'] == eid] if not df_con.empty else pd.DataFrame()
        
        if not current_contacts.empty:
            for idx, row in current_contacts.iterrows():
                with st.expander(f"{row['Role']}: {row['Name']}"):
                    st.write(f"📞 {row['Phone']} | 📧 {row['Email']}")
                    st.write(f"💬 Preferred: {row.get('Preferred_Method', 'Not Specified')}")
                    # Only Admin can delete contacts
                    if is_adm and st.button("🗑️ Remove", key=f"del_{idx}"):
                        conn.update(worksheet="Event_Contacts", data=df_con.drop(idx))
                        st.rerun()

        # --- 🛡️ ADD CONTACT WITH VALIDATION (COMPACT LAYOUT) ---
        with st.popover("➕ Add New Contact", use_container_width=True):
            with st.form("add_contact_form", clear_on_submit=True):
                # Row 1: Name and Role
                r1c1, r1c2 = st.columns([2, 1])
                c_name = r1c1.text_input("Full Name*")
                c_role = r1c2.selectbox("Role", ["Site Manager", "Organizer", "Billing", "Electrician", "Security"])
                
                # Row 2: Phone and Email
                r2c1, r2c2 = st.columns(2)
                c_phone = r2c1.text_input("Phone Number*")
                c_email = r2c2.text_input("Email Address*")
                
                # Row 3: Preferred Method and Submit
                r3c1, r3c2 = st.columns([2, 1])
                c_pref = r3c1.radio("Preferred Contact Method", ["Phone", "Email", "WhatsApp"], horizontal=True)
                
                # Align button to bottom of the row
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("💾 Save Contact", use_container_width=True):
                    # Concise Validation
                    is_email = bool(re.match(r"[^@]+@[^@]+\.[^@]+", c_email))
                    is_phone = len(re.sub(r'\D', '', c_phone)) >= 10
                    
                    if not (c_name and is_email and is_phone):
                        st.error("Check Name, Email (@), and Phone (10 digits).")
                    else:
                        new_c = {
                            "Event_ID": eid, "Name": c_name, "Phone": c_phone, 
                            "Email": c_email, "Role": c_role, "Preferred_Method": c_pref
                        }
                        conn.update(worksheet="Event_Contacts", data=pd.concat([df_con, pd.DataFrame([new_c])], ignore_index=True))
                        st.success(f"Added {c_name}!"); st.rerun()

        render_mini_map(event_core.get('Address', ''))

    # ==========================================
    # 🚛 TAB 2: LOGISTICS
    # ==========================================
    with tab_log:
        st.subheader("🚛 Logistics & Setup Details")

        df_log = get_data("Logistics")
        
        if not df_log.empty and 'Event_ID' in df_log.columns:
            log_match = df_log[df_log['Event_ID'] == eid]
            curr_log = log_match.iloc[0] if not log_match.empty else {}
        else:
            curr_log = {}
            if 'Event_ID' not in df_log.columns:
                df_log = pd.DataFrame(columns=['Event_ID', 'Setup_Type', 'Bump_In', 'Bump_Out', 'Parking', 'Log_Notes'])

        # Admin Toggle
        edit_log = False
        if is_adm:
            edit_log = st.toggle("🔓 Edit Logistics", key="log_edit_toggle", value=False)
        else:
            st.info("🔒 View Only: Logistics are managed by Admins.")

        with st.form("logistics_details_form", border=True):
            # Row 1: Bump In & Bump Out
            r1c1, r1c2 = st.columns(2)
            new_bump_in = r1c1.text_input("Bump In Time", value=str(curr_log.get("Bump_In", "08:00")), disabled=not edit_log)
            new_bump_out = r1c2.text_input("Bump Out Time", value=str(curr_log.get("Bump_Out", "18:00")), disabled=not edit_log)

            # Row 2: Setup Type & Parking
            r2c1, r2c2 = st.columns(2)
            setup_list = ["Marquee", "Food Truck", "Indoor", "Cart"]
            try:
                current_setup_idx = setup_list.index(curr_log.get("Setup_Type", "Food Truck"))
            except ValueError:
                current_setup_idx = 0
            
            new_setup = r2c1.selectbox("Setup Type", setup_list, index=current_setup_idx, disabled=not edit_log)
            new_parking = r2c2.text_input("Parking Info", value=str(curr_log.get("Parking", "")), disabled=not edit_log)

            # Row 3: Full Width Notes
            new_log_notes = st.text_area("Logistics Notes", value=str(curr_log.get("Log_Notes", "")), disabled=not edit_log)

            # Submit Button
            log_save_btn = st.form_submit_button("💾 Save Logistics", use_container_width=True, disabled=not edit_log)

            if log_save_btn and edit_log:
                new_log_data = {
                    "Event_ID": eid, 
                    "Setup_Type": new_setup, 
                    "Bump_In": new_bump_in,
                    "Bump_Out": new_bump_out, 
                    "Parking": new_parking, 
                    "Log_Notes": new_log_notes
                }
                
                # Filter old record and update
                df_log = df_log[df_log['Event_ID'] != eid] if 'Event_ID' in df_log.columns else df_log
                df_log = pd.concat([df_log, pd.DataFrame([new_log_data])], ignore_index=True)
                conn.update(worksheet="Logistics_Details", data=df_log)
                st.success("Logistics Updated!")
                st.rerun()

    # ==========================================
    # 📝 TAB 3: DAILY REPORT (Matches Schema)
    # ==========================================
    with tab_rep:
        rep_date_str = selected_report_date.strftime('%d/%m/%Y')
        st.subheader(f"📝 Report: {selected_report_date.strftime('%A, %d %b')}")
        
        df_rep = get_data("Event_Reports")
        
        # --- CRITICAL: Normalize Column Names ---
        df_rep.columns = [str(c).strip() for c in df_rep.columns]
        
        # Filter for the specific event and date
        day_match = df_rep[(df_rep['Event_ID'] == eid) & (df_rep['Report_Date'] == rep_date_str)]
        curr_rep = day_match.iloc[0] if not day_match.empty else {}

        # --- DATA CLEANING (The Full Stack Habit) ---
        raw_stalls = curr_rep.get("Other_Stalls", 0)
        try:
            clean_stalls = int(float(raw_stalls)) if pd.notna(raw_stalls) and str(raw_stalls).strip() != "" else 0
        except:
            clean_stalls = 0

        # --- WEATHER SAFETY ---
        weather_options = ["Sunny", "Cloudy", "Rainy", "Windy", "Heat"]
        saved_weather = curr_rep.get("Weather", "Sunny")
        w_index = weather_options.index(saved_weather) if saved_weather in weather_options else 0

        with st.form("daily_rep"):
            c1, c2 = st.columns(2)
            weather = c1.selectbox("☀️ Weather", options=weather_options, index=w_index)
            
            t_leave = c1.text_input("🚗 Time Leave House", value=curr_rep.get("Time_Leave", "06:00"))
            t_reach = c1.text_input("📍 Time Reach Site", value=curr_rep.get("Time_Reach", "07:30"))
            
            stalls = c2.number_input("🍟 Other Stalls", min_value=0, value=clean_stalls)
            
            water = c2.toggle("🚰 Water Access?", value=(curr_rep.get("Water_Access") == "Yes"))
            power = c2.toggle("🔌 Power Access?", value=(curr_rep.get("Power_Access") == "Yes"))
            gen = st.text_area("✍️ General Comments", value=str(curr_rep.get("General_Comments", "")))
            
            # The Save Button
            save_btn = st.form_submit_button("💾 Save Daily Report")
            
            if save_btn:
                new_r = {
                    "Event_ID": eid, 
                    "Report_Date": rep_date_str, 
                    "Weather": weather,
                    "Time_Leave": t_leave, 
                    "Time_Reach": t_reach, 
                    "Other_Stalls": stalls,
                    "Water_Access": "Yes" if water else "No", 
                    "Power_Access": "Yes" if power else "No",
                    "General_Comments": gen
                }
                
                # Update the dataframe
                mask = (df_rep['Event_ID'] == eid) & (df_rep['Report_Date'] == rep_date_str)
                df_rep = pd.concat([df_rep[~mask], pd.DataFrame([new_r])], ignore_index=True)
                
                # Write back to Google Sheets
                conn.update(worksheet="Event_Reports", data=df_rep)
                st.cache_data.clear() 
                st.success("Report Saved!")
                st.rerun()

    # ==========================================
    # 👥 TAB 4: STAFFING
    # ==========================================
    with tab_staff:
        st.subheader("📋 Available Staff Gallery")

        df_staff_db = get_data("Staff_Database")
        df_staffing = get_data("Event_Staffing")
        
        if df_staffing.empty or 'Event_ID' not in df_staffing.columns:
            df_staffing = pd.DataFrame(columns=['Event_ID', 'Staff_Name', 'Start_Time', 'End_Time', 'Payment_Status', 'Type'])

        assigned_names = df_staffing[df_staffing['Event_ID'] == eid]['Staff_Name'].tolist()

        if not df_staff_db.empty:
            card_grid = st.columns(2)
            
            for i, (idx, s_row) in enumerate(df_staff_db.iterrows()):
                name = s_row['Staff_Name']
                phone = str(s_row.get('Phone', ''))

                # --- 📞 PHONE CLEANING (Removes the .0) ---
                # raw_phone = str(s_row.get('Phone', ''))
                # clean_phone = int(raw_phone)
               # 1. Get raw string and remove decimal
                raw_phone = str(s_row.get('Phone', ''))
                clean_phone = raw_phone.split('.')[0].strip()

                # 2. Re-add the leading zero if it's an Australian mobile (9 digits needs a 0)
                if len(clean_phone) == 9 and clean_phone.startswith('4'):
                    clean_phone = "0" + clean_phone

                # 3. Handle 'nan' or empty cells
                if clean_phone.lower() == "nan" or not clean_phone:
                    clean_phone = None
                # --- ⭐ STAR RATING LOGIC ---
                try:
                    num_stars = int(s_row.get('Rating', 0))
                except:
                    num_stars = 0
                star_display = "⭐" * num_stars if num_stars > 0 else "No Rating"

                with card_grid[i % 2]:
                    with st.container(border=True):
                        h1, h2 = st.columns([3, 1])
                        h1.markdown(f"**{name}**")
                        h2.markdown("🟢 **Active**" if name in assigned_names else "⚪ **Idle**")
                        
                        # --- 📞 CLICK-TO-CALL LINK ---
                        # if phone:
                        #     st.markdown(f"📞 [ {phone} ](tel:{phone})")
                        # else:
                        #     st.caption("No phone number")
                        if clean_phone:
                            st.markdown(f"📞 [ {clean_phone} ](tel:{clean_phone})")
                        else:
                            st.caption("📞 Phone: N/A")
                            

                        st.caption(f"Rating: {star_display}")
                        st.write(f"🛠️ **Skills:** {s_row.get('Skills', 'N/A')}")
                        
                        if name in assigned_names:
                            if is_adm:
                                if st.button(f"❌ Remove {name.split()[0]}", key=f"rem_{idx}", use_container_width=True):
                                    df_staffing = df_staffing[~((df_staffing['Event_ID'] == eid) & (df_staffing['Staff_Name'] == name))]
                                    conn.update(worksheet="Event_Staffing", data=df_staffing)
                                    st.rerun()
                        else:
                            with st.expander("➕ Assign to Event"):
                                with st.form(key=f"assign_f_{idx}"):
                                    c1, c2 = st.columns(2)
                                    def_in = locals().get('new_bump_in', "08:00")
                                    def_out = locals().get('new_bump_out', "18:00")
                                    
                                    st_time_str = c1.text_input("Start", value=def_in)
                                    en_time_str = c2.text_input("End", value=def_out)

                                    # --- ⚠️ 8-HOUR WARNING LOGIC ---
                                    from datetime import datetime
                                    try:
                                        fmt = '%H:%M'
                                        t1 = datetime.strptime(st_time_str, fmt)
                                        t2 = datetime.strptime(en_time_str, fmt)
                                        delta = (t2 - t1).total_seconds() / 3600
                                        if delta < 0: delta += 24 # Handle shifts crossing midnight
                                        
                                        if delta > 8:
                                            st.warning(f"⚠️ Long Shift: {delta:.1f} hours. Ensure staff gets breaks!")
                                    except:
                                        pass # If time format is invalid, skip warning

                                    if st.form_submit_button("Confirm Assignment", use_container_width=True):
                                        new_entry = {
                                            "Event_ID": eid, "Staff_Name": name, "Start_Time": st_time_str,
                                            "End_Time": en_time_str, "Payment_Status": "Pending", "Type": "Standard"
                                        }
                                        df_staffing = pd.concat([df_staffing, pd.DataFrame([new_entry])], ignore_index=True)
                                        conn.update(worksheet="Event_Staffing", data=df_staffing)
                                        st.success(f"{name} added!")
                                        st.rerun()
        else:
            st.warning("No staff found in Staff_Database.")
        # else:
        #     st.info("No staff assigned to this event yet.")

        st.divider()

        # --- ➕ ADD STAFF (Matching Staff_Database columns) ---
        if is_adm:
            with st.expander("➕ Assign Staff Member"):
                with st.form("add_staff_form", clear_on_submit=True):
                    # Get names from Staff_Database
                    staff_options = df_staff_db['Staff_Name'].tolist() if not df_staff_db.empty else []
                    sel_staff = st.selectbox("Select Staff", staff_options)
                    
                    # Layout for adding
                    col1, col2 = st.columns(2)
                    # Pull defaults from Logistics (locals) if available
                    def_in = locals().get('new_bump_in', "08:00")
                    def_out = locals().get('new_bump_out', "18:00")
                    
                    s_time = col1.text_input("Start Time", value=def_in)
                    e_time = col2.text_input("End Time", value=def_out)
                    
                    if st.form_submit_button("Assign to Event", use_container_width=True):
                        if sel_staff:
                            new_entry = {
                                "Event_ID": eid,
                                "Staff_Name": sel_staff,
                                "Start_Time": s_time,
                                "End_Time": e_time,
                                "Payment_Status": "Pending",
                                "Type": "Standard" # Default type
                            }
                            # APPEND: This ensures we don't overwrite other staff
                            df_staffing = pd.concat([df_staffing, pd.DataFrame([new_entry])], ignore_index=True)
                            conn.update(worksheet="Event_Staffing", data=df_staffing)
                            st.success(f"Added {sel_staff}!")
                            st.rerun()
        else:
            st.caption("Only Admins can modify the roster.")

    # ==========================================
    # 💰 TAB 5: SALES (Balanced Layout)
    # ==========================================
    with tab_sales:
        # 1. FETCH DATA (Same as before)
        @st.cache_data(ttl=600)
        def get_sales_data():
            return conn.read(worksheet="Event_Sales")

        df_master_events = get_data("Events") 
        df_sales_dest = get_sales_data()

        event_info = df_master_events[df_master_events['Event_ID'] == eid]
        venue_name = event_info.iloc[0]['Venue'] if not event_info.empty else "Unknown"
        is_multi = str(event_info.iloc[0].get('Is_Multi_Day', 'No')) == "Yes"
        
        # METRICS
        day_total = 0.0
        grand_total = 0.0
        if not df_sales_dest.empty:
            day_total = df_sales_dest[df_sales_dest['Event_ID'] == eid]['Total_Gross_Sales'].sum()
            venue_history = df_sales_dest[df_sales_dest['Event_Venue'] == venue_name]
            grand_total = venue_history['Total_Gross_Sales'].sum()
        
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("Today's Gross", f"${day_total:,.2f}")
        if is_multi:
            m_col2.metric("Event Total (All Days)", f"${grand_total:,.2f}")
        
        st.divider()

        # 2. FORM STATE
        if "form_id" not in st.session_state: st.session_state.form_id = 0
        if "fill_val" not in st.session_state: st.session_state.fill_val = 0.0

        # 3. THE FRAGMENT
        @st.fragment
        def render_sales_form():
            st.subheader(f"📝 Sales Entry: {selected_report_date.strftime('%d/%m/%Y')}")
            fid = st.session_state.form_id
            
            # --- STEP 1: TOTAL PAYMENTS ---
            st.markdown("#### 1. Total Payments")
            p1, p2 = st.columns(2)
            v_eftpos = p1.number_input("Card / Eftpos", min_value=0.0, step=1.0, key=f"eftpos_{fid}")
            v_cash = p2.number_input("Cash", min_value=0.0, step=1.0, key=f"cash_{fid}")
            
            t_gross = v_eftpos + v_cash
            st.markdown(f"### Gross Total: :green[${t_gross:,.2f}]")
            st.divider()
            
            # --- STEP 2: CATEGORY INPUTS ---
            st.markdown("#### 2. Categories")
            c1, c2, c3, c4 = st.columns(4)
            v_quick = c1.number_input("Quick", min_value=0.0, step=1.0, key=f"quick_{fid}")
            v_food = c2.number_input("Food", min_value=0.0, step=1.0, key=f"food_{fid}")
            v_drinks = c3.number_input("Drinks", min_value=0.0, step=1.0, key=f"drinks_{fid}")
            
            # Uncategorised Input
            v_uncat = c4.number_input(
                "Uncategorised", 
                min_value=0.0, 
                step=1.0, 
                value=st.session_state.fill_val, 
                key=f"uncat_{fid}"
            )
            # This ensures that if you manually type in Uncategorised, the state updates
            st.session_state.fill_val = v_uncat

            # --- STEP 3: BALANCING & FILL ---
            # Moved after inputs for better flow
            cat_sum = v_quick + v_food + v_drinks + v_uncat
            diff = t_gross - cat_sum
            
            st.divider()
            
            if abs(diff) > 0.01: # Use small float check instead of 0
                b_col1, b_col2 = st.columns([2, 1])
                b_col1.warning(f"⚠️ **Remaining to balance: ${diff:,.2f}**")
                
                # Show Fill button if there is a gap
                if diff > 0:
                    if b_col2.button(f"Auto-Fill ${diff:,.0f}", use_container_width=True):
                        # Add current diff to whatever is already in Uncategorised
                        st.session_state.fill_val = float(v_uncat + diff)
                        st.rerun(scope="fragment")
            else:
                st.success("✅ Totals Balance Perfectly!")

            # --- SAVE LOGIC ---
            if round(t_gross, 2) == round(cat_sum, 2) and t_gross > 0:
                if st.button("💾 Save Sales Record", use_container_width=True, type="primary"):
                    new_row = {
                        "Event_ID": eid, "Event_Date": selected_report_date.strftime('%d/%m/%Y'),
                        "Event_Venue": venue_name, "Eftpos": v_eftpos, "Cash": v_cash,
                        "Total_Gross_Sales": t_gross, "Total_Quick": v_quick,
                        "Total_Food": v_food, "Total_Drinks": v_drinks, "Total_Uncategorised": v_uncat
                    }
                    try:
                        fresh_df = conn.read(worksheet="Event_Sales", ttl=0)
                        updated_df = pd.concat([fresh_df, pd.DataFrame([new_row])], ignore_index=True)
                        conn.update(worksheet="Event_Sales", data=updated_df)
                        
                        # Reset UI
                        st.session_state.form_id += 1
                        st.session_state.fill_val = 0.0
                        st.cache_data.clear() 
                        st.success("✅ Saved!")
                        time.sleep(1)
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Error: {e}")

        # 4. EXECUTE
        render_sales_form()


   
