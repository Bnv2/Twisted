import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re
import random
from datetime import datetime, timedelta

# 1. Custom Module Imports
from modules.auth import send_admin_code, nuclear_clean
from modules.drive_utils import upload_to_drive

# 2. Page Imports
from app_pages.home import show_home
from app_pages.create_event import show_create_event
from app_pages.staff import show_staff
from app_pages.logs import show_logs
from app_pages.all_events import show_all_events
from app_pages.event_workspace import show_event_workspace
from app_pages.create_staff import show_create_staff


# --- CONFIG ---
st.set_page_config(page_title="Twisted Potato Hub", layout="wide", page_icon="🚚")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ROLE PERMISSIONS ---
PAGE_PERMISSIONS = {
    "🏠 Event Hub": ["Admin", "Staff", "Manager", "Logistics"],
    "➕ Create Event":    ["Admin", "Manager"],
    "👥 Staff":          ["Admin"],
    "📦 Inventory":      ["Admin", "Logistics", "Manager"],
    "📂 Workspace":      ["Admin", "Staff", "Manager", "Logistics"],
    "📜 History":        ["Admin"],
    "🗂️ All Events Archive": ["Admin", "Staff", "Manager"],
}

# --- SESSION STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "🏠 Event Hub"
if "user_role" not in st.session_state:
    st.session_state.user_role = "Staff"
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --- GLOBAL HELPERS ---
def get_data(sheet_name):
    try:
        return conn.read(worksheet=sheet_name, ttl=0)
    except Exception:
        return pd.DataFrame()

# ==========================================
# 🔐 AUTHENTICATION LAYER
# ==========================================
if not st.session_state.authenticated:
    st.title("🔐 Staff Login")
    staff_df = get_data("Staff")
    
    if not staff_df.empty:
        staff_df['Email'] = staff_df['Email'].astype(str).str.lower().str.strip()
        # Using the helper we defined in this file for the login specifically
        staff_df['PIN'] = staff_df['PIN'].apply(nuclear_clean)

    with st.container(border=True):
        email_in = st.text_input("Staff Email", key="auth_email_input").lower().strip()
        pin_in = st.text_input("Enter PIN or Recovery Code", type="password", key="auth_pin_input").strip()
        clean_input = re.sub(r'\D', '', pin_in) 
        
        col_login, col_req = st.columns(2)
        
        if col_login.button("Login", use_container_width=True):
            if "recovery_code" in st.session_state and pin_in == st.session_state.recovery_code:
                st.session_state.authenticated = True
                st.session_state.user_email = email_in
                st.session_state.user_role = "Admin"
                del st.session_state.recovery_code 
                st.rerun()
            else:
                user_match = staff_df[staff_df['Email'] == email_in]
                if not user_match.empty:
                    stored_pin = user_match.iloc[0]['PIN']
                    if clean_input == stored_pin and clean_input != "":
                        st.session_state.authenticated = True
                        st.session_state.user_email = email_in
                        st.session_state.user_role = str(user_match.iloc[0].get('Role', 'Staff'))
                        st.rerun()
                    else:
                        st.error("❌ Invalid PIN.")
                else:
                    st.error("❌ Email not found.")

        if col_req.button("📧 Request Admin Link", use_container_width=True):
            recovery_target = str(st.secrets.get("ADMIN_RECOVERY_EMAIL", "")).lower().strip()
            if email_in == recovery_target and recovery_target != "":
                new_code = str(random.randint(1000, 9999))
                st.session_state.recovery_code = new_code
                if send_admin_code(email_in, new_code):
                    st.success(f"Security code sent to {email_in}")
                else:
                    st.error("Email service failed.")
            else:
                st.error("Unauthorized email.")

# 
# ==========================================
# 🏎️ MAIN APP ROUTING (POST-LOGIN)
# ==========================================
else:
    # --- SIDEBAR HEADER ---
    st.sidebar.title(f"👋 {st.session_state.user_email.split('@')[0].capitalize()}")
    st.sidebar.caption(f"Role: {st.session_state.user_role}")

    # --- 🔵 ACTION BUTTONS (TOP) ---
    if st.session_state.user_role == "Admin":
        col1, col2 = st.sidebar.columns(2)
        
        # Red Button (Primary)
        if col1.button("➕ Event", use_container_width=True, type="primary", help="Create New Event"):
            st.session_state.page = "➕ Create Event"
            st.rerun()
            
        # Blue/Standard Button (Secondary - we'll keep it standard for now)
        if col2.button("➕ Staff", use_container_width=True, type="secondary", help="Register New Staff"):
            # Note: You'll need to create app_pages/create_staff.py later
            st.session_state.page = "➕ Create Staff" 
            st.rerun()
        # new code =========================
        if st.session_state.user_role == "Manager":
            col1, col2 = st.sidebar.columns(2)
        
        # Red Button (Primary)
        if col1.button("➕ Event", use_container_width=True, type="primary", help="Create New Event"):
            st.session_state.page = "➕ Create Event"
            st.rerun()

    # new code end =======================
            
    st.sidebar.divider()

    # --- 📋 NAVIGATION MENU ---
    menu_items = [
        {"label": "🏠 Event Hub", "page": "🏠 Event Hub"},
        {"label": "🗂️ All Events Archive", "page": "🗂️ All Events Archive"},
        {"label": "👥 Staff List",     "page": "👥 Staff"},
        {"label": "📦 Logs",           "page": "📦 Inventory"},
    ]

    for item in menu_items:
        allowed = PAGE_PERMISSIONS.get(item["page"], ["Admin"])
        if st.session_state.user_role in allowed:
            if st.sidebar.button(item["label"], use_container_width=True):
                st.session_state.page = item["page"]
                st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    # --- THE ROUTER ---
    # This part actually triggers the functions inside your app_pages files
    page = st.session_state.page
    
    if page == "🏠 Event Hub":
        show_home(get_data, conn)
    elif page == "➕ Create Event":
        show_create_event(get_data, conn)
    elif page == "➕ Create Staff":
        from app_pages.create_staff import show_create_staff # Import here or at top
        show_create_staff(get_data, conn)
    elif page == "👥 Staff":
        show_staff(get_data, conn)
    elif page == "🗂️ All Events Archive": 
        show_all_events(get_data)
    elif page == "📦 Inventory":
        show_logs(get_data, conn)
    elif page == "📈 Event Workspace":    
        show_event_workspace(st.session_state.selected_event_id, get_data, conn)
