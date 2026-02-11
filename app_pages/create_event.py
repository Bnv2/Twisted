import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re

def show_create_event(get_data, conn):
    if st.session_state.user_role != "Admin":
        st.error("Access Denied.")
        st.session_state.page = "🏠 Home Dashboard"
        st.rerun()

    st.title("Register New Event")
    k = st.session_state.get('form_key', 0)
    
    # --- 📋 SECTION 1: CORE DETAILS ---
    with st.container(border=True):
        st.subheader("📋 1. Core Details")
        
        # Row 1: Venue, Type, Stall
        col_v1, col_v2, col_v3 = st.columns([2, 1, 1])
        venue = col_v1.text_input("Venue Name*", placeholder="Bondi Market", key=f"v_{k}")
        event_type = col_v2.selectbox("Event Type*", ["Market", "Festival", "School", "Ethnic", "Party", "Corporate", "Other"], key=f"etype_{k}")
        setup_type = col_v3.selectbox("Stall Type*", ["Truck", "Marquee", "Trailer", "Stall", "Other"], key=f"setup_{k}")
        
        # Row 2: Date logic (Clean side-by-side layout)
        d_col1, d_col2, d_col3 = st.columns([1.5, 1, 1.5])
        event_date = d_col1.date_input("Start Date*", datetime.now(), key=f"d_{k}")
        is_multi_day = d_col2.checkbox("Multi-day?", value=False, key=f"md_{k}")
        
        end_date = event_date
        if is_multi_day:
            end_date = d_col3.date_input("End Date*", event_date + timedelta(days=1), key=f"ed_{k}")
        else:
            # Displays a disabled placeholder so the UI doesn't "jump" when toggled
            d_col3.text_input("End Date", value=str(event_date), disabled=True, key=f"ed_dis_{k}")

    # --- 💰 SECTION 2: FINANCIALS ---
    with st.container(border=True):
        st.subheader("💰 2. Financials")
        fee_logic = st.radio("Fee Structure*", ["Fixed Rent", "Commission %", "Hybrid (Both)"], horizontal=True, key=f"flog_{k}")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            # LOGIC FIX: Only show relevant fields
            rent_val = 0.0
            comm_val = 0.0

            if fee_logic in ["Fixed Rent", "Hybrid (Both)"]:
                rent_val = st.number_input("Rent/Site Fee ($)", min_value=0.0, step=50.0, key=f"r_{k}")
            
            if fee_logic in ["Commission %", "Hybrid (Both)"]:
                comm_val = st.number_input("Commission Rate (%)", min_value=0.0, max_value=100.0, step=1.0, key=f"comm_{k}")

            rent_status = st.selectbox("Rent Status", ["Paid", "Due Later"], key=f"rs_{k}")
            date_input = st.date_input("Payment OR Due Date", datetime.now(), key=f"rd_val_{k}")

        with col_f2:
            deposit = st.number_input("Deposit ($)", min_value=0.0, step=50.0, key=f"dep_{k}")
            dep_paid = st.radio("Deposit Paid?", ["No", "Yes"], horizontal=True, key=f"dp_{k}")

    # --- 👤 SECTION 3: ORGANISER DETAILS ---
    with st.container(border=True):
        st.subheader("👤 3. Organiser Details")
        org_name = st.text_input("Primary Contact Name*", key=f"org_{k}")
        p1, p2 = st.columns(2)
        phone = p1.text_input("Phone Number*", key=f"p_{k}")
        email = p2.text_input("Email Address*", key=f"e_{k}")
        pref_contact = st.radio("Preferred Contact Method*", ["Phone", "Email"], horizontal=True, key=f"pref_{k}")
        
        clean_phone = re.sub(r'\s+', '', phone)
        is_valid_phone = bool(re.match(r'^(?:\+61|0)4\d{8}$', clean_phone))
        is_valid_email = bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))

    # --- 📍 SECTION 4: LOCATION & NOTES ---
    with st.container(border=True):
        st.subheader("📍 4. Location & Notes")
        address = st.text_input("Address", key=f"addr_{k}")
        notes = st.text_area("Internal Event Notes", key=f"notes_{k}")

    # --- 🚀 SUBMIT LOGIC ---
    st.divider()
    if st.button("🚀 Register Event", use_container_width=True, type="primary"):
        if not (venue and org_name and is_valid_phone and is_valid_email):
            st.error("Please fill all mandatory fields correctly.")
        else:
            with st.status("🛰️ Syncing Ledger...") as status:
                try:
                    eid = f"{event_date.strftime('%Y%m%d')}_{venue.replace(' ', '_').upper()[:10]}"
                    cid = f"CON_{datetime.now().strftime('%H%M%S')}" 
                    
                    row_event = {
                        "Event_ID": eid, "Date": str(event_date), "End_Date": str(end_date),
                        "Venue": venue, "Event_Type": event_type, "Address": address, 
                        "Status": "Planned", "Notes": notes
                    }
                    
                    row_finance = {
                        "Event_ID": eid, 
                        "Rent": rent_val, 
                        "Rent_Status": rent_status,
                        "Rent_Paid_Date": str(date_input) if rent_status == "Paid" else "",
                        "Rent_Due_Date": str(date_input) if rent_status == "Due Later" else "",
                        "Deposit": deposit,
                        "Deposit_Paid": dep_paid,
                        "Deposit_Refunded": "No",
                        "Fee_Structure": fee_logic,
                        "Commission_Rate": comm_val,
                        "Payment_Date": str(date_input) if rent_status == "Paid" else "",
                        "Due_Date": str(date_input) if rent_status == "Due Later" else ""
                    }
                    
                    row_logistics = {
                        "Event_ID": eid, "Setup_Type": setup_type, "Bump_In": "TBA", "Bump_Out": "TBA"
                    }
                    
                    row_contact = {
                        "Contact_ID": cid,
                        "Event_ID": eid, 
                        "Name": org_name, 
                        "Phone": clean_phone, 
                        "Email": email,
                        "Role": "Primary Contact",
                        "Pref_Method": pref_contact 
                    }

                    # APPEND DATA
                    conn.update(worksheet="Events", data=pd.concat([get_data("Events"), pd.DataFrame([row_event])], ignore_index=True))
                    conn.update(worksheet="Event_Financials", data=pd.concat([get_data("Event_Financials"), pd.DataFrame([row_finance])], ignore_index=True))
                    conn.update(worksheet="Logistics_Details", data=pd.concat([get_data("Logistics_Details"), pd.DataFrame([row_logistics])], ignore_index=True))
                    conn.update(worksheet="Event_Contacts", data=pd.concat([get_data("Event_Contacts"), pd.DataFrame([row_contact])], ignore_index=True))

                    status.update(label="✅ Success!", state="complete")
                    st.balloons()
                    st.session_state.form_key = k + 1
                    st.session_state.page = "🏠 Home Dashboard"
                    st.rerun()
                except Exception as e:
                    st.error(f"Sync failed: {e}")