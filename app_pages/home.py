import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modules.ui_utils import render_mini_map 
from streamlit_gsheets import GSheetsConnection

# Keep your existing connection
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NEW DATA HANDLING START ---
if "data_loaded" not in st.session_state:
    # This runs ONLY ONCE. 
    # It fetches all 10 sheets and puts them in the app's memory.
    st.session_state.df_events = conn.read(worksheet="Events")
    st.session_state.df_logistics = conn.read(worksheet="Logistics_Details")
    st.session_state.df_finance = conn.read(worksheet="Event_Financials")
    st.session_state.df_contacts = conn.read(worksheet="Event_Contacts")
    st.session_state.df_reports = conn.read(worksheet="Event_Reports")
    # ... add your other 5 tabs here ...
    st.session_state.data_loaded = True
# --- NEW DATA HANDLING END ---

def show_home(get_data, conn):
    # --- 🎨 1. CSS STYLING (Restoring your Screenshot Look) ---
    st.markdown("""
        <style>
        .status-badge {
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.75rem;
            color: white;
            font-weight: bold;
        }
        .logistics-box {
            background-color: #f9f9f9; 
            padding: 10px; 
            border-radius: 8px; 
            border-left: 5px solid #FF4B4B; 
            margin: 8px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- TOP HEADER ---
    head_col, time_col = st.columns([3, 1])
    with head_col:
        st.title("🚀 Event Hub")
    with time_col:
        now = datetime.now().strftime("%d %b | %I:%M %p")
        st.markdown(f"<div style='text-align: right; color: gray; padding-top:20px;'>🕒 {now}</div>", unsafe_allow_html=True)

    # --- 🛰️ 2. DATA ACQUISITION & CLEANING ---
    df = get_data("Events")
    df_log_all = get_data("Logistics_Details")
    df_fin_all = get_data("Event_Financials")
    df_con_all = get_data("Event_Contacts")
    df_reports_all = get_data("Event_Reports")

    if df.empty:
        st.info("No events found in the database."); return

    # ✅ Fix: Convert dates to objects and handle the End_Date string error
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    if 'End_Date' not in df.columns:
        df['End_Date'] = df['Date']
    else:
        df['End_Date'] = pd.to_datetime(df['End_Date'], dayfirst=True, errors='coerce')

    # Drop invalid start dates and create simple date objects for filtering
    df = df.dropna(subset=['Date'])
    df['Date_Only'] = df['Date'].dt.date
    today = datetime.now().date()
    
    # --- 🛠️ 3. SEARCH & FILTERS ---
    col_search, col_setup = st.columns([2, 1])
    search_query = col_search.text_input("🔍 Search Venue", placeholder="Search...").lower()
    
    unique_setups = ["All"]
    if not df_log_all.empty:
        unique_setups += sorted(df_log_all['Setup_Type'].dropna().unique().tolist())
    setup_filter = col_setup.selectbox("🚚 Setup Type", unique_setups)

    # --- 🕒 4. RECENTLY COMPLETED (PAST 30 DAYS) ---
    past_limit = today - timedelta(days=30)
    # Filter using the Date_Only objects
    history_df = df[(df['Date_Only'] < today) & (df['Date_Only'] >= past_limit)].sort_values('Date', ascending=False)
    
    with st.expander("🕒 View Recently Completed (Past 30 Days)", expanded=False):
        render_grid(history_df, df_log_all, df_fin_all, df_con_all, df_reports_all, "past", search_query, setup_filter)

    st.divider()

    # --- 📅 5. UPCOMING SCHEDULE (ASCENDING) ---
    display_df = df[df['Date_Only'] >= today].sort_values('Date', ascending=True)
    st.subheader("📅 Upcoming Schedule")
    render_grid(display_df, df_log_all, df_fin_all, df_con_all, df_reports_all, "up", search_query, setup_filter)

# --- 🖼️ 6. GRID RENDERER HELPER ---
def render_grid(dataframe, df_log, df_fin, df_con, df_rep, prefix, search, setup_f):
    if dataframe.empty:
        st.write("No events match your criteria.")
        return

    # Final filter for search query
    if search:
        dataframe = dataframe[dataframe['Venue'].str.lower().str.contains(search)]

    grid_cols = st.columns(3)
    visible_idx = 0

    for idx, row in dataframe.iterrows():
        eid = row['Event_ID']
        address = row.get('Address', row['Venue'])
        
        # Cross-reference data
        fin = df_fin[df_fin['Event_ID'] == eid].iloc[0] if not df_fin[df_fin['Event_ID'] == eid].empty else {}
        con = df_con[(df_con['Event_ID'] == eid) & (df_con['Role'] == 'Primary Contact')].iloc[0] if not df_con[(df_con['Event_ID'] == eid) & (df_con['Role'] == 'Primary Contact')].empty else {}
        log_match = df_log[df_log['Event_ID'] == eid]
        rep_match = df_rep[df_rep['Event_ID'] == eid]

        # Setup Filter Check
        if setup_f != "All":
            if log_match.empty or log_match.iloc[0]['Setup_Type'] != setup_f:
                continue

        with grid_cols[visible_idx % 3]:
            with st.container(border=True):
                # Title
                st.markdown(f"### {row['Venue']}")
                
                # Date Formatting (Correctly handling Timestamp objects)
                dt_text = f"📅 **{row['Date'].strftime('%d %b')}**"
                if pd.notnull(row['End_Date']) and row['Date'].date() != row['End_Date'].date():
                     dt_text += f" – **{row['End_Date'].strftime('%d %b %Y')}**"
                st.write(dt_text)

                # Contact & Rent Status Badge
                c1, c2 = st.columns([2, 1])
                c1.caption(f"👤 {con.get('Name', 'TBA')}")
                r_stat = fin.get('Rent_Status', 'Due')
                r_col = "#28a745" if r_stat == "Paid" else "#ffc107" 
                c2.markdown(f"<p style='text-align:right; margin:0;'><span class='status-badge' style='background-color:{r_col};'>💰 {r_stat}</span></p>", unsafe_allow_html=True)

                # Logistics Box (Red Border Style)
                if not log_match.empty:
                    log = log_match.iloc[0]
                    st.markdown(f"""
                        <div class="logistics-box">
                            <p style="margin:0; font-size: 0.85rem;">🚚 <b>{log.get('Setup_Type', 'TBA')}</b></p>
                            <p style="margin:0; font-size: 0.75rem;">🔽 In: {log.get('Bump_In', '--')} | 🔼 Out: {log.get('Bump_Out', '--')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.caption("🚚 Logistics: Pending")

                # Weather or Forecast
                if not rep_match.empty:
                    rep = rep_match.iloc[0]
                    st.success(f"☀️ **Recorded:** {rep.get('Weather', 'Sunny')}")
                else:
                    search_q = f"weather+at+{str(address).replace(' ', '+')}+on+{row['Date'].strftime('%Y-%m-%d')}"
                    st.markdown(f"""
                        <a href="https://www.google.com/search?q={search_q}" target="_blank" style="text-decoration: none;">
                            <div style="background-color: #e8f0fe; color: #1967d2; padding: 8px; border-radius: 8px; text-align: center; font-size: 0.75rem; border: 1px solid #d2e3fc; margin-bottom: 8px;">
                                🌤️ <b>Check Forecast</b>
                            </div>
                        </a>        
                    """, unsafe_allow_html=True)

                # Map Preview
                render_mini_map(address)
                
                if st.button("📈 Open Workspace", key=f"btn_{prefix}_{eid}_{idx}", use_container_width=True):
                    st.session_state.selected_event_id = eid
                    st.session_state.page = "📈 Event Workspace"
                    st.rerun()
        visible_idx += 1
        
