import streamlit as st
from streamlit_gsheets import GSheetsConnection
from modules.supabase_db import get_supabase
import pandas as pd
from pathlib import Path
from datetime import datetime

def migrate_all_data():
    """One-time migration from Google Sheets to Supabase"""
    
    print("🚀 Starting migration to Supabase...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Connect to both
    gsheets = st.connection("gsheets", type=GSheetsConnection)
    supabase = get_supabase()
    
    # Your 10 tables
    sheets = [
        "Staff",
        "Events",
        "Event_Financials",
        "Event_Contacts",
        "Logistics_Details",
        "Event_Reports",
        "Inventory",
        "Event_Sales",
        "Event_Staffing",
        "Staff_Database"
    ]
    
    # Create backup directory
    backup_dir = Path("data/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    successful = 0
    failed = 0
    
    for sheet_name in sheets:
        try:
            print(f"📥 Processing {sheet_name}...")
            
            # Read from Google Sheets
            df = gsheets.read(worksheet=sheet_name, ttl=0)
            
            if df.empty:
                print(f"  ⚠️  {sheet_name} is empty, skipping...\n")
                continue
            
            # Backup to CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_path = backup_dir / f"{sheet_name}_{timestamp}.csv"
            df.to_csv(csv_path, index=False)
            print(f"  💾 Backed up to {csv_path}")
            
            # Write to Supabase
            if supabase.update_table(sheet_name, df):
                print(f"  ✅ Migrated {len(df)} rows to Supabase")
                successful += 1
            else:
                print(f"  ❌ Failed to migrate {sheet_name}")
                failed += 1
            
            print()  # Blank line
            
        except Exception as e:
            print(f"  ❌ Error with {sheet_name}: {e}\n")
            failed += 1
    
    print("=" * 50)
    print(f"🎉 Migration Complete!")
    print(f"✅ Successful: {successful}/{len(sheets)}")
    print(f"❌ Failed: {failed}/{len(sheets)}")
    print(f"💾 Backups saved to: {backup_dir}")
    print("=" * 50)

if __name__ == "__main__":
    migrate_all_data()
