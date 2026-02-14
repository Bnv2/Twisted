import streamlit as st
import pandas as pd

def render_reports_tab(eid, selected_report_date, db, get_data):
    """
    Modular Daily Report Tab for Event Workspace.
    """
    rep_date_str = selected_report_date.strftime('%d/%m/%Y')
    st.subheader(f"📝 Report: {selected_report_date.strftime('%A, %d %b')}")
    
    # 1. FETCH DATA
    df_rep = get_data("Event_Reports")
    
    # --- CRITICAL: Normalize Column Names ---
    df_rep.columns = [str(c).strip() for c in df_rep.columns]
    
    # 2. FILTER FOR SPECIFIC DAY
    if not df_rep.empty and 'Event_ID' in df_rep.columns:
        day_match = df_rep[(df_rep['Event_ID'].astype(str) == str(eid)) & 
                           (df_rep['Report_Date'] == rep_date_str)]
        curr_rep = day_match.iloc[0] if not day_match.empty else {}
    else:
        curr_rep = {}

    # --- DATA CLEANING ---
    raw_stalls = curr_rep.get("Other_Stalls", 0)
    try:
        clean_stalls = int(float(raw_stalls)) if pd.notna(raw_stalls) and str(raw_stalls).strip() != "" else 0
    except (ValueError, TypeError):
        clean_stalls = 0

    # --- WEATHER SAFETY ---
    weather_options = ["Sunny", "Cloudy", "Rainy", "Windy", "Heat"]
    saved_weather = curr_rep.get("Weather", "Sunny")
    w_index = weather_options.index(saved_weather) if saved_weather in weather_options else 0

    # 3. REPORT FORM
    with st.form("daily_rep", border=True):
        c1, c2 = st.columns(2)
        weather = c1.selectbox("☀️ Weather", options=weather_options, index=w_index)
        
        t_leave = c1.text_input("🚗 Time Leave House", value=curr_rep.get("Time_Leave", "06:00"))
        t_reach = c1.text_input("📍 Time Reach Site", value=curr_rep.get("Time_Reach", "07:30"))
        
        stalls = c2.number_input("🍟 Other Stalls", min_value=0, value=clean_stalls)
        
        water = c2.toggle("🚰 Water Access?", value=(curr_rep.get("Water_Access") == "Yes"))
        power = c2.toggle("🔌 Power Access?", value=(curr_rep.get("Power_Access") == "Yes"))
        gen = st.text_area("✍️ General Comments", value=str(curr_rep.get("General_Comments", "")))
        
        # 4. SAVE LOGIC
        save_btn = st.form_submit_button("💾 Save Daily Report", use_container_width=True)
        
        if save_btn:
            new_report_row = {
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
            
            # SUPABASE MIGRATION: Update-by-Replacement logic
            if not df_rep.empty and 'Event_ID' in df_rep.columns:
                mask = (df_rep['Event_ID'].astype(str) == str(eid)) & (df_rep['Report_Date'] == rep_date_str)
                df_rep_updated = pd.concat([df_rep[~mask], pd.DataFrame([new_report_row])], ignore_index=True)
            else:
                df_rep_updated = pd.DataFrame([new_report_row])
            
            # Push update to Supabase
            if db.update_table("Event_Reports", df_rep_updated):
                st.cache_data.clear() 
                st.success(f"Report for {rep_date_str} Saved!")
                st.rerun()