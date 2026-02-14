#### new script 4 ####
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from modules.supabase_db import get_supabase
import pandas as pd
import numpy as np
import time

def migrate_ui():
    st.title("🎯 Final Table Migration: Event_Sales")
    
    st.info("Ensure you have clicked 'Reload PostgREST Config' in Supabase Settings -> API before running this.")

    if st.button("Finalize Event_Sales Migration"):
        db = get_supabase()
        gsheets = st.connection("gsheets", type=GSheetsConnection)
        
        # We are targeting ONLY the last failing table
        sheet_name = "Event_Sales"
        unique_key = "id" 

        try:
            df = gsheets.read(worksheet=sheet_name, ttl=0)
            if df is None or df.empty:
                st.warning("Sheet is empty.")
                return

            # 1. Clean NaN
            df_cleaned = df.replace({np.nan: None, pd.NA: None, pd.NaT: None})
            
            # 2. FORCE MAPPING: Rename Google Sheet columns to match your SQL table columns
            # Edit the right-hand side strings if your Supabase columns have different names
            rename_map = {
                "Cash": "cash",
                "Eftpos": "card_sales",  # or 'eftpos'
                "Total": "total_revenue",
                "Opening Float": "opening_float",
                "Closing Float": "closing_float"
            }
            df_cleaned = df_cleaned.rename(columns=rename_map)
            
            # 3. Standardize remaining columns
            df_cleaned.columns = [c.lower().strip() for c in df_cleaned.columns]

            # 4. Filter: Only keep columns that actually exist in your Supabase table
            # This prevents 'column does not exist' errors from extra columns in Sheets
            # Replace these with your ACTUAL Supabase column names for this table
            allowed_cols = ['id', 'event_id', 'cash', 'card_sales', 'total_revenue', 'opening_float', 'closing_float']
            df_final = df_cleaned[[c for c in allowed_cols if c in df_cleaned.columns]]

            data_dict = df_final.to_dict(orient='records')
            
            # 5. Push
            db.client.table("event_sales").upsert(data_dict, on_conflict=unique_key).execute()
            
            st.success(f"✅ {sheet_name}: Migrated {len(df_final)} rows. Database is now 100% complete!")
            st.balloons()

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.code("Try this SQL in Supabase if 'cash' column isn't found:\nALTER TABLE event_sales ADD COLUMN IF NOT EXISTS cash NUMERIC;")

if __name__ == "__main__":
    migrate_ui()


#### new script 4 end ####




# ### new script 3 ###
# import streamlit as st
# from streamlit_gsheets import GSheetsConnection
# from modules.supabase_db import get_supabase
# import pandas as pd
# import numpy as np
# import time

# def migrate_ui():
#     st.title("🚀 Final Cleanup Migration")
    
#     if st.button("Run Final Cleanup"):
#         db = get_supabase()
#         gsheets = st.connection("gsheets", type=GSheetsConnection)
        
#         # TARGETED CONFIG for the remaining errors
#         sheets_config = {
#             "Event_Contacts": "contact_id", # Reverted to contact_id as per your error log
#             "Event_Sales": "id"             # Standard ID
#         }

#         log_area = st.container(border=True)

#         for sheet_name, unique_key in sheets_config.items():
#             try:
#                 df = gsheets.read(worksheet=sheet_name, ttl=0)
#                 if df is None or df.empty:
#                     continue
                
#                 df_cleaned = df.replace({np.nan: None, pd.NA: None, pd.NaT: None})
#                 df_cleaned.columns = [c.lower().strip() for c in df_cleaned.columns]
                
#                 # Special fix for Event_Sales if the column is actually 'cash_sales' or similar
#                 # You can manually rename columns here if needed:
#                 # if sheet_name == "Event_Sales" and "cash" not in df_cleaned.columns:
#                 #     st.warning("Column 'cash' not found in Sheet. Available: " + str(list(df_cleaned.columns)))

#                 data_dict = df_cleaned.to_dict(orient='records')
                
#                 # Use UPSERT to overwrite duplicates
#                 db.client.table(sheet_name.lower()).upsert(data_dict, on_conflict=unique_key).execute()
                
#                 log_area.success(f"✅ {sheet_name}: Migrated {len(df_cleaned)} rows.")

#             except Exception as e:
#                 log_area.error(f"❌ {sheet_name}: {str(e)}")
        
#         st.info("💡 If Event_Sales still fails with 'schema cache', go to Supabase Settings -> API -> Reload PostgREST Config.")

# if __name__ == "__main__":
#     migrate_ui()

# ### end new script 3 ###



# ### new script 2 #### 7/9 tables worked 
# import streamlit as st
# from streamlit_gsheets import GSheetsConnection
# from modules.supabase_db import get_supabase
# import pandas as pd
# import numpy as np
# import time

# def migrate_ui():
#     st.title("🚀 Supabase Migration Tool")
    
#     # ADDED: Button to refresh Supabase cache if columns aren't being found
#     st.sidebar.warning("If 'Column Not Found' errors persist, go to Supabase -> Settings -> API -> 'Refresh PostgREST Cache'")

#     if st.button("Start Full Migration"):
#         db = get_supabase()
#         gsheets = st.connection("gsheets", type=GSheetsConnection)
        
#         # REVISED CONFIG: Based on your error logs
#         # If a table has no UNIQUE constraint, we set the key to None
#         sheets_config = {
#             "Staff": "email",
#             "Events": "event_id",
#             "Event_Financials": "id",
#             "Event_Contacts": "id",          # Changed from contact_id
#             "Logistics_Details": None,       # Removed unique constraint requirement
#             "Event_Reports": "id",           # Changed from report_id
#             "Event_Sales": "id",
#             "Event_Staffing": "id",
#             "Staff_Database": "id"           # Changed from email
#         }

#         progress_bar = st.progress(0)
#         log_area = st.container(border=True)

#         for i, (sheet_name, unique_key) in enumerate(sheets_config.items()):
#             try:
#                 # 1. Read
#                 df = gsheets.read(worksheet=sheet_name, ttl=0)
#                 if df is None or df.empty:
#                     log_area.warning(f"⚠️ {sheet_name}: Empty")
#                     continue
                
#                 # 2. Clean & Lowercase
#                 df_cleaned = df.replace({np.nan: None, pd.NA: None, pd.NaT: None})
#                 df_cleaned.columns = [c.lower().strip() for c in df_cleaned.columns]
                
#                 # 3. Date Fix
#                 for col in df_cleaned.columns:
#                     if 'date' in col or 'created_at' in col:
#                         df_cleaned[col] = pd.to_datetime(df_cleaned[col], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
#                         df_cleaned[col] = df_cleaned[col].replace({'NaT': None, np.nan: None})

#                 # 4. Push to Supabase
#                 data_dict = df_cleaned.to_dict(orient='records')
#                 table = db.client.table(sheet_name.lower())
                
#                 if unique_key:
#                     # Use upsert if we have a unique key
#                     table.upsert(data_dict, on_conflict=unique_key).execute()
#                 else:
#                     # Use normal insert if no unique constraint exists
#                     table.insert(data_dict).execute()
                
#                 log_area.success(f"✅ {sheet_name}: Migrated {len(df_cleaned)} rows.")
#                 progress_bar.progress((i + 1) / len(sheets_config))
#                 time.sleep(1)

#             except Exception as e:
#                 log_area.error(f"❌ {sheet_name}: {str(e)}")

#         st.balloons()

# if __name__ == "__main__":
#     migrate_ui()

# ### end new script 2 ####

# # ### new script 1 ### - worked for 50%

# # import streamlit as st
# # from streamlit_gsheets import GSheetsConnection
# # from modules.supabase_db import get_supabase
# # import pandas as pd
# # import numpy as np
# # import time

# # def migrate_ui():
# #     st.title("🚀 Supabase Migration Tool")
# #     st.info("This tool will pull data from Google Sheets and UPSERT it into Supabase.")

# #     if st.button("Start Full Migration"):
# #         db = get_supabase()
# #         gsheets = st.connection("gsheets", type=GSheetsConnection)
        
# #         sheets_config = {
# #             "Staff": "email",
# #             "Events": "event_id",
# #             "Event_Financials": "id",
# #             "Event_Contacts": "contact_id",
# #             "Logistics_Details": "event_id",
# #             "Event_Reports": "report_id",
# #             "Event_Sales": "id",
# #             "Event_Staffing": "id",
# #             "Staff_Database": "email"
# #         }

# #         progress_bar = st.progress(0)
# #         status_text = st.empty()
# #         log_area = st.container(border=True)

# #         for i, (sheet_name, unique_key) in enumerate(sheets_config.items()):
# #             try:
# #                 status_text.text(f"Processing {sheet_name}...")
                
# #                 # 1. Read
# #                 df = gsheets.read(worksheet=sheet_name, ttl=0)
                
# #                 if df is not None and not df.empty:
# #                     # 2. Clean
# #                     df_cleaned = df.replace({np.nan: None, pd.NA: None, pd.NaT: None})
# #                     df_cleaned.columns = [c.lower().strip() for c in df_cleaned.columns]
                    
# #                     # 3. Fix Dates
# #                     for col in df_cleaned.columns:
# #                         if 'date' in col or 'created_at' in col:
# #                             df_cleaned[col] = pd.to_datetime(df_cleaned[col], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
# #                             df_cleaned[col] = df_cleaned[col].replace({'NaT': None, np.nan: None})

# #                     # 4. Push
# #                     data_dict = df_cleaned.to_dict(orient='records')
# #                     db.client.table(sheet_name.lower()).upsert(data_dict, on_conflict=unique_key.lower()).execute()
                    
# #                     log_area.success(f"✅ {sheet_name}: Migrated {len(df_cleaned)} rows.")
# #                 else:
# #                     log_area.warning(f"⚠️ {sheet_name}: Sheet is empty.")

# #                 # Update Progress
# #                 progress_bar.progress((i + 1) / len(sheets_config))
# #                 time.sleep(1) # Breath for the API

# #             except Exception as e:
# #                 log_area.error(f"❌ {sheet_name}: {str(e)}")

# #         st.balloons()
# #         st.success("Migration Process Finished!")

# # if __name__ == "__main__":
# #     migrate_ui()
# #### end new script 1 ####







# # import streamlit as st
# # from streamlit_gsheets import GSheetsConnection
# # from modules.supabase_db import get_supabase
# # import pandas as pd
# # import numpy as np
# # import time

# # def clean_dates(df, date_columns):
# #     for col in date_columns:
# #         if col in df.columns:
# #             df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
# #             df[col] = df[col].dt.strftime('%Y-%m-%d').replace({np.nan: None})
# #     return df

# # def migrate_all_data():
# #     st.title("🎯 Final Table Migration")
    
# #     gsheets = st.connection("gsheets", type=GSheetsConnection)
# #     supabase = get_supabase()

# #     # We are ONLY doing the one that failed
# #     sheets = ["Event_Sales"]

# #     for sheet_name in sheets:
# #         try:
# #             st.write(f"📥 Fetching {sheet_name}...")
# #             df = gsheets.read(worksheet=sheet_name, ttl=0)
            
# #             if df.empty: continue

# #             # Clean NaN/Inf
# #             df = df.replace([np.nan, np.inf, -np.inf], None)
# #             df = df.where(pd.notnull(df), None)

# #             # --- THE FINAL FIX: Drop ALL non-database columns ---
# #             if sheet_name == "Event_Sales":
# #                 # Rename the columns we want to keep first
# #                 df = df.rename(columns={
# #                     "Eftpos": "Card_Sales",
# #                     "Cash": "Cash_Sales",
# #                     "Total": "Total_Revenue",
# #                     "Opening Float": "Opening_Float",
# #                     "Closing Float": "Closing_Float"
# #                 })
                
# #                 # List ONLY the columns that exist in your Supabase 'event_sales' table
# #                 allowed_columns = [
# #                     'Event_ID', 'Opening_Float', 'Cash_Sales', 
# #                     'Card_Sales', 'Closing_Float', 'Total_Revenue'
# #                 ]
                
# #                 # Drop everything else (like Event_Venue, Event_Date, etc.)
# #                 existing_allowed = [c for c in allowed_columns if c in df.columns]
# #                 df = df[existing_allowed]

# #             if supabase.update_table(sheet_name, df):
# #                 st.success(f"✅ {sheet_name} Migrated! Database is now 100% complete.")
# #                 st.balloons()
# #             else:
# #                 st.error(f"❌ {sheet_name} Failed. Check Supabase column names.")

# #         except Exception as e:
# #             st.error(f"Error: {e}")

# # if __name__ == "__main__":
# #     migrate_all_data()
# # # import streamlit as st
# # # from streamlit_gsheets import GSheetsConnection
# # # from modules.supabase_db import get_supabase
# # # import pandas as pd
# # # import numpy as np
# # # import time  # Added to fix the 429 error

# # # def clean_dates(df, date_columns):
# # #     for col in date_columns:
# # #         if col in df.columns:
# # #             df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
# # #             df[col] = df[col].dt.strftime('%Y-%m-%d').replace({np.nan: None})
# # #     return df

# # # def migrate_all_data():
# # #     st.title("🚀 Final Migration Push")
    
# # #     gsheets = st.connection("gsheets", type=GSheetsConnection)
# # #     supabase = get_supabase()

# # #     # We only need to focus on the ones that failed or were skipped
# # #     sheets = [
# # #         "Event_Sales", 
# # #         "Event_Staffing", 
# # #         "Staff_Database"
# # #     ]

# # #     for sheet_name in sheets:
# # #         try:
# # #             st.write(f"📥 Fetching {sheet_name}...")
# # #             df = gsheets.read(worksheet=sheet_name, ttl=0)
            
# # #             # --- FIX: Handling Google's Rate Limit ---
# # #             time.sleep(2) # Wait 2 seconds between sheets to avoid 429 errors

# # #             if df.empty: continue

# # #             # Clean NaN
# # #             df = df.replace([np.nan, np.inf, -np.inf], None)
# # #             df = df.where(pd.notnull(df), None)

# # #             # --- FIX: Event_Sales Specific Clean up ---
# # #             if sheet_name == "Event_Sales":
# # #                 # Remove 'Event_Date' because it's not in your SQL Table 8
# # #                 if 'Event_Date' in df.columns:
# # #                     df = df.drop(columns=['Event_Date'])
                
# # #                 df = df.rename(columns={
# # #                     "Eftpos": "Card_Sales",
# # #                     "Cash": "Cash_Sales",
# # #                     "Total": "Total_Revenue",
# # #                     "Opening Float": "Opening_Float",
# # #                     "Closing Float": "Closing_Float"
# # #                 })

# # #             # Format Dates
# # #             date_cols = ['Date', 'End_Date', 'Rent_Paid_Date', 'Rent_Due_Date', 'Payment_Date', 'Due_Date', 'Report_Date']
# # #             df = clean_dates(df, date_cols)

# # #             if supabase.update_table(sheet_name, df):
# # #                 st.success(f"✅ {sheet_name} Migrated!")
# # #             else:
# # #                 st.error(f"❌ {sheet_name} Failed.")

# # #         except Exception as e:
# # #             if "429" in str(e):
# # #                 st.error(f"🛑 Google is rate-limiting us. Wait 1 minute and refresh.")
# # #             else:
# # #                 st.error(f"Error on {sheet_name}: {e}")

# # # if __name__ == "__main__":
# # #     migrate_all_data()
# # # # import streamlit as st
# # # # from streamlit_gsheets import GSheetsConnection
# # # # from modules.supabase_db import get_supabase
# # # # import pandas as pd
# # # # import numpy as np

# # # # def clean_dates(df, date_columns):
# # # #     """Convert DD/MM/YYYY to YYYY-MM-DD for Supabase"""
# # # #     for col in date_columns:
# # # #         if col in df.columns:
# # # #             # Dayfirst=True handles the DD/MM/YYYY format
# # # #             df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
# # # #             # Convert to string format YYYY-MM-DD or None if invalid
# # # #             df[col] = df[col].dt.strftime('%Y-%m-%d').replace({np.nan: None})
# # # #     return df

# # # # def migrate_all_data():
# # # #     st.title("🚀 Finalizing Migration")
    
# # # #     gsheets = st.connection("gsheets", type=GSheetsConnection)
# # # #     supabase = get_supabase()

# # # #     sheets = [
# # # #         "Staff", "Events", "Event_Financials", "Event_Contacts",
# # # #         "Logistics_Details", "Event_Reports", "Inventory", 
# # # #         "Event_Sales", "Event_Staffing", "Staff_Database"
# # # #     ]

# # # #     for sheet_name in sheets:
# # # #         try:
# # # #             df = gsheets.read(worksheet=sheet_name, ttl=0)
# # # #             if df.empty: continue

# # # #             # --- FIX 1: Cleaning NaN/Infinity ---
# # # #             df = df.replace([np.nan, np.inf, -np.inf], None)
# # # #             df = df.where(pd.notnull(df), None)

# # # #             # --- FIX 2: Formatting Dates ---
# # # #             # List every column that contains a date in your Google Sheets
# # # #             date_cols = ['Date', 'End_Date', 'Rent_Paid_Date', 'Rent_Due_Date', 
# # # #                          'Payment_Date', 'Due_Date', 'Report_Date']
# # # #             df = clean_dates(df, date_cols)

# # # #             # --- FIX 3: Column Mappings ---
# # # #             if sheet_name == "Event_Sales":
# # # #                 df = df.rename(columns={
# # # #                     "Eftpos": "Card_Sales",     # Fixes the 'Eftpos' error
# # # #                     "Cash": "Cash_Sales",
# # # #                     "Total": "Total_Revenue",
# # # #                     "Opening Float": "Opening_Float",
# # # #                     "Closing Float": "Closing_Float"
# # # #                 })

# # # #             if supabase.update_table(sheet_name, df):
# # # #                 st.success(f"✅ {sheet_name} Migrated!")
# # # #             else:
# # # #                 st.error(f"❌ {sheet_name} Failed.")

# # # #         except Exception as e:
# # # #             st.error(f"Error on {sheet_name}: {e}")

# # # # if __name__ == "__main__":
# # # #     migrate_all_data()
# # # # # import streamlit as st
# # # # # from streamlit_gsheets import GSheetsConnection
# # # # # from modules.supabase_db import get_supabase
# # # # # import pandas as pd
# # # # # import numpy as np
# # # # # from pathlib import Path
# # # # # from datetime import datetime

# # # # # def migrate_all_data():
# # # # #     """One-time migration from Google Sheets to Supabase with Data Cleaning"""
    
# # # # #     st.title("🚀 Supabase Migration Tool")
# # # # #     st.info("Watch the logs in the bottom right for detailed progress.")
    
# # # # #     print("🚀 Starting migration to Supabase...")
    
# # # # #     # Connect to both
# # # # #     try:
# # # # #         gsheets = st.connection("gsheets", type=GSheetsConnection)
# # # # #         supabase = get_supabase()
# # # # #     except Exception as e:
# # # # #         st.error(f"Connection Error: {e}")
# # # # #         return

# # # # #     # Your 10 tables
# # # # #     sheets = [
# # # # #         "Staff", "Events", "Event_Financials", "Event_Contacts",
# # # # #         "Logistics_Details", "Event_Reports", "Inventory", 
# # # # #         "Event_Sales", "Event_Staffing", "Staff_Database"
# # # # #     ]
    
# # # # #     successful = 0
# # # # #     failed = 0
    
# # # # #     for sheet_name in sheets:
# # # # #         try:
# # # # #             print(f"📥 Processing {sheet_name}...")
            
# # # # #             # 1. Read from Google Sheets
# # # # #             df = gsheets.read(worksheet=sheet_name, ttl=0)
            
# # # # #             if df.empty:
# # # # #                 print(f"  ⚠️  {sheet_name} is empty, skipping...")
# # # # #                 continue

# # # # #             # --- 🛠️ FIX 1: CLEAN THE 'NAN' DATA ---
# # # # #             # Replace 'NaN', 'inf', and empty strings with None so Supabase doesn't crash
# # # # #             df = df.replace([np.nan, np.inf, -np.inf], None)
# # # # #             # Ensure everything is a standard Python type
# # # # #             df = df.where(pd.notnull(df), None)

# # # # #             # --- 🛠️ FIX 2: HANDLE COLUMN MISMATCHES ---
# # # # #             # If Google Sheets uses 'Cash' or 'Card', rename them to match your reverse_map
# # # # #             if sheet_name == "Event_Sales":
# # # # #                 rename_map = {
# # # # #                     "Cash": "Cash_Sales",
# # # # #                     "Card": "Card_Sales",
# # # # #                     "Total": "Total_Revenue"
# # # # #                 }
# # # # #                 df = df.rename(columns=rename_map)
            
# # # # #             # 2. Write to Supabase
# # # # #             # This calls the update_table function in your modules/supabase_db.py
# # # # #             if supabase.update_table(sheet_name, df):
# # # # #                 st.success(f"✅ {sheet_name}: Migrated {len(df)} rows")
# # # # #                 print(f"  ✅ Migrated {len(df)} rows to Supabase")
# # # # #                 successful += 1
# # # # #             else:
# # # # #                 st.error(f"❌ {sheet_name}: Failed to update table")
# # # # #                 failed += 1
            
# # # # #         except Exception as e:
# # # # #             st.error(f"❌ Error with {sheet_name}: {e}")
# # # # #             print(f"  ❌ Error with {sheet_name}: {e}")
# # # # #             failed += 1
    
# # # # #     st.divider()
# # # # #     st.balloons()
# # # # #     st.write(f"🎉 Migration Complete! {successful}/{len(sheets)} successful.")

# # # # # if __name__ == "__main__":
# # # # #     migrate_all_data()
# # # # # # import streamlit as st
# # # # # # from streamlit_gsheets import GSheetsConnection
# # # # # # from modules.supabase_db import get_supabase
# # # # # # import pandas as pd
# # # # # # from pathlib import Path
# # # # # # from datetime import datetime

# # # # # # def migrate_all_data():
# # # # # #     """One-time migration from Google Sheets to Supabase"""
    
# # # # # #     print("🚀 Starting migration to Supabase...")
# # # # # #     print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
# # # # # #     # Connect to both
# # # # # #     gsheets = st.connection("gsheets", type=GSheetsConnection)
# # # # # #     supabase = get_supabase()
    
# # # # # #     # Your 10 tables
# # # # # #     sheets = [
# # # # # #         "Staff",
# # # # # #         "Events",
# # # # # #         "Event_Financials",
# # # # # #         "Event_Contacts",
# # # # # #         "Logistics_Details",
# # # # # #         "Event_Reports",
# # # # # #         "Inventory",
# # # # # #         "Event_Sales",
# # # # # #         "Event_Staffing",
# # # # # #         "Staff_Database"
# # # # # #     ]
    
# # # # # #     # Create backup directory
# # # # # #     backup_dir = Path("data/backups")
# # # # # #     backup_dir.mkdir(parents=True, exist_ok=True)
    
# # # # # #     successful = 0
# # # # # #     failed = 0
    
# # # # # #     for sheet_name in sheets:
# # # # # #         try:
# # # # # #             print(f"📥 Processing {sheet_name}...")
            
# # # # # #             # Read from Google Sheets
# # # # # #             df = gsheets.read(worksheet=sheet_name, ttl=0)
            
# # # # # #             if df.empty:
# # # # # #                 print(f"  ⚠️  {sheet_name} is empty, skipping...\n")
# # # # # #                 continue
            
# # # # # #             # Backup to CSV
# # # # # #             timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
# # # # # #             csv_path = backup_dir / f"{sheet_name}_{timestamp}.csv"
# # # # # #             df.to_csv(csv_path, index=False)
# # # # # #             print(f"  💾 Backed up to {csv_path}")
            
# # # # # #             # Write to Supabase
# # # # # #             if supabase.update_table(sheet_name, df):
# # # # # #                 print(f"  ✅ Migrated {len(df)} rows to Supabase")
# # # # # #                 successful += 1
# # # # # #             else:
# # # # # #                 print(f"  ❌ Failed to migrate {sheet_name}")
# # # # # #                 failed += 1
            
# # # # # #             print()  # Blank line
            
# # # # # #         except Exception as e:
# # # # # #             print(f"  ❌ Error with {sheet_name}: {e}\n")
# # # # # #             failed += 1
    
# # # # # #     print("=" * 50)
# # # # # #     print(f"🎉 Migration Complete!")
# # # # # #     print(f"✅ Successful: {successful}/{len(sheets)}")
# # # # # #     print(f"❌ Failed: {failed}/{len(sheets)}")
# # # # # #     print(f"💾 Backups saved to: {backup_dir}")
# # # # # #     print("=" * 50)

# # # # # # if __name__ == "__main__":
# # # # # #     migrate_all_data()
