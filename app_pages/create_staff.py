import streamlit as st
import pandas as pd
import re

def show_create_staff(get_data, conn):
    st.title("👤 Staff Onboarding")

    # --- 🛡️ 1. DATA CACHING ---
    # We pull data once per session or every few minutes to stop the "Loading" loop
    df_staff_db = get_data("Staff_Database")
    df_staff_auth = get_data("Staff")

    # --- 2. CORE INFO (Outside form to keep it snappy) ---
    st.subheader("📋 Personal & Contact Details")
    
    col1, col2 = st.columns([2, 1])
    s_name = col1.text_input("Full Name*")
    s_role = col2.selectbox("Primary Role", ["Staff", "Supervisor", "Manager", "Admin"])

    col3, col4 = st.columns(2)
    s_phone = col3.text_input("Phone Number*")
    s_email = col4.text_input("Email Address")
    
    s_address = st.text_input("Residential Address")

    st.divider()
    
    # --- 3. PAYROLL & SKILLS ---
    st.subheader("💰 Payroll & Skills")
    p1, p2 = st.columns(2)
    s_rate = p1.number_input("Hourly Rate ($)", min_value=0.0, step=0.50, value=30.0)
    s_tfn = p2.text_input("TFN (Tax File Number)")
    s_skills = st.text_area("Skills / Certifications", placeholder="e.g. RSA, Forklift", height=68)

    st.divider()

    # --- 4. THE APP ACCESS SECTION ---
    # We use a container to keep things organized
    with st.container(border=True):
        st.subheader("🛡️ App Access")
        enable_app = st.toggle("Enable App Access / Generate Login PIN", value=False)
        
        a1, a2 = st.columns(2)
        # Login email defaults to personal email if toggle is flipped
        login_email = a1.text_input("Login Email (for App)", value=s_email if enable_app else "", disabled=not enable_app)
        s_pin = a2.text_input("System PIN (4 Digits)", max_chars=4, disabled=not enable_app, placeholder="1234")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- 5. SUBMIT ACTION ---
    if st.button("🚀 Initialize Staff Member", use_container_width=True, type="primary"):
        # Basic validation
        is_phone = len(re.sub(r'\D', '', s_phone)) >= 10
        
        if not s_name or not is_phone:
            st.error("Please provide a Name and a valid 10-digit Phone Number.")
        elif enable_app and (not login_email or len(s_pin) != 4):
            st.error("For App Access, a Login Email and 4-digit PIN are required.")
        elif not df_staff_db.empty and s_name in df_staff_db['Staff_Name'].values:
            st.error(f"Staff member '{s_name}' already exists.")
        else:
            with st.spinner("Writing to Google Sheets..."):
                # --- 💾 DB RECORD ---
                new_db = {
                    "Staff_Name": s_name, "Phone": s_phone, "Address": s_address,
                    "Rating": 5.0, "Hourly_Rate": s_rate, "Skills": s_skills, "TFN": s_tfn
                }
                
                # --- 💾 AUTH RECORD ---
                if enable_app:
                    new_auth = {
                        "Email": login_email, "Name": s_name, "Role": s_role,
                        "PIN": s_pin, "Type": "Casual", "Phone": s_phone
                    }
                    # Update Staff Sheet
                    updated_auth = pd.concat([df_staff_auth, pd.DataFrame([new_auth])], ignore_index=True)
                    conn.update(worksheet="Staff", data=updated_auth)

                # Update Database Sheet
                updated_db = pd.concat([df_staff_db, pd.DataFrame([new_db])], ignore_index=True)
                conn.update(worksheet="Staff_Database", data=updated_db)

                st.success(f"Successfully initialized {s_name}!")
                st.balloons()