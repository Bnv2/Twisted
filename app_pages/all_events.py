import streamlit as st
import pandas as pd
from datetime import datetime
from modules.ui_utils import render_mini_map 

def show_all_events(get_data):
    # --- 🎨 1. CSS STYLING (Matching Home Dashboard) ---
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

    st.title("🗂️ All Events Archive")
    st.write("Complete searchable history of all venue bookings.")

    # --- 🛰️ 2. DATA ACQUISITION ---
    df = get_data("Events")
    df_log_all = get_data("Logistics_Details")
    df_fin_all = get_data("Event_Financials")
    df_con_all = get_data("Event_Contacts")
    df_rep_all = get_data("Event_Reports")

    if df.empty:
        st.info("No records found."); return

    # Clean Dates
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['End_Date'] = pd.to_datetime(df.get('End_Date', df['Date']), dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])

    # --- 🛠️ 3. ADVANCED SEARCH & FILTERS ---
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        
        search_query = c1.text_input("🔍 Global Search", placeholder="Venue, ID, or Contact...").lower()
        
        # Filter by Type
        types = ["All"] + sorted(df['Event_Type'].dropna().unique().tolist())
        type_filter = c2.selectbox("🏷️ Event Type", types)
        
        # Filter by Year
        years = ["All"] + sorted(df['Date'].dt.year.unique().astype(str).tolist(), reverse=True)
        year_filter = c3.selectbox("📅 Year", years)

        # Sort Order
        sort_order = c4.selectbox("🔃 Sort", ["Newest First", "Oldest First", "Rent (High)"])

    # --- 🧪 4. FILTERING LOGIC ---
    filtered_df = df.copy()

    if search_query:
        # Check Venue and Event_ID
        filtered_df = filtered_df[
            filtered_df['Venue'].str.lower().str.contains(search_query) |
            filtered_df['Event_ID'].str.lower().str.contains(search_query)
        ]

    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['Event_Type'] == type_filter]

    if year_filter != "All":
        filtered_df = filtered_df[filtered_df['Date'].dt.year == int(year_filter)]

    # Sorting
    if sort_order == "Newest First":
        filtered_df = filtered_df.sort_values('Date', ascending=False)
    elif sort_order == "Oldest First":
        filtered_df = filtered_df.sort_values('Date', ascending=True)
    elif sort_order == "Rent (High)":
        # Merge rent to sort
        filtered_df = filtered_df.merge(df_fin_all[['Event_ID', 'Rent']], on="Event_ID", how="left")
        filtered_df = filtered_df.sort_values('Rent', ascending=False)

    # --- 🖼️ 5. GRID RENDERER (Archive Version) ---
    st.write(f"Showing **{len(filtered_df)}** events")
    
    grid_cols = st.columns(3)
    
    for idx, row in filtered_df.reset_index().iterrows():
        eid = row['Event_ID']
        address = row.get('Address', row['Venue'])
        
        # Cross-reference
        fin = df_fin_all[df_fin_all['Event_ID'] == eid].iloc[0] if not df_fin_all[df_fin_all['Event_ID'] == eid].empty else {}
        con = df_con_all[(df_con_all['Event_ID'] == eid)].iloc[0] if not df_con_all[df_con_all['Event_ID'] == eid].empty else {}
        log_match = df_log_all[df_log_all['Event_ID'] == eid]
        rep_match = df_rep_all[df_rep_all['Event_ID'] == eid]

        with grid_cols[idx % 3]:
            with st.container(border=True):
                # Title & ID
                st.markdown(f"### {row['Venue']}")
                st.caption(f"ID: `{eid}`")
                
                # Date
                dt_text = f"📅 **{row['Date'].strftime('%d %b %Y')}**"
                if pd.notnull(row['End_Date']) and row['Date'].date() != row['End_Date'].date():
                     dt_text = f"📅 **{row['Date'].strftime('%d %b')} – {row['End_Date'].strftime('%d %b %Y')}**"
                st.write(dt_text)

                # Contact & Rent Status
                c1, c2 = st.columns([2, 1])
                c1.caption(f"👤 {con.get('Name', 'Imported')}")
                r_stat = fin.get('Rent_Status', 'Paid')
                r_col = "#28a745" if r_stat == "Paid" else "#ffc107" 
                c2.markdown(f"<p style='text-align:right; margin:0;'><span class='status-badge' style='background-color:{r_col};'>💰 {r_stat}</span></p>", unsafe_allow_html=True)

                # Logistics Box
                if not log_match.empty:
                    log = log_match.iloc[0]
                    st.markdown(f"""
                        <div class="logistics-box">
                            <p style="margin:0; font-size: 0.85rem;">🚚 <b>{log.get('Setup_Type', 'Standard')}</b></p>
                            <p style="margin:0; font-size: 0.75rem;">🔽 In: {log.get('Bump_In', '--')} | 🔼 Out: {log.get('Bump_Out', '--')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.caption("🚚 Logistics: Legacy Import")

                # Weather or Report Status
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

                # Mini Map
                render_mini_map(address)
                
                # Open Workspace
                if st.button("📂 Open Workspace", key=f"arch_{eid}_{idx}", use_container_width=True):
                    st.session_state.selected_event_id = eid
                    st.session_state.page = "📈 Event Workspace"
                    st.rerun()