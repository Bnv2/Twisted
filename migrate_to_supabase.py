import streamlit as st
from streamlit_gsheets import GSheetsConnection
from modules.supabase_db import get_supabase
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def migrate_all_data():
    """One-time migration from Google Sheets to Supabase with Data Cleaning"""
    
    st.title("🚀 Supabase Migration Tool")
    st.info("Watch the logs in the bottom right for detailed progress.")
    
    print("🚀 Starting migration to Supabase...")
    
    # Connect to both
    try:
        gsheets = st.connection("gsheets", type=GSheetsConnection)
        supabase = get_supabase()
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return

    # Your 10 tables
    sheets = [
        "Staff", "Events", "Event_Financials", "Event_Contacts",
        "Logistics_Details", "Event_Reports", "Inventory", 
        "Event_Sales", "Event_Staffing", "Staff_Database"
    ]
    
    successful = 0
    failed = 0
    
    for sheet_name in sheets:
        try:
            print(f"📥 Processing {sheet_name}...")
            
            # 1. Read from Google Sheets
            df = gsheets.read(worksheet=sheet_name, ttl=0)
            
            if df.empty:
                print(f"  ⚠️  {sheet_name} is empty, skipping...")
                continue

            # --- 🛠️ FIX 1: CLEAN THE 'NAN' DATA ---
            # Replace 'NaN', 'inf', and empty strings with None so Supabase doesn't crash
            df = df.replace([np.nan, np.inf, -np.inf], None)
            # Ensure everything is a standard Python type
            df = df.where(pd.notnull(df), None)

            # --- 🛠️ FIX 2: HANDLE COLUMN MISMATCHES ---
            # If Google Sheets uses 'Cash' or 'Card', rename them to match your reverse_map
            if sheet_name == "Event_Sales":
                rename_map = {
                    "Cash": "Cash_Sales",
                    "Card": "Card_Sales",
                    "Total": "Total_Revenue"
                }
                df = df.rename(columns=rename_map)
            
            # 2. Write to Supabase
            # This calls the update_table function in your modules/supabase_db.py
            if supabase.update_table(sheet_name, df):
                st.success(f"✅ {sheet_name}: Migrated {len(df)} rows")
                print(f"  ✅ Migrated {len(df)} rows to Supabase")
                successful += 1
            else:
                st.error(f"❌ {sheet_name}: Failed to update table")
                failed += 1
            
        except Exception as e:
            st.error(f"❌ Error with {sheet_name}: {e}")
            print(f"  ❌ Error with {sheet_name}: {e}")
            failed += 1
    
    st.divider()
    st.balloons()
    st.write(f"🎉 Migration Complete! {successful}/{len(sheets)} successful.")

if __name__ == "__main__":
    migrate_all_data()
# import streamlit as st
# from streamlit_gsheets import GSheetsConnection
# from modules.supabase_db import get_supabase
# import pandas as pd
# from pathlib import Path
# from datetime import datetime

# def migrate_all_data():
#     """One-time migration from Google Sheets to Supabase"""
    
#     print("🚀 Starting migration to Supabase...")
#     print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
#     # Connect to both
#     gsheets = st.connection("gsheets", type=GSheetsConnection)
#     supabase = get_supabase()
    
#     # Your 10 tables
#     sheets = [
#         "Staff",
#         "Events",
#         "Event_Financials",
#         "Event_Contacts",
#         "Logistics_Details",
#         "Event_Reports",
#         "Inventory",
#         "Event_Sales",
#         "Event_Staffing",
#         "Staff_Database"
#     ]
    
#     # Create backup directory
#     backup_dir = Path("data/backups")
#     backup_dir.mkdir(parents=True, exist_ok=True)
    
#     successful = 0
#     failed = 0
    
#     for sheet_name in sheets:
#         try:
#             print(f"📥 Processing {sheet_name}...")
            
#             # Read from Google Sheets
#             df = gsheets.read(worksheet=sheet_name, ttl=0)
            
#             if df.empty:
#                 print(f"  ⚠️  {sheet_name} is empty, skipping...\n")
#                 continue
            
#             # Backup to CSV
#             timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#             csv_path = backup_dir / f"{sheet_name}_{timestamp}.csv"
#             df.to_csv(csv_path, index=False)
#             print(f"  💾 Backed up to {csv_path}")
            
#             # Write to Supabase
#             if supabase.update_table(sheet_name, df):
#                 print(f"  ✅ Migrated {len(df)} rows to Supabase")
#                 successful += 1
#             else:
#                 print(f"  ❌ Failed to migrate {sheet_name}")
#                 failed += 1
            
#             print()  # Blank line
            
#         except Exception as e:
#             print(f"  ❌ Error with {sheet_name}: {e}\n")
#             failed += 1
    
#     print("=" * 50)
#     print(f"🎉 Migration Complete!")
#     print(f"✅ Successful: {successful}/{len(sheets)}")
#     print(f"❌ Failed: {failed}/{len(sheets)}")
#     print(f"💾 Backups saved to: {backup_dir}")
#     print("=" * 50)

# if __name__ == "__main__":
#     migrate_all_data()
